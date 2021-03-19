import requests

import bs4
from bs4 import BeautifulSoup

from verse import Verse
from utils import text_purification

def search(query, version, limit = 50000):
    try:
        response = requests.get(f'https://www.biblegateway.com/quicksearch/?search=${ query }&version=${ version }&searchtype=all&limit={ limit }&interface=print')
        sp = BeautifulSoup(response.content, 'html.parser')

        results = []

        for row in sp.find_all(class_ = 'row'):
            for tag in row.find_all(class_ = 'bible-item-extras', recursive = True):
                tag.decompose()
            for tag in row.find_all('h3', recursive = True):
                tag.decompose()

            result = [row.find(class_ = 'bible-item-title'),
                        row.find(class_ = 'bible-item-text')]
            
            if result[0] and result[1]:
                result[0] = result[0].text.strip()
                result[1] = text_purification.purify_verse_text(result[1].text.strip())

                results.append(result)

        return results
    except Exception as e:
        print(e.message, e.args)
        return None

def search_verse(reference, version, indent, titles):
    try:
        response = requests.get(f'https://www.biblegateway.com/passage/?search={ reference }&version={ version }&interface=print')
        sp = BeautifulSoup(response.content, 'html.parser')

        container = sp.find(class_ = 'passage-cols')

        h3 = sp.find('h3')
        if h3 and h3.text.strip() == 'No results found.':
            return None
        
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
        text = delimiter.join([('\n' + tag.text.strip() + '' if indent else '\n')
                                if titles and tag.name == 'h3' else tag.text.strip()
                                for tag in container.find_all(['h3', 'p'])])

        dropdown = sp.find_all(class_ = 'dropdown-display-text')
        reference = dropdown[0].text.strip()
        version = dropdown[1].text.strip()

        return Verse(passage, text_purification.purify_verse_text(text), reference, version)
    except Exception as e:
        print(e.message, e.args)
        return None

def is_valid_version(input):
    response = requests.get(f'https://www.biblegateway.com/passage/?search=John 3:16&version={ input }&interface=print')
    sp = BeautifulSoup(response.content, 'html.parser')

    legend = sp.find('legend')
    if legend:
        return legend.text.strip() != 'Enter passage(s)'
    else:
        return True