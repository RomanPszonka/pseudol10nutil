import filecmp
import re
from pathlib import Path

import pytest

from pseudol10nutil import POFileUtil, PseudoL10nUtil, transforms

TESTDATA_DIR = Path(__file__).resolve().parent.parent / "testdata"

TEST_DATA = "The quick brown fox jumps over the lazy dog"


@pytest.fixture
def util() -> PseudoL10nUtil:
    return PseudoL10nUtil()


class TestPOFileUtil:
    def test_generate_pseudolocalized_po(self, tmp_path: Path) -> None:
        input_file = TESTDATA_DIR / "locales" / "helloworld.pot"
        expected_file = (
            TESTDATA_DIR / "locales" / "eo" / "LC_MESSAGES" / "helloworld.po"
        )
        generated_file = tmp_path / "helloworld_generated.po"
        POFileUtil().pseudolocalizefile(input_file, generated_file)
        assert filecmp.cmp(expected_file, generated_file, shallow=False)
        assert generated_file.with_suffix(".mo").is_file()

    def test_missing_input_file_raises(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            POFileUtil().pseudolocalizefile(
                tmp_path / "does_not_exist.pot", tmp_path / "out.po"
            )

    def test_existing_output_file_raises(self, tmp_path: Path) -> None:
        input_file = TESTDATA_DIR / "locales" / "helloworld.pot"
        output_file = tmp_path / "out.po"
        output_file.touch()
        with pytest.raises(FileExistsError):
            POFileUtil().pseudolocalizefile(
                input_file, output_file, overwrite_existing=False
            )


class TestPseudoL10nUtil:
    def test_default(self, util: PseudoL10nUtil) -> None:
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ ƒøẋ ǰüɱƥš øṽêȓ ťȟê ĺàźÿ đøğ﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ⟧"
        assert util.pseudolocalize(TEST_DATA) == expected

    def test_empty_string(self, util: PseudoL10nUtil) -> None:
        assert util.pseudolocalize("") == ""
        assert util.pseudolocalize(None) == ""

    def test_non_string_input_raises(self, util: PseudoL10nUtil) -> None:
        with pytest.raises(TypeError):
            util.pseudolocalize(42)  # type: ignore[arg-type]

    def test_no_transforms_returns_input(self) -> None:
        util = PseudoL10nUtil(init_transforms=[])
        assert util.pseudolocalize(TEST_DATA) == TEST_DATA

    def test_default_fmtspec(self, util: PseudoL10nUtil) -> None:
        test_data_fmtspec = "The quick brown {0} jumps over the lazy {1}."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ {0} ǰüɱƥš øṽêȓ ťȟê ĺàźÿ {1}.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝא⟧"
        assert util.pseudolocalize(test_data_fmtspec) == expected
        test_data_fmtspec = "The quick brown {animal1} jumps over the lazy {animal2}."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ {animal1} ǰüɱƥš øṽêȓ ťȟê ĺàźÿ {animal2}.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘⟧"
        assert util.pseudolocalize(test_data_fmtspec) == expected

    def test_default_printffmtspec(self, util: PseudoL10nUtil) -> None:
        test_data_printffmtspec = "The quick brown %s jumps over the lazy %s."
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ %s ǰüɱƥš øṽêȓ ťȟê ĺàźÿ %s.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ⟧"
        assert util.pseudolocalize(test_data_printffmtspec) == expected
        test_data_printffmtspec = (
            "The quick brown %(animal1)s jumps over the lazy %(animal2)s."
        )
        expected = "⟦Ťȟê ʠüıċǩ ƀȓøẁñ %(animal1)s ǰüɱƥš øṽêȓ ťȟê ĺàźÿ %(animal2)s.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦⟧"
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    def test_custom_placeholder_regex(self) -> None:
        util = PseudoL10nUtil(
            init_transforms=[transforms.transliterate_diacritic],
            placeholder_regex=re.compile(r"(\$\w+)"),
        )
        assert util.pseudolocalize("Hello $name world") == "Ȟêĺĺø $name ẁøȓĺđ"

    def test_transliterate_diacritic(self, util: PseudoL10nUtil) -> None:
        expected = "Ťȟê ʠüıċǩ ƀȓøẁñ ƒøẋ ǰüɱƥš øṽêȓ ťȟê ĺàźÿ đøğ"
        util.transforms = [transforms.transliterate_diacritic]
        assert util.pseudolocalize(TEST_DATA) == expected
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Șøüȓċê {0} ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê {1} ȓêťüȓñêđ 1 ȓøẁ."
        assert util.pseudolocalize(test_data_fmtspec) == expected
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = (
            "Șøüȓċê %(source0)s ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê %(source1)s ȓêťüȓñêđ 1 ȓøẁ."
        )
        assert util.pseudolocalize(test_data_printffmtspec) == expected
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Șøüȓċê %s ȓêťüȓñêđ %d ȓøẁš."
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    def test_transliterate_circled(self, util: PseudoL10nUtil) -> None:
        expected = "Ⓣⓗⓔ ⓠⓤⓘⓒⓚ ⓑⓡⓞⓦⓝ ⓕⓞⓧ ⓙⓤⓜⓟⓢ ⓞⓥⓔⓡ ⓣⓗⓔ ⓛⓐⓩⓨ ⓓⓞⓖ"
        util.transforms = [transforms.transliterate_circled]
        assert util.pseudolocalize(TEST_DATA) == expected
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Ⓢⓞⓤⓡⓒⓔ {0} ⓡⓔⓣⓤⓡⓝⓔⓓ ⓪ ⓡⓞⓦⓢ, ⓢⓞⓤⓡⓒⓔ {1} ⓡⓔⓣⓤⓡⓝⓔⓓ ① ⓡⓞⓦ."
        assert util.pseudolocalize(test_data_fmtspec) == expected
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = (
            "Ⓢⓞⓤⓡⓒⓔ %(source0)s ⓡⓔⓣⓤⓡⓝⓔⓓ ⓪ ⓡⓞⓦⓢ, ⓢⓞⓤⓡⓒⓔ %(source1)s ⓡⓔⓣⓤⓡⓝⓔⓓ ① ⓡⓞⓦ."
        )
        assert util.pseudolocalize(test_data_printffmtspec) == expected
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Ⓢⓞⓤⓡⓒⓔ %s ⓡⓔⓣⓤⓡⓝⓔⓓ %d ⓡⓞⓦⓢ."
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    def test_transliterate_fullwidth(self, util: PseudoL10nUtil) -> None:
        expected = "Ｔｈｅ ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ｊｕｍｐｓ ｏｖｅｒ ｔｈｅ ｌａｚｙ ｄｏｇ"
        util.transforms = [transforms.transliterate_fullwidth]
        assert util.pseudolocalize(TEST_DATA) == expected
        test_data_fmtspec = "Source {0} returned 0 rows, source {1} returned 1 row."
        expected = "Ｓｏｕｒｃｅ {0} ｒｅｔｕｒｎｅｄ ０ ｒｏｗｓ, ｓｏｕｒｃｅ {1} ｒｅｔｕｒｎｅｄ １ ｒｏｗ."
        assert util.pseudolocalize(test_data_fmtspec) == expected
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = "Ｓｏｕｒｃｅ %(source0)s ｒｅｔｕｒｎｅｄ ０ ｒｏｗｓ, ｓｏｕｒｃｅ %(source1)s ｒｅｔｕｒｎｅｄ １ ｒｏｗ."
        assert util.pseudolocalize(test_data_printffmtspec) == expected
        test_data_printffmtspec = "Source %s returned %d rows."
        expected = "Ｓｏｕｒｃｅ %s ｒｅｔｕｒｎｅｄ %d ｒｏｗｓ."
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    @pytest.mark.parametrize(
        ("transform", "expected"),
        [
            (transforms.angle_brackets, f"《{TEST_DATA}》"),
            (transforms.curly_brackets, f"❴{TEST_DATA}❵"),
            (transforms.square_brackets, f"⟦{TEST_DATA}⟧"),
            (transforms.simple_square_brackets, f"[{TEST_DATA}]"),
        ],
    )
    def test_brackets(
        self,
        util: PseudoL10nUtil,
        transform: transforms.Transform,
        expected: str,
    ) -> None:
        util.transforms = [transform]
        assert util.pseudolocalize(TEST_DATA) == expected

    def test_pad_length(self, util: PseudoL10nUtil) -> None:
        expected = "The quick brown fox jumps over the lazy dog﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝ"
        util.transforms = [transforms.pad_length]
        assert util.pseudolocalize(TEST_DATA) == expected

    def test_expand_vowels_no_vowels(self, util: PseudoL10nUtil) -> None:
        util.transforms = [transforms.expand_vowels]
        assert util.pseudolocalize("jmpng") == "jmpnggggggggggg"

    def test_expand_vowels_one_vowel(self, util: PseudoL10nUtil) -> None:
        util.transforms = [transforms.expand_vowels]
        assert util.pseudolocalize("Row") == "Rooooooow"

    def test_expand_vowels_vowel_in_placeholder(self, util: PseudoL10nUtil) -> None:
        test_data_printffmtspec = (
            "Source %(source0)s returned 0 rows, source %(source1)s returned 1 row."
        )
        expected = "Sooouuurceee %(source0)s reeetuuurneeed 0 rooows, sooouuurceee %(source1)s reeetuuurneeed 1 roooow."
        util.transforms = [transforms.expand_vowels]
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    def test_expand_vowels_transliterated_source(self, util: PseudoL10nUtil) -> None:
        test_data_printffmtspec = (
            "Șøüȓċê %(source0)s ȓêťüȓñêđ 0 ȓøẁš, šøüȓċê %(source1)s ȓêťüȓñêđ 1 ȓøẁ."
        )
        expected = "Șøøøüüüȓċêêê %(source0)s ȓêêêťüüüȓñêêêđ 0 ȓøøøẁš, šøøøüüüȓċêêê %(source1)s ȓêêêťüüüȓñêêêđ 1 ȓøøøøẁ."
        util.transforms = [transforms.expand_vowels]
        assert util.pseudolocalize(test_data_printffmtspec) == expected

    def test_expand_vowels_placeholder_only(self, util: PseudoL10nUtil) -> None:
        util.transforms = [transforms.expand_vowels]
        assert util.pseudolocalize("%(source0)s") == "%(source0)s"
