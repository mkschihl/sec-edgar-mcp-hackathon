"""Build xbrl_concepts_data.py from the FASB US-GAAP 2026 taxonomy.

Usage (run once from the repo root):
    python toolkits/sec_edgar_tools/build_xbrl_concepts.py \\
        --lab  .bob/artifacts/us-gaap-2026/elts/us-gaap-lab-2026.xml \\
        --xsd  .bob/artifacts/us-gaap-2026/elts/us-gaap-2026.xsd \\
        --out  toolkits/sec_edgar_tools/xbrl_concepts_data.py

The generated file is committed; the taxonomy source files are not.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from xml.etree import ElementTree as ET

# XML namespace shortcuts
_NS_XS   = "http://www.w3.org/2001/XMLSchema"
_NS_XBRL = "http://xbrl.org/2006/xbrldi"          # not used, just for reference
_NS_LINK = "http://www.xbrl.org/2003/linkbase"
_NS_XLINK = "http://www.w3.org/1999/xlink"

_MONETARY = "xbrli:monetaryItemType"
_SHARES   = "xbrli:sharesItemType"
_PER_SHARE = "dtr-types:perShareItemType"
_STRING   = "xbrli:stringItemType"
_TEXT     = "dtr-types:textBlockItemType"
_DOMAIN   = "dtr-types:domainItemType"

# Types we want to include (monetary, shares, per-share; skip text/domain/abstract)
_NUMERIC_TYPES = {_MONETARY, _SHARES, _PER_SHARE}


def parse_xsd(xsd_path: Path) -> dict[str, dict]:
    """Return {name: {type, periodType, balance, abstract}} for all elements."""
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    concepts: dict[str, dict] = {}
    for el in root.iter(f"{{{_NS_XS}}}element"):
        name = el.get("name")
        if not name:
            continue
        concepts[name] = {
            "type":       el.get("type", ""),
            "periodType": el.get(f"{{http://www.xbrl.org/2001/XMLSchema-instance}}periodType")
                          or el.get("{http://xbrl.org/2001/XMLSchema-instance}periodType")
                          or el.get("xbrli:periodType", ""),
            "balance":    el.get("{http://xbrl.org/2001/XMLSchema-instance}balance")
                          or el.get("xbrli:balance", ""),
            "abstract":   el.get("abstract", "false").lower() == "true",
        }
    return concepts


def parse_xsd_raw(xsd_path: Path) -> dict[str, dict]:
    """Parse XSD with regex to capture xbrli:periodType and xbrli:balance
    which ElementTree drops because they're in an unregistered namespace."""
    text = xsd_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'<xs:element\s([^>]+?)(?:/>|>)',
        re.DOTALL,
    )
    concepts: dict[str, dict] = {}
    for m in pattern.finditer(text):
        attrs_str = m.group(1)
        def _attr(key: str) -> str:
            am = re.search(rf'{re.escape(key)}=["\']([^"\']*)["\']', attrs_str)
            return am.group(1) if am else ""
        name = _attr("name")
        if not name:
            continue
        concepts[name] = {
            "type":       _attr("type"),
            "periodType": _attr("xbrli:periodType"),
            "balance":    _attr("xbrli:balance"),
            "abstract":   _attr("abstract").lower() == "true",
        }
    return concepts


def parse_labels(lab_path: Path) -> dict[str, str]:
    """Return {concept_name: standard_label_text} from the linkbase."""
    text = lab_path.read_text(encoding="utf-8")
    # Extract concept name from loc href: ...us-gaap-2026.xsd#us-gaap_<Name>
    # and standard label text from the paired label element.
    # Strategy: collect (loc_label_attr -> concept_name) then
    #           collect (lab_label_attr -> text) for role=.../role/label (not terseLabel etc.)
    # Then join via labelArc from->to.

    # 1. loc: xlink:label -> concept name
    loc_to_name: dict[str, str] = {}
    for m in re.finditer(
        r'<link:loc[^>]+xlink:href=["\'][^"\']*#us-gaap_([A-Za-z0-9_]+)["\'][^>]*'
        r'xlink:label=["\']([^"\']+)["\']',
        text,
    ):
        loc_to_name[m.group(2)] = m.group(1)
    # also reversed attribute order
    for m in re.finditer(
        r'<link:loc[^>]+xlink:label=["\']([^"\']+)["\'][^>]*'
        r'xlink:href=["\'][^"\']*#us-gaap_([A-Za-z0-9_]+)["\']',
        text,
    ):
        loc_to_name[m.group(1)] = m.group(2)

    # 2. label elements: xlink:label -> text, only for standard label role
    lab_to_text: dict[str, str] = {}
    for m in re.finditer(
        r'<link:label[^>]+xlink:role=["\']http://www\.xbrl\.org/2003/role/label["\']'
        r'[^>]*xlink:label=["\']([^"\']+)["\'][^>]*>([^<]*)</link:label>',
        text,
    ):
        lab_to_text[m.group(1)] = m.group(2).strip()
    # also reversed attribute order
    for m in re.finditer(
        r'<link:label[^>]+xlink:label=["\']([^"\']+)["\']'
        r'[^>]*xlink:role=["\']http://www\.xbrl\.org/2003/role/label["\']'
        r'[^>]*>([^<]*)</link:label>',
        text,
    ):
        lab_to_text.setdefault(m.group(1), m.group(2).strip())

    # 3. arc: from (loc) -> to (label)
    name_to_label: dict[str, str] = {}
    for m in re.finditer(
        r'<link:labelArc[^>]+xlink:from=["\']([^"\']+)["\'][^>]*xlink:to=["\']([^"\']+)["\']',
        text,
    ):
        frm, to = m.group(1), m.group(2)
        name = loc_to_name.get(frm)
        label_text = lab_to_text.get(to)
        if name and label_text:
            name_to_label.setdefault(name, label_text)

    return name_to_label


def build(lab_path: Path, xsd_path: Path, out_path: Path) -> None:
    print(f"Parsing XSD:    {xsd_path}")
    concepts = parse_xsd_raw(xsd_path)
    print(f"  {len(concepts):,} concepts found")

    print(f"Parsing labels: {lab_path}")
    labels = parse_labels(lab_path)
    print(f"  {len(labels):,} standard labels found")

    # Build the output: only numeric (monetary/shares/perShare) non-abstract concepts
    rows: list[dict] = []
    for name, meta in sorted(concepts.items()):
        if meta["abstract"]:
            continue
        if meta["type"] not in _NUMERIC_TYPES:
            continue
        label_text = labels.get(name, "")
        # Skip deprecated concepts (label contains "(Deprecated")
        if "(Deprecated" in label_text:
            continue
        rows.append({
            "name":       name,
            "label":      label_text,
            "periodType": meta["periodType"],
            "balance":    meta["balance"],
            "type":       meta["type"],
        })

    print(f"  {len(rows):,} non-abstract numeric non-deprecated concepts to emit")

    lines = [
        '"""XBRL concept data generated from the FASB US-GAAP 2026 taxonomy.',
        '',
        'Generated by: python toolkits/sec_edgar_tools/build_xbrl_concepts.py',
        'Source:       https://xbrl.fasb.org/us-gaap/2026/us-gaap-2026.zip',
        'Do not edit manually — re-run build_xbrl_concepts.py to regenerate.',
        '"""',
        '# fmt: off',
        '# ruff: noqa',
        'from __future__ import annotations',
        '',
        '# Each entry: (concept_name, human_label, period_type, balance, xbrl_type)',
        '# period_type: "duration" (income-stmt / cash-flow) | "instant" (balance-sheet)',
        '# balance:     "debit" | "credit" | "" (shares/per-share have no balance)',
        '# xbrl_type:   "xbrli:monetaryItemType" | "xbrli:sharesItemType" | "dtr-types:perShareItemType"',
        'XBRL_CONCEPTS: list[tuple[str, str, str, str, str]] = [',
    ]
    for r in rows:
        lines.append(
            f'    ({r["name"]!r}, {r["label"]!r}, {r["periodType"]!r}, {r["balance"]!r}, {r["type"]!r}),'
        )
    lines += [']', '# fmt: on', '']

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Written:        {out_path}  ({len(rows):,} concepts)")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lab", required=True, help="Path to us-gaap-lab-2026.xml")
    parser.add_argument("--xsd", required=True, help="Path to us-gaap-2026.xsd")
    parser.add_argument("--out", required=True, help="Output .py file path")
    args = parser.parse_args()
    build(Path(args.lab), Path(args.xsd), Path(args.out))


if __name__ == "__main__":
    main()
