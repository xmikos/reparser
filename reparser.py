import re


class Segment:
    """Segment of parsed text"""
    def __init__(self, text, final=False, match=None, **params):
        self.text = text
        self.params = params
        self.final = final
        if match:
            self.update_text(match)
            self.update_params(match)

    def update_text(self, match):
        """Update text from results of regex match"""
        if isinstance(self.text, MatchGroup):
            self.text = self.text.get_group_value(match)

    def update_params(self, match):
        """Update dict of params from results of regex match"""
        for k, v in self.params.items():
            if isinstance(v, MatchGroup):
                self.params[k] = v.get_group_value(match)


class Token:
    """Definition of token which should be parsed from text"""
    def __init__(self, pattern, text=None, final=False, text_group='text',
                 start_group='start', end_group='end', **params):
        self.regex = re.compile(pattern, re.DOTALL)
        self.text = text
        self.final = final
        self.params = params
        self.text_group = text_group
        self.start_group = start_group
        self.end_group = end_group

    def find(self, segment):
        """Find this token in Segment"""
        segment_list = []

        # Return immediately if there is no match
        match = self.regex.search(segment.text)
        if not match:
            return (None, [segment])

        # Append previous (non-matched) text
        try:
            start_pos = match.start(self.start_group)
        except IndexError:
            start_pos = match.start(self.text_group)

        if start_pos != 0:
            segment_list.append(Segment(segment.text[:start_pos], **segment.params))

        # Append matched text
        text = self.text if self.text is not None else match.group(self.text_group)
        params = segment.params.copy()
        params.update(self.params)
        segment_list.append(Segment(text, final=self.final, match=match, **params))

        # Append anything that's left
        try:
            last_pos = match.end(self.end_group)
        except IndexError:
            last_pos = match.end(self.text_group)

        if last_pos != len(segment.text):
            segment_list.append(Segment(segment.text[last_pos:], **segment.params))

        return (start_pos, segment_list)


class MatchGroup:
    """Name of regex group which should be replaced by its value when token is parsed"""
    def __init__(self, group, func=None):
        self.group = group
        self.func = func

    def get_group_value(self, match):
        """Return value of regex match for the specified group"""
        try:
            value = match.group(self.group)
        except IndexError:
            value = ''
        return self.func(value) if callable(self.func) else value


class Parser:
    """Simple regex-based lexer/parser for inline markup"""
    def __init__(self, tokens):
        self.tokens = tokens

    def preprocess(self, text):
        """Preprocess text before parsing (should be reimplemented by subclass)"""
        return text

    def parse(self, text):
        """Parse text to obtain list of Segments"""
        return self.parse_recursive([Segment(self.preprocess(text))])

    def parse_recursive(self, segment_list):
        """Parse list of Segments recursively"""
        new_segment_list = []
        for segment in segment_list:
            # If segment is final, skip recursion
            if segment.final:
                new_segment_list.append(segment)
                continue

            # Build list of matches with their positions
            match_list = []
            for token in self.tokens:
                match = token.find(segment)
                if match[0] is not None:
                    match_list.append(match)

            # If we have matches, find leftmost match and recurse
            if match_list:
                leftmost_match = min(match_list)
                new_segment_list.extend(self.parse_recursive(leftmost_match[1]))
            else:
                new_segment_list.append(segment)
        return new_segment_list
