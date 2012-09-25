#!/usr/bin/env python3.2
# by Jakukyo Friel <weakish@gmail.com> under GPL-2

from diff_match_patch import diff_match_patch


dmp = diff_match_patch()

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


if __name__ == '__main__':
  import sys
  print(dmpdiff(open(sys.argv[2]).read(), open(sys.argv[2]).read()))
