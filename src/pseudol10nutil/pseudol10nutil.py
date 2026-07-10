"""Core classes for performing pseudo-localization on strings and PO files."""

import os
import re
from pathlib import Path

import polib

from . import transforms
from .transforms import Transform

type StrPath = str | os.PathLike[str]

#: Default regex used to detect placeholders that should not be transliterated.
DEFAULT_PLACEHOLDER_REGEX = re.compile(
    r"""(
    \\n$
    |
    <[^>]*>
    |
    {.*?}  # https://docs.python.org/3/library/string.html#formatstrings
    |
    %(?:\(\w+?\))?.*?[acdeEfFgGiorsuxX%]  # https://docs.python.org/3/library/stdtypes.html#printf-style-string-formatting
    )""",
    re.VERBOSE,
)


class PseudoL10nUtil:
    """
    Class for performing pseudo-localization on strings.
    """

    def __init__(
        self,
        init_transforms: list[Transform] | None = None,
        placeholder_regex: re.Pattern[str] | None = None,
    ) -> None:
        """
        Initializer for class.

        :param init_transforms: Optional list of initial transforms.  If not
                                specified, the default list of transforms is
                                transliterate_diacritic, pad_length and
                                square_brackets.
        :param placeholder_regex: Overwrite what PseudoL10nUtil considers a
                                  placeholder and skips transliteration.
                                  Has to be a single group!
        """
        if init_transforms is not None:
            self.transforms = init_transforms
        else:
            self.transforms = [
                transforms.transliterate_diacritic,
                transforms.pad_length,
                transforms.square_brackets,
            ]
        self.placeholder_regex = placeholder_regex

    def pseudolocalize(self, s: str | None) -> str:
        """
        Performs pseudo-localization on a string.  The specific transforms to be
        applied to the string is defined in the transforms field of the object.

        :param s: String to pseudo-localize.
        :returns: Copy of the string s with the transforms applied.  If the input
                  string is an empty string or None, an empty string is returned.
        """
        if not s:  # If the string is empty or None
            return ""
        if not isinstance(s, str):
            raise TypeError(
                f"String to pseudo-localize must be of type '{str.__name__}'."
            )
        # If no transforms are defined, return the string as-is.
        if not self.transforms:
            return s
        fmt_spec = self.placeholder_regex or DEFAULT_PLACEHOLDER_REGEX
        # If we don't find any format specifiers in the input string, just munge the entire string at once.
        if not fmt_spec.search(s):
            result = s
            for munge in self.transforms:
                result = munge(result, fmt_spec)
            return result
        # If there are format specifiers, we do transliterations on the sections of the string that are not format
        # specifiers, then do any other munging (padding the length, adding brackets) on the entire string.
        substrings = fmt_spec.split(s)
        for munge in self.transforms:
            if munge in transforms.transliterations:
                substrings = [
                    substring
                    if fmt_spec.match(substring)
                    else munge(substring, fmt_spec)
                    for substring in substrings
                ]
        result = "".join(substrings)
        for munge in self.transforms:
            if munge not in transforms.transliterations:
                result = munge(result, fmt_spec)
        return result


class POFileUtil:
    """
    Class for performing pseudo-localization on gettext PO (Portable Object) message catalogs.
    """

    def __init__(self, l10nutil: PseudoL10nUtil | None = None) -> None:
        """
        Initializer for class.

        :param l10nutil: Optional instance of PseudoL10nUtil object.  This can be used to pass in an instance of the
                         PseudoL10nUtil class with the transforms already configured.  Otherwise, an instance of the
                         PseudoL10nUtil class will be created with the default transforms.
        """
        self.l10nutil = l10nutil if l10nutil is not None else PseudoL10nUtil()

    def pseudolocalizefile(
        self,
        input_filename: StrPath,
        output_filename: StrPath,
        overwrite_existing: bool = True,
    ) -> None:
        """
        Method for pseudo-localizing the message catalog file.  In addition to
        the PO file, the compiled MO file is written next to it.

        :param input_filename: Filename of the source (input) message catalog file.
        :param output_filename: Filename of the target (output) message catalog file.
        :param overwrite_existing: Boolean indicating if an existing output message catalog file should be overwritten.
                                   True by default. If False, a FileExistsError will be raised.
        """
        input_path = Path(input_filename)
        output_path = Path(output_filename)
        if not input_path.is_file():
            raise FileNotFoundError(
                f"Input message catalog not found: {input_path.resolve()}"
            )
        if output_path.is_file() and not overwrite_existing:
            raise FileExistsError(
                f"Error, output message catalog already exists: {output_path.resolve()}"
            )

        po_file = polib.pofile(str(input_path))
        for entry in po_file:
            if entry.msgid_plural:
                entry.msgstr_plural[0] = self.l10nutil.pseudolocalize(entry.msgid)
                entry.msgstr_plural[1] = self.l10nutil.pseudolocalize(
                    entry.msgid_plural
                )
            else:
                entry.msgstr = self.l10nutil.pseudolocalize(entry.msgid)
        po_file.save(str(output_path))
        po_file.save_as_mofile(str(output_path.with_suffix(".mo")))
