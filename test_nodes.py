# python -m unittest test_nodes.py

import unittest
import os
import json
from nodes import (
    TagFilter, TagIf, TagSwitcher, TagMerger, TagSelector, 
    TagComparator, TagRemover, TagEnhance, TagCategoryEnhance, 
    TagCategory, TagWildcardFilter, parse_tags, tagdata_to_string,
    TagFlag, TagFlagImage, TagRandom
)


class TestTagNodes(unittest.TestCase):
    def setUp(self):
        # テスト用のサンプルタグ
        self.sample_tags = "school_uniform, (long hair, v:1.2), (sitting:1.5), (standing:0.5), attack, ((1girl)), original_tag"
        self.hair_tags = "1girl, long hair, lovery twintails, white long twintails, original tag x, (hoge short hair:1.5)"
        self.looking_tags = "(looking at viewer:1.2), looking back, looking back at viewer, looking at another, looking at camera"
        self.wildcard_tags = "hair_ornament, long_hair, straight_hair, short hair, hair accessory, (medium hair:1.2), unknown_tag"
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
        self.assertTrue(result[1])
        
        # ホワイトリストなしでposeカテゴリを選択するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            whitelist_only=False
        )
        self.assertEqual('(v:1.2), (sitting:1.5), (standing:0.5), attack, original_tag', result[0])
        self.assertTrue(result[1])
        
        # ホワイトリストありでposeカテゴリを除外するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            exclude=True,
            whitelist_only=True
        )
        self.assertEqual('school_uniform, (long hair:1.2), (1girl:1.2)', result[0])
        self.assertTrue(result[1])
        
        # ホワイトリストなしでposeカテゴリを除外するテスト
        result = ts.tag(
            tags=self.sample_tags, 
            categorys="pose", 
            exclude=True,
            whitelist_only=False
        )
        self.assertEqual('school_uniform, (long hair:1.2), (1girl:1.2), original_tag', result[0])
        self.assertTrue(result[1])
        
        # フレキシブルフィルタありでhair_styleカテゴリを選択するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=False,
            whitelist_only=True,
            flexible_filter=True
        )
        self.assertEqual('long hair, lovery twintails, white long twintails, (hoge short hair:1.5)', result[0])
        self.assertTrue(result[1])
        
        # フレキシブルフィルタなしでhair styleカテゴリを選択するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair style",
            exclude=False,
            whitelist_only=True,
            flexible_filter=False
        )
        self.assertEqual('long hair', result[0])
        self.assertTrue(result[1])
        
        # フレキシブルフィルタありでhair_styleカテゴリを選択するテスト（ホワイトリストなし）
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=False,
            whitelist_only=False,
            flexible_filter=True
        )
        self.assertEqual('long hair, lovery twintails, white long twintails, (hoge short hair:1.5)', result[0])
        self.assertTrue(result[1])
        
        # フレキシブルフィルタありでhair_styleカテゴリを除外するテスト
        result = ts.tag(
            tags=self.hair_tags,
            categorys="hair_style",
            exclude=True,
            whitelist_only=False,
            flexible_filter=True
        )
        self.assertEqual('1girl, original tag x', result[0])
        self.assertTrue(result[1])

        result = ts.tag(
            tags=self.hair_tags,
            categorys="character", # not exist category
            exclude=False,
            whitelist_only=False,
            flexible_filter=True
        )
        self.assertEqual('', result[0])
        self.assertFalse(result[1])

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
        self.assertTrue(result[1])
        
        # ワイルドカード "*uniform" でフィルタするテスト
        result = twf.tag(tags=self.sample_tags, wildcard="*uniform")
        self.assertEqual('school_uniform', result[0])
        self.assertTrue(result[1])
        
        # ワイルドカード "looking *" でフィルタするテスト
        result = twf.tag(tags=self.custom_tags, wildcard="looking *")
        self.assertEqual(self.looking_tags, result[0])
        self.assertTrue(result[1])
        
        # ワイルドカード "l*k" でフィルタするテスト
        result = twf.tag(tags=self.custom_tags, wildcard="l*k")
        self.assertEqual('looking back', result[0])
        self.assertTrue(result[1])

        result = twf.tag(tags=self.wildcard_tags, wildcard="*hair*")
        self.assertEqual('hair_ornament, long_hair, straight_hair, short hair, hair accessory, (medium hair:1.2)', result[0])
        self.assertTrue(result[1])

        result = twf.tag(tags=self.wildcard_tags, wildcard="hair*")
        self.assertEqual('hair_ornament, hair accessory', result[0])
        self.assertTrue(result[1])

        result = twf.tag(tags=self.wildcard_tags, wildcard="*hair")
        self.assertEqual('long_hair, straight_hair, short hair, (medium hair:1.2)', result[0])
        self.assertTrue(result[1])

        result = twf.tag(tags=self.wildcard_tags, wildcard="*skirt")
        self.assertFalse(result[1])

        result = twf.tag(tags=self.wildcard_tags, wildcard="skirt*")
        self.assertFalse(result[1])

    
    def test_parse_tags_escape(self):
        n2b = '2b_\\(nier:automata\\)'
        n9s = '9s \\(nier\\:automata\\)'
        tag1 = "1girl, 1boy, 2b_\\(nier:automata\\), (9s \\(nier\\:automata\\):1.2)"
        
        tag2 = parse_tags(tag1)
        # tagdata_to_stringはweight=1.0のとき括弧なし、weight!=1.0のとき括弧付き
        self.assertEqual(tag1, tagdata_to_string(tag2))
        
        tag3 = parse_tags(n9s)[0]
        self.assertEqual(n9s.replace('\\', '').replace(' ', '_'), tag3.format_unescape)
        self.assertEqual(tag3.weight, 1.0)

        tf = TagFilter()
        result_tags = tf.tag(tag1, include_categories="character")[0]
        self.assertIn(n2b, result_tags)
        self.assertIn(n9s, result_tags)

        te = TagEnhance()
        result_tags = te.tag(tag1, n9s.replace(' ', '_'), 0.5, True)[0]
        self.assertIn('(9s \\(nier\\:automata\\):1.7)', result_tags)

        result_tags = te.tag(tag1, n9s.replace(' ', '_'), 0.5, False)[0]
        self.assertIn('(9s \\(nier\\:automata\\):0.5)', result_tags)

        result_tags = te.tag(tag1, "1girl", 1.0, False)[0]
        self.assertIn('1girl', result_tags)

        result_tags = te.tag(tag1, "1girl", 1.1, False)[0]
        self.assertIn('(1girl:1.1)', result_tags)

        result_tags = te.tag(result_tags, "1girl", 0.1, True)[0]
        self.assertIn('(1girl:1.2)', result_tags)

        result_tags = te.tag(result_tags, "1girl", 0.1, True)[0]
        self.assertIn('(1girl:1.3)', result_tags)

        result_tags = te.tag(result_tags, "1girl", 0.1, True)[0]
        self.assertIn('(1girl:1.4)', result_tags)

        tc = TagCategory()
        result_tags = tc.tag(tag1)[0]
        self.assertIn('character', result_tags)
        self.assertIn('gender', result_tags)

        tce = TagCategoryEnhance()
        result_tags = tce.tag(tag1, 'character', 0.5, False)[0]
        self.assertIn('(2b_\\(nier:automata\\):0.5)', result_tags)
        self.assertIn('(9s \\(nier\\:automata\\):0.5)', result_tags)


    def test_tag_flag(self):
        tf = TagFlag()
        
        # タグのフラグを取得するテスト
        result = tf.tag(output_tags1="1girl, 1boy", output_flag1=True, 
                        output_tags2="2girls", output_flag2=False, 
                        output_tags3="3girls", output_flag3=True, 
                        output_tags4="4girls", output_flag4=False)
        self.assertEqual(type(result), tuple)
        self.assertEqual('1girl, 1boy', result[0])
        self.assertEqual('', result[1])
        self.assertEqual('3girls', result[2])
        self.assertEqual('', result[3])
        self.assertEqual('1girl, 1boy, 3girls', result[4])

        result = tf.tag(output_tags1="1girl, 1boy", output_flag1=False, 
                        output_tags2="2girls", output_flag2=False, 
                        output_tags3="3girls", output_flag3=False, 
                        output_tags4="4girls", output_flag4=False)
        self.assertEqual('', result[4])

        result = tf.tag(output_tags1="1girl, 1boy", output_flag1=True, 
                        output_tags2="2girls", output_flag2=True, 
                        output_tags3="3girls", output_flag3=True, 
                        output_tags4="4girls", output_flag4=True)
        self.assertEqual('1girl, 1boy, 2girls, 3girls, 4girls', result[4])

        # no tag merge
        result = tf.tag(output_tags1="1girl, 1boy", output_flag1=True, 
                        output_tags2="1girl", output_flag2=True, 
                        output_tags3="3girls", output_flag3=True, 
                        output_tags4="4girls", output_flag4=True)
        self.assertEqual('1girl, 1boy, 1girl, 3girls, 4girls', result[4])

        result = tf.tag(output_tags1="(1girl:1.2), 1boy", output_flag1=True, 
                        output_tags2="1girl", output_flag2=True, 
                        output_tags3="3girls", output_flag3=True, 
                        output_tags4="(4girls:1.5)", output_flag4=True)
        self.assertEqual('(1girl:1.2), 1boy, 1girl, 3girls, (4girls:1.5)', result[4])


    def test_tag_flag_image(self):
        tfi = TagFlagImage()
        
        # タグのフラグを取得するテスト
        result = tfi.tag(
            default_image="default_image",
            output_image1="image1", output_flag1=True, 
            output_image2="image2", output_flag2=False, 
            output_image3="image3", output_flag3=True, 
            output_image4="image4", output_flag4=False)
        
        self.assertEqual(type(result), tuple)
        self.assertIsNotNone(result[0])
        self.assertEqual('image1', result[0])
        self.assertIsNotNone(result[1])
        self.assertEqual('default_image', result[1])
        self.assertIsNotNone(result[2])
        self.assertEqual('image3', result[2])
        self.assertIsNotNone(result[3])
        self.assertEqual('default_image', result[3])
        self.assertEqual('image3', result[4])

        result = tfi.tag(
            default_image="default_image",
            output_image1="image1", output_flag1=True, 
            output_image2="image2", output_flag2=False, 
            output_image3="image3", output_flag3=False, 
            output_image4="image4", output_flag4=False)
        
        self.assertEqual(type(result), tuple)
        self.assertIsNotNone(result[0])
        self.assertEqual('image1', result[0])
        self.assertIsNotNone(result[1])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])
        self.assertEqual('image1', result[4])

        result = tfi.tag(
            default_image="default_image",
            output_image1="image1", output_flag1=False, 
            output_image2="image2", output_flag2=False, 
            output_image3="image3", output_flag3=False, 
            output_image4="image4", output_flag4=False)
        
        self.assertEqual(type(result), tuple)
        self.assertIsNotNone(result[0])
        self.assertIsNotNone(result[1])
        self.assertIsNotNone(result[2])
        self.assertIsNotNone(result[3])        
        self.assertEqual('default_image', result[4])
    

    def test_tag_random_category(self):
        from nodes import TagRandomCategory
        trc = TagRandomCategory()

        result = trc.tag(
            category="hair_style, eye_color, celestial_body, sky",
            negative_category="hair_accessory, nature",
            count=2
        )
        
        tc = TagCategory()
        result_tags = tc.tag(result[0])[0]
        self.assertIn('hair_style', result_tags)
        self.assertIn('eye_color', result_tags)
        self.assertNotIn('nature', result_tags)
        self.assertNotIn('hair_accessory', result_tags)


    def test_tag_pipe(self):
        from nodes import TagPipeIn, TagPipeOut, TagPipeUpdate, TagPipeOutOne, TagPipeMerge
        tpi = TagPipeIn()
        result = tpi.tag(
            key1="tag1", value1="value1",
            key2="tag2", value2="value2",
            key3="tag3", value3="value3",
            key4="tag4", value4="value4",
            key5="tag5", value5="value5",
            key6="tag6", value6="value6"
        )[0]
        self.assertIn('tag1', result)
        self.assertIn('tag2', result)
        self.assertIn('tag3', result)
        self.assertIn('tag4', result)
        self.assertIn('tag5', result)
        self.assertIn('tag6', result)


        tpu = TagPipeUpdate()
        pipe_data = tpu.tag(
            tagsets=result,
            key="tag1", val="new_value1",
        )[0]

        tpo = TagPipeOut()
        result = tpo.tag(
            tagsets=pipe_data,
            key1="tag1",
            key2="tag2",
            key3="tag3",
            key4="tag4",
            key5="tag5",
            key6="tag6"
        )
        self.assertEqual('new_value1', result[0])
        self.assertEqual('value2', result[1])
        self.assertEqual('value3', result[2])
        self.assertEqual('value4', result[3])
        self.assertEqual('value5', result[4])
        self.assertEqual('value6', result[5])

        tpo = TagPipeOutOne()
        result = tpo.tag(pipe_data, key1="tag1")
        self.assertEqual('new_value1', result[0])

        tpm = TagPipeMerge()
        pipe_data2 = tpm.tag(pipe_data, {"key1": "tag1"})[0]
        self.assertIn('tag1', pipe_data2)
        self.assertIn('tag2', pipe_data2)
        self.assertEqual('tag1', pipe_data2['key1'])

    def test_tag_random(self):
        tr = TagRandom()

        for _ in range(20):
            result = tr.tag(
                tags=self.sample_tags,
                count_min=2,
                count_max=4
            )

            tags = parse_tags(result[0])
            self.assertTrue(len(tags) >= 2)
            self.assertTrue(len(tags) <= 4)

        for _ in range(20):
            result = tr.tag(
                tags=self.sample_tags,
                count_min=5,
                count_max=1
            )

            tags = parse_tags(result[0])
            self.assertTrue(len(tags) >= 1)
            self.assertTrue(len(tags) <= 5)

        for _ in range(20):
            result = tr.tag(
                tags=self.sample_tags,
                count_min=2,
                count_max=4,
                seed=1234
            )

            tags = parse_tags(result[0])
            self.assertTrue(len(tags) >= 2)
            self.assertTrue(len(tags) <= 4)

        for _ in range(20):
            result = tr.tag(
                tags=self.sample_tags,
                count_min=5,
                count_max=1,
                seed=1234
            )

            tags = parse_tags(result[0])
            self.assertTrue(len(tags) >= 1)
            self.assertTrue(len(tags) <= 5)

if __name__ == "__main__":
    unittest.main()
