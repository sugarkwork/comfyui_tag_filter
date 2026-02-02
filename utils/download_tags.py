import requests
import json
import time



page = 0
tags = []

while True:
    url = f"https://danbooru.donmai.us/tags.json?limit=1000&page={page}"
    response = requests.get(url)
    if response.status_code != 200 or not response.json():
        print(f"response.status_code = {response.status_code}")
        print(f"response.json() = {response.json()}")
        print(f"url = {url}")
        break
    data = response.json()
    tags.extend(data)
    print(f"ページ {page} 取得: {len(data)} 件（合計 {len(tags)} 件）")
    page += 1
    time.sleep(0.3)  # レートリミット回避のため少し待機

    if page % 100 == 0:
        # ファイル保存
        with open(f"danbooru_all_tags.json", "w", encoding="utf-8") as f:
            json.dump(tags, f, ensure_ascii=True, indent=2)

with open(f"danbooru_all_tags.json", "w", encoding="utf-8") as f:
    json.dump(tags, f, ensure_ascii=True, indent=2)


categories = [0, 1, 3, 4, 5]


for cate in categories:
    page = 0
    tags = []

    while True:
        url = f"https://danbooru.donmai.us/tags.json?limit=1000&page={page}&search[category]={cate}"
        response = requests.get(url)
        if response.status_code != 200 or not response.json():
            print(f"response.status_code = {response.status_code}")
            print(f"response.json() = {response.json()}")
            print(f"url = {url}")
            break
        data = response.json()
        tags.extend(data)
        print(f"ページ {page} 取得: {len(data)} 件（合計 {len(tags)} 件）")
        page += 1
        time.sleep(0.3)  # レートリミット回避のため少し待機

        if page % 100 == 0:
            # ファイル保存
            with open(f"danbooru_all_tags_{cate}.json", "w", encoding="utf-8") as f:
                json.dump(tags, f, ensure_ascii=True, indent=2)

    with open(f"danbooru_all_tags_{cate}.json", "w", encoding="utf-8") as f:
        json.dump(tags, f, ensure_ascii=True, indent=2)

