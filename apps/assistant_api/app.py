import os

from dotenv import load_dotenv
from fastapi import FastAPI

from feature.assistant.infrastructure.entrypoint.rest.handler.assistant_handler import AssistantHandler

class AssistantApi(FastAPI):
    def __init__(
        self,
        handler: AssistantHandler,
        **extra: any
    ):
        super().__init__(**extra)

        self.handler = handler

        env = os.getenv('env') or 'dev'
        path = f"config/.env.{env}"

        load_dotenv(path)

        self.add_api_route("/parrot/train", self.handler.train, methods=["POST"])
        self.add_api_route("/parrot/query", self.handler.query, methods=["GET"])
        