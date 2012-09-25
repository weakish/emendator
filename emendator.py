#!/usr/bin/env python3.1
# by Jakukyo Friel <weakish@gmail.com> under GPL-2

'''compare two files, ignore unimportant characters.

'''

import re
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()

Ignored_marks = '''[,.;:!'"?-]'''
Del_begin = '[-'
Del_end = '-]'
Ins_begin = '{+'
Ins_end = '+}'


def dmpdiff(from_text, to_text):
  '''return diff in a list of tuples

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk! Thank you.'
  >>> dmpdiff(text1, text2)
  [(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (-1, '-'), (1, ' '), (0, 'milk'), (-1, '.'), (1, '!'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')]
  '''
  text_diffs = dmp.diff_main(from_text, to_text)
  dmp.diff_cleanupSemantic(text_diffs)
  return text_diffs

def dmpdiff_text(diffs): 
  '''return diff in plain text.

  Use marks similar to wdiff.

  >>> diffs = [(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (-1, '-'), (1, ' '), (0, 'milk'), (-1, '.'), (1, '!'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')]
  >>> dmpdiff_text(diffs)
  '{+please +}give m[-e-]{+om+} a cup of bean[---]{+ +}milk[-.-]{+!+} Thank[-s-]{+ you+}.'
  '''
  text = []
  for (op, data) in diffs:
    if op == 1: # insert
      text.append(Ins_begin + data + Ins_end)
    elif op == -1: # delete
      text.append(Del_begin + data + Del_end)
    elif op == 0: # equal
      text.append(data)
  return ''.join(text)



def main():
  ''' main function

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk! Thank you.'
  >>> dmpdiff_text(dmpdiff(text1, text2))
  '{+please +}give m[-e-]{+om+} a cup of bean[---]{+ +}milk[-.-]{+!+} Thank[-s-]{+ you+}.'
  '''
  import sys
  from_text = open(sys.argv[1]).read()
  to_text = open(sys.argv[2]).read()
  print(dmpdiff_text(dmpdiff(from_text, to_text)))

if __name__ == '__main__':
  main()
