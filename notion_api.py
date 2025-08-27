import json
import requests

# https://developers.notion.com/reference/intro
class NotionApi:
    def __init__(self, token):
        self.token = token

    def query_database(self, database_id: str, body: dict):
        return requests.post(
            f"https://api.notion.com/v1/databases/{database_id}/query",
            data = json.dumps(body),
            headers = self.__header()
        )

    def patch_page(self, page_id: str, properties: dict):
        requests.patch(
            f"https://api.notion.com/v1/pages/{page_id}",
            data = json.dumps(properties),
            headers = self.__header()
        )

    def create_page(self, database_id: str, properties: dict):
        body = {
            "parent": { "database_id": database_id },
            "properties": properties
        }
        
        return requests.post(
            "https://api.notion.com/v1/pages", 
            data = json.dumps(body),
            headers = self.__header()
        )

    def __header(self) -> dict:
        return {
            "Content-type": "application/json",
            "Notion-Version": "2022-06-28",
            "Authorization": f"Bearer {self.token}"
        }
    