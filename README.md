`emendator` is a commend line tool based on the [google-diff-match-patch][dmp] library.

[dmp]: https://code.google.com/p/google-diff-match-patch/

It also offers some additional functions, like ignore certain characters (punctuation marks, etc).

It depends on [this const.py module][const], because python does not support constant variables or symbols.
(But I want to use them.)
Old version `3d939afe` does not use `const.py`, and may have better performance (since I wrote it in a different style), so you may prefer this version.

[const]: https://gitcafe.com/weakish/whci/blob/master/const.py
