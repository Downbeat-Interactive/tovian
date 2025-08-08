#!/usr/bin/env python3
import os
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MD_DIR = ROOT / 'docs' / 'guide' / 'md'
OUT = ROOT / 'docs' / 'guide' / 'manifest.json'

def slug_to_title(slug: str) -> str:
    s = slug.replace('-', ' ').strip()
    return s[:1].upper() + s[1:]

def extract_title_summary(md_text: str, fallback_title: str):
    # Title: first H1 line or fallback
    m = re.search(r'^#\s+(.+?)\s*$', md_text, re.MULTILINE)
    title = m.group(1).strip() if m else fallback_title
    # Summary: first non-empty paragraph line without backticks
    for line in md_text.splitlines():
        t = line.strip()
        if not t or t.startswith('#') or t.startswith('```'):
            continue
        # strip markdown links/brackets lightly
        t = re.sub(r'\[(.*?)\]\((.*?)\)', r'\1', t)
        return (title, t)
    return (title, '')

def main():
    items = []
    for p in sorted(MD_DIR.glob('*.md')):
        slug = p.stem
        title_fallback = slug_to_title(slug)
        txt = p.read_text(encoding='utf-8')
        title, summary = extract_title_summary(txt, title_fallback)
        items.append({
            'id': slug,
            'path': f'{slug}.html',
            'title': title,
            'summary': summary
        })
    OUT.write_text(json.dumps(items, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(f'Wrote {len(items)} items to {OUT}')

if __name__ == '__main__':
    main()
