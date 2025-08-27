from notion_api import NotionApi
import datetime
import calendar
import os


notion_secret = os.getenv('NOTION_SECRET')
if not notion_secret:
    raise ValueError("請設定 NOTION_SECRET 環境變數")
notion_api = NotionApi(notion_secret)

today = datetime.date.today()
first_day_of_this_month = datetime.date(today.year, today.month, 1)
month_range = calendar.monthrange(first_day_of_this_month.year, first_day_of_this_month.month)[1]
last_day_of_this_month = first_day_of_this_month + datetime.timedelta(days=month_range-1)

print(first_day_of_this_month)
print(last_day_of_this_month)

filter_body = {
    "filter": {
        "and": [
            {
                "property": "時間",
                "date": {
                    "after": first_day_of_this_month.strftime("%Y-%m-%d")
                }
            },
            {
                "property": "時間",
                "date": {
                    "before": last_day_of_this_month.strftime("%Y-%m-%d")
                }
            },
            {
                "or": [
                    {
                        "property": "分類",
                        "select": {
                            "equals": "娛樂"
                        }
                    },
                    {
                        "property": "分類",
                        "select": {
                            "equals": "飲食"
                        }
                    },
                    {
                        "property": "分類",
                        "select": {
                            "equals": "日常用品"
                        }
                    },
                    {
                        "property": "分類",
                        "select": {
                            "equals": "水電管理費"
                        }
                    }
                ],
            }
        ]
    }
}


response = notion_api.query_database('43c59e00321e49a69d85037f0f45ba7e', filter_body)
results = response.json()["results"]
#print(results)

entertainment = 0
bill = 0
food = 0
sundries = 0

for result in results:
    catalog = result["properties"]["分類"]["select"]["name"]

    paul = 0 if result["properties"]["Paul"]["number"] is None else result["properties"]["Paul"]["number"]
    lily = 0 if result["properties"]["Lily"]["number"] is None else result["properties"]["Lily"]["number"]
    cash = 0 if result["properties"]["現金"]["number"] is None else result["properties"]["現金"]["number"]
    bank = 0 if result["properties"]["銀行存款"]["number"] is None else result["properties"]["銀行存款"]["number"]
    
    print(f"(paul: {paul}), (lily: {lily}), (cash: {cash}), (bank: {bank})")
    if catalog == "水電管理費":
        bill += paul + lily + cash + bank
    if catalog == "娛樂":
        entertainment += paul + lily + cash + bank
    if catalog == "飲食":
        food += paul + lily + cash + bank
    if catalog == "日常用品":
        sundries += paul + lily + cash + bank

total = entertainment + bill + food + sundries

title = first_day_of_this_month.strftime("%Y-%m")
data = f"\npie showData\n\ttitle {title} 分析 - 總額: {-total}\n\t\"娛樂\" : {-entertainment}\n\t\"日常用品\" : {-sundries}\n\t\"飲食\" : {-food}\n\t\"水電管理費\" : {-bill}"

print(f"{data}")

#print(f"""\%%{init:\ {'theme': 'base', 'themeVariables': { 'pie1': '#FF0000', 'pie2': '#FFFF00', 'pie3': '#00FF00', 'pie4': '#0000FF'}}}%%\npie showData\n\ttitle {title} 分析 - 總額: {-total}\n\t\"娛樂\" : {-entertainment}\n\t\"日常用品\" : {-sundries}\n\t\"飲食\" : {-food}\n\t\"水電管理費\" : {-bill}""")