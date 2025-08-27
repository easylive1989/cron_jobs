import sys
import requests
import json
import os
from notion_api import NotionApi


def get_notion_page_content(page_id: str):
    """從 Notion 獲取頁面內容並轉換為 markdown 格式"""
    notion_token = os.getenv('NOTION_TOKEN')
    if not notion_token:
        raise ValueError("請設定 NOTION_TOKEN 環境變數")
    
    notion_api = NotionApi(notion_token)
    content = notion_api.get_page_content(page_id)
    
    return convert_notion_to_markdown(content["page"], content["blocks"])


def convert_notion_to_markdown(page_data, blocks_data):
    """將 Notion 內容轉換為 markdown 格式"""
    markdown_content = ""
    
    # 獲取標題
    title = ""
    if "properties" in page_data:
        for prop_name, prop_data in page_data["properties"].items():
            if prop_data["type"] == "title" and prop_data["title"]:
                title = "".join([text["plain_text"] for text in prop_data["title"]])
                break
    
    # 如果有標題，加入 markdown
    if title:
        markdown_content += f"# {title}\n\n"
    
    # 轉換內容塊
    for block in blocks_data["results"]:
        markdown_content += convert_block_to_markdown(block)
    
    return {"title": title, "content": markdown_content, "tags": []}


def convert_block_to_markdown(block):
    """將單個 Notion 塊轉換為 markdown"""
    block_type = block["type"]
    markdown = ""
    
    if block_type == "paragraph":
        text = extract_rich_text(block["paragraph"]["rich_text"])
        markdown = f"{text}\n\n"
    
    elif block_type == "heading_1":
        text = extract_rich_text(block["heading_1"]["rich_text"])
        markdown = f"# {text}\n\n"
    
    elif block_type == "heading_2":
        text = extract_rich_text(block["heading_2"]["rich_text"])
        markdown = f"## {text}\n\n"
    
    elif block_type == "heading_3":
        text = extract_rich_text(block["heading_3"]["rich_text"])
        markdown = f"### {text}\n\n"
    
    elif block_type == "bulleted_list_item":
        text = extract_rich_text(block["bulleted_list_item"]["rich_text"])
        markdown = f"- {text}\n"
    
    elif block_type == "numbered_list_item":
        text = extract_rich_text(block["numbered_list_item"]["rich_text"])
        markdown = f"1. {text}\n"
    
    elif block_type == "quote":
        text = extract_rich_text(block["quote"]["rich_text"])
        markdown = f"> {text}\n\n"
    
    elif block_type == "code":
        language = block["code"]["language"] or ""
        text = extract_rich_text(block["code"]["rich_text"])
        markdown = f"```{language}\n{text}\n```\n\n"
    
    elif block_type == "divider":
        markdown = "---\n\n"
    
    return markdown


def extract_rich_text(rich_text_array):
    """從 Notion rich text 陣列中提取純文字"""
    if not rich_text_array:
        return ""
    
    text = ""
    for text_obj in rich_text_array:
        plain_text = text_obj.get("plain_text", "")
        
        # 處理格式化
        annotations = text_obj.get("annotations", {})
        if annotations.get("bold"):
            plain_text = f"**{plain_text}**"
        if annotations.get("italic"):
            plain_text = f"*{plain_text}*"
        if annotations.get("code"):
            plain_text = f"`{plain_text}`"
        if annotations.get("strikethrough"):
            plain_text = f"~~{plain_text}~~"
        
        # 處理連結
        if text_obj.get("href"):
            plain_text = f"[{plain_text}]({text_obj['href']})"
        
        text += plain_text
    
    return text


def create_post(title: str, content: str, tags):
    medium_token = os.getenv('MEDIUM_TOKEN')
    medium_user_id = os.getenv('MEDIUM_USER_ID')
    
    if not medium_token:
        raise ValueError("請設定 MEDIUM_TOKEN 環境變數")
    if not medium_user_id:
        raise ValueError("請設定 MEDIUM_USER_ID 環境變數")
    
    print(content)
    result = requests.post(
            f"https://api.medium.com/v1/users/{medium_user_id}/posts",
                data = json.dumps({
                    "title": title,
                    "contentFormat": "markdown",
                    "content": content,
                    "tags": tags,
                    "publishStatus": "draft"
                }),
                headers = {
                    "Content-type": "application/json",
                    "Accept": "application/json",
                    "Accept-Charset": "utf-8",
                    "Authorization": f"Bearer {medium_token}"
                }
            )
    
    print(result.json())

def upload_image(title, file):
    medium_token = os.getenv('MEDIUM_TOKEN')
    if not medium_token:
        raise ValueError("請設定 MEDIUM_TOKEN 環境變數")
    
    print(title +"/"+ file)
    data = "--FormBoundaryXYZ\r\n"
    data += "Content-Disposition: form-data; name=\"image\"; filename=\"" + file + "\"\r\n"
    data += "Content-Type: image/" + file[-3:0] + "\r\n\r\n"

    with open(title + "/" + file, "rb") as image:
        f = image.read()
        b = bytearray(f)
        data += "".join(map(chr, b)) + "\r\n"
        data += str(b) + "\r\n"
    data += "--FormBoundaryXYZ--\r\n"
    print(data)
    result = requests.post(
            "https://api.medium.com/v1/images",
                data = """
                --FormBoundaryXYZ
                Content-Disposition: form-data; name="image"; filename="filename.png"
                Content-Type: image/png

                IMAGE_DATA
                --FormBoundaryXYZ--""",
                headers = {
                    "Content-type": "multipart/form-data; boundary=FormBoundaryXYZ",
                    "Accept": "application/json",
                    "Accept-Charset": "utf-8",
                    "Authorization": f"Bearer {medium_token}"
                }
            )
    
    print(result.json())

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python post_a_note_to_medium.py <notion_page_id>")
        sys.exit(1)
    
    notion_page_id = sys.argv[1]
    
    try:
        # 從 Notion 獲取頁面內容
        notion_data = get_notion_page_content(notion_page_id)
        
        print(f"title: {notion_data['title']}")
        print(f"tags: {notion_data['tags']}")
        print(f"content preview: {notion_data['content'][:100]}...")
        
        # 發佈到 Medium
        create_post(notion_data['title'], notion_data['content'], notion_data['tags'])
        
        print("create post successfully")
        
    except Exception as e:
        print(f"錯誤: {e}")
        sys.exit(1)


