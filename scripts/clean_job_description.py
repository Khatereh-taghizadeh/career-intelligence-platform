from html.parser import HTMLParser

class HTMLTextExtractor(HTMLParser):
    """Extract readable text from HTML."""


    def __init__(self):
        super().__init__()
        self.text_parts = []


    def handle_data(self, data):
        self.text_parts.append(data)


    def get_text(self):
        return " ".join(" ".join(self.text_parts).split())



def clean_html(html_text):
    if html_text is None:
        return ""
    
    parser = HTMLTextExtractor()
    parser.feed(html_text)
    return parser.get_text()    