`emendator` is a commend line tool based on the [google-diff-match-patch][dmp] library.

[dmp]: https://code.google.com/p/google-diff-match-patch/

It ignores punctuation marks in English and Chinese.

Usage:

    emendator.py file1 file2

`ememdator` is compatible with `colordiff`:

    emendator.py file1 file2 | colordiff

It depends on [this const.py module][const], because python does not support constant variables or symbols.
(But I want to use them.)

[const]: https://gitcafe.com/weakish/whci/blob/master/const.py

Bugs

Diff on certain text will fail.
However, if we divide that text into two parts, then diff on each part separately, diff succeeds.


