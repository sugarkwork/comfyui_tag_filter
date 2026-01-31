import os
import json
import decimal
from typing import List, Dict
import random
import math


tag_category1: Dict[str, List[str]] = {}
tag_category2: Dict[str, List[str]] = {}


def get_tag_category(version=1) -> dict:
    global tag_category1, tag_category2
    code_dir = os.path.dirname(os.path.realpath(__file__))
    if version == 1:
        if not tag_category1:
            with open(os.path.join(code_dir, "tag_category.json"), encoding="utf-8-sig") as f: # file encoding is utf-8
                tag_category1 = json.load(f)
        return tag_category1
    else:
        if not tag_category2:
            with open(os.path.join(code_dir, "tag_category_v2.json"), encoding="utf-8-sig") as f: # file encoding is utf-8
                tag_category2 = json.load(f)
        return tag_category2


def format_category(categories: str) -> list:
    return [category.lower().strip().replace(" ", "_") for category in categories.replace("\n",",").replace(".",",").split(",")]


class TagData:
    def __init__(self, tag:str, weight:float):
        self.tag:str = tag
        self.weight:decimal.Decimal = decimal.Decimal(str(round(weight, 3)))
        self.format:str = tag.lower().strip().replace(' ', '_')
        self.format_escape:str = escape_tag_special_chars(self.format)
        self.format_unescape:str = remove_escape(unescape_tag_special_chars(self.format_escape))
    
    def get_categores(self):
        return get_tag_category(2).get(self.format_unescape, [])
    
    def __str__(self):
        return self.format
    
    def __repr__(self):
        return self.format

    def __eq__(self, other):
        if isinstance(other, TagData):
            return self.format == other.format
        return False

    def __hash__(self):
        return hash(self.format)
    
    def text(self, format=False, underscore=False):
        tag_text = self.tag
        if format:
            tag_text = self.format
        if underscore:
            tag_text = tag_text.replace(' ', '_')

        tag_text = unescape_tag_special_chars(tag_text)
        
        if self.weight != decimal.Decimal("1.0"):
            return f"({tag_text}:{self.weight})"
        return tag_text


def parse_tags(tag_string:str) -> list[TagData]:
    if tag_string is None:
        return []
    if not tag_string:
        return []
    tag_string = tag_string.strip()
    if not tag_string:
        return []
    
    tag_string = escape_tag_special_chars(tag_string)
    #print(tag_string)

    def clean_tag(tag):
        # Remove any leading/trailing whitespace and parentheses
        tag = tag.strip()
        while tag.startswith(('(', ')')) or tag.endswith(('(', ')')):
            tag = tag.strip('()')
        return tag.strip()

    def get_weight_and_tags(group):
        group = clean_tag(group)
        if ':' in group:
            tags_part, weight_part = group.split(':', 1)
            try:
                weight = float(weight_part)
            except ValueError:
                weight = 1.0
                tags_part = group
            tags = [t.strip() for t in tags_part.split(',')]
        else:
            tags = [t.strip() for t in group.split(',')]
            weight = 1.0
        return tags, weight

    result = []
    paren_count = 0
    
    # First pass: split into proper groups
    groups = []
    current = ''
    for char in tag_string:
        if char == '(':
            paren_count += 1
        elif char == ')':
            paren_count -= 1
        
        current += char
        
        if paren_count == 0 and char == ',':
            if current.strip(',').strip():
                groups.append(current.strip(',').strip())
            current = ''
    if current.strip(',').strip():
        groups.append(current.strip(',').strip())

    # Second pass: process each group
    for group in groups:
        group = group.strip()
        if not group:
            continue

        # Count the number of opening parentheses at the start
        opening_count = 0
        for char in group:
            if char == '(':
                opening_count += 1
            else:
                break

        # Count the number of closing parentheses at the end
        closing_count = 0
        for char in reversed(group):
            if char == ')':
                closing_count += 1
            else:
                break

        # Get the actual parentheses pairs count (use the minimum to ensure matching pairs)
        paren_pairs = min(opening_count, closing_count)

        tags, custom_weight = get_weight_and_tags(group)
        
        # Set weight based on parentheses pairs
        if custom_weight != 1.0:
            weight = custom_weight
        else:
            if paren_pairs == 0:
                weight = 1.0
            else:
                weight = 1.0 + (paren_pairs * 0.1)

        # Add each tag with its weight
        for tag in tags:
            tag = clean_tag(tag)
            if tag:
                result.append(TagData(tag, weight))
    
    return result


def remove_duplicates(lst):
    return list(dict.fromkeys(lst))


def tagdata_to_string(tags:list[TagData], underscore=False) -> str:
    return ", ".join([tag.text(underscore=underscore) for tag in tags])


# エスケープ対象とトークンの対応表
ESCAPE_MAP = {
    '\\(':  '__escape_kakko_start__',
    '\\)':  '__escape_kakko_end__',
    '\\:':  '__escape_colon__',
    '\\,':  '__escape_comma__',
    '\\\\': '__escape_backslash__',  # 最後に展開。二重エスケープ用
}

UNESCAPE_MAP = {v: k for k, v in ESCAPE_MAP.items()}

def escape_tag_special_chars(s: str) -> str:
    # バックスラッシュは一番最後に処理するため、順番を工夫
    for orig, repl in sorted(ESCAPE_MAP.items(), key=lambda x: -len(x[0])):
        s = s.replace(orig, repl)
    return s

def unescape_tag_special_chars(s: str) -> str:
    for repl, orig in UNESCAPE_MAP.items():
        s = s.replace(repl, orig)
    return s

def remove_escape(s: str) -> str:
    return s.replace('\\\\', '\\').replace('\\(', '(').replace('\\)', ')').replace('\\:', ':').replace('\\,', ',')


class TagIf:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "find": ("STRING", {"default": ""}),
                "anytag": ("BOOLEAN", {"default": True}),
                "output1": ("STRING", {"default": ""}),
            },
            "optional": {
                "output2": ("STRING", {"default": ""}),
                "output3": ("STRING", {"default": ""}),
                "else_output1": ("STRING", {"default": ""}),
                "else_output2": ("STRING", {"default": ""}),
                "else_output3": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING","STRING","STRING","STRING","STRING","STRING","BOOLEAN")
    RETURN_NAMES = ("output1","output2","output3","else_output1","else_output2","else_output3","tagin")

    FUNCTION = "tag"

    CATEGORY = "string"

    OUTPUT_NODE = True

    def tag(self, tags:str, find:str, anytag:bool=True, output1:str="", output2:str="", output3:str="", else_output1:str="", else_output2:str="", else_output3:str=""):
        tags = parse_tags(tags)
        find = parse_tags(find)

        tagin = False
        if anytag:
            tagin = any(tag in tags for tag in find)
        else:
            tagin = all(tag in tags for tag in find)

        if tagin:
            return (output1, output2, output3, "", "", "", True)
        else:
            return ("", "", "", else_output1, else_output2, else_output3, False)


class TagFlag:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "output_tags1": ("STRING", {"default": ""}),
                "output_flag1": ("BOOLEAN", {"default": True}),
            },
            "optional": {
                "output_tags2": ("STRING", {"default": ""}),
                "output_flag2": ("BOOLEAN", {"default": True}),
                "output_tags3": ("STRING", {"default": ""}),
                "output_flag3": ("BOOLEAN", {"default": True}),
                "output_tags4": ("STRING", {"default": ""}),
                "output_flag4": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING","STRING","STRING","STRING","STRING")
    RETURN_NAMES = ("output_tags1","output_tags2","output_tags3","output_tags4", "all_tags")

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, output_tags1:str="", output_flag1:bool=True, output_tags2:str="", output_flag2:bool=True, output_tags3:str="", output_flag3:bool=True, output_tags4:str="", output_flag4:bool=True):
        result = ["", "", "", "", ""]
        if output_flag1:
            result[0] = output_tags1
        if output_flag2:
            result[1] = output_tags2    
        if output_flag3:
            result[2] = output_tags3
        if output_flag4:
            result[3] = output_tags4
        
        result[4] = tagdata_to_string(parse_tags(result[0]) + parse_tags(result[1]) + parse_tags(result[2]) + parse_tags(result[3]))

        return tuple(result)


class TagRandom:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "count_min": ("INT", {"default": 1, "min": 1}),
                "count_max": ("INT", {"default": 1, "min": 1}),
                "seed": ("INT", {"default": 1234, "min": 0}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)
    
    FUNCTION = "tag"
    
    CATEGORY = "text"
    
    def tag(self, tags:str="", count_min:int=1, count_max:int=1, seed:int=1234):
        myrand = random.Random(seed)
        tag_list = parse_tags(tags)
        myrand.shuffle(tag_list)
        if count_min > count_max:
            count_min, count_max = count_max, count_min 
        return (tagdata_to_string(tag_list[:myrand.randint(count_min, count_max)]),)


class TagFlagImage:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "default_image": ("IMAGE", ),
                "output_image1": ("IMAGE", ),
                "output_flag1": ("BOOLEAN", {"default": True}),
                "output_image2": ("IMAGE", ),
                "output_flag2": ("BOOLEAN", {"default": True}),
                "output_image3": ("IMAGE", ),
                "output_flag3": ("BOOLEAN", {"default": True}),
                "output_image4": ("IMAGE", ),
                "output_flag4": ("BOOLEAN", {"default": True}),
            }
        }
    
    RETURN_TYPES = ("IMAGE", "IMAGE", "IMAGE", "IMAGE", "IMAGE")
    RETURN_NAMES = ("output_image1", "output_image2", "output_image3", "output_image4", "any_one")

    FUNCTION = "tag"

    CATEGORY = "image"

    OUTPUT_NODE = True

    def tag(self, 
            default_image = None,
            output_image1 = None, output_flag1:bool=True, 
            output_image2 = None, output_flag2:bool=True, 
            output_image3 = None, output_flag3:bool=True, 
            output_image4 = None, output_flag4:bool=True):
        
        result = [default_image, default_image, default_image, default_image, default_image]
        if output_flag1 and output_image1 is not None:
            result[0] = output_image1
            result[4] = output_image1
        if output_flag2 and output_image2 is not None:
            result[1] = output_image2 
            result[4] = output_image2   
        if output_flag3 and output_image3 is not None:
            result[2] = output_image3
            result[4] = output_image3
        if output_flag4 and output_image4 is not None:
            result[3] = output_image4
            result[4] = output_image4

        return tuple(result)


class TagSwitcher:
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "input_tags": ("STRING",),
                "default_image": ("IMAGE",),
                "tags1": ("STRING", {"default": ""}),
                "image1": ("IMAGE", {"default": ""}),
                "any1": ("BOOLEAN", {"default": True}),
            },
            "optional": {   
                "tags2": ("STRING", {"default": ""}),
                "image2": ("IMAGE", {"default": ""}),
                "any2": ("BOOLEAN", {"default": True}),
                "tags3": ("STRING", {"default": ""}),
                "image3": ("IMAGE", {"default": ""}),
                "any3": ("BOOLEAN", {"default": True}),
                "tags4": ("STRING", {"default": ""}),
                "image4": ("IMAGE", {"default": ""}),
                "any4": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)

    FUNCTION = "tag"

    CATEGORY = "image"

    OUTPUT_NODE = True

    def tag(self, input_tags="", default_image=None, tags1="", image1=None, any1=True, tags2="", image2=None, any2=True, tags3="", image3=None, any3=True, tags4="", image4=None, any4=True):
        input_tags = parse_tags(input_tags)

        target_tags = []
        tags1 = set(parse_tags(tags1))
        target_tags.append((tags1, image1, any1))

        tags2 = set(parse_tags(tags2))
        target_tags.append((tags2, image2, any2))

        tags3 = set(parse_tags(tags3))
        target_tags.append((tags3, image3, any3))

        tags4 = set(parse_tags(tags4))
        target_tags.append((tags4, image4, any4))

        for tags, image, any_flag in target_tags:
            if any_flag:
                if any(tag in tags for tag in input_tags):
                    return (image,)
            else:
                if all(tag in input_tags for tag in tags):
                    return (image,)

        return (default_image,)


class TagMerger:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "tags1": ("STRING",),
                "tags2": ("STRING",),
                "under_score": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str=None, tags2:str=None, under_score=True):
        if tags1 is None:
            tags1 = ""
        if tags2 is None:
            tags2 = ""
        taglist1 = parse_tags(tags1)
        taglist2 = parse_tags(tags2)

        tags = remove_duplicates(taglist1 + taglist2)

        return (tagdata_to_string(tags, underscore=under_score),)


class TagMerger4:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "tags1": ("STRING",),
                "tags2": ("STRING",),
                "tags3": ("STRING",),
                "tags4": ("STRING",),
                "under_score": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str=None, tags2:str=None, tags3:str=None, tags4:str=None, under_score=True):
        taglist1 = parse_tags(tags1)
        taglist2 = parse_tags(tags2)
        taglist3 = parse_tags(tags3)
        taglist4 = parse_tags(tags4)

        tags = remove_duplicates(taglist1 + taglist2 + taglist3 + taglist4)

        return (tagdata_to_string(tags, underscore=under_score),)


class TagMerger6:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "tags1": ("STRING",),
                "tags2": ("STRING",),
                "tags3": ("STRING",),
                "tags4": ("STRING",),
                "tags5": ("STRING",),
                "tags6": ("STRING",),
                "under_score": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str=None, tags2:str=None, tags3:str=None, tags4:str=None, tags5:str=None, tags6:str=None, under_score=True):
        taglist1 = parse_tags(tags1)
        taglist2 = parse_tags(tags2)
        taglist3 = parse_tags(tags3)
        taglist4 = parse_tags(tags4)
        taglist5 = parse_tags(tags5)
        taglist6 = parse_tags(tags6)

        tags = remove_duplicates(taglist1 + taglist2 + taglist3 + taglist4 + taglist5 + taglist6)

        return (tagdata_to_string(tags, underscore=under_score),)


class TagRemover:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING",),
                "exclude_tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, exclude_tags:str=""):
        tag_data = parse_tags(tags)
        exclude_tag_data = parse_tags(exclude_tags)

        uniq_tags = [tag for tag in tag_data if tag not in exclude_tag_data]
        
        return (tagdata_to_string(uniq_tags) ,)


class TagReplace:
    # TODO: use TagData class

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "replace_tags": ("STRING", {"default": ""}),
                "match": ("FLOAT", {"default": 0.3}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def _get_categories(self, tag: str) -> set:
        """タグのカテゴリーを取得する"""
        tag_category = get_tag_category(2)
        return set(tag_category.get(tag, []))

    def _category_match_percentage(self, categories1: set, categories2: set) -> float:
        """2つのカテゴリセット間の一致度(%)を計算する"""
        if not categories1 or not categories2:
            return 0
        intersection = categories1.intersection(categories2)
        union = categories1.union(categories2)
        return len(intersection) / len(union)

    def tag(self, tags:str, replace_tags:str="", match:float=0.3):
        tags = [tag.strip() for tag in tags.replace("\n",",").split(",")]
        tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in tags]

        replace_tags = [tag.strip() for tag in replace_tags.replace("\n",",").split(",")]
        replace_tags_normalized = [tag.replace(" ", "_").lower().strip() for tag in replace_tags]
        replace_tags_used = {tag:False for tag in replace_tags_normalized}

        result = []
        for i, tag in enumerate(tags_normalized):
            tag_categories = self._get_categories(tag)
            best_match_tag = None
            best_match_tag_id = None
            best_match_percentage = 0

            for k, replace_tag in enumerate(replace_tags_normalized):
                replace_categories = self._get_categories(replace_tag)
                match_percentage = self._category_match_percentage(tag_categories, replace_categories)

                if match_percentage and match_percentage > best_match_percentage:
                    best_match_percentage = match_percentage
                    best_match_tag = replace_tag
                    replace_tags_used[replace_tag] = True
                    best_match_tag_id = k

            
            if best_match_tag and best_match_percentage >= match:
                result.append(replace_tags[best_match_tag_id])
            else:
                result.append(tags[i])

        # replace_tags の中から、tags に存在しないタグを追加
        extra_tags = [replace_tag for replace_tag, used in replace_tags_used.items() if not used]
        result.extend(extra_tags)
        
        return (", ".join(result),)


def tag_flexible_category(tag_text:str, tag_category:dict):
    org_tag_text = tag_text
    tag_text_alt = None

    if tag_text in tag_category:
        return tag_text
        
    while tag_text_alt is None:
        tag_text_split = org_tag_text.split("_")
        del tag_text_split[0]
        org_tag_text = " ".join(tag_text_split).strip().replace(" ", "_")

        if not org_tag_text:
            tag_text_alt = None
            break
        
        if tag_category.get(org_tag_text, None):
            tag_text_alt = org_tag_text
            break
    
    return tag_text_alt


class TagSelector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "categorys": ("STRING", {"default": "*"}),
                "exclude" : ("BOOLEAN", {"default": False}),
                "whitelist_only": ("BOOLEAN", {"default": False}),
                "flexible_filter": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("result", "found")

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, categorys:str, exclude:bool=False, whitelist_only:bool=False, flexible_filter:bool=False):
        tag_list = parse_tags(tags)
        tag_category = get_tag_category(2)
        target_category = format_category(categorys)

        result = []
        for i, tag in enumerate(tag_list):
            tag_text = tag.format_unescape
            tag_text_alt = None

            if flexible_filter and tag_text not in tag_category:
                tag_text_alt = tag_flexible_category(tag_text, tag_category)
            else:
                tag_text_alt = None

            #print("tag_text_alt", f"{tag_text} == {tag_text_alt}")

            if (tag_text in tag_category) or (flexible_filter and tag_text_alt and tag_text_alt in tag_category):
                if '*' == categorys:
                    result.append(tag)
                    continue
                
                category_list = tag_category.get(tag_text, tag_category.get(tag_text_alt, []))
                #print("    category_list", category_list)

                tag_is_taget_category = False
                for category in category_list:
                    if category in target_category:
                        tag_is_taget_category = True
                        break
                #print(f"        tag_is_taget_category tag={tag} in={tag_is_taget_category}")
                if tag_is_taget_category:
                    if exclude:
                        continue
                    else:
                        result.append(tag)
                else:
                    if exclude:
                        result.append(tag)
                    else:
                        continue
            else:
                #print("    without category", tag)
                if whitelist_only:
                    continue
                else:
                    result.append(tag)

        return (tagdata_to_string(result), len(result) > 0)


class TagComparator:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags1": ("STRING", ),
                "tags2": ("STRING", ),
            },
        }
    
    RETURN_TYPES = ("STRING", "STRING", "STRING",)
    RETURN_NAMES = ("tags1_unique", "tags2_unique", "common_tags",)

    FUNCTION = "tag"
    
    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags1:str, tags2:str):
        tag_list1 = parse_tags(tags1)
        tag_list2 = parse_tags(tags2)

        tags1_unique = [tag for tag in tag_list1 if tag not in tag_list2]
        tags2_unique = [tag for tag in tag_list2 if tag not in tag_list1]
        common_tags = [tag for tag in tag_list1 if tag in tag_list2]

        return (tagdata_to_string(tags1_unique), tagdata_to_string(tags2_unique), tagdata_to_string(common_tags))


class TagFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "pose": ("BOOLEAN", {"default": True}),
                "gesture": ("BOOLEAN", {"default": True}),
                "action": ("BOOLEAN", {"default": True}),
                "emotion": ("BOOLEAN", {"default": True}),
                "expression": ("BOOLEAN", {"default": True}),
                "camera": ("BOOLEAN", {"default": True}),
                "angle": ("BOOLEAN", {"default": True}),
                "sensitive": ("BOOLEAN", {"default": True}),
                "liquid": ("BOOLEAN", {"default": True}),
                "include_categories": ("STRING", {"default": ""}),
                "exclude_categories": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags, pose=True, gesture=True, action=True, emotion=True, expression=True, camera=True, angle=True, sensitive=True, liquid=True, include_categories="", exclude_categories=""):

        targets = []
        exclude_targets = []
        if pose:
            targets.append("pose")
        if gesture:
            targets.append("gesture")
        if action:
            targets.append("action")
        if emotion:
            targets.append("emotion")
        if expression:
            targets.append("expression")
        if camera:
            targets.append("camera")
        if angle:
            targets.append("angle")
        if sensitive:
            targets.append("sensitive")
        if liquid:
            targets.append("liquid")
        
        include_categories = include_categories.strip()
        if include_categories:
            targets += format_category(include_categories)

        if exclude_categories:
            exclude_targets = format_category(exclude_categories)
            targets = [target for target in targets if target not in exclude_targets]
        
        tag_list = parse_tags(tags)

        result = []
        tag_category = get_tag_category(2)

        for i, tag in enumerate(tag_list):
            tag_text = tag.format_unescape
            if tag_text in tag_category:
                category_list = tag_category.get(tag_text, tag_category.get(tag.format_unescape, []))

                if not category_list:
                    continue

                for category in category_list:
                    if category in exclude_targets:
                        # not include this tag
                        break
                else:
                    if '*' == include_categories:
                        # include all tags
                        result.append(tag)
                    else:
                        for category in category_list:
                            if category in targets:
                                # include this tag
                                result.append(tag)
                                break

        return (tagdata_to_string(result),)



class TagEnhance:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "enhance_tags": ("STRING", ),
                "strength": ("FLOAT", {"default": 1.2, "min": 0, "max": 5.0, "step": 0.05}),
                "add_strength": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, enhance_tags:str, strength:float=1.2, add_strength:bool=False):
        tag_list = parse_tags(tags)
        enhance_tag_list = parse_tags(enhance_tags)

        result = []
        for i, tag in enumerate(tag_list):
            if tag in enhance_tag_list:
                if add_strength:
                    tag.weight += decimal.Decimal(str(round(strength, 3)))
                else:
                    tag.weight = decimal.Decimal(str(round(strength, 3)))
            result.append(tag)
        
        return (tagdata_to_string(result),)


class TagCategoryEnhance:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "enhance_category": ("STRING", ),
                "strength": ("FLOAT", {"default": 1.2, "min": -5.0, "max": 5.0, "step": 0.05}),
                "add_strength": ("BOOLEAN", {"default": False}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, enhance_category:str, strength:float=1.2, add_strength:bool=False):
        tag_list = parse_tags(tags)
        categories = format_category(enhance_category)

        result = []
        for i, tag in enumerate(tag_list):
            tag_category = tag.get_categores()
            if tag_category and any(c in tag_category for c in categories):
                if add_strength:
                    tag.weight += decimal.Decimal(str(round(strength, 3)))
                else:
                    tag.weight = decimal.Decimal(str(round(strength, 3)))
            result.append(tag)
        
        return (tagdata_to_string(result),)


class TagCategory:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("categories",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, flexible_filter:bool=False):
        if not tags:
            return ("",)

        tag_list = parse_tags(tags)
        tag_category = get_tag_category(2)
        
        result = []
        for tag in tag_list:
            tag_text = tag.format_unescape
            category = []
            if flexible_filter:
                flex_tag_text = tag_flexible_category(tag_text, tag_category)
                if flex_tag_text:
                    category = tag_category.get(flex_tag_text, [])
            else:
                category = tag_category.get(tag_text, [])
            result.extend(category)
        
        result = sorted(list(set(result)))

        return (", ".join(result),)



class TagWildcardFilter:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", ),
                "wildcard": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING", "BOOLEAN")
    RETURN_NAMES = ("tags", "found")

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, wildcard:str) -> tuple:
        if not tags or not wildcard:
            return (tags,)
        
        tag_list = parse_tags(tags)
        
        wildcard = wildcard.lower().strip().replace(' ', '_')

        regex_on = False
        if '*' in wildcard:
            wildcard = wildcard.replace('*', '.*')
            wildcard = f"^{wildcard}$"
            regex_on = True
            import re

        result = []
        for tag in tag_list:
            if regex_on:
                if re.match(wildcard, tag.format_unescape):
                    result.append(tag)
            else:    
                if wildcard in tag.format_unescape:
                    result.append(tag)
        
        return (tagdata_to_string(result), len(result) > 0)



class TagRandomCategory:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "category": ("STRING", {"default": ""}),
                "negative_category": ("STRING", {"default": ""}),
                "count": ("INT", {"default": 1, "min": 1, "max": 100}),
                "seed": ("INT", {"default": 1234, "min": 0}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, category:str, negative_category:str, count:int=1, seed:int=1234) -> tuple:
        category_list = format_category(category)
        negative_category_list = format_category(negative_category)
        if not category_list:
            return ("",)
        tag_category:Dict[str, List[str]] = get_tag_category(2)

        

        selected_tags = []
        for cat in category_list:
            if not cat:
                continue

            cat_select_tags = []
            for tag, cats in tag_category.items():
                if cat in cats:
                    if negative_category_list and any(neg_cat in cats for neg_cat in negative_category_list):
                        continue
                    cat_select_tags.append(tag.replace("(", "\\(").replace(")", "\\)").replace(":", "\\:").replace(",", "\\,"))

            if not cat_select_tags:
                continue

            myrand = random.Random(seed)
            selected_tags += myrand.choices(cat_select_tags, k=count)

        selected_tags = remove_duplicates(parse_tags(", ".join(selected_tags)))

        return (tagdata_to_string(selected_tags),)


class TagPipeIn:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "optional": {
                "key1": ("STRING", {"default": ""}),
                "value1": ("STRING", {"default": ""}),
                "key2": ("STRING", {"default": ""}),
                "value2": ("STRING", {"default": ""}),
                "key3": ("STRING", {"default": ""}),
                "value3": ("STRING", {"default": ""}),
                "key4": ("STRING", {"default": ""}),
                "value4": ("STRING", {"default": ""}),
                "key5": ("STRING", {"default": ""}),
                "value5": ("STRING", {"default": ""}),
                "key6": ("STRING", {"default": ""}),
                "value6": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("TAGSET",)
    RETURN_NAMES = ("tagset",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, key1:str, value1:str, key2:str, value2:str, key3:str, value3:str, key4:str, value4:str, key5:str, value5:str, key6:str, value6:str) -> tuple:
        tagsets = {}
        tagsets[key1] = value1
        tagsets[key2] = value2
        tagsets[key3] = value3
        tagsets[key4] = value4
        tagsets[key5] = value5
        tagsets[key6] = value6
        return (tagsets,)


class TagPipeOutOne:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tagsets": ("TAGSET",),
                "key1": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("value1",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tagsets:dict, key1:str) -> tuple:
        return (
            tagsets.get(key1, ""),
            )


class TagPipeOut:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tagsets": ("TAGSET",),
                "key1": ("STRING", {"default": ""}),
                "key2": ("STRING", {"default": ""}),
                "key3": ("STRING", {"default": ""}),
                "key4": ("STRING", {"default": ""}),
                "key5": ("STRING", {"default": ""}),
                "key6": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("STRING","STRING","STRING","STRING","STRING","STRING",)
    RETURN_NAMES = ("value1","value2","value3","value4","value5","value6")

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tagsets:dict, key1:str, key2:str, key3:str, key4:str, key5:str, key6:str) -> tuple:
        return (
            tagsets.get(key1, ""),
            tagsets.get(key2, ""),
            tagsets.get(key3, ""),
            tagsets.get(key4, ""),
            tagsets.get(key5, ""),
            tagsets.get(key6, ""),
            )


class TagPipeUpdate:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tagsets": ("TAGSET",),
                "key": ("STRING", {"default": ""}),
                "val": ("STRING", {"default": ""}),
            },
        }

    RETURN_TYPES = ("TAGSET",)
    RETURN_NAMES = ("tagsets",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tagsets:dict, key:str, val:str) -> tuple:
        tagsets[key] = val
        return (tagsets,)


class TagPipeMerge:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tagsets1": ("TAGSET",),
                "tagsets2": ("TAGSET",),
            },
        }

    RETURN_TYPES = ("TAGSET",)
    RETURN_NAMES = ("tagsets",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tagsets1:dict, tagsets2:dict) -> tuple:
        result = tagsets1.copy()
        result.update(tagsets2)
        return (result,)


class TagDetector:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "tags": ("STRING", {"default": ""}),
                "max_join": ("INT", {"default": 4}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, max_join:int=4) -> tuple:
        keys = ["_", "-", ";", "|", "&", "*", "?", "!", "@", "#", "$", "%", "^", "(`)", "( )", "(,)", "(" , ")", "[", "]", "{", "}", "<", ">", "/", "\\", "`", "\n", "\r", "\t"]

        def split_tags(target:str, mykey:str, result:set):
            if not target:
                return
            mysplits = target.split(mykey)
            for mysplit in mysplits:
                mysplit = mysplit.strip()
                if not mysplit:
                    continue
                key_in = False
                for key in keys:
                    if key in mysplit:
                        split_tags(mysplit, key, result)
                        key_in = True

                if not key_in:
                    if mysplit not in result:
                        result.append(mysplit)

        result = []
        
        split_tags(tags, " ", result)

        merge_tags = []
        for i in range(len(result)):
            for j in range(max_join):
                merge_tag = "_".join(result[i:i+j+1])
                if merge_tag not in merge_tags:
                    merge_tags.append(merge_tag)


        tag_category = get_tag_category(2)

        result_tags = []
        for tag in merge_tags:
            if tag in tag_category:
                result_tags.append(tag)

        return (tagdata_to_string(parse_tags(",".join(result_tags))),)


NODE_CLASS_MAPPINGS = {
    "TagSwitcher": TagSwitcher,
    "TagMerger": TagMerger,
    "TagFilter": TagFilter,
    "TagReplace": TagReplace,
    "TagRemover": TagRemover,
    "TagIf": TagIf,
    "TagSelector": TagSelector,
    "TagComparator": TagComparator,
    "TagEnhance": TagEnhance,
    "TagCategoryEnhance": TagCategoryEnhance,
    "TagCategory": TagCategory,
    "TagWildcardFilter": TagWildcardFilter,
    "TagMerger4": TagMerger4,
    "TagMerger6": TagMerger6,
    "TagFlag": TagFlag,
    "TagFlagImage": TagFlagImage,
    "TagRandomCategory": TagRandomCategory,
    "TagPipeIn": TagPipeIn,
    "TagPipeOut": TagPipeOut,
    "TagPipeUpdate": TagPipeUpdate,
    "TagRandom": TagRandom,
    "TagPipeOutOne": TagPipeOutOne,
    "TagDetector": TagDetector,
}


NODE_DISPLAY_NAME_MAPPINGS = {
    "TagSwitcher": "TagSwitcher",
    "TagMerger": "TagMerger",
    "TagFilter": "TagFilter",
    "TagReplace": "TagReplace",
    "TagRemover": "TagRemover",
    "TagIf": "TagIf",
    "TagSelector": "TagSelector",
    "TagComparator": "TagComparator",
    "TagEnhance": "TagEnhance",
    "TagCategoryEnhance": "TagCategoryEnhance",
    "TagCategory": "TagCategory",
    "TagWildcardFilter": "TagWildcardFilter",
    "TagMerger4": "TagMerger4",
    "TagMerger6": "TagMerger6",
    "TagFlag": "TagFlag",
    "TagFlagImage": "TagFlagImage",
    "TagRandomCategory": "TagRandomCategory",
    "TagPipeIn": "TagPipeIn",
    "TagPipeOut": "TagPipeOut",
    "TagPipeUpdate": "TagPipeUpdate",
    "TagRandom": "TagRandom",
    "TagPipeOutOne": "TagPipeOutOne", 
    "TagDetector": "TagDetector",
}
