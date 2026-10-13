#!/usr/bin/env python3
"""Fetch selected pages from Arabic Wikisource and convert them to LawCodex Markdown.

Usage: kw_wikisource.py RAW_DIR REPO_DIR
The list of pages and their target files is in PAGES below.
"""
import datetime, json, os, re, sys, time, urllib.parse
import requests

UA = 'LawCodex/1.0 (+https://github.com/LawCodex)'
API = 'https://ar.wikisource.org/w/api.php'
TODAY = datetime.date.today().isoformat()
JURIS = 'kw'
PAGES = [
    # (wikisource title, output path, front matter extras)
    ('دستور الكويت', 'ar/constitution/1962-constitution.md',
     {'title': 'دستور دولة الكويت', 'identifier': 'constitution-1962', 'type': 'constitution',
      'date': '1962-11-11', 'status': 'in_force',
      'status_note': 'Never amended. Amiri Order of 10 May 2024 dissolved the National Assembly and suspended some articles for up to four years; the text below is the constitution as adopted in 1962.'}),
    ('قانون رقم 64 لسنة 1999 في شأن حقوق الملكية الفكرية (الكويت)', 'ar/laws/1999/1999-64.md',
     {'title': 'قانون رقم 64 لسنة 1999 في شأن حقوق الملكية الفكرية', 'identifier': 'law/1999/64',
      'type': 'law', 'number': '64', 'year': 1999, 'status': 'repealed',
      'status_note': 'Replaced by Law No. 75 of 2019 on Copyright and Related Rights.'}),
]


def yq(s):
    return '"' + str(s).replace('\\', '\\\\').replace('"', '\\"') + '"'


def strip_templates(t):
    out, depth, i = [], 0, 0
    while i < len(t):
        if t.startswith('{{', i):
            depth += 1
            i += 2
        elif t.startswith('}}', i) and depth:
            depth -= 1
            i += 2
        else:
            if not depth:
                out.append(t[i])
            i += 1
    return ''.join(out)


def wiki_inline(s):
    s = re.sub(r'\[\[(?:[^\]|]*\|)?([^\]]*)\]\]', r'\1', s)
    s = re.sub(r'\[(?:https?://|//)\S+\s+([^\]]*)\]', r'\1', s)
    s = re.sub(r'\[(?:https?://|//)\S+\]', '', s)
    s = re.sub(r"'''(.+?)'''", r'**\1**', s)
    s = re.sub(r"''(.+?)''", r'\1', s)
    s = s.replace("'''", '').replace('<br />', ' ').replace('<br/>', ' ').replace('<br>', ' ')
    s = re.sub(r'<ref[^>]*>.*?</ref>|<ref[^>]*/>', '', s)
    s = re.sub(r'</?(span|div|center|big|small|font|u|b|i|p)[^>]*>', '', s)
    s = re.sub(r'__[A-Z]+__', '', s)
    return re.sub(r'[ \t ]+', ' ', s).strip()


ART = re.compile(r'^\**\s*(?:ال)?مادة\s*\(?\s*([0-9٠-٩]+(?:\s*مكرر[اًا]*\s*\S*)?)\s*\)?\s*[:\-–.]?\s*\**\s*[:\-–]?\s*(.*)$')
SEC = re.compile(r'^\**\s*(الباب|الفصل|الفرع|القسم|الكتاب)\s+\S+')
RANK = {'الكتاب': 0, 'القسم': 1, 'الباب': 2, 'الفصل': 3, 'الفرع': 4}


def convert(wikitext):
    t = strip_templates(wikitext)
    t = re.sub(r'\[\[(?:تصنيف|Category):[^\]]*\]\]', '', t)
    lines = [l.rstrip() for l in t.split('\n')]
    items = []  # (kind, text)
    counter = 0
    for l in lines:
        raw = l.strip()
        if not raw or raw == '----':
            items.append(('blank', ''))
            continue
        m = re.match(r'^(=+)\s*(.*?)\s*=+$', raw)
        if m:
            h = wiki_inline(m.group(2)).replace('**', '').strip()
            sm = SEC.match(h)
            items.append(('sec', h, RANK[sm.group(1)]) if sm else ('wsec', h, len(m.group(1))))
            continue
        prefix = ''
        lead = re.match(r'^[#*:;]*', raw).group(0)
        if lead == '#':
            counter += 1
            prefix = f'{counter}. '
        elif lead and lead[-1] in '#*':
            prefix = '- '
        if not lead.startswith('#'):
            counter = 0
        raw = raw.lstrip(':;*# ').strip() if raw[0] in ':;*#' else raw
        s = wiki_inline(raw)
        if not s:
            items.append(('blank', ''))
            continue
        a = ART.match(s.replace('**', '')) if len(s) < 400 else None
        if a and (s.replace('**', '').strip().startswith(('مادة', 'المادة'))):
            items.append(('art', f'المادة {a.group(1).strip()}' if s.replace('**', '').startswith('المادة') else f'مادة {a.group(1).strip()}'))
            if a.group(2).strip():
                items.append(('p', a.group(2).strip().strip('*').strip()))
            continue
        if SEC.match(s) and len(s) < 80:
            items.append(('sec', s.replace('**', '').strip(), RANK[SEC.match(s).group(1)]))
            continue
        items.append(('p', prefix + s))
    # merge a section heading with a short title line that follows it
    merged, i = [], 0
    while i < len(items):
        it = items[i]
        if it[0] in ('sec', 'wsec'):
            j = i + 1
            while j < len(items) and items[j][0] == 'blank':
                j += 1
            if j < len(items) and items[j][0] == 'p' and len(items[j][1]) < 80 and not items[j][1].endswith(('.', '،', ':')):
                it = (it[0], f'{it[1]} — {items[j][1].replace("**", "")}', it[2])
                i = j
            merged.append(it)
        else:
            merged.append(it)
        i += 1
    ranks = sorted({x[2] for x in merged if x[0] == 'sec'})
    wranks = sorted({x[2] for x in merged if x[0] == 'wsec'})
    out, cur = [], 1
    for it in merged:
        if it[0] == 'sec':
            cur = min(2 + ranks.index(it[2]), 5)
            out.append('#' * cur + ' ' + it[1])
        elif it[0] == 'wsec':
            cur = min(2 + wranks.index(it[2]), 5)
            out.append('#' * cur + ' ' + it[1])
        elif it[0] == 'art':
            out.append('#' * min(cur + 1, 6) + ' ' + it[1])
        elif it[0] == 'p':
            out.append(it[1])
    return '\n\n'.join(out)


def main():
    raw, repo = sys.argv[1], sys.argv[2]
    os.makedirs(os.path.join(raw, 'ws'), exist_ok=True)
    s = requests.Session()
    s.headers['User-Agent'] = UA
    for title, path, fmx in PAGES:
        cache = os.path.join(raw, 'ws', re.sub(r'\W+', '_', title)[:80] + '.json')
        if not os.path.exists(cache):
            r = s.get(API, params={'action': 'parse', 'page': title, 'prop': 'wikitext|revid', 'format': 'json'},
                      timeout=60)
            r.raise_for_status()
            open(cache, 'w').write(r.text)
            time.sleep(1)
        d = json.load(open(cache))['parse']
        body = convert(d['wikitext']['*'])
        url = 'https://ar.wikisource.org/wiki/' + urllib.parse.quote(title.replace(' ', '_'))
        fm = ['---', f'title: {yq(fmx["title"])}', f'identifier: {yq(fmx["identifier"])}', f'type: {fmx["type"]}',
              f'jurisdiction: {JURIS}', 'language: ar']
        for k in ('number', 'year', 'date'):
            if k in fmx:
                fm.append(f'{k}: {yq(fmx[k]) if k == "number" else fmx[k]}')
        fm.append(f'status: {fmx["status"]}')
        if 'status_note' in fmx:
            fm.append(f'status_note: {yq(fmx["status_note"])}')
        fm += [f'source: {yq(url)}', f'source_revision: {d["revid"]}',
               f'source_note: "Unofficial transcription on Arabic Wikisource"', f'retrieved: {TODAY}', '---']
        out = os.path.join(repo, path)
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, 'w', encoding='utf-8', newline='\n') as fh:
            fh.write('\n'.join(fm) + '\n\n# ' + fmx['title'] + '\n\n' + body.strip() + '\n')
        print(path, len(body))


if __name__ == '__main__':
    main()
