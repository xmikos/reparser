import re, enum


# Precompiled regex for matching named groups in regex patterns
group_regex = re.compile(r'\?P<(.+?)>')


class Segment:
    """Segment of parsed text"""
    def __init__(self, text, token=None, match=None, **params):
        self.text = text
        self.params = params
        if token and match:
            self.update_text(token, match)
            self.update_params(token, match)

    def update_text(self, token, match):
        """Update text from results of regex match"""
        if isinstance(self.text, MatchGroup):
            self.text = self.text.get_group_value(token, match)

    def update_params(self, token, match):
        """Update dict of params from results of regex match"""
        for k, v in self.params.items():
            if isinstance(v, MatchGroup):
                self.params[k] = v.get_group_value(token, match)


class Token:
    """Definition of token which should be parsed from text"""
    def __init__(self, name, pattern_start, pattern_end=None, text=None, skip=False, **params):
        self.name = name
        self.group_start = '{}_start'.format(self.name)
        self.group_end = '{}_end'.format(self.name) if pattern_end else None
        self.pattern_start = self.modify_pattern(pattern_start, self.group_start)
        self.pattern_end = self.modify_pattern(pattern_end, self.group_end) if pattern_end else None
        self.text = text
        self.skip = skip
        self.params = params

    def modify_pattern(self, pattern, group):
        """Rename groups in regex pattern and enclose it in named group"""
        pattern = group_regex.sub(r'?P<{}_\1>'.format(self.name), pattern)
        return r'(?P<{}>{})'.format(group, pattern)


class MatchGroup:
    """Name of regex group which should be replaced by its value when token is parsed"""
    def __init__(self, group, func=None):
        self.group = group
        self.func = func

    def get_group_value(self, token, match):
        """Return value of regex match for the specified group"""
        try:
            value = match.group('{}_{}'.format(token.name, self.group))
        except IndexError:
            value = ''
        return self.func(value) if callable(self.func) else value


class MatchType(enum.Enum):
    """Type of token matched by regex"""
    start = 1
    end = 2
    single = 3


class Parser:
    """Simple regex-based lexer/parser for inline markup"""
    def __init__(self, tokens):
        self.tokens = tokens
        self.regex = self.build_regex(tokens)
        self.groups = self.build_groups(tokens)

    def preprocess(self, text):
        """Preprocess text before parsing (should be reimplemented by subclass)"""
        return text

    def postprocess(self, text):
        """Postprocess text after parsing (should be reimplemented by subclass)"""
        return text

    def build_regex(self, tokens):
        """Build compound regex from list of tokens"""
        patterns = []
        for token in tokens:
            patterns.append(token.pattern_start)
            if token.pattern_end:
                patterns.append(token.pattern_end)
        return re.compile('|'.join(patterns), re.DOTALL)

    def build_groups(self, tokens):
        """Build dict of groups from list of tokens"""
        groups = {}
        for token in tokens:
            match_type = MatchType.start if token.group_end else MatchType.single
            groups[token.group_start] = (token, match_type)
            if token.group_end:
                groups[token.group_end] = (token, MatchType.end)
        return groups

    def get_matched_token(self, match):
        """Find which token has been matched by compound regex"""
        match_groupdict = match.groupdict()
        for group in self.groups:
            if match_groupdict[group] is not None:
                token, match_type = self.groups[group]
                return (token, match_type, group)

    def get_params(self, token_stack):
        """Get params from stack of tokens"""
        params = {}
        for token in token_stack:
            params.update(token.params)
        return params

    def remove_token(self, token_stack, token):
        """Remove last occurance of token from stack"""
        token_stack.reverse()
        try:
            token_stack.remove(token)
            retval = True
        except ValueError:
            retval = False
        token_stack.reverse()
        return retval

    def parse(self, text):
        """Parse text to obtain list of Segments"""
        text = self.preprocess(text)
        token_stack = []
        last_pos = 0

        # Iterate through all matched tokens
        for match in self.regex.finditer(text):
            # Find which token has been matched by regex
            token, match_type, group = self.get_matched_token(match)

            # Get params from stack of tokens
            params = self.get_params(token_stack)

            # Should we skip interpreting tokens?
            skip = token_stack[-1].skip if token_stack else False

            # Check for end token first
            if match_type == MatchType.end:
                if not skip or token_stack[-1] == token:
                    removed = self.remove_token(token_stack, token)
                    if removed:
                        skip = False
                    else:
                        skip = True

            if not skip:
                # Append text preceding matched token
                start_pos = match.start(group)
                if start_pos > last_pos:
                    yield Segment(self.postprocess(text[last_pos:start_pos]), **params)

                # Actions specific for start token or single token
                if match_type == MatchType.start:
                    token_stack.append(token)
                elif match_type == MatchType.single:
                    single_params = params.copy()
                    single_params.update(token.params)
                    single_text = token.text if token.text is not None else match.group(group)
                    yield Segment(single_text, token=token, match=match, **single_params)

                # Move last position pointer to the end of matched token
                last_pos = match.end(group)

        # Append anything that's left
        if last_pos < len(text):
            params = self.get_params(token_stack)
            yield Segment(self.postprocess(text[last_pos:]), **params)
