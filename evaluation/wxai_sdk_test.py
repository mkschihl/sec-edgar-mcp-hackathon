import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

load_dotenv()

# WXAI_BASE_URL points at the model gateway (.../ml/gateway/v1); the SDK needs only the region URL.
parsed = urlparse(os.environ["WXAI_BASE_URL"])
url = f"{parsed.scheme}://{parsed.netloc}"

credentials = Credentials(url=url, api_key=os.environ["WXAI_API_KEY"])

model = ModelInference(
    model_id=os.getenv("WXAI_MODEL_ID", "meta-llama/llama-3-3-70b-instruct"),
    credentials=credentials,
    project_id=os.environ["WXAI_PROJ_ID"],
    params={"max_tokens": 200, "temperature": 0.2},
)

# Plain text generation
print("--- generate_text ---")
print(model.generate_text(prompt="Write a one-sentence description of watsonx.ai."))

# Chat
print("\n--- chat ---")
response = model.chat(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello! Who are you?"},
    ]
)
print(response["choices"][0]["message"]["content"])
