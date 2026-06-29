"""
tag_normalizer.py
-----------------
ממיר תגיות בפורמט מקוצר של CAL (n.m., vb., conj., prep. וכו')
לרשימת קטגוריות שהמודל מכיר, מבוסס אך ורק על תגיות שמופיעות בנתוני התלמוד.

כלל המפתח: לא מוסיפים שום קטגוריה שלא קיימת כבר ב-config.py
"""

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, PLURAL_TAGS, SINGULAR_TAGS,
    PASSIVE_VERB_TAGS
)

# כל הקטגוריות שהמודל מכיר — נגזר ישירות מ-config.py
ALL_KNOWN = {
    'VERB':        set(VERB_TAGS),
    'NOUN':        set(NOUN_TAGS),
    'PREP':        set(PREPOSITION_TAGS),
    'CONJ':        set(CONJUNCTION_TAGS),
    'EMPHATIC':    set(EMPHATIC_STATE_TAGS),
    'ABSOLUTE':    set(ABSOLUTE_STATE_TAGS),
    'PLURAL':      set(PLURAL_TAGS),
    'SINGULAR':    set(SINGULAR_TAGS),
    'PASSIVE':     set(PASSIVE_VERB_TAGS),
}

# ייצוגים מרובים — ערכי config שנשתמש בהם בתור "נציגים"
_VERB_REP     = 'verb'           # מופיע ב-VERB_TAGS
_NOUN_REP     = 'noun'           # מופיע ב-NOUN_TAGS
_PREP_REP     = 'prep'           # מופיע ב-PREPOSITION_TAGS
_CONJ_REP     = 'conjunction'    # מופיע ב-CONJUNCTION_TAGS
_EMPH_REP     = 'emphatic'       # מופיע ב-EMPHATIC_STATE_TAGS
_ABS_REP      = 'absolute'       # מופיע ב-ABSOLUTE_STATE_TAGS
_PLUR_REP     = 'pl.'            # מופיע ב-PLURAL_TAGS
_SING_REP     = 'sg.'            # מופיע ב-SINGULAR_TAGS
_PASS_REP     = 'ethpeel'        # מופיע ב-PASSIVE_VERB_TAGS


def is_short_format(tag: str) -> bool:
    """
    מזהה אם התגית היא בפורמט הקצר של CAL
    (ולא פורמט מלא שכבר קיים בתלמוד).
    """
    tag_l = tag.lower().strip()
    prefixes = ('n.m', 'n.f', 'n.(', 'vb.', 'conj.', 'prep.', 
                'adj.', 'adv.', 'pron.', 'num.', 'interj.', 'v.n.')
    return any(tag_l.startswith(p) for p in prefixes)


def normalize_short_tag(tag: str) -> list[str]:
    """
    ממיר תגית קצרה לרשימת ערכי config שרלוונטיים לחישוב הפיצ'רים.
    מחזיר רשימה ריקה אם לא נמצא מיפוי רלוונטי.
    """
    t = tag.lower().strip()
    result = []

    # ─── VERB ────────────────────────────────────────────────────────────────
    if 'vb.' in t:
        result.append(_VERB_REP)         # ספירת פעלים כלליים
        # PASSIVE: בינייני סביל בפורמט הקצר: gt, dt, ct, ethpolal, ethpay, palpel, polel
        if any(x in t for x in (' gt', ' dt', ' ct', 
                                  'ethpolal', 'ethpay',
                                  'palpel', 'polel,')):
            result.append(_PASS_REP)     # ספירת פעלים סבילים

    # ─── NOUN ────────────────────────────────────────────────────────────────
    if any(t.startswith(x) or (' ' + x) in t
           for x in ('n.m', 'n.f', 'n.(', 'v.n.')):
        result.append(_NOUN_REP)

    # ─── PREPOSITION ─────────────────────────────────────────────────────────
    if t.startswith('prep.') or ' prep.' in t or t.startswith('prep '):
        result.append(_PREP_REP)

    # ─── CONJUNCTION ─────────────────────────────────────────────────────────
    if t.startswith('conj.') or t.startswith('conj ') or t == 'conj.':
        result.append(_CONJ_REP)

    # ─── EMPHATIC (determined) — pl.t. = emphatic plural ────────────────────
    if any(x in t for x in ('pl.t.', 'pl.t', '.t.')):
        result.append(_EMPH_REP)

    # ─── ABSOLUTE ────────────────────────────────────────────────────────────
    # n.m. / n.f. בלי t (לא emphatic) ובלי pl. = absolute singular
    if any(t.startswith(x) for x in ('n.m.', 'n.f.', 'n.(')):
        if 'pl.' not in t and '.t.' not in t and 'pl.t' not in t:
            result.append(_ABS_REP)

    # ─── PLURAL ──────────────────────────────────────────────────────────────
    if 'pl.' in t:
        result.append(_PLUR_REP)

    # ─── SINGULAR ────────────────────────────────────────────────────────────
    # n.m. / n.f. יחיד (לא רבים)
    if any(t.startswith(x) for x in ('n.m.', 'n.f.', 'n.(')):
        if 'pl.' not in t:
            result.append(_SING_REP)

    return result


def expand_tag(tag: str) -> list[str]:
    """
    פונקציה ראשית: מחזירה את התגית עצמה (אם היא כבר בפורמט תלמוד)
    או את הרשימה המנורמלת (אם היא בפורמט קצר).
    """
    if is_short_format(tag):
        normalized = normalize_short_tag(tag)
        return normalized if normalized else [tag]   # fallback לתגית המקורית
    else:
        return [tag]