from parser import parse_queries


class Highlight_Set():
    def __init__(self, txt_doc, color):
        self.queries = parse_queries(txt_doc)
        self.color = color

