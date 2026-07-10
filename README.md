# `pseudol10nutil`

[![CI](https://github.com/RomanPszonka/pseudol10nutil/actions/workflows/python-tests.yml/badge.svg)](https://github.com/RomanPszonka/pseudol10nutil/actions/workflows/python-tests.yml)

Python module for performing pseudo-localization on strings and gettext
PO files. Requires Python 3.12 or later.

## Installation

The module is available on
[PyPI](https://pypi.org/project/pseudol10nutil/) and is installable via
`pip`:

`pip install pseudol10nutil`

or via [uv](https://docs.astral.sh/uv/):

`uv add pseudol10nutil`

## Dependencies

This package has the following external dependencies:

- [polib](https://polib.readthedocs.io/) - for manipulating gettext PO
  and MO message catalogs

## `PseudoL10nUtil` class

Class for pseudo-localizing strings. The class currently has the
following members:

- `transforms` - field that contains the list of transforms to apply to
  the string. The transforms will be applied in order. Default is
  `[transliterate_diacritic, pad_length, square_brackets]`
- `pseudolocalize(s)` - method that returns a new string where the
  transforms to the input string `s` have been applied.

## `pseudol10nutil.transforms` module

The following transforms are currently available:

- `transliterate_diacritic` - Takes the input string and returns a copy
  with diacritics added e.g. `Hello` -\> `Ȟêĺĺø`.
- `transliterate_circled` - Takes the input string and returns a copy
  with circled versions of the letters e.g. `Hello` -\> `Ⓗⓔⓛⓛⓞ`
- `transliterate_fullwidth` - Takes the input string and returns a copy
  with the letters converted to their fullwidth counterparts e.g.
  `Hello` -\> `Ｈｅｌｌｏ`
- `pad_length` - Appends a series of characters to the end of the input
  string to increase the string length per [IBM Globalization Design
  Guideline A3: UI
  Expansion](https://www-01.ibm.com/software/globalization/guidelines/a3.html).
- `expand_vowels` - Replicates the vowels of the input string to
  increase the string length per [IBM Globalization Design Guideline A3:
  UI
  Expansion](https://www-01.ibm.com/software/globalization/guidelines/a3.html).
- `angle_brackets` - Surrounds the input string with \'《\' and \'》\'
  characters.
- `curly_brackets` - Surrounds the input string with \'❴\' and \'❵\'
  characters.
- `square_brackets` - Surrounds the input string with \'⟦\' and \'⟧\'
  characters.
- `simple_square_brackets` - Surrounds the input string with \'\[\' and
  \'\]\' characters.

## Format string support

When performing pseudo-localization on a string, the process will skip
performing pseudo-localization on format strings. Python style format
strings (e.g. `{foo}`) and printf style format strings (e.g. `%s`) are
supported. For example:

    Input [1]: Source {source1} returned 0 rows.
    Output [1]: '⟦Șøüȓċê {source1} ȓêťüȓñêđ 0 ȓøẁš.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹⟧

    Input [2]: Source %(source2)s returned 1 row.
    Output [2]: ⟦Șøüȓċê %(source2)s ȓêťüȓñêđ 1 ȓøẁ.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛⟧

    Input [3]: Source %s returned %d rows.
    Output [3]: ⟦Șøüȓċê %s ȓêťüȓñêđ %d ȓøẁš.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ⟧

The regex used to detect placeholders can be overridden by passing a
compiled regex (with a single capture group) as the `placeholder_regex`
parameter of `PseudoL10nUtil`.

### Example usage

    >>> from pseudol10nutil import PseudoL10nUtil
    >>> import pseudol10nutil.transforms
    >>> util = PseudoL10nUtil()
    >>> s = "The quick brown fox jumps over the lazy dog."
    >>> util.pseudolocalize(s)
    '⟦Ťȟê ʠüıċǩ ƀȓøẁñ ƒøẋ ǰüɱƥš øṽêȓ ťȟê ĺàźÿ đøğ.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝא⟧'
    >>> util.transforms = [pseudol10nutil.transforms.transliterate_fullwidth, pseudol10nutil.transforms.curly_brackets]
    >>> util.pseudolocalize(s)
    '❴Ｔｈｅ ｑｕｉｃｋ ｂｒｏｗｎ ｆｏｘ ｊｕｍｐｓ ｏｖｅｒ ｔｈｅ ｌａｚｙ ｄｏｇ.❵'
    >>> util.transforms = [pseudol10nutil.transforms.transliterate_circled, pseudol10nutil.transforms.pad_length, pseudol10nutil.transforms.angle_brackets]
    >>> util.pseudolocalize(s)
    '《Ⓣⓗⓔ ⓠⓤⓘⓒⓚ ⓑⓡⓞⓦⓝ ⓕⓞⓧ ⓙⓤⓜⓟⓢ ⓞⓥⓔⓡ ⓣⓗⓔ ⓛⓐⓩⓨ ⓓⓞⓖ.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝא》'

## Example web app

There is an example web app in the `examples/webapp/` directory that
provides a web UI and a REST endpoint for pseudo-localizing strings.
This example is also available on [Docker
hub](https://hub.docker.com/r/leonidessaguisagjr/pseudol10nutil/).

Once the docker container is running, the web UI could be accessed via
the following URL:

<http://localhost:8080/pseudol10nutil/>

The REST endpoint could be accessed as follows:

    >>> import pprint
    >>> import requests
    >>> strings = { "s1": "The quick brown {0} jumps over the lazy {1}.", }
    >>> data = { "strings": strings }
    >>> headers = { "Accept": "application/json", "Content-Type": "application/json" }
    >>> api_url = "http://localhost:8080/pseudol10nutil/api/v1.0/pseudo"
    >>> resp = requests.post(api_url, headers=headers, json=data)
    >>> resp.status_code
    200
    >>> pprint.pprint(resp.json())
    {'strings': {'s1': '⟦Ťȟê ʠüıċǩ ƀȓøẁñ {0} ǰüɱƥš øṽêȓ ťȟê ĺàźÿ '
                       '{1}.﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎Ѝא⟧'}}

## `POFileUtil` class

Class for performing pseudo-localization on .po (Portable Object)
message catalogs. Currently the class has a single method,
`pseudolocalizefile(input_filename, output_filename, overwrite_existing=True)`.
In addition to the output PO file, the compiled MO file is written next
to it.

The default transforms will be applied to the strings in the input file.
To override this behavior, create an instance of the `PseudoL10nUtil`
class with the desired behavior and assign it to the `l10nutil` field
prior to calling the `pseudolocalizefile()` method.

### Example usage

    >>> from pseudol10nutil import POFileUtil
    >>> pofileutil = POFileUtil()
    >>> input_file = "./testdata/locales/helloworld.pot"
    >>> output_file = "./testdata/locales/eo/LC_MESSAGES/helloworld_pseudo.po"
    >>> pofileutil.pseudolocalizefile(input_file, output_file)
    >>> with open(input_file, mode="r") as fileobj:
    ...     for line in fileobj:
    ...         if line.startswith("msgstr"):
    ...             print(line)
    ...
    msgstr ""

    msgstr ""

    msgstr ""

    >>> with open(output_file, mode="r") as fileobj:
    ...     for line in fileobj:
    ...         if line.startswith("msgstr"):
    ...             print(line)
    ...
    msgstr ""

    msgstr "⟦Ẃȟàť ıš ÿøüȓ ñàɱê?: ﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹⟧"

    msgstr "⟦Ȟêĺĺø {0}!﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹⟧"

    >>> from pseudol10nutil import PseudoL10nUtil
    >>> import pseudol10nutil.transforms
    >>> util = PseudoL10nUtil()
    >>> util.transforms = [pseudol10nutil.transforms.transliterate_circled, pseudol10nutil.transforms.pad_length]
    >>> pofileutil.l10nutil = util
    >>> pofileutil.pseudolocalizefile(input_file, output_file)
    >>> with open(output_file, mode="r") as fileobj:
    ...     for line in fileobj:
    ...         if line.startswith("msgstr"):
    ...             print(line)
    ...
    msgstr ""

    msgstr "Ⓦⓗⓐⓣ ⓘⓢ ⓨⓞⓤⓡ ⓝⓐⓜⓔ?: ﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹"

    msgstr "Ⓗⓔⓛⓛⓞ {0}!﹎ЍאǆᾏⅧ㈴㋹퓛ﺏ𝟘🚦﹎ЍאǆᾏⅧ㈴㋹"

## Development

This project uses [uv](https://docs.astral.sh/uv/) for dependency
management and [hatchling](https://hatch.pypa.io/) as the build backend.

    # create a virtualenv and install the package plus dev dependencies
    uv sync

    # run the test suite
    uv run pytest

    # run the linter, formatter and type checker
    uv run ruff check .
    uv run ruff format --check .
    uv run mypy

    # run the full matrix (tests on all supported interpreters, lint, type)
    uvx tox

## License

This is released under an MIT license. See the `LICENSE` file in this
repository for more information.
