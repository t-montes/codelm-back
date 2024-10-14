from difflib import SequenceMatcher

tagmap = {
    'insert': '\033[92m',
    'delete': '\033[91m',
    'replace': '\033[93m'
}

def printso(tag, *args, **kwargs):
    if tag in tagmap:
        print(tagmap[tag], end='')
    print(*args, **kwargs)
    if tag in tagmap:
        print('\033[0m', end='')

def diff(code1, code2, encode, decode):
    tokens1 = encode(code1)
    tokens2 = encode(code2)
    similarity = SequenceMatcher(None, tokens1, tokens2)

    return [(
        tag, decode(tokens1[i1:i2]), decode(tokens2[j1:j2])
    ) for tag, i1, i2, j1, j2 in similarity.get_opcodes()]

def reconstruct(changes, original=False):
    if original:
        return "".join([original for _, original, _ in changes])
    else:
        return "".join([updated for _, _, updated in changes])

def show_diff(changes, original=False):
    if original:
        for tag, original, _ in changes: printso(tag, original, end='')
    else:
        for tag, _, updated in changes: printso(tag, updated, end='')
