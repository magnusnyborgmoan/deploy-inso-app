from actions import handle
import os


CDF_PROJECT = os.getenv("INPUT_CDF_PROJECT")
CDF_CREDENTIALS = os.getenv("INPUT_CDF_CREDENTIALS")
CDF_BASE_URL = os.getenv("INPUT_CDF_BASE_URL", "https://api.cognitedata.com")
DOCKER_IMAGE = os.getenv("INPUT_DOCKER_IMAGE")
APP_NAME = os.getenv("INPUT_APP_NAME")
GITHUB_EVENT_NAME = os.environ["GITHUB_EVENT_NAME"]
GITHUB_REF = os.environ["GITHUB_HEAD_REF"]


for name, val in [("cdf_project", CDF_PROJECT), ("cdf_credentials", CDF_CREDENTIALS), ("docker_image", DOCKER_IMAGE)]:
    if not val:
        raise ValueError(f"Missing input {name}")

print(f"Handling event {GITHUB_EVENT_NAME} on {GITHUB_REF}", flush=True)
handle(base_url=CDF_BASE_URL, api_key=CDF_CREDENTIALS, project=CDF_PROJECT, image_name=DOCKER_IMAGE, app_name=APP_NAME)
