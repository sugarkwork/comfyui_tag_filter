import json
import random
import os
import shutil
import math
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()


print("tag_category_v2.jsonを読み込み中...")
with open("tag_category_v2.json", "r", encoding="utf-8") as f:
    tag_category_v2 = dict(json.load(f))

print("tag_category_v3.jsonを読み込み中...")
if not os.path.exists("tag_category_v3.json"):
    shutil.copyfile("tag_category_v2.json", "tag_category_v3.json")
with open("tag_category_v3.json", "r", encoding="utf-8") as f:
    tag_category_v3 = dict(json.load(f))

with open("new_danbooru_tags.json", "r", encoding="utf-8") as f:
    new_danbooru_tags = list(json.load(f))
  

print(f"tag_category_v2: {len(tag_category_v2)}")
print(f"tag_category_v3: {len(tag_category_v3)}")
print(f"new_danbooru_tags: {len(new_danbooru_tags)}")


sample_separate = {}
for key, val in tag_category_v3.items():
    key_separate = key.split("_")
    for se in key_separate:
        if se not in sample_separate:
            sample_separate[se] = []
        sample_separate[se].append(key)


def releted_tags(tag:str, count:int=3) -> list[str]:
    tag_separate = []
    for se in tag.split("_"):
        tag_separate.extend(se.split("-"))
    tag_separate.reverse()
    releted_tags = []
    for se in tag_separate:
        if se in sample_separate:
            releted_tags.extend(sample_separate.get(se, []))
    return releted_tags[:count]


def categorize_tags(tags:list[str]):
    sample_keys = []
    for tag in tags:
        sample_keys.extend(releted_tags(tag))

    sample_tags = json.dumps({k: tag_category_v3[k] for k in sample_keys}, indent=2, ensure_ascii=True)
    input_tags = json.dumps(sample_keys, indent=2, ensure_ascii=True)


    system_prompt = f"""
Please categorize the tags into groups.
Please do not output your impressions or comments, only the final json result.
Please consider 4 to 6 group names.

EXAMPLE INPUT: 
{input_tags}

EXAMPLE JSON OUTPUT:
{sample_tags}
    """.strip()

    print("\n")
    print(system_prompt)

    user_prompt = json.dumps(tags, indent=2, ensure_ascii=True)

    print("\n")
    print(user_prompt)

    client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
    )

    messages = [{"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}]

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        response_format={
            'type': 'json_object'
        },
        temperature=0.5
    )

    return json.loads(response.choices[0].message.content)


if __name__ == "__main__":
    slice_count = 30

    for i in range(math.floor(len(new_danbooru_tags) / slice_count)):
        result = categorize_tags(new_danbooru_tags[i*slice_count:(i+1)*slice_count])
        tag_category_v3.update(result)

        with open("tag_category_v3.json", "w", encoding="utf-8") as f:
            json.dump(tag_category_v3, f, indent=2, ensure_ascii=True)

