import requests

import bs4
from bs4 import BeautifulSoup

from verse import Verse
from utils import text_purification

def search(reference, version, indent, titles):
    try:
        response = requests.get(f'https://www.biblegateway.com/quicksearch/?search={ reference }&version={ version }&searchtype=all&limit=50000&interface=print')
        sp = BeautifulSoup(response.content, 'html.parser')

        container = sp.find(class_ = 'passage-cols')

        delimiter = '\n' if indent else ' '

        for tag in container.find_all(class_ = 'chapternum'):
            tag.string = '<󠀀󠀀**1**> '

        for tag in container.find_all(class_ = 'versenum'):
            tag.string = f'<**{ tag.text[0:-1] }**>󠀀󠀀 󠀀󠀀󠀀󠀀󠀀󠀀󠀀󠀀󠀀'

        for tag in container.find_all('br'):
            tag.insert_before(sp.new_string(delimiter))
            tag.decompose()

        for tag in container.find_all('crossreference'):
            tag.decompose()

        for tag in container.find_all('footnote'):
            tag.decompose()

        for tag in container.find_all('h3'):
            tag.string = f'**{ tag.text }**'

        if not indent:
            for tag in container.find_all(class_ = 'indent-1-breaks'):
                tag.string = ' '

        passage = sp.find(class_ = 'bcv').text

        if (titles):
            text = delimiter.join([(f'\n{ tag.text.strip() }' + (' ' if indent else '\n')) if tag.name == 'h3' else tag.text.strip() for tag in container.find_all(['h3', 'p'])])
        else:
            text = delimiter.join([tag.text.strip() for tag in container.find_all('p')])

        dropdown = sp.find_all(class_ = 'dropdown-display-text')

        reference = dropdown[0].text.strip()
        version = dropdown[1].text.strip()

        return Verse(passage, text_purification.purify_verse_text(text), reference, version)
    except:
        return None