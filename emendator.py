#!/usr/bin/env python3.2
# by Jakukyo Friel <weakish@gmail.com> under GPL-2

import re
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()

Ignored_marks = r'''[][`~!@#(){}/?+\|'",.;:-]''' 
Del_begin = '<del style="background:#ffe6e6;">'
Del_end = '</del>'
Ins_begin = '<ins style="background:#e6ffe6;">'
Ins_end = '</ins>'


def dmpdiff(from_text, to_text): 
  '''return pretty html of diff.

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk!  Thank you.'
  >>> dmpdiff(text1, text2)
  '<ins style="background:#e6ffe6;">please </ins><span>give m</span><del style="background:#ffe6e6;">e</del><ins style="background:#e6ffe6;">om</ins><span> a cup of bean</span><del style="background:#ffe6e6;">-</del><ins style="background:#e6ffe6;"> </ins><span>milk</span><del style="background:#ffe6e6;">.</del><ins style="background:#e6ffe6;">! </ins><span> Thank</span><del style="background:#ffe6e6;">s</del><ins style="background:#e6ffe6;"> you</ins><span>.</span>'
  
  '''
  text_diffs = dmp.diff_main(from_text, to_text)
  dmp.diff_cleanupSemantic(text_diffs)
  diff_html = dmp.diff_prettyHtml(text_diffs)
  return diff_html

def split_text(text, ignored_marks):
  '''split text, put ignored_marks on separated lines
  
  >>> text = 'give me a cup of bean-milk. Thanks.'

  >>> split_text(text, Ignored_marks)
  'give me a cup of bean\n-\nmilk\n.\n Thanks\n.\n'
  '''.replace('+IGNORE_RESULT', '+ELLIPSIS\n<...>')
  # A pitfall of doctest. See http://bugs.python.org/issue7381
  # and http://stackoverflow.com/questions/3862274/doctests-how-to-suppress-ignore-output
  cooked_text = re.sub(ignored_marks, '\n\g<0>\n', text)
  return cooked_text

def ediff(from_text, to_text, ignored_marks):
  '''return pretty html of diff, ignore unimportant characters

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk!  Thank you.'
  >>> ediff(text1, text2, Ignored_marks)
  '<ins style="background:#e6ffe6;">please </ins><span>give m</span><del style="background:#ffe6e6;">e</del><ins style="background:#e6ffe6;">om</ins><span> a cup of bean</span><del style="background:#ffe6e6;">&para;<br>-&para;<br></del><ins style="background:#e6ffe6;"> </ins><span>milk&para;<br></span><del style="background:#ffe6e6;">.&para;<br></del><ins style="background:#e6ffe6;">!&para;<br> </ins><span> Thank</span><del style="background:#ffe6e6;">s</del><ins style="background:#e6ffe6;"> you</ins><span>&para;<br>.&para;<br></span>'
  '''
  cooked_from_text = split_text(from_text, ignored_marks)
  cooked_to_text = split_text(to_text, ignored_marks)
  diff_html = dmpdiff(cooked_from_text, cooked_to_text)
  diff_html = unmark_unimportant(diff_html, ignored_marks)
  return diff_html

def unmark_unimportant(diff_html, ignored_marks):
  '''remove unimportant marks
  
  >>> to_unmark_text = '<ins style="background:#e6ffe6;">please </ins><span>give m</span><del style="background:#ffe6e6;">e</del><ins style="background:#e6ffe6;">om</ins><span> a cup of bean</span><del style="background:#ffe6e6;">?<br>-?<br></del><ins style="background:#e6ffe6;"> </ins><span>milk?<br></span><del style="background:#ffe6e6;">. </del><ins style="background:#e6ffe6;">!</ins><span>?<br>Thank</span><del style="background:#ffe6e6;">s</del><ins style="background:#e6ffe6;"> you</ins><span>?<br>.</span>'
  >>> unmark_unimportant(to_unmark_text, Ignored_marks)
  '<ins style="background:#e6ffe6;">please </ins><span>give m</span><del style="background:#ffe6e6;">e</del><ins style="background:#e6ffe6;">om</ins><span> a cup of bean</span><del style="background:#ffe6e6;">?<br>-?<br></del><ins style="background:#e6ffe6;"> </ins><span>milk?<br></span><del style="background:#ffe6e6;">. </del><ins style="background:#e6ffe6;">!</ins><span>?<br>Thank</span><del style="background:#ffe6e6;">s</del><ins style="background:#e6ffe6;"> you</ins><span>?<br>.</span>'
  '''
  minor_insert = Ins_begin + Ignored_marks + Ins_end + '$'
  minor_delete = '^' + Del_begin + '(' + Ignored_marks + ')' + Del_end 
  diff_html = re.sub(minor_insert, '', diff_html)
  diff_html = re.sub(minor_delete, '\g<1>', diff_html)
  return diff_html

if __name__ == '__main__':
  import sys
  print(ediff(open(sys.argv[2]).read(), open(sys.argv[2]).read()))
