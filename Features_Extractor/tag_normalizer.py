"""
Convert CAL tags written in abbreviated format, such as `n.m.`, `vb.`,
`conj.`, and `prep.`, into grammatical categories recognized by the model.

The mappings are based exclusively on tags that appear in the Talmudic data.
No category is introduced unless it is already defined in `config.py`.
"""

import sys
import os

# Add the project root directory to the Python module search path.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PLURAL_TAGS, SINGULAR_TAGS,
    PASSIVE_VERB_TAGS
)

# Collect all grammatical categories recognized by the model directly from `config.py`.
ALL_KNOWN = {
    'VERB': set(VERB_TAGS),
    'NOUN': set(NOUN_TAGS),
    'PREP': set(PREPOSITION_TAGS),
    'CONJ': set(CONJUNCTION_TAGS),
    'EMPHATIC': set(EMPHATIC_STATE_TAGS),
    'ABSOLUTE': set(ABSOLUTE_STATE_TAGS),
    'PLURAL': set(PLURAL_TAGS),
    'SINGULAR': set(SINGULAR_TAGS),
    'PASSIVE': set(PASSIVE_VERB_TAGS),
}

# Representative values selected from the corresponding tag lists in `config.py`.
_VERB_REP = 'verb'
_NOUN_REP = 'noun'
_PREP_REP = 'prep'
_CONJ_REP = 'conjunction'
_EMPH_REP = 'emphatic'
_ABS_REP = 'absolute'
_PLUR_REP = 'pl.'
_SING_REP = 'sg.'
_PASS_REP = 'ethpeel'


def is_short_format(tag: str) -> bool:
    """
    Determine whether a tag uses the abbreviated CAL format rather than
    the full annotation format already found in the Talmudic datasets.
    """

    tag_l = tag.lower().strip()
    prefixes = (
        'n.m', 'n.f', 'n.(', 'vb.', 'conj.', 'prep.',
        'adj.', 'adv.', 'pron.', 'num.', 'interj.', 'v.n.'
    )
    return any(tag_l.startswith(p) for p in prefixes)


def normalize_short_tag(tag: str) -> list[str]:
    """
    Convert an abbreviated CAL tag into the configured values required for
    feature extraction.

    Return an empty list when no relevant mapping is identified.
    """

    t = tag.lower().strip()
    result = []

    # Identify general verb forms and recognized passive patterns.
    if 'vb.' in t:
        result.append(_VERB_REP)

        # Passive patterns represented in the abbreviated CAL format.
        if any(x in t for x in (
            ' gt', ' dt', ' ct',
            'ethpolal', 'ethpay',
            'palpel', 'polel,'
        )):
            result.append(_PASS_REP)

    # Identify nominal forms, including verbal nouns.
    if any(
        t.startswith(x) or (' ' + x) in t
        for x in ('n.m', 'n.f', 'n.(', 'v.n.')
    ):
        result.append(_NOUN_REP)

    # Identify prepositions.
    if t.startswith('prep.') or ' prep.' in t or t.startswith('prep '):
        result.append(_PREP_REP)

    # Identify conjunctions.
    if t.startswith('conj.') or t.startswith('conj ') or t == 'conj.':
        result.append(_CONJ_REP)

    # Identify emphatic forms, including emphatic plural notation.
    if any(x in t for x in ('pl.t.', 'pl.t', '.t.')):
        result.append(_EMPH_REP)

    # Treat singular nominal forms without emphatic or plural notation as absolute.
    if any(t.startswith(x) for x in ('n.m.', 'n.f.', 'n.(')):
        if 'pl.' not in t and '.t.' not in t and 'pl.t' not in t:
            result.append(_ABS_REP)

    # Identify plural forms.
    if 'pl.' in t:
        result.append(_PLUR_REP)

    # Identify singular nominal forms.
    if any(t.startswith(x) for x in ('n.m.', 'n.f.', 'n.(')):
        if 'pl.' not in t:
            result.append(_SING_REP)

    return result


def expand_tag(tag: str) -> list[str]:
    """
    Return a normalized list for abbreviated CAL tags, or preserve the original
    tag when it already uses the annotation format found in the Talmudic data.
    """

    if is_short_format(tag):
        normalized = normalize_short_tag(tag)

        # Preserve the original tag when no abbreviated-format mapping is available.
        return normalized if normalized else [tag]
    else:
        return [tag]