from notion_api import NotionApi
import datetime
import calendar
import os


notion_secret = os.getenv('NOTION_SECRET')
if not notion_secret:
    raise ValueError("請設定 NOTION_SECRET 環境變數")
notion_api = NotionApi(notion_secret)

today = datetime.date.today()

# 計算上個月
if today.month == 1:
    last_month_year = today.year - 1
    last_month = 12
else:
    last_month_year = today.year
    last_month = today.month - 1

first_day_of_this_month = datetime.date(last_month_year, last_month, 1)
month_range = calendar.monthrange(first_day_of_this_month.year, first_day_of_this_month.month)[1]
last_day_of_this_month = first_day_of_this_month + datetime.timedelta(days=month_range-1)

# 下個月（實際上是這個月）
next_month_year = today.year
next_month = today.month

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

# 累計各 property 總和
total_paul = 0
total_lily = 0
total_cash = 0
total_bank = 0

for result in results:
    catalog = result["properties"]["分類"]["select"]["name"]

    paul = 0 if result["properties"]["Paul"]["number"] is None else result["properties"]["Paul"]["number"]
    lily = 0 if result["properties"]["Lily"]["number"] is None else result["properties"]["Lily"]["number"]
    cash = 0 if result["properties"]["現金"]["number"] is None else result["properties"]["現金"]["number"]
    bank = 0 if result["properties"]["銀行存款"]["number"] is None else result["properties"]["銀行存款"]["number"]
    
    # 累計各 property 總和
    total_paul += paul
    total_lily += lily
    total_cash += cash
    total_bank += bank
    
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
mermaid_content = f"""%%{{init: {{'theme': 'base', 'themeVariables': {{ 'pie1': '#FF0000', 'pie2': '#FFFF00', 'pie3': '#00FF00', 'pie4': '#0000FF', 'pie5': '#800080', 'pie6': '#ff0000', 'pie7': '#FFA500'}}}}}}%%
pie showData
        title {title} 分析 - 總額: {-total}
        "娛樂" : {-entertainment}
        "日常用品" : {-sundries}
        "飲食" : {-food}
        "水電管理費" : {-bill}"""

print(f"{mermaid_content}")

# 創建 Notion 頁面的屬性
page_properties = {
    "標題": {
        "title": [
            {
                "text": {
                    "content": title
                }
            }
        ]
    },
    "內容": {
        "rich_text": [
            {
                "text": {
                    "content": mermaid_content
                }
            }
        ]
    }
}

# 創建新的 Notion 頁面
result_database_id = '25c8303f78f780fd9227e5e9d54c6b43'
create_response = notion_api.create_page(result_database_id, page_properties)

if create_response.status_code == 200:
    print(f"成功創建 Notion 頁面: {title}")
else:
    print(f"創建 Notion 頁面失敗: {create_response.status_code}")
    print(create_response.text)

# 創建關帳記錄（沖銷歸零）
close_title = f"{title} 關帳"
close_properties = {
    "標題": {
        "title": [
            {
                "text": {
                    "content": close_title
                }
            }
        ]
    },
    "分類": {
        "select": {
            "name": "財務整理"
        }
    },
    "Paul": {
        "number": -total_paul
    },
    "Lily": {
        "number": -total_lily
    },
    "現金": {
        "number": -total_cash
    },
    "銀行存款": {
        "number": -total_bank
    }
}

# 創建開帳記錄（下月開帳）
next_month_title = f"{next_month_year}-{next_month:02d} 開帳"
open_properties = {
    "標題": {
        "title": [
            {
                "text": {
                    "content": next_month_title
                }
            }
        ]
    },
    "分類": {
        "select": {
            "name": "財務整理"
        }
    },
    "Paul": {
        "number": total_paul
    },
    "Lily": {
        "number": total_lily
    },
    "現金": {
        "number": total_cash
    },
    "銀行存款": {
        "number": total_bank
    }
}

# 創建關帳記錄
ledger_database_id = '43c59e00321e49a69d85037f0f45ba7e'
close_response = notion_api.create_page(ledger_database_id, close_properties)
if close_response.status_code == 200:
    print(f"成功創建關帳記錄: {close_title}")
else:
    print(f"創建關帳記錄失敗: {close_response.status_code}")
    print(close_response.text)

# 創建開帳記錄
open_response = notion_api.create_page(ledger_database_id, open_properties)
if open_response.status_code == 200:
    print(f"成功創建開帳記錄: {next_month_title}")
else:
    print(f"創建開帳記錄失敗: {open_response.status_code}")
    print(open_response.text)

print(f"當月各項總額 - Paul: {total_paul}, Lily: {total_lily}, 現金: {total_cash}, 銀行存款: {total_bank}")
print(f"關帳金額 - Paul: {-total_paul}, Lily: {-total_lily}, 現金: {-total_cash}, 銀行存款: {-total_bank}")
print(f"開帳金額 - Paul: {total_paul}, Lily: {total_lily}, 現金: {total_cash}, 銀行存款: {total_bank}")