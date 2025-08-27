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

    def get_page(self, page_id: str):
        """獲取頁面屬性和基本資訊"""
        return requests.get(
            f"https://api.notion.com/v1/pages/{page_id}",
            headers=self.__header()
        )
    
    def get_block_children(self, block_id: str):
        """獲取區塊的子內容"""
        return requests.get(
            f"https://api.notion.com/v1/blocks/{block_id}/children",
            headers=self.__header()
        )
    
    def get_page_content(self, page_id: str):
        """獲取完整的頁面內容，包含屬性和所有區塊"""
        page_response = self.get_page(page_id)
        blocks_response = self.get_block_children(page_id)
        
        if page_response.status_code != 200:
            raise Exception(f"無法獲取頁面: {page_response.text}")
        
        if blocks_response.status_code != 200:
            raise Exception(f"無法獲取頁面內容: {blocks_response.text}")
        
        return {
            "page": page_response.json(),
            "blocks": blocks_response.json()
        }

    def __header(self) -> dict:
        return {
            "Content-type": "application/json",
            "Notion-Version": "2022-06-28",
            "Authorization": f"Bearer {self.token}"
        }
    