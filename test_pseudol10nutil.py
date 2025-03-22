# -*- coding: utf-8 -*-

import filecmp
import os.path
import unittest

from pseudol10nutil import POFileUtil, PseudoL10nUtil, transforms


class TestPOFileUtil(unittest.TestCase):
    def setUp(self):
        self.pofileutil = POFileUtil()

    def test_generate_pseudolocalized_po(self):
        input_file = "./testdata/locales/helloworld.pot"
        expected_file = "./testdata/locales/eo/LC_MESSAGES/helloworld.po"
        basename, ext = os.path.splitext(expected_file)
        generated_file = basename + "_generated" + ext
        self.pofileutil.pseudolocalizefile(input_file, generated_file)
        self.assertTrue(filecmp.cmp(expected_file, generated_file))
        os.remove(generated_file)


class TestPseudoL10nUtil(unittest.TestCase):
    def setUp(self):
        self.util = PseudoL10nUtil()
        self.test_data = "The quick brown fox jumps over the lazy dog"

    def test_default(self):
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ ƒøẋ ǰüɱƥš øṽêȓ ťȟê ĺàźÿ đøğ﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ⟧"
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_empty_string(self):
        self.assertEqual("", self.util.pseudolocalize(""))
        self.assertEqual("", self.util.pseudolocalize(None))

    def test_default_fmtspec(self):
        test_data_fmtspec = "The quick brown {0} jumps over the lazy {1}."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ {0} ǰüɱƥš øṽêȓ ťȟê ĺàźÿ {1}.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝא⟧"
        self.assertEqual(expected, self.util.pseudolocalize(test_data_fmtspec))
        test_data_fmtspec = "The quick brown {animal1} jumps over the lazy {animal2}."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ {animal1} ǰüɱƥš øṽêȓ ťȟê ĺàźÿ {animal2}.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘⟧"
        self.assertEqual(expected, self.util.pseudolocalize(test_data_fmtspec))

    def test_default_printffmtspec(self):
        test_data_printffmtspec = "The quick brown %s jumps over the lazy %s."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ %s ǰüɱƥš øṽêȓ ťȟê ĺàźÿ %s.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ⟧"
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))
        test_data_printffmtspec = (
            "The quick brown %(animal1)s jumps over the lazy %(animal2)s."
        )
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ %(animal1)s ǰüɱƥš øṽêȓ ťȟê ĺàźÿ %(animal2)s.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦⟧"
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_transliterate_diacritic(self):
        expected = "Ťȟê ʠüıċǩ ƀȓøẁñ ƒøẋ ǰüɱƥš øṽêȓ ťȟê ĺàźÿ đøğ"
        self.util.transforms = [transforms.transliterate_diacritic]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Șøüȓċê {0} ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê {1} ȓêťüȓñêđ 1 ȓøẁ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_fmtspec))
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = (
            "Șøüȓċê %(source0)s ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê %(source1)s ȓêťüȓñêđ 1 ȓøẁ."
        )
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Șøüȓċê %s ȓêťüȓñêđ %d ȓøẁš."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_transliterate_circled(self):
        expected = "Ⓣⓗⓔ ⓠⓤⓘⓒⓚ ⓑⓡⓞⓦⓝ ⓕⓞⓧ ⓙⓤⓜⓟⓢ ⓞⓥⓔⓡ ⓣⓗⓔ ⓛⓐⓩⓨ ⓓⓞⓖ"
        self.util.transforms = [transforms.transliterate_circled]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Ⓢⓞⓤⓡⓒⓔ {0} ⓡⓔⓣⓤⓡⓝⓔⓓ ⓪ ⓡⓞⓦⓢ, ⓢⓞⓤⓡⓒⓔ {1} ⓡⓔⓣⓤⓡⓝⓔⓓ ① ⓡⓞⓦ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_fmtspec))
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = (
            "Ⓢⓞⓤⓡⓒⓔ %(source0)s ⓡⓔⓣⓤⓡⓝⓔⓓ ⓪ ⓡⓞⓦⓢ, ⓢⓞⓤⓡⓒⓔ %(source1)s ⓡⓔⓣⓤⓡⓝⓔⓓ ① ⓡⓞⓦ."
        )
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Ⓢⓞⓤⓡⓒⓔ %s ⓡⓔⓣⓤⓡⓝⓔⓓ %d ⓡⓞⓦⓢ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_transliterate_fullwidth(self):
        expected = "Ｔｈｅ ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ｊｕｍｐｓ ｏｖｅｒ ｔｈｅ ｌａｚｙ ｄｏｇ"
        self.util.transforms = [transforms.transliterate_fullwidth]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Ｓｏｕｒｃｅ {0} ｒｅｔｕｒｎｅｄ ０ ｒｏｗｓ, ｓｏｕｒｃｅ {1} ｒｅｔｕｒｎｅｄ １ ｒｏｗ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_fmtspec))
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = "Ｓｏｕｒｃｅ %(source0)s ｒｅｔｕｒｎｅｄ ０ ｒｏｗｓ, ｓｏｕｒｃｅ %(source1)s ｒｅｔｕｒｎｅｄ １ ｒｏｗ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Ｓｏｕｒｃｅ %s ｒｅｔｕｒｎｅｄ %d ｒｏｗｓ."
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_angle_brackets(self):
        expected = "《The quick brown fox jumps over the lazy dog》"
        self.util.transforms = [transforms.angle_brackets]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_curly_brackets(self):
        expected = "❴The quick brown fox jumps over the lazy dog❵"
        self.util.transforms = [transforms.curly_brackets]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_square_brackets(self):
        expected = "⟦The quick brown fox jumps over the lazy dog⟧"
        self.util.transforms = [transforms.square_brackets]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_simple_square_brackets(self):
        expected = "[The quick brown fox jumps over the lazy dog]"
        self.util.transforms = [transforms.simple_square_brackets]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_pad_length(self):
        expected = "The quick brown fox jumps over the lazy dog﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ"
        self.util.transforms = [transforms.pad_length]
        self.assertEqual(expected, self.util.pseudolocalize(self.test_data))

    def test_expand_vowels_no_vowels(self):
        test_data = "jmpng"
        expected = "jmpnggggggggggg"
        self.util.transforms = [transforms.expand_vowels]
        self.assertEqual(expected, self.util.pseudolocalize(test_data))

    def test_expand_vowels_one_vowel(self):
        test_data = "Row"
        expected = "Rooooooow"
        self.util.transforms = [transforms.expand_vowels]
        self.assertEqual(expected, self.util.pseudolocalize(test_data))

    def test_expand_vowels_vowel_in_placeholder(self):
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = "Sooouuurceee %(source0)s reeetuuurneeed 0 rooows, sooouuurceee %(source1)s reeetuuurneeed 1 roooow."
        self.util.transforms = [transforms.expand_vowels]
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_expand_vowels_transliterated_source(self):
        test_data_printffmtspec = (
            "Șøüȓċê %(source0)s ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê %(source1)s ȓêťüȓñêđ 1 ȓøẁ."
        )
        expected = "Șøøøüüüȓċêêê %(source0)s ȓêêêťüüüȓñêêêđ 0 ȓøøøẁš, šøøøüüüȓċêêê %(source1)s ȓêêêťüüüȓñêêêđ 1 ȓøøøøẁ."
        self.util.transforms = [transforms.expand_vowels]
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))

    def test_expand_vowels_placeholder_only(self):
        test_data_printffmtspec = "%(source0)s"
        expected = "%(source0)s"
        self.util.transforms = [transforms.expand_vowels]
        self.assertEqual(expected, self.util.pseudolocalize(test_data_printffmtspec))


if __name__ == "__main__":
    unittest.main()
