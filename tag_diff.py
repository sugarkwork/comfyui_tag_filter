import json
import os
import shutil

# 最終的な結果を保存しているデータ
print("tag_category_v2.jsonを読み込み中...")
if not os.path.exists("tag_category_v3.json"):
    shutil.copyfile("tag_category_v2.json", "tag_category_v3.json")
with open("tag_category_v3.json", "r", encoding="utf-8") as f:
    tag_category_v3 = json.load(f)

# 最新のタグデータ
print("danbooru_all_tags_*.jsonを読み込み中...")
danbooru_tags = set()
for cate in ['', '_0', '_3', '_4', '_5']:
    print(f"danbooru_all_tags{cate}.jsonを読み込み中...")
    with open(f"utils/danbooru_all_tags{cate}.json", "r", encoding="utf-8") as f:
        danbooru_all_tags_cate = json.load(f)
        for tag in danbooru_all_tags_cate:

            if (tag["post_count"] > 200 
                and not tag["is_deprecated"] 
                and tag["name"] not in tag_category_v3 
                and tag["category"] == 1):

                danbooru_tags.add(tag["name"])


danbooru_tags = list(danbooru_tags)

# 追加が何件あるか表示
print(f"追加されたタグの数: {len(danbooru_tags)}")

# 追加されたタグを10件表示
print(f"追加されたタグ: {danbooru_tags[0:10]}")

# save danbooru_tags
with open("new_danbooru_tags.json", "w", encoding="utf-8") as f:
    json.dump(danbooru_tags, f, indent=2, ensure_ascii=True)

