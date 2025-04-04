import os
import json


tag_category1 = [] 
tag_category2 = []


def get_tag_category(version=1):
    global tag_category1, tag_category2
    if version == 1:
        if not tag_category1:
            tag_category1 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category.json")))
        return tag_category1
    else:
        if not tag_category2:
            tag_category2 = json.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"tag_category_v2.json")))
        return tag_category2


def format_category(categories: str) -> list:
    return [category.lower().strip().replace(" ", "_") for category in categories.replace("\n",",").replace(".",",").split(",")]


class TagData:
    def __init__(self, tag, weight):
        self.tag = tag
        self.weight = weight
        self.format = tag.lower().strip().replace(' ', '_')
    
    def get_categores(self):
        return get_tag_category(2).get(self.format, [])
    
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
        
        if self.weight != 1.0:
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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("result",)

    FUNCTION = "tag"

    CATEGORY = "text"

    OUTPUT_NODE = True

    def tag(self, tags:str, categorys:str, exclude:bool=False, whitelist_only:bool=False, flexible_filter:bool=False):
        tag_list = parse_tags(tags)
        tag_category = get_tag_category(2)
        target_category = format_category(categorys)

        result = []
        for i, tag in enumerate(tag_list):
            tag_text = tag.format
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

        return (tagdata_to_string(result),)


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
            tag_text = tag.format
            if tag_text in tag_category:
                category_list = tag_category.get(tag_text, [])

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
                    tag.weight += strength
                else:
                    tag.weight = strength
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
                    tag.weight += strength
                else:
                    tag.weight = strength
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
            tag_text = tag.format
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

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("tags",)

    FUNCTION = "tag"
    CATEGORY = "text"
    OUTPUT_NODE = True

    def tag(self, tags:str, wildcard:str):
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
                if re.match(wildcard, tag.format):
                    result.append(tag)
            else:    
                if wildcard in tag.format:
                    result.append(tag)
        
        return (tagdata_to_string(result),)


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
    "TagWildcardFilter": TagWildcardFilter
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
    "TagWildcardFilter": "TagWildcardFilter"
}
