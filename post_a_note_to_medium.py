import sys
import requests
import json
import os


language_map = {
    "dart": "dart",
    "bash": "sh",
    "html": "html",
    "json": "json",
    "yaml": "yaml",
    "": "txt",
}

def create_secret_gist(title: str, file_map: dict):
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        raise ValueError("請設定 GITHUB_TOKEN 環境變數")
    
    result = requests.post(
            f"https://api.github.com/gists",
                data = json.dumps({
                  "description": title,
                  "public": False,
                  "files": file_map,
                }),
                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "Content-type": "application/json",
                    "Authorization": f"Bearer {github_token}"
                }
            ).json()
    
    if "id" in result:
        return result["id"]
    print(result)

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

class PostParser:
    def __init__(self):
        self.code_snippet_map = {}
        self.image_map = []
        self.result_post = ""
        self.tags = []
        self.title = ""
        self.skip_keywords = ["功能分類", "新增時間", "最後編輯時間", "!["]
        self.stateMap = {
            "code_parsing": self.parse_code,
            "text_parsing": self.parse_text,
        }
    
    def parse(self, file):
        self.state = "text_parsing"
        while True:
            curline = file.readline()
            if not curline :
                break

            if curline.split(":")[0] in self.skip_keywords:
                continue

            self.result_post += self.stateMap[self.state](curline)
        
        self.result_post

    def parse_text(self, line) -> str:
        if (self.title == ""):
            self.title = line[2:].strip("\n")
            return line

        #if line.startswith("```") and self.state != "code_parsing":
        #    self.state = "code_parsing"
        #    self.code_snippet_map[self.get_code_snippet_name(line)] = {
        #        "content": ""
        #    }
        #    return ""

        # if line.startswith("!["):
        #     image_file_name = line[2:line.index("]")]
        #     print(image_file_name)
        #     self.image_map.append(image_file_name)
        #     return image_file_name

        if line.startswith("標籤:"):
            self.tags = line[3:].strip(" \n").split(",")
            return ""
        return line

    def parse_code(self, line) -> str:
        self.code_string = ""
        
        last_code_snippet_name = sorted(list(self.code_snippet_map.keys()))[-1]
        if line.startswith("```"):
            self.state = "text_parsing"
            return last_code_snippet_name + "\n"
        else:
            self.code_snippet_map[last_code_snippet_name]["content"] += line
            return ""

    def get_code_snippet_name(self, line):
        return "code_" + '{0:02d}'.format(len(self.code_snippet_map)) + "." + language_map[line.rstrip("\n")[3:]]

if __name__ == '__main__':
    input_filename = sys.argv[1]
    # input_filename="Medium/畫面莫名其妙地重\ build\ 了\ 5892991469d84cb1818cc9b10c09c220.md"

    parser = PostParser()
    with open(input_filename, 'r', encoding = 'utf-8') as file:
        parser.parse(file)

        print("title:" + parser.title)
        print(f"tags: {parser.tags}")
        print(f"code_snippet: {len(parser.code_snippet_map.keys())}")

        #gist_id = create_secret_gist(input_filename[:len(input_filename)-3], parser.code_snippet_map)

        #print("gist posted")

        final_post = parser.result_post
        #for key in parser.code_snippet_map.keys():
        #    url = "<script src='https://gist.github.com/easylive1989/" + gist_id + ".js?file=" + key + "'></script>"
        #    final_post = final_post.replace(key, url)

        # for image in parser.image_map:
        #     url = upload_image(input_filename[0:-3], image)
        #     final_post = final_post.replace(image, "![" + image + "](" + url + ")")

        print("code snippet url replaced")

        create_post(parser.title, final_post, parser.tags)

        print("create post successfully")


