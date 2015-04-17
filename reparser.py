import re


class Segment:
    """Segment of parsed text"""
    def __init__(self, text, match=None, **params):
        self.text = text
        self.params = params
        if match:
            self.update_params(match)

    def update_params(self, match):
        """Update dict of params from results of regex match"""
        for k, v in self.params.items():
            if isinstance(v, MatchGroup):
                try:
                    value = match.group(v.group)
                except IndexError:
                    value = ''
                self.params[k] = v.func(value) if callable(v.func) else value


class Token:
    """Definition of token which should be parsed from text"""
    def __init__(self, pattern, text_group='text', start_group='start', end_group='end', **params):
        self.regex = re.compile(pattern, re.DOTALL)
        self.params = params
        self.text_group = text_group
        self.start_group = start_group
        self.end_group = end_group


class MatchGroup:
    """Name of regex group which should be replaced by its value when token is parsed"""
    def __init__(self, group, func=None):
        self.group = group
        self.func = func


class Parser:
    """Simple regex-based lexer/parser for inline markup"""
    def __init__(self, tokens):
        self.tokens = tokens

    def preprocess(self, text):
        """Preprocess text before parsing (should be reimplemented by subclass)"""
        return text

    def find_tokens(self, token, segment):
        """Find tokens in Segment"""
        segment_list = []
        last_pos = 0

        for match in token.regex.finditer(segment.text):
            # Append previous (non-matched) text
            try:
                start_pos = match.start(token.start_group)
            except IndexError:
                start_pos = match.start(token.text_group)

            if start_pos != last_pos:
                segment_list.append(Segment(segment.text[last_pos:start_pos], **segment.params))

            # Append matched text
            params = segment.params.copy()
            params.update(token.params)
            segment_list.append(Segment(match.group(token.text_group), match=match, **params))

            # Move last position pointer after matched text
            try:
                last_pos = match.end(token.end_group)
            except IndexError:
                last_pos = match.end(token.text_group)

        # Append anything that's left
        if last_pos != len(segment.text):
            segment_list.append(Segment(segment.text[last_pos:], **segment.params))

        return segment_list

    def parse(self, text):
        """Parse text to obtain list of Segments"""
        segment_list = [Segment(self.preprocess(text))]
        for token in self.tokens:
            new_segment_list = []
            for segment in segment_list:
                new_segment_list.extend(self.find_tokens(token, segment))
            segment_list = new_segment_list
        return segment_list
