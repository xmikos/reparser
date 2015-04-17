ReParser
========

Simple regex-based lexer/parser for inline markup

Requirements
------------

- Python 3

Usage
-----

Example:

```
import re
from pprint import pprint
from reparser import Parser, Token, MatchGroup

boundary_chars = r'\s`!()\[\]{{}};:\'".,<>?«»“”‘’'
b_left = r'(?:(?<=[' + boundary_chars + r'])|(?<=^))' # Lookbehind
b_right = r'(?:(?=[' + boundary_chars + r'])|(?=$))' # Lookahead

markdown = b_left + r'(?P<start>{tag})(?P<text>\S.+?\S)(?P<end>{tag})' + b_right
markdown_link = r'(?P<start>\[)(?P<text>.+?)\]\((?P<url>.+?)(?P<end>\))'
newline = r'(?P<text>\n|\r\n)'

url_proto_re = re.compile(r'(?i)^[a-z][\w-]+:/{1,3}')
url_complete = lambda u: u if url_proto_re.search(u) else 'http://' + u

tokens = [
    Token(markdown.format(tag=r'\*\*\*'), is_bold=True, is_italic=True),
    Token(markdown.format(tag=r'___'), is_bold=True, is_italic=True),
    Token(markdown.format(tag=r'\*\*'), is_bold=True),
    Token(markdown.format(tag=r'__'), is_bold=True),
    Token(markdown.format(tag=r'\*'), is_italic=True),
    Token(markdown.format(tag=r'_'), is_italic=True),
    Token(markdown.format(tag=r'~~'), is_strikethrough=True),
    Token(markdown.format(tag=r'=='), is_underline=True),
    Token(markdown_link, link_target=MatchGroup('url', func=url_complete)),
    Token(newline, text='\n', segment_type='LINE_BREAK')
]

parser = Parser(tokens)
text = ('Hello **bold** world!\n'
        'You can **try *this* awesome** [link](www.eff.org).')

segments = parser.parse(text)
pprint([(segment.text, segment.params) for segment in segments])
```

Output:

```
[('Hello ', {}),
 ('bold', {'is_bold': True}),
 (' world!', {}),
 ('\n', {'segment_type': 'LINE_BREAK'}),
 ('You can ', {}),
 ('try ', {'is_bold': True}),
 ('this', {'is_bold': True, 'is_italic': True}),
 (' awesome', {'is_bold': True}),
 (' ', {}),
 ('link', {'link_target': 'http://www.eff.org'}),
 ('.', {})]
```

Limitations
-----------

Nested tags are supported only partially. Order of tokens is significant.

In the example above, `**some *nested* text**` would be parsed to:

    [('some ', {'is_bold': True}),
     ('nested', {'is_bold': True, 'is_italic': True}),
     (' text', {'is_bold': True})]

But `*some **nested** text*` would be instead parsed to:

    [('*some ', {}),
     ('nested', {'is_bold': True}),
     (' text*', {})]

This is because `**` token is specified before `*` token and therefore
parsed first. This behavior may change in the future.
