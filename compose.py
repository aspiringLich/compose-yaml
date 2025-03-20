from typing import Dict, List, Tuple
import yaml
import os
from os.path import expanduser

with open('keysym.yaml', 'r') as file:
    keysyms = yaml.safe_load(file)

files: Dict[str, dict] = {}
for filename in os.listdir('.'):
    if filename.endswith('.yaml') and filename != 'keysym.yaml':
        with open(filename, 'r') as file:
            files[filename[:-5]] = yaml.safe_load(file)

def str_to_keysym(s: str) -> str:
    return '<Multi_key> ' + ' '.join([f'<{keysyms[c]}>' for c in s])

def rec_process(root: str, d: dict) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for k, v in d.items():
        if isinstance(v, dict):
            out += rec_process(root + k, v)
        elif isinstance(v, str):
            out.append((str_to_keysym(root + k), v + f" # ({root + k.replace('\n', '\\n')})"))
    return out

template = """\
include "%L"

# generated by compose.py

"""

for k, v in files.items():
    if v is None:
        continue
    template += f"# {k}\n"
    ret = rec_process('', v)
    lens = [len(x[0]) for x in ret]
    lens.sort()

    # determine best targetlen
    targetlen = lens[-int(len(lens) * 0.1)]
    besterr = 1e9
    for test in range(lens[0], lens[-1] + 1):
        err = 0
        for l in lens:
            diff = test - l
            if diff < 0:
                err += abs(diff) * 20
            else:
                err += diff
        if err < besterr:
            besterr = err
            targetlen = test

    for (seq, res) in ret:
        (pre, post) = (res + ' ').split(' ', 1)
        first = post.split(' ', 1)[0]
        if first[0].isdigit():
            post = '0' * (6 - len(first)) + post
        template += f'   {seq + " " * (targetlen - len(seq))} : "{pre}" {post}\n'

with open(expanduser('~/.XCompose'), 'w') as file:
    file.write(template)
