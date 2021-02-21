import re

replacements = {
    '    ': ' ',
    '  ': ' ',
    '“': '"',
    '”': '"',
    '\n': ' ',
    '¶ ': '',
    ' , ': ', ',
    ' .': '.'
}

def purify_verse_text(text) -> str:
    for nuisance in replacements:
        text.replace(nuisance, replacements[nuisance])

    return re.sub(r'\(\w+\)|\[\w+\]', '', text)