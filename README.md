ReParser
========

Simple regex-based lexer/parser for inline markup

Requirements
------------

- Python 3

Usage
-----

```
from reparser import Parser, Token, MatchGroup

markdown_re = r'(^|\s)(?P<start>{tag})(?P<text>\S.+?\S)(?P<end>{tag})(\s|$)'
markdown_link_re = r'(?P<start>\[)(?P<text>.+?)\]\((?P<url>.+?)(?P<end>\))'
newline_re = r'(?P<text>\n|\r\n)'

tokens = [
    Token(markdown_re.format(tag=r'\*\*\*'), is_bold=True, is_italic=True),
    Token(markdown_re.format(tag=r'___'), is_bold=True, is_italic=True),
    Token(markdown_re.format(tag=r'\*\*'), is_bold=True),
    Token(markdown_re.format(tag=r'__'), is_bold=True),
    Token(markdown_re.format(tag=r'\*'), is_italic=True),
    Token(markdown_re.format(tag=r'_'), is_italic=True),
    Token(markdown_re.format(tag=r'~~'), is_strikethrough=True),
    Token(markdown_re.format(tag=r'=='), is_underline=True),
    Token(markdown_link_re, link_target=MatchGroup('url')),
]

parser = Parser(tokens)

text = ('Hello **bold** world!\n
        'You can *try* this [link](https://www.eff.org).')

segments = parser.parse(text)
```
