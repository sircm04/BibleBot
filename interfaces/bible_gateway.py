import requests
import bs4
from bs4 import BeautifulSoup

from itertools import chain

import re

p = re.compile(r'(?:(?P<number>\d+)(?:\s+)?)?(?P<verse>.*)',
            flags = re.IGNORECASE)


# Use web-scraping to get passage-data from biblegateway.com
def search(verse, version, DEFAULT_VERSION) -> (dict, str, str):
    sp = query(verse, version)
    
    # Switch to default version if inputted version is invalid
    for tag in sp.find_all('legend'):
        if isinstance(tag, bs4.element.Tag) and tag.text.strip() == 'Select version(s)':
            version = DEFAULT_VERSION
            sp = query(verse, version)
            break

    # Return None if verse is invalid
    if (sp.find(class_ = 'results-info')):
        return None

    for tag in sp.find_all('p'):
        if isinstance(tag, bs4.element.Tag) and tag.text.startswith('Sorry'):
            return None

    for tag in sp.find('h3'):
        if isinstance(tag, bs4.element.Tag) and tag.text.startswith('No results found.'):
            return None

    dropdown = sp.find_all(class_ = 'dropdown-display-text')
    verse = dropdown[0].text.strip()
    version = dropdown[1].text.strip()

    dictionary = {}
    num = 1
    for tag_p in sp.find(class_ = 'passage-cols').find_all('p'):
        for tag in tag_p.findChildren(recursive = False):
            chapternum = tag.find(class_ = 'chapternum')
            if chapternum:
                chapternum.string = '1'

            for m in re.finditer(p, tag.text.strip()):
                num = m.group('number') or num
                    
                if dictionary.get(num):
                    dictionary[num] += ' ' + m.group('verse')
                else:
                    dictionary[num] = m.group('verse')

    return (dictionary, verse, version)

# Query bible-gateway
def query(verse, version) -> BeautifulSoup:
    response = requests.get(f'https://www.biblegateway.com/quicksearch/?search={ verse }&version={ version }&searchtype=all&limit=50000&interface=print')
    return BeautifulSoup(response.content, 'html.parser')