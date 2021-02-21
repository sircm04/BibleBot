import requests
from bs4 import BeautifulSoup

from itertools import chain

import re

p = re.compile(r'(?P<number>\d+)\s(?P<verse>.*)',
            flags = re.IGNORECASE)


# Use web-scraping to get passage-data from biblegateway.com
def search(verse, version, DEFAULT_VERSION) -> (dict, str, str):
    sp = query(verse, version)
    
    # Switch to default version if inputted version is invalid
    for tag in sp.find_all('legend'):
        if tag.text.strip() == 'Select version(s)':
            version = DEFAULT_VERSION
            sp = query(verse, version)
            break

    # Return None if verse is invalid
    for tag in sp.find_all('h3'):
        if tag.text == 'No results found.':
            return None

    verse = None
    version = None
    for i, tag in enumerate(sp.find_all(class_ = 'dropdown-display-text')):
        if i == 0:
            verse = tag.text
        if i == 1:
            version = tag.text
    
    dictionary = {}
    for i, tag in enumerate(chain(sp.find_all(class_ = 'chapternum'), sp.find_all(class_ = 'versenum'))):
        for m in re.finditer(p, tag.parent.text.strip()):
            dictionary[m.group('number')] = (m.group('verse'))
    
    return (dictionary, verse, version)

# Query bible-gateway
def query(verse, version) -> BeautifulSoup:
    response = requests.get(f'https://www.biblegateway.com/quicksearch/?search={ verse }&version={ version }&searchtype=all&limit=50000&interface=print')
    return BeautifulSoup(response.content, 'html.parser')