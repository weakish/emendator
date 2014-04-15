#!/usr/bin/env python3.1
# by Jakukyo Friel <weakish@gmail.com> under GPL-2

'''compare two files, ignore unimportant characters.

Usage:

    emendator.py file1 file2

'''

import re
from itertools import chain
from diff_match_patch import diff_match_patch
import const

# Do not timeout. Let diff run until completion.
diff_match_patch.Diff_Timeout = 0

dmp = diff_match_patch()

# Ignore common punctuation marks in Chinese and English.
const.ignored_marks = '·～！……（）「」『』‘’“”《》，。、；：？—— ,\.;:!\'"?~-'
const.ignored = '[' + const.ignored_marks + ']' + '+'
const.ignored_begin_regex = re.compile('^' + const.ignored)
const.ignored_end_regex = re.compile(const.ignored + '$')
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
  [(1, 'please'), (0, 'give m'), (-1, 'e'), (1, 'om'), (0, ' a cup of bean'), (0, '-'), (0, 'milk'), (0, '.'), (0, ' Thank'), (-1, 's'), (1, 'you'), (0, '.')]
  '''
  return swap_insert(
    flatten_diffs(
      map(
        cleanup_minor_delete,
        map(
          unmark_minor_delete,
          map(
            cleanup_minor_insert,
            filter(
              is_not_minor_insert,
              diffs))))))

def flatten_diffs(diffs):
  '''

  >>> flatten_diffs(((1, 's'), ((0, 't'), (1, 'w')), (-1, 'z')))
  ((1, 's'), (0, 't'), (1, 'w'), (-1, 'z'))
  >>> flatten_diffs(((1, 's'), (-1, 'z')))
  ((1, 's'), (-1, 'z'))
  
  I'm not going to reinvent itertools.chain.
  itertools.chain produces '(1, 's', (0, 't'), (1, 'w'), -1, 'z')'.
  '''
  return tuple(
    chain.from_iterable(
      ( t
        if isinstance(t[0], tuple)
        else (t,))
      for t in diffs))

def cleanup_minor_insert(diff_tuple):
  '''

  >>> cleanup_minor_insert((1, '~user~'))
  (1, 'user')
  >>> cleanup_minor_insert((1, 'i~j'))
  (1, 'i~j')
  '''
  op, data = diff_tuple
  return (
    ( op,
      re.sub(
        const.ignored_begin_regex, '',
        (re.sub(const.ignored_end_regex, '', data))))
    if is_insert(diff_tuple)
    else diff_tuple)

def cleanup_minor_delete(diff_tuple):
  '''

  >>> cleanup_minor_delete((-1, '~we~'))
  ((0, '~'), (-1, 'we'), (0, '~'))
  >>> cleanup_minor_delete((-1, '~we'))
  ((0, '~'), (-1, 'we'))
  >>> cleanup_minor_delete((-1, 'we~'))
  ((-1, 'we'), (0, '~'))
  >>> cleanup_minor_delete((-1, 'we'))
  (-1, 'we')
  '''
  op, data = diff_tuple
  data_regex = re.compile(
    '(^[' +
    const.ignored_marks +
    ']*)([^' +
    const.ignored_marks +
    ']+)([' +
    const.ignored_marks +
    ']*$)')
  prefix = 0, re.sub(data_regex, '\g<1>', data)
  body = -1, re.sub(data_regex, '\g<2>', data)
  suffix = 0, re.sub(data_regex, '\g<3>', data)
  return (
    ( (prefix, body, suffix)
      if (all((prefix[1], suffix[1])))
      else (
        body
        if (not any((prefix[1], suffix[1])))
        else (
          (prefix, body)
          if (prefix[1])
          else (body, suffix))))
    if is_delete(diff_tuple)
    else diff_tuple) 

def swap_insert(diffs):
  '''

  >>> tuple(swap_insert(((-1, 'foo'), (0, '~'), (1, 'us'), (0, 'me'))))
  ((-1, 'foo'), (1, 'us'), (0, '~'), (0, 'me'))
  '''
  return (
    ( diffs[t+1]
      if
        t != (len(diffs) - 1)
        and all(
          (diffs[t][0] == 0, is_not_important(diffs[t]), diffs[t+1][0] == 1))
      else (
        diffs[t-1]
        if 
          t != 0
          and all(
            (diffs[t][0] == 1, diffs[t-1][0] == 0, is_not_important(diffs[t-1])))
        else (diffs[t])))
    for t in range(len(diffs)))

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
  return (
    (0, data)
    if all((is_delete(diff_tuple), is_not_important(diff_tuple)))
    else diff_tuple)

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
  return (
    False
    if all((is_insert(diff_tuple), is_not_important(diff_tuple)))
    else True)

def is_not_important(diff_tuple):
  '''decide if the diff tuple contains only ignored characters

  >>> is_not_important((0, 'we'))
  False
  >>> is_not_important((0, '.'))
  True
  '''
  return True if const.ignored_end_regex.match(diff_tuple[1]) else False

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
  return (
    const.ins_begin + data + const.ins_end
    if is_insert(diff_tuple)
    else (
      const.del_begin + data + const.del_end
      if is_delete(diff_tuple)
      else data))


def main():
  ''' main function

  >>> text1 = 'give me a cup of bean-milk. Thanks.'
  >>> text2 = 'please give mom a cup of bean milk! Thank you.'
  >>> dmpdiff_text(unmark_minor_diffs(dmpdiff(text1, text2)))
  '{+please+}give m[-e-]{+om+} a cup of bean-milk. Thank[-s-]{+you+}.'
  
  Chinese tests
  >>> text3 = '西周武公之共太子死，有五庶子，毋適立也。'
  >>> text4 = '周共太子死，有五庶子，皆愛之而無適立。'
  >>> dmpdiff_text(unmark_minor_diffs(dmpdiff(text3, text4)))
  '[-西-]周[-武公之-]共太子死，有五庶子，[-毋-]{+皆愛之而無+}適立[-也-]。'

  Well, the diff made by a human being (aka. me) is: 

      [-西-]周[-武公之-]共太子死，有五庶子，
      {+皆愛之而+}[-毋-]{+無+}適立[-也-]。

  The Levenshtein distance is the same.
  The difference is due to the Chinese characters '無' and '毋' are
  similar in both pronunciation and meaning.
  So the result is not perfect but expected,
  since computers can not produce a perfect result *unless*
  it actually understand the **semantics** of the language.
  If the diff was made by a human being who does not understand Chinese,
  the result would be the same.
 
  >>> text5 = """I say:'we'."""
  >>> text6 = """I say:"us"."""
  >>> dmpdiff_text(unmark_minor_diffs(dmpdiff(text5, text6)))
  "I say:'[-we-]{+us+}'."
  '''
  import sys
  from_text = open(sys.argv[1]).read()
  to_text = open(sys.argv[2]).read()
  print(dmpdiff_text(unmark_minor_diffs(dmpdiff(from_text, to_text))))

if __name__ == '__main__':
  main()
