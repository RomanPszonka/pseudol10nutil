import os.path
import re

import polib
import six

from . import transforms


class PseudoL10nUtil:
    """
    Class for performing pseudo-localization on strings.
    """

    def __init__(self, init_transforms=None, placeholder_regex=None):
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

    def pseudolocalize(self, s):
        """
        Performs pseudo-localization on a string.  The specific transforms to be
        applied to the string is defined in the transforms field of the object.

        :param s: String to pseudo-localize.
        :returns: Copy of the string s with the transforms applied.  If the input
                  string is an empty string or None, an empty string is returned.
        """
        if not s:  # If the string is empty or None
            return u""
        if not isinstance(s, six.text_type):
            raise TypeError(
                "String to pseudo-localize must be of type '{0}'.".format(
                    six.text_type.__name__
                )
            )
        # If no transforms are defined, return the string as-is.
        if not self.transforms:
            return s
        fmt_spec = self.placeholder_regex or re.compile(
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
        # If we don't find any format specifiers in the input string, just munge the entire string at once.
        if not fmt_spec.search(s):
            result = s
            for munge in self.transforms:
                result = munge(result, fmt_spec)
        # If there are format specifiers, we do transliterations on the sections of the string that are not format
        # specifiers, then do any other munging (padding the length, adding brackets) on the entire string.
        else:
            substrings = fmt_spec.split(s)
            for munge in self.transforms:
                if munge in transforms.transliterations:
                    for idx in range(len(substrings)):
                        if not fmt_spec.match(substrings[idx]):
                            substrings[idx] = munge(substrings[idx], fmt_spec)
                    else:
                        continue
                else:
                    continue
            result = u"".join(substrings)
            for munge in self.transforms:
                if munge not in transforms.transliterations:
                    result = munge(result, fmt_spec)
        return result


class POFileUtil:
    """
    Class for performing pseudo-localization on gettext PO (Portable Object) message catalogs.
    """

    def __init__(self, l10nutil=None):
        """
        Initializer for class.

        :param l10nutil: Optional instance of PseudoL10nUtil object.  This can be used to pass in an instance of the
                         PseudoL10nUtil class with the transforms already configured.  Otherwise, an instance of the
                         PseudoL10nUtil class will be created with the default transforms.
        """
        if not l10nutil:
            self.l10nutil = PseudoL10nUtil()
        else:
            self.l10nutil = l10nutil

    def pseudolocalizefile(
        self,
        input_filename,
        output_filename,
        overwrite_existing=True,
    ):
        """
        Method for pseudo-localizing the message catalog file.

        :param input_filename: Filename of the source (input) message catalog file.
        :param output_filename: Filename of the target (output) message catalog file.
        :param overwrite_existing: Boolean indicating if an existing output message catalog file should be overwritten.
                                   True by default. If False, an IOError will be raised.
        """

        if not os.path.isfile(input_filename):
            raise IOError(
                "Input message catalog not found: {0}".format(
                    os.path.abspath(input_filename)
                )
            )
        if os.path.isfile(output_filename) and not overwrite_existing:
            raise IOError(
                "Error, output message catalog already exists: {0}".format(
                    os.path.abspath(output_filename)
                )
            )

        po_file = polib.pofile(input_filename)
        for entry in po_file:
            if entry.msgid_plural:
                entry.msgstr_plural[0] = self.l10nutil.pseudolocalize(entry.msgid)
                entry.msgstr_plural[1] = self.l10nutil.pseudolocalize(
                    entry.msgid_plural
                )
            else:
                entry.msgstr = self.l10nutil.pseudolocalize(entry.msgid)
        po_file.save(output_filename)
        po_file.save_as_mofile(output_filename[:-2] + "mo")
