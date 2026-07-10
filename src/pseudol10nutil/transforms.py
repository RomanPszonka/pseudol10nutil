"""Transform functions for pseudo-localizing strings.

Each transform takes the string to transform and the compiled placeholder
regex and returns the transformed string.  Transforms can be composed by
assigning a list of them to :attr:`PseudoL10nUtil.transforms`.
"""

import itertools
import math
import re
from collections.abc import Callable

type Transform = Callable[[str, re.Pattern[str]], str]
"""Signature shared by all transform functions."""

_DIACRITIC_TABLE: dict[int, int] = {
    0x0041: 0x00C5,  # LATIN CAPITAL LETTER A -> LATIN CAPITAL LETTER A WITH RING ABOVE
    0x0042: 0x0181,  # LATIN CAPITAL LETTER B -> LATIN CAPITAL LETTER B WITH HOOK
    0x0043: 0x010A,  # LATIN CAPITAL LETTER C -> LATIN CAPITAL LETTER C WITH DOT ABOVE
    0x0044: 0x0110,  # LATIN CAPITAL LETTER D -> LATIN CAPITAL LETTER D WITH STROKE
    0x0045: 0x0204,  # LATIN CAPITAL LETTER E -> LATIN CAPITAL LETTER E WITH DOUBLE GRAVE
    0x0046: 0x1E1E,  # LATIN CAPITAL LETTER F -> LATIN CAPITAL LETTER F WITH DOT ABOVE
    0x0047: 0x0120,  # LATIN CAPITAL LETTER G -> LATIN CAPITAL LETTER G WITH DOT ABOVE
    0x0048: 0x021E,  # LATIN CAPITAL LETTER H -> LATIN CAPITAL LETTER H WITH CARON
    0x0049: 0x0130,  # LATIN CAPITAL LETTER I -> LATIN CAPITAL LETTER I WITH DOT ABOVE
    0x004A: 0x0134,  # LATIN CAPITAL LETTER J -> LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    0x004B: 0x01E8,  # LATIN CAPITAL LETTER K -> LATIN CAPITAL LETTER K WITH CARON
    0x004C: 0x0139,  # LATIN CAPITAL LETTER L -> LATIN CAPITAL LETTER L WITH ACUTE
    0x004D: 0x1E40,  # LATIN CAPITAL LETTER M -> LATIN CAPITAL LETTER M WITH DOT ABOVE
    0x004E: 0x00D1,  # LATIN CAPITAL LETTER N -> LATIN CAPITAL LETTER N WITH TILDE
    0x004F: 0x00D2,  # LATIN CAPITAL LETTER O -> LATIN CAPITAL LETTER O WITH GRAVE
    0x0050: 0x01A4,  # LATIN CAPITAL LETTER P -> LATIN CAPITAL LETTER P WITH HOOK
    0x0051: 0xA756,  # LATIN CAPITAL LETTER Q -> LATIN CAPITAL LETTER Q WITH STROKE THROUGH DESCENDER
    0x0052: 0x0212,  # LATIN CAPITAL LETTER R -> LATIN CAPITAL LETTER R WITH INVERTED BREVE
    0x0053: 0x0218,  # LATIN CAPITAL LETTER S -> LATIN CAPITAL LETTER S WITH COMMA BELOW
    0x0054: 0x0164,  # LATIN CAPITAL LETTER T -> LATIN CAPITAL LETTER T WITH CARON
    0x0055: 0x00DC,  # LATIN CAPITAL LETTER U -> LATIN CAPITAL LETTER U WITH DIAERESIS
    0x0056: 0x1E7C,  # LATIN CAPITAL LETTER V -> LATIN CAPITAL LETTER V WITH TILDE
    0x0057: 0x1E82,  # LATIN CAPITAL LETTER W -> LATIN CAPITAL LETTER W WITH ACUTE
    0x0058: 0x1E8C,  # LATIN CAPITAL LETTER X -> LATIN CAPITAL LETTER X WITH DIAERESIS
    0x0059: 0x1E8E,  # LATIN CAPITAL LETTER Y -> LATIN CAPITAL LETTER Y WITH DOT ABOVE
    0x005A: 0x017D,  # LATIN CAPITAL LETTER Z -> LATIN CAPITAL LETTER Z WITH CARON
    0x0061: 0x00E0,  # LATIN SMALL LETTER A -> LATIN SMALL LETTER A WITH GRAVE
    0x0062: 0x0180,  # LATIN SMALL LETTER B -> LATIN SMALL LETTER B WITH STROKE
    0x0063: 0x010B,  # LATIN SMALL LETTER C -> LATIN SMALL LETTER C WITH DOT ABOVE
    0x0064: 0x0111,  # LATIN SMALL LETTER D -> LATIN SMALL LETTER D WITH STROKE
    0x0065: 0x00EA,  # LATIN SMALL LETTER E -> LATIN SMALL LETTER E WITH CIRCUMFLEX
    0x0066: 0x0192,  # LATIN SMALL LETTER F -> LATIN SMALL LETTER F WITH HOOK
    0x0067: 0x011F,  # LATIN SMALL LETTER G -> LATIN SMALL LETTER G WITH BREVE
    0x0068: 0x021F,  # LATIN SMALL LETTER H -> LATIN SMALL LETTER H WITH CARON
    0x0069: 0x0131,  # LATIN SMALL LETTER I -> LATIN SMALL LETTER DOTLESS I
    0x006A: 0x01F0,  # LATIN SMALL LETTER J -> LATIN SMALL LETTER J WITH CARON
    0x006B: 0x01E9,  # LATIN SMALL LETTER K -> LATIN SMALL LETTER K WITH CARON
    0x006C: 0x013A,  # LATIN SMALL LETTER L -> LATIN SMALL LETTER L WITH ACUTE
    0x006D: 0x0271,  # LATIN SMALL LETTER M -> LATIN SMALL LETTER M WITH HOOK
    0x006E: 0x00F1,  # LATIN SMALL LETTER N -> LATIN SMALL LETTER N WITH TILDE
    0x006F: 0x00F8,  # LATIN SMALL LETTER O -> LATIN SMALL LETTER O WITH STROKE
    0x0070: 0x01A5,  # LATIN SMALL LETTER P -> LATIN SMALL LETTER P WITH HOOK
    0x0071: 0x02A0,  # LATIN SMALL LETTER Q -> LATIN SMALL LETTER Q WITH HOOK
    0x0072: 0x0213,  # LATIN SMALL LETTER R -> LATIN SMALL LETTER R WITH INVERTED BREVE
    0x0073: 0x0161,  # LATIN SMALL LETTER S -> LATIN SMALL LETTER S WITH CARON
    0x0074: 0x0165,  # LATIN SMALL LETTER T -> LATIN SMALL LETTER T WITH CARON
    0x0075: 0x00FC,  # LATIN SMALL LETTER U -> LATIN SMALL LETTER U WITH DIAERESIS
    0x0076: 0x1E7D,  # LATIN SMALL LETTER V -> LATIN SMALL LETTER V WITH TILDE
    0x0077: 0x1E81,  # LATIN SMALL LETTER W -> LATIN SMALL LETTER W WITH GRAVE
    0x0078: 0x1E8B,  # LATIN SMALL LETTER X -> LATIN SMALL LETTER X WITH DOT ABOVE
    0x0079: 0x00FF,  # LATIN SMALL LETTER Y -> LATIN SMALL LETTER Y WITH DIAERESIS
    0x007A: 0x017A,  # LATIN SMALL LETTER Z -> LATIN SMALL LETTER Z WITH ACUTE
}

_CIRCLED_TABLE: dict[int, int] = {
    0x0030: 0x24EA,  # DIGIT ZERO -> CIRCLED DIGIT ZERO
    0x0031: 0x2460,  # DIGIT ONE -> CIRCLED DIGIT ONE
    0x0032: 0x2461,  # DIGIT TWO -> CIRCLED DIGIT TWO
    0x0033: 0x2462,  # DIGIT THREE -> CIRCLED DIGIT THREE
    0x0034: 0x2463,  # DIGIT FOUR -> CIRCLED DIGIT FOUR
    0x0035: 0x2464,  # DIGIT FIVE -> CIRCLED DIGIT FIVE
    0x0036: 0x2465,  # DIGIT SIX -> CIRCLED DIGIT SIX
    0x0037: 0x2466,  # DIGIT SEVEN -> CIRCLED DIGIT SEVEN
    0x0038: 0x2467,  # DIGIT EIGHT -> CIRCLED DIGIT EIGHT
    0x0039: 0x2468,  # DIGIT NINE -> CIRCLED DIGIT NINE
    0x0041: 0x24B6,  # LATIN CAPITAL LETTER A -> CIRCLED LATIN CAPITAL LETTER A
    0x0042: 0x24B7,  # LATIN CAPITAL LETTER B -> CIRCLED LATIN CAPITAL LETTER B
    0x0043: 0x24B8,  # LATIN CAPITAL LETTER C -> CIRCLED LATIN CAPITAL LETTER C
    0x0044: 0x24B9,  # LATIN CAPITAL LETTER D -> CIRCLED LATIN CAPITAL LETTER D
    0x0045: 0x24BA,  # LATIN CAPITAL LETTER E -> CIRCLED LATIN CAPITAL LETTER E
    0x0046: 0x24BB,  # LATIN CAPITAL LETTER F -> CIRCLED LATIN CAPITAL LETTER F
    0x0047: 0x24BC,  # LATIN CAPITAL LETTER G -> CIRCLED LATIN CAPITAL LETTER G
    0x0048: 0x24BD,  # LATIN CAPITAL LETTER H -> CIRCLED LATIN CAPITAL LETTER H
    0x0049: 0x24BE,  # LATIN CAPITAL LETTER I -> CIRCLED LATIN CAPITAL LETTER I
    0x004A: 0x24BF,  # LATIN CAPITAL LETTER J -> CIRCLED LATIN CAPITAL LETTER J
    0x004B: 0x24C0,  # LATIN CAPITAL LETTER K -> CIRCLED LATIN CAPITAL LETTER K
    0x004C: 0x24C1,  # LATIN CAPITAL LETTER L -> CIRCLED LATIN CAPITAL LETTER L
    0x004D: 0x24C2,  # LATIN CAPITAL LETTER M -> CIRCLED LATIN CAPITAL LETTER M
    0x004E: 0x24C3,  # LATIN CAPITAL LETTER N -> CIRCLED LATIN CAPITAL LETTER N
    0x004F: 0x24C4,  # LATIN CAPITAL LETTER O -> CIRCLED LATIN CAPITAL LETTER O
    0x0050: 0x24C5,  # LATIN CAPITAL LETTER P -> CIRCLED LATIN CAPITAL LETTER P
    0x0051: 0x24C6,  # LATIN CAPITAL LETTER Q -> CIRCLED LATIN CAPITAL LETTER Q
    0x0052: 0x24C7,  # LATIN CAPITAL LETTER R -> CIRCLED LATIN CAPITAL LETTER R
    0x0053: 0x24C8,  # LATIN CAPITAL LETTER S -> CIRCLED LATIN CAPITAL LETTER S
    0x0054: 0x24C9,  # LATIN CAPITAL LETTER T -> CIRCLED LATIN CAPITAL LETTER T
    0x0055: 0x24CA,  # LATIN CAPITAL LETTER U -> CIRCLED LATIN CAPITAL LETTER U
    0x0056: 0x24CB,  # LATIN CAPITAL LETTER V -> CIRCLED LATIN CAPITAL LETTER V
    0x0057: 0x24CC,  # LATIN CAPITAL LETTER W -> CIRCLED LATIN CAPITAL LETTER W
    0x0058: 0x24CD,  # LATIN CAPITAL LETTER X -> CIRCLED LATIN CAPITAL LETTER X
    0x0059: 0x24CE,  # LATIN CAPITAL LETTER Y -> CIRCLED LATIN CAPITAL LETTER Y
    0x005A: 0x24CF,  # LATIN CAPITAL LETTER Z -> CIRCLED LATIN CAPITAL LETTER Z
    0x0061: 0x24D0,  # LATIN SMALL LETTER A -> CIRCLED LATIN SMALL LETTER A
    0x0062: 0x24D1,  # LATIN SMALL LETTER B -> CIRCLED LATIN SMALL LETTER B
    0x0063: 0x24D2,  # LATIN SMALL LETTER C -> CIRCLED LATIN SMALL LETTER C
    0x0064: 0x24D3,  # LATIN SMALL LETTER D -> CIRCLED LATIN SMALL LETTER D
    0x0065: 0x24D4,  # LATIN SMALL LETTER E -> CIRCLED LATIN SMALL LETTER E
    0x0066: 0x24D5,  # LATIN SMALL LETTER F -> CIRCLED LATIN SMALL LETTER F
    0x0067: 0x24D6,  # LATIN SMALL LETTER G -> CIRCLED LATIN SMALL LETTER G
    0x0068: 0x24D7,  # LATIN SMALL LETTER H -> CIRCLED LATIN SMALL LETTER H
    0x0069: 0x24D8,  # LATIN SMALL LETTER I -> CIRCLED LATIN SMALL LETTER I
    0x006A: 0x24D9,  # LATIN SMALL LETTER J -> CIRCLED LATIN SMALL LETTER J
    0x006B: 0x24DA,  # LATIN SMALL LETTER K -> CIRCLED LATIN SMALL LETTER K
    0x006C: 0x24DB,  # LATIN SMALL LETTER L -> CIRCLED LATIN SMALL LETTER L
    0x006D: 0x24DC,  # LATIN SMALL LETTER M -> CIRCLED LATIN SMALL LETTER M
    0x006E: 0x24DD,  # LATIN SMALL LETTER N -> CIRCLED LATIN SMALL LETTER N
    0x006F: 0x24DE,  # LATIN SMALL LETTER O -> CIRCLED LATIN SMALL LETTER O
    0x0070: 0x24DF,  # LATIN SMALL LETTER P -> CIRCLED LATIN SMALL LETTER P
    0x0071: 0x24E0,  # LATIN SMALL LETTER Q -> CIRCLED LATIN SMALL LETTER Q
    0x0072: 0x24E1,  # LATIN SMALL LETTER R -> CIRCLED LATIN SMALL LETTER R
    0x0073: 0x24E2,  # LATIN SMALL LETTER S -> CIRCLED LATIN SMALL LETTER S
    0x0074: 0x24E3,  # LATIN SMALL LETTER T -> CIRCLED LATIN SMALL LETTER T
    0x0075: 0x24E4,  # LATIN SMALL LETTER U -> CIRCLED LATIN SMALL LETTER U
    0x0076: 0x24E5,  # LATIN SMALL LETTER V -> CIRCLED LATIN SMALL LETTER V
    0x0077: 0x24E6,  # LATIN SMALL LETTER W -> CIRCLED LATIN SMALL LETTER W
    0x0078: 0x24E7,  # LATIN SMALL LETTER X -> CIRCLED LATIN SMALL LETTER X
    0x0079: 0x24E8,  # LATIN SMALL LETTER Y -> CIRCLED LATIN SMALL LETTER Y
    0x007A: 0x24E9,  # LATIN SMALL LETTER Z -> CIRCLED LATIN SMALL LETTER Z
}

_FULLWIDTH_TABLE: dict[int, int] = {
    0x0030: 0xFF10,  # DIGIT ZERO -> FULLWIDTH DIGIT ZERO
    0x0031: 0xFF11,  # DIGIT ONE -> FULLWIDTH DIGIT ONE
    0x0032: 0xFF12,  # DIGIT TWO -> FULLWIDTH DIGIT TWO
    0x0033: 0xFF13,  # DIGIT THREE -> FULLWIDTH DIGIT THREE
    0x0034: 0xFF14,  # DIGIT FOUR -> FULLWIDTH DIGIT FOUR
    0x0035: 0xFF15,  # DIGIT FIVE -> FULLWIDTH DIGIT FIVE
    0x0036: 0xFF16,  # DIGIT SIX -> FULLWIDTH DIGIT SIX
    0x0037: 0xFF17,  # DIGIT SEVEN -> FULLWIDTH DIGIT SEVEN
    0x0038: 0xFF18,  # DIGIT EIGHT -> FULLWIDTH DIGIT EIGHT
    0x0039: 0xFF19,  # DIGIT NINE -> FULLWIDTH DIGIT NINE
    0x0041: 0xFF21,  # LATIN CAPITAL LETTER A -> FULLWIDTH LATIN CAPITAL LETTER A
    0x0042: 0xFF22,  # LATIN CAPITAL LETTER B -> FULLWIDTH LATIN CAPITAL LETTER B
    0x0043: 0xFF23,  # LATIN CAPITAL LETTER C -> FULLWIDTH LATIN CAPITAL LETTER C
    0x0044: 0xFF24,  # LATIN CAPITAL LETTER D -> FULLWIDTH LATIN CAPITAL LETTER D
    0x0045: 0xFF25,  # LATIN CAPITAL LETTER E -> FULLWIDTH LATIN CAPITAL LETTER E
    0x0046: 0xFF26,  # LATIN CAPITAL LETTER F -> FULLWIDTH LATIN CAPITAL LETTER F
    0x0047: 0xFF27,  # LATIN CAPITAL LETTER G -> FULLWIDTH LATIN CAPITAL LETTER G
    0x0048: 0xFF28,  # LATIN CAPITAL LETTER H -> FULLWIDTH LATIN CAPITAL LETTER H
    0x0049: 0xFF29,  # LATIN CAPITAL LETTER I -> FULLWIDTH LATIN CAPITAL LETTER I
    0x004A: 0xFF2A,  # LATIN CAPITAL LETTER J -> FULLWIDTH LATIN CAPITAL LETTER J
    0x004B: 0xFF2B,  # LATIN CAPITAL LETTER K -> FULLWIDTH LATIN CAPITAL LETTER K
    0x004C: 0xFF2C,  # LATIN CAPITAL LETTER L -> FULLWIDTH LATIN CAPITAL LETTER L
    0x004D: 0xFF2D,  # LATIN CAPITAL LETTER M -> FULLWIDTH LATIN CAPITAL LETTER M
    0x004E: 0xFF2E,  # LATIN CAPITAL LETTER N -> FULLWIDTH LATIN CAPITAL LETTER N
    0x004F: 0xFF2F,  # LATIN CAPITAL LETTER O -> FULLWIDTH LATIN CAPITAL LETTER O
    0x0050: 0xFF30,  # LATIN CAPITAL LETTER P -> FULLWIDTH LATIN CAPITAL LETTER P
    0x0051: 0xFF31,  # LATIN CAPITAL LETTER Q -> FULLWIDTH LATIN CAPITAL LETTER Q
    0x0052: 0xFF32,  # LATIN CAPITAL LETTER R -> FULLWIDTH LATIN CAPITAL LETTER R
    0x0053: 0xFF33,  # LATIN CAPITAL LETTER S -> FULLWIDTH LATIN CAPITAL LETTER S
    0x0054: 0xFF34,  # LATIN CAPITAL LETTER T -> FULLWIDTH LATIN CAPITAL LETTER T
    0x0055: 0xFF35,  # LATIN CAPITAL LETTER U -> FULLWIDTH LATIN CAPITAL LETTER U
    0x0056: 0xFF36,  # LATIN CAPITAL LETTER V -> FULLWIDTH LATIN CAPITAL LETTER V
    0x0057: 0xFF37,  # LATIN CAPITAL LETTER W -> FULLWIDTH LATIN CAPITAL LETTER W
    0x0058: 0xFF38,  # LATIN CAPITAL LETTER X -> FULLWIDTH LATIN CAPITAL LETTER X
    0x0059: 0xFF39,  # LATIN CAPITAL LETTER Y -> FULLWIDTH LATIN CAPITAL LETTER Y
    0x005A: 0xFF3A,  # LATIN CAPITAL LETTER Z -> FULLWIDTH LATIN CAPITAL LETTER Z
    0x0061: 0xFF41,  # LATIN SMALL LETTER A -> FULLWIDTH LATIN SMALL LETTER A
    0x0062: 0xFF42,  # LATIN SMALL LETTER B -> FULLWIDTH LATIN SMALL LETTER B
    0x0063: 0xFF43,  # LATIN SMALL LETTER C -> FULLWIDTH LATIN SMALL LETTER C
    0x0064: 0xFF44,  # LATIN SMALL LETTER D -> FULLWIDTH LATIN SMALL LETTER D
    0x0065: 0xFF45,  # LATIN SMALL LETTER E -> FULLWIDTH LATIN SMALL LETTER E
    0x0066: 0xFF46,  # LATIN SMALL LETTER F -> FULLWIDTH LATIN SMALL LETTER F
    0x0067: 0xFF47,  # LATIN SMALL LETTER G -> FULLWIDTH LATIN SMALL LETTER G
    0x0068: 0xFF48,  # LATIN SMALL LETTER H -> FULLWIDTH LATIN SMALL LETTER H
    0x0069: 0xFF49,  # LATIN SMALL LETTER I -> FULLWIDTH LATIN SMALL LETTER I
    0x006A: 0xFF4A,  # LATIN SMALL LETTER J -> FULLWIDTH LATIN SMALL LETTER J
    0x006B: 0xFF4B,  # LATIN SMALL LETTER K -> FULLWIDTH LATIN SMALL LETTER K
    0x006C: 0xFF4C,  # LATIN SMALL LETTER L -> FULLWIDTH LATIN SMALL LETTER L
    0x006D: 0xFF4D,  # LATIN SMALL LETTER M -> FULLWIDTH LATIN SMALL LETTER M
    0x006E: 0xFF4E,  # LATIN SMALL LETTER N -> FULLWIDTH LATIN SMALL LETTER N
    0x006F: 0xFF4F,  # LATIN SMALL LETTER O -> FULLWIDTH LATIN SMALL LETTER O
    0x0070: 0xFF50,  # LATIN SMALL LETTER P -> FULLWIDTH LATIN SMALL LETTER P
    0x0071: 0xFF51,  # LATIN SMALL LETTER Q -> FULLWIDTH LATIN SMALL LETTER Q
    0x0072: 0xFF52,  # LATIN SMALL LETTER R -> FULLWIDTH LATIN SMALL LETTER R
    0x0073: 0xFF53,  # LATIN SMALL LETTER S -> FULLWIDTH LATIN SMALL LETTER S
    0x0074: 0xFF54,  # LATIN SMALL LETTER T -> FULLWIDTH LATIN SMALL LETTER T
    0x0075: 0xFF55,  # LATIN SMALL LETTER U -> FULLWIDTH LATIN SMALL LETTER U
    0x0076: 0xFF56,  # LATIN SMALL LETTER V -> FULLWIDTH LATIN SMALL LETTER V
    0x0077: 0xFF57,  # LATIN SMALL LETTER W -> FULLWIDTH LATIN SMALL LETTER W
    0x0078: 0xFF58,  # LATIN SMALL LETTER X -> FULLWIDTH LATIN SMALL LETTER X
    0x0079: 0xFF59,  # LATIN SMALL LETTER Y -> FULLWIDTH LATIN SMALL LETTER Y
    0x007A: 0xFF5A,  # LATIN SMALL LETTER Z -> FULLWIDTH LATIN SMALL LETTER Z
}

_PADDING_CHARS: tuple[str, ...] = (
    "\ufe4e",  # ﹎: CENTRELINE LOW LINE
    "\u040d",  # Ѝ: CYRILLIC CAPITAL LETTER I WITH GRAVE
    "\u05d0",  # א: HEBREW LETTER ALEF
    "\u01c6",  # ǆ: LATIN SMALL LETTER DZ WITH CARON
    "\u1f8f",  # ᾏ: GREEK CAPITAL LETTER ALPHA WITH DASIA AND PERISPOMENI AND PROSGEGRAMMENI
    "\u2167",  # Ⅷ: ROMAN NUMERAL EIGHT
    "\u3234",  # ㈴: PARENTHESIZED IDEOGRAPH NAME
    "\u32f9",  # ㋹: CIRCLED KATAKANA RE
    "\ud4db",  # 퓛: HANGUL SYLLABLE PWILH
    "\ufe8f",  # ﺏ: ARABIC LETTER BEH ISOLATED FORM
    "\U0001d7d8",  # 𝟘: MATHEMATICAL DOUBLE-STRUCK DIGIT ZERO
    "\U0001f6a6",  # 🚦: VERTICAL TRAFFIC LIGHT
)


def _get_target_length(size: int) -> int:
    """
    Figures out the increased size of the string per
    IBM Globalization Design Guideline A3: UI Expansion.

    https://www-01.ibm.com/software/globalization/guidelines/a3.html

    :param size: Current size of the string.
    :returns: The desired increased size.
    """
    target_lengths: dict[range, float] = {
        range(1, 11): 3,
        range(11, 21): 2,
        range(21, 31): 1.8,
        range(31, 51): 1.6,
        range(51, 71): 1.4,
    }
    if size > 70:
        return math.ceil(size * 1.3)
    for r, factor in target_lengths.items():
        if size in r:
            return math.ceil(size * factor)
    return 0


def transliterate_diacritic(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Transliterates an input string by replacing each latin letter with the same
    letter with a diacritic added e.g. "Hello" -> "Ȟêĺĺø"

    :param s: String to perform transliteration upon.
    :param fmt_spec: Regex for placeholders (unused).
    :returns: Transliterated string.
    """
    return s.translate(_DIACRITIC_TABLE)


def transliterate_circled(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Transliterates an input string by replacing each latin letter or digit with
    the circled version of the same letter or digit e.g. "Hello" -> "🅗ⓔⓛⓛⓞ"

    :param s: String to perform transliteration upon.
    :param fmt_spec: Regex for placeholders (unused).
    :returns: Transliterated string.
    """
    return s.translate(_CIRCLED_TABLE)


def transliterate_fullwidth(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Transliterates an input string by replacing each latin letter or digit with
    the full width of the same letter or digit e.g. "Hello" -> "Ｈｅｌｌｏ"

    :param s: String to perform transliteration upon.
    :param fmt_spec: Regex for placeholders (unused).
    :returns: Transliterated string.
    """
    return s.translate(_FULLWIDTH_TABLE)


# Need to keep track of which of the transforms perform transliteration so that when we do format-string handling,
# we can do munging on the substrings that are not format-strings before we do any other munging.
transliterations: list[Transform] = [
    transliterate_diacritic,
    transliterate_circled,
    transliterate_fullwidth,
]


def angle_brackets(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Surrounds the string with 《 》 characters.  Useful when verifying string
    truncation i.e. when checking the UI these characters should be visible.

    :param s: String to surround
    :param fmt_spec: Regex for placeholders (unused).
    :returns: String surrounded with 《 》
    """
    return f"《{s}》"


def curly_brackets(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Surrounds the string with ❴ ❵ characters.  Useful when verifying string
    truncation i.e. when checking the UI these characters should be visible.

    :param s: String to surround
    :param fmt_spec: Regex for placeholders (unused).
    :returns: String surrounded with ❴ ❵
    """
    return f"❴{s}❵"


def square_brackets(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Surrounds the string with ⟦ ⟧ characters.  Useful when verifying string
    truncation i.e. when checking the UI these characters should be visible.

    :param s: String to surround
    :param fmt_spec: Regex for placeholders (unused).
    :returns: String surrounded with ⟦ ⟧
    """
    return f"⟦{s}⟧"


def simple_square_brackets(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Surrounds the string with [ ] characters.  Useful when verifying string
    truncation i.e. when checking the UI these characters should be visible.

    :param s: String to surround
    :param fmt_spec: Regex for placeholders (unused).
    :returns: String surrounded with [ ]
    """
    return f"[{s}]"


def pad_length(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Appends characters to the end of the string to increase the string length per
    IBM Globalization Design Guideline A3: UI Expansion.

    https://www-01.ibm.com/software/globalization/guidelines/a3.html

    :param s: String to pad.
    :param fmt_spec: Regex for placeholders (unused).
    :returns: Padded string.
    """
    diff = _get_target_length(len(s)) - len(s)
    pad = "".join(itertools.islice(itertools.cycle(_PADDING_CHARS), max(diff, 0)))
    return s + pad


def expand_vowels(s: str, fmt_spec: re.Pattern[str]) -> str:
    """
    Duplicates vowels in the string to increase the string length per
    IBM Globalization Design Guideline A3: UI Expansion.

    Note that it subtracts the length of the placeholders.
    If no vowels are present the last character will be repeated instead.

    https://www-01.ibm.com/software/globalization/guidelines/a3.html

    :param s: String to pad.
    :param fmt_spec: Regex for placeholders.
    :returns: Padded string.
    """
    if not s:
        return s

    base_vowels = "aeiouAEIOU"
    vowels: set[str] = set(base_vowels)
    for munge in transliterations:
        vowels.update(munge(base_vowels, fmt_spec))

    substrings = fmt_spec.split(s)
    length_without_placeholders = 0
    total_vowels = 0
    for substring in substrings:
        if not fmt_spec.match(substring):
            length_without_placeholders += len(substring)
            total_vowels += sum(1 for c in substring if c in vowels)

    target_length = _get_target_length(length_without_placeholders)
    diff = target_length - length_without_placeholders

    if total_vowels == 0:
        return s + s[-1] * diff

    for idx, substring in enumerate(substrings):
        if fmt_spec.match(substring):
            continue
        expanded: list[str] = []
        for c in substring:
            if c in vowels and total_vowels > 0:
                next_vowel_addition = diff // total_vowels
                expanded.append(c * (next_vowel_addition + 1))
                total_vowels -= 1
                diff -= next_vowel_addition
            else:
                expanded.append(c)
        substrings[idx] = "".join(expanded)
    return "".join(substrings)
