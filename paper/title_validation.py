"""Limit preservation-check exceptions to the author's recorded title edit."""

import json
import math
from pathlib import Path
import re


PAPER = Path(__file__).resolve().parent


def approved_title_edit():
    edits = json.loads((PAPER / 'applied-edits.json').read_text())
    changes = [change for change in edits['changes'] if change['edit'] == 'Update paper title']
    assert len(changes) == 1, 'Expected one recorded, author-approved title edit.'
    return changes[0]


def apply_approved_title_edit(text):
    change = approved_title_edit()
    assert text.count(change['before']) == 1, 'Baseline title is missing or ambiguous.'
    return text.replace(change['before'], change['after'], 1)


def without_approved_title(text, *, original=False):
    title = approved_title_edit()['before' if original else 'after']
    characters = list(re.finditer(r'\S', text))
    expected = re.sub(r'\s', '', title)
    assert ''.join(match.group() for match in characters[:len(expected)]) == expected
    return text[characters[len(expected) - 1].end():]


def split_title_characters(page, *, original=False):
    expected = re.sub(r'\s', '', approved_title_edit()['before' if original else 'after'])
    prefix = ''
    for index, character in enumerate(page.chars):
        prefix += re.sub(r'\s', '', character['text'])
        if len(prefix) >= len(expected):
            assert prefix == expected, 'Rendered title differs from the approved title.'
            return page.chars[:index + 1], page.chars[index + 1:]
    raise AssertionError('Rendered page has no complete approved title.')


def mask_approved_title(image, page, *, original=False):
    characters, _ = split_title_characters(page, original=original)
    xscale, yscale = image.width / page.width, image.height / page.height
    box = (
        math.floor((min(c['x0'] for c in characters) - 2) * xscale),
        math.floor((min(c['top'] for c in characters) - 2) * yscale),
        math.ceil((max(c['x1'] for c in characters) + 2) * xscale),
        math.ceil((max(c['bottom'] for c in characters) + 2) * yscale),
    )
    masked = image.copy()
    masked.paste('white', box)
    return masked
