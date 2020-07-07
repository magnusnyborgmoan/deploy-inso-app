import os
import time
from typing import Dict, Union

import requests
from requests import HTTPError

GITHUB_REPOSITORY = os.environ["GITHUB_REPOSITORY"]
GITHUB_EVENT_NAME = os.environ["GITHUB_EVENT_NAME"]
GITHUB_SHA = os.environ["GITHUB_SHA"]


class InsoAppTimeout(Exception):
    pass


class InsoApp:
    def __init__(self, name: str, image: str, available: bool = False, url: str = ""):
        self.name = name
        self.image = image
        self.available = available
        self.url = url

    @classmethod
    def from_dict(cls, data: Dict[str, str]):
        return cls(data["name"], data["image"], bool(data["available"]), data["url"])


class InsoAppHandler:
    def __init__(self, base_url: str, api_key: str, project: str):
        self.base_url = f"{base_url}/api/playground/projects/{project}/insoapps"
        self.headers = {"content-type": "application/json", "api-key": api_key}

    def _delete(self, app: InsoApp):
        name = app.name
        url = f"{self.base_url}/{name}/delete"
        response = requests.post(url=url, headers=self.headers)
        response.raise_for_status()

    def _deploy(self, app: InsoApp):
        name = app.name
        body = {"name": name, "image": app.image}
        response = requests.post(url=self.base_url, headers=self.headers, json=body)
        response.raise_for_status()

    def get(self, app_name: str) -> InsoApp:
        url = f"{self.base_url}/{app_name}"
        response = requests.get(url=url, headers=self.headers)
        response.raise_for_status()
        return InsoApp.from_dict(response.json())

    def check_existence(self, app_name: str) -> Union[InsoApp, None]:
        try:
            return self.get(app_name)
        except HTTPError:
            return None

    def deploy_and_wait(self, app: InsoApp) -> InsoApp:
        print(f"Deploying app {app.name} ...")
        self._deploy(app)
        t_end = time.time() + 31
        while time.time() < t_end:
            app = self.get(app.name)
            if not app.available:
                time.sleep(3.0)
            else:
                print(f"Successfully deployed app {app.name}.")
                return app

        raise InsoAppTimeout(f"Deployment of {app.name} timed out.")

    def delete_and_wait(self, app: InsoApp):
        print(f"Deleting app {app.name} ... ")
        self._delete(app)
        t_end = time.time() + 31
        while time.time() < t_end:
            if not self.check_existence(app.name):
                print(f"Successfully deleted app {app.name}.")
                return
            time.sleep(3.0)

        raise InsoAppTimeout(f"Deletion of {app.name} timed out.")


def handle(base_url: str, api_key: str, project: str, image_name: str, app_name: str = ""):
    base_name = app_name if app_name else GITHUB_REPOSITORY
    if GITHUB_EVENT_NAME == "pull_request":
        app_name = f"{base_name}/{GITHUB_SHA[0:8]}"
    elif GITHUB_EVENT_NAME != "push":
        return

    app_name = app_name.replace(":", "/").replace("/", "-")
    handler = InsoAppHandler(base_url=base_url, api_key=api_key, project=project)
    app = handler.check_existence(app_name=app_name)

    if app:
        print(f"App {app.name} already exists, will delete.")
        handler.delete_and_wait(app=app)
    else:
        app = InsoApp(name=app_name, image=image_name)

    if os.getenv("DELETE_PR_FUNCTION"):
        return

    app = handler.deploy_and_wait(app)
    print(f"Go to {app.url} to see the app.")
