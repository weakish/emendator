#!/usr/bin/env python3.1
# by Jakukyo Friel <weakish@gmail.com> under GPL-2

'''compare two files, ignore unimportant characters.

Usage:

    emendator.py file1 file2

'''

import re
from diff_match_patch import diff_match_patch
import const

# Do not timeout. Let diff run until completion.
diff_match_patch.Diff_Timeout = 0

dmp = diff_match_patch()


const.ignored_regex = re.compile('[ ,\.;:!\'"?-]+$')
const.del_begin = '[-'
const.del_end = '-]'
const.ins_begin = '{+'
const.ins_end = '+}'


def dmpdiff(from_text, to_text):
  '''return diff in a list of tuples

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk! Thank you.'
  >>> list(dmpdiff(text1, text2))
  [(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (-1, '-'), (1, ' '), (0, 'milk'), (-1, '.'), (1, '!'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')]
  '''
  text_diffs = dmp.diff_main(from_text, to_text)
  dmp.diff_cleanupSemanticLossless(text_diffs)
  return iter(text_diffs)

def unmark_minor_diffs(diffs):
  '''unmark minor diffs

  >>> diffs = [(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (-1, '-'), (1, ' '), (0, 'milk'), (-1, '.'), (1, '!'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')]
  >>> list(unmark_minor_diffs(diffs))
  [(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (0, '-'), (0, 'milk'), (0, '.'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')]
  '''

  diffs_without_minor_inserts = filter(is_not_minor_insert, diffs)
  diffs_we_care = map(unmark_minor_delete, diffs_without_minor_inserts)
  return diffs_we_care

def unmark_minor_delete(diff_tuple):
  '''

  >>> unmark_minor_delete((-1, '.'))
  (0, '.')
  >>> unmark_minor_delete((-1, 'foo'))
  (-1, 'foo')
  >>> unmark_minor_delete((0, '.'))
  (0, '.')
  >>> unmark_minor_delete((1, 'foo'))
  (1, 'foo')
  '''
  op, data = diff_tuple
  return (0, data) if all((is_delete(diff_tuple), is_not_important(diff_tuple))) else diff_tuple

def is_not_minor_insert(diff_tuple):
  '''decide if the diff tuple is important

  >>> is_not_minor_insert((1, 'please '))
  True
  >>> is_not_minor_insert((0, '.'))
  True
  >>> is_not_minor_insert((-1, '.'))
  True
  >>> is_not_minor_insert((1, '.'))
  False
  '''
  return False if all((is_insert(diff_tuple), is_not_important(diff_tuple))) else True 

def is_not_important(diff_tuple):
  '''decide if the diff tuple contains only ignored characters

  >>> is_not_important((0, 'we'))
  False
  >>> is_not_important((0, '.'))
  True
  '''
  return True if const.ignored_regex.match(diff_tuple[1]) else False

def is_insert(diff_tuple):
  '''

  >>> is_insert((0, '.'))
  False
  >>> is_insert((-1, '.'))
  False
  >>> is_insert((1, '.'))
  True
  '''
  return True if diff_tuple[0] == 1 else False

def is_delete(diff_tuple):
  '''

  >>> is_delete((0, '.'))
  False
  >>> is_delete((-1, '.'))
  True
  >>> is_delete((1, '.'))
  False
  '''
  return True if diff_tuple[0] == -1 else False


def dmpdiff_text(diffs): 
  '''return diffs in plain text.

  >>> dmpdiff_text([(1, 'please '), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (-1, '-'), (1, ' '), (0, 'milk'), (-1, '.'), (1, '!'), (0, ' Thank'), (-1, 's'), (1, ' you'), (0, '.')])
  '{+please +}give m[-e-]{+om+} a cup of bean[---]{+ +}milk[-.-]{+!+} Thank[-s-]{+ you+}.'
  '''
  return str.join('', map(format_diff, diffs))

def format_diff(diff_tuple):
  '''format diff with a style of wdiff

  >>> format_diff((1, 'please'))
  '{+please+}'
  >>> format_diff((0, 'give'))
  'give'
  >>> format_diff((-1, 'e'))
  '[-e-]'
  '''
  data = diff_tuple[1]
  return (const.ins_begin + data + const.ins_end) if (is_insert(diff_tuple)) else (
    (const.del_begin + data + const.del_end) if (is_delete(diff_tuple)) else data)


def main():
  ''' main function

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk! Thank you.'
  >>> dmpdiff_text(unmark_minor_diffs(dmpdiff(text1, text2)))
  '{+please +}give m[-e-]{+om+} a cup of bean-milk. Thank[-s-]{+ you+}.'
  '''
  import sys
  from_text = open(sys.argv[1]).read()
  to_text = open(sys.argv[2]).read()
  print(dmpdiff_text(unmark_minor_diffs(dmpdiff(from_text, to_text))))

if __name__ == '__main__':
  main()
