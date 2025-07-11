import re

class TextFormat():

    def remove_html(text):
        if text is None:
            return ''
        regex = re.compile('<[^>]+>')
        return re.sub(regex, '', text)