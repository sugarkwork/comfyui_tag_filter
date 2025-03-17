# python -m unittest test_nodes.py

import unittest
import os
import json
from nodes import (
    TagFilter, TagIf, TagSwitcher, TagMerger, TagSelector, 
    TagComparator, TagRemover, TagEnhance, TagCategoryEnhance, 
    TagCategory, TagWildcardFilter, parse_tags, tagdata_to_string
)


class TestTagNodes(unittest.TestCase):
    def setUp(self):
        # テスト用のサンプルタグ
        self.sample_tags = "school_uniform, (long hair, v:1.2), (sitting:1.5), (standing:0.5), attack, ((1girl)), original_tag"
        self.hair_tags = "1girl, long hair, lovery twintails, white long twintails, original tag x, (hoge short hair:1.5)"
        self.looking_tags = "(looking at viewer:1.2), looking back, looking back at viewer, looking at another, looking at camera"
        self.custom_tags = self.looking_tags + ", " + self.sample_tags

    def test_tag_filter(self):
        tf = TagFilter()
        
        # すべてのカテゴリを含め、poseカテゴリを除外するテスト
        result = tf.tag(
            self.sample_tags, 
            pose=False, gesture=False, action=False, emotion=False, 
            expression=False, camera=False, angle=False, sensitive=False, liquid=False,
            include_categories="*", exclude_categories="pose"
        )
        self.assertEqual('school_uniform, (long hair:1.2), (1girl:1.2)', result[0])
        
        # clothingカテゴリのみを含めるテスト
        result = tf.tag(
            self.sample_tags, 
            pose=False, gesture=False, action=False, emotion=False, 
            expression=False, camera=False, angle=False, sensitive=False, liquid=False,
            include_categories="clothing"
        )
        self.assertEqual('school_uniform', result[0])
        
        # actionカテゴリのみを含めるテスト
        result = tf.tag(
            self.sample_tags, 
            pose=False, gesture=False, action=True, emotion=False, 
            expression=False, camera=False, angle=False, sensitive=False, liquid=False
        )
        self.assertEqual('attack', result[0])
        
        # pose, gesture, action, emotion, cameraカテゴリを含めるテスト
        result = tf.tag(
            self.sample_tags, 
            pose=True, gesture=True, action=True, emotion=True, 
            expression=False, camera=True, angle=False, sensitive=False, liquid=False
        )
        self.assertEqual('(v:1.2), (sitting:1.5), (standing:0.5), attack', result[0])

    def test_tag_if(self):
        ti = TagIf()
        
        # sittingタグが存在する場合のテスト
        result = ti.tag(
            tags=self.sample_tags, 
            find="sitting", 
            output1="sitting found"
        )
        self.assertEqual('sitting found', result[0])
        self.assertTrue(result[6])
        
        # 存在しないタグを検索するテスト
        result = ti.tag(
            tags=self.sample_tags, 
            find="school_uniform1", 
            output1="found"
        )
        self.assertEqual('', result[0])
        self.assertFalse(result[6])
        
        # 複数タグの全一致（anytag=False）テスト
        result = ti.tag(
            tags=self.sample_tags,
            find="school_uniform, very long hair",
            anytag=False,
            output1="uniform and long hair found",
            else_output1="not found"
        )
        self.assertEqual('not found', result[3])
        self.assertFalse(result[6])
        
        # 複数タグの部分一致（anytag=True）テスト
        result = ti.tag(
            tags=self.sample_tags,
            find="school_uniform, very long hair",
            anytag=True,
            output1="uniform or very long hair found",
            else_output1="not found"
        )
        self.assertEqual('uniform or very long hair found', result[0])
        self.assertTrue(result[6])

    def test_tag_switcher(self):
        ts = TagSwitcher()
        
        # タグが一致する場合のテスト（any1=True）
        result = ts.tag(
            input_tags=self.sample_tags, 
            default_image="default", 
            tags1="1girl,2girls", 
            image1="image1", 
            any1=True
        )
        self.assertEqual('image1', result[0])
        
        # タグが部分一致するが全一致しない場合のテスト（any1=False）
        result = ts.tag(
            input_tags=self.sample_tags, 
            default_image="default", 
            tags1="1girl,2girls", 
            image1="image1", 
            any1=False
        )
        self.assertEqual('default', result[0])
        
        # タグが一致しない場合のテスト
        result = ts.tag(
            input_tags=self.sample_tags, 
            default_image="default", 
            tags1="2girls", 
            image1="image1", 
            any1=True
        )
        self.assertEqual('default', result[0])

    def test_tag_merger(self):
        tm = TagMerger()
        
        # アンダースコアありでタグをマージするテスト
        result = tm.tag(
            tags1=self.sample_tags, 
            tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long hair", 
            under_score=True
        )
        self.assertEqual('school_uniform, (long_hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2), original_tag, (1boy:1.5), (lying:0.5)', result[0])
        
        # アンダースコアなしでタグをマージするテスト
        result = tm.tag(
            tags1=self.sample_tags, 
            tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long_hair", 
            under_score=False
        )
        self.assertEqual('school_uniform, (long hair:1.2), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.2), original_tag, (1boy:1.5), (lying:0.5)', result[0])

    def test_tag_selector(self):
        ts = TagSelector()
        
        # ホワイトリストありでposeカテゴリを選択するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            whitelist_only=True
        )
        self.assertEqual('(v:1.2), (sitting:1.5), (standing:0.5), attack', result[0])
        
        # ホワイトリストなしでposeカテゴリを選択するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            whitelist_only=False
        )
        self.assertEqual('(v:1.2), (sitting:1.5), (standing:0.5), attack, original_tag', result[0])
        
        # ホワイトリストありでposeカテゴリを除外するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            exclude=True,
            whitelist_only=True
        )
        self.assertEqual('school_uniform, (long hair:1.2), (1girl:1.2)', result[0])
        
        # ホワイトリストなしでposeカテゴリを除外するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            exclude=True,
            whitelist_only=False
        )
        self.assertEqual('school_uniform, (long hair:1.2), (1girl:1.2), original_tag', result[0])
        
        # フレキシブルフィルタありでhair_styleカテゴリを選択するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=False,
            whitelist_only=True,
            flexible_filter=True
        )
        self.assertEqual('long hair, lovery twintails, white long twintails, (hoge short hair:1.5)', result[0])
        
        # フレキシブルフィルタなしでhair styleカテゴリを選択するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair style",
            exclude=False,
            whitelist_only=True,
            flexible_filter=False
        )
        self.assertEqual('long hair', result[0])
        
        # フレキシブルフィルタありでhair_styleカテゴリを選択するテスト（ホワイトリストなし）
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=False,
            whitelist_only=False,
            flexible_filter=True
        )
        self.assertEqual('long hair, lovery twintails, white long twintails, (hoge short hair:1.5)', result[0])
        
        # フレキシブルフィルタありでhair_styleカテゴリを除外するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=True,
            whitelist_only=False,
            flexible_filter=True
        )
        self.assertEqual('1girl, original tag x', result[0])

    def test_tag_comparator(self):
        tc = TagComparator()
        
        # 2つのタグリストを比較するテスト
        result = tc.tag(
            tags1=self.sample_tags, 
            tags2="(1boy:1.5), (1girl:1.5), ((sitting)), (lying:0.5), long hair, twintails"
        )
        self.assertEqual('school_uniform, (v:1.2), (standing:0.5), attack, original_tag', result[0])
        self.assertEqual('(1boy:1.5), (lying:0.5), twintails', result[1])
        self.assertEqual('(long hair:1.2), (sitting:1.5), (1girl:1.2)', result[2])

    def test_tag_remover(self):
        tr = TagRemover()
        
        # 特定のタグを除外するテスト
        result = tr.tag(
            tags=self.sample_tags, 
            exclude_tags="school_uniform, long hair, 1girl"
        )
        self.assertEqual('(v:1.2), (sitting:1.5), (standing:0.5), attack, original_tag', result[0])

    def test_tag_enhance(self):
        te = TagEnhance()
        
        # 特定のタグの重みを加算するテスト
        result = te.tag(
            tags=self.sample_tags, 
            enhance_tags="school_uniform, long hair, 1girl", 
            strength=0.5, 
            add_strength=True
        )
        self.assertEqual('(school_uniform:1.5), (long hair:1.7), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:1.7), original_tag', result[0])
        
        # 特定のタグの重みを設定するテスト
        result = te.tag(
            tags=self.sample_tags, 
            enhance_tags="school_uniform, long hair, 1girl", 
            strength=0.5, 
            add_strength=False
        )
        self.assertEqual('(school_uniform:0.5), (long hair:0.5), (v:1.2), (sitting:1.5), (standing:0.5), attack, (1girl:0.5), original_tag', result[0])

    def test_tag_category_enhance(self):
        tce = TagCategoryEnhance()
        
        # 特定のカテゴリのタグの重みを加算するテスト
        result = tce.tag(
            tags=self.sample_tags, 
            enhance_category="pose", 
            strength=0.5, 
            add_strength=True
        )
        self.assertEqual('school_uniform, (long hair:1.2), (v:1.7), (sitting:2.0), standing, (attack:1.5), (1girl:1.2), original_tag', result[0])
        
        # 特定のカテゴリのタグの重みを設定するテスト
        result = tce.tag(
            tags=self.sample_tags, 
            enhance_category="pose", 
            strength=0.5, 
            add_strength=False
        )
        self.assertEqual('school_uniform, (long hair:1.2), (v:0.5), (sitting:0.5), (standing:0.5), (attack:0.5), (1girl:1.2), original_tag', result[0])

    def test_tag_category(self):
        tc = TagCategory()
        
        # タグのカテゴリを取得するテスト
        result = tc.tag(tags="1girl, long hair")
        # カテゴリの順序は保証されていないため、特定のカテゴリが含まれているかをチェック
        self.assertIn('camera_subject', result[0])
        self.assertIn('hair_style', result[0])
        self.assertIn('hair', result[0])
        self.assertIn('gender', result[0])

    def test_tag_wildcard_filter(self):
        twf = TagWildcardFilter()
        
        # ワイルドカード "long*" でフィルタするテスト
        result = twf.tag(tags=self.sample_tags, wildcard="long*")
        self.assertEqual('(long hair:1.2)', result[0])
        
        # ワイルドカード "*uniform" でフィルタするテスト
        result = twf.tag(tags=self.sample_tags, wildcard="*uniform")
        self.assertEqual('school_uniform', result[0])
        
        # ワイルドカード "looking *" でフィルタするテスト
        result = twf.tag(tags=self.custom_tags, wildcard="looking *")
        self.assertEqual(self.looking_tags, result[0])
        
        # ワイルドカード "l*k" でフィルタするテスト
        result = twf.tag(tags=self.custom_tags, wildcard="l*k")
        self.assertEqual('looking back', result[0])


if __name__ == "__main__":
    unittest.main()