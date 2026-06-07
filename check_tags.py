import os
import pandas as pd

# ייבוא הקבועים והתגיות בלבד מתוך קובץ הקונפיגורציה החדש
from config import (
    DIR_BAVLI, DIR_YERUSHALMI,
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, CONSTRUCT_STATE_TAGS,
    PLURAL_TAGS, SINGULAR_TAGS, ADJECTIVE_TAGS, ADVERB_TAGS,
    PERSONAL_PRONOUN_TAGS, PRONOMINAL_SUFFIX_TAGS, NUMERAL_TAGS,
    INTERJECTION_TAGS, UNRESOLVED_TEXT_TAGS, MANUSCRIPT_GAP_TAGS,
    IRRELEVANT_TAGS, PASSIVE_VERB_TAGS
)

# =========================================================================
# DYNAMIC TRACTATE EXTRACTION LOGIC
# =========================================================================

# 1. סריקת קבצי ה-CSV בפועל מהתיקיות שהוגדרו ב-Config
_files_bavli = [f for f in os.listdir(DIR_BAVLI) if f.endswith('.csv')] if os.path.exists(DIR_BAVLI) else []
_files_yerushalmi = [f for f in os.listdir(DIR_YERUSHALMI) if f.endswith('.csv')] if os.path.exists(DIR_YERUSHALMI) else []

# 2. פונקציות עזר פנימיות לנרמול וחילוץ קוד המסכת
def _get_bavli_code(filename):
    return filename.replace('df_', '').replace('_csv.csv', '')

def _get_yer_code(filename):
    return filename.replace('df_yer_', '').replace('_csv.csv', '')

# 3. מיפוי קודים לקבצים מקוריים וחישוב קבוצות
_bavli_map = {_get_bavli_code(f): f for f in _files_bavli}
_yer_map = {_get_yer_code(f): f for f in _files_yerushalmi}

_bavli_codes = set(_bavli_map.keys())
_yer_codes = set(_yer_map.keys())

_shared_codes = _bavli_codes & _yer_codes
_unique_to_bavli = _bavli_codes - _yer_codes
_unique_to_yerushalmi = _yer_codes - _bavli_codes

# 4. יצירת רשימות המסכתות המשותפות הסופיות לשימוש בקובץ זה
BAVLI_TRACTATES = [_bavli_map[code] for code in _shared_codes]
YERUSHALMI_TRACTATES = [_yer_map[code] for code in _shared_codes]

# =========================================================================
# PRINT TRACTATES AUDIT REPORT
# =========================================================================
print("\n=========================================================")
print("             DATA TRACTATES AUDIT REPORT                 ")
print("=========================================================")

print(f"\n[+] SHARED TRACTATES ({len(_shared_codes)}):")
print("---------------------------------------------------------")
for code in sorted(_shared_codes):
    print(f"  - Code: {code:<5} | Bavli: {_bavli_map[code]:<18} | Yerushalmi: {_yer_map[code]}")

if _unique_to_bavli:
    print(f"\n[-] UNIQUE TO BAVLI ({len(_unique_to_bavli)}) - OMITTED FROM TRAINING:")
    print("---------------------------------------------------------")
    for code in sorted(_unique_to_bavli):
        print(f"  - Code: {code:<5} | File: {_bavli_map[code]}")

if _unique_to_yerushalmi:
    print(f"\n[-] UNIQUE TO YERUSHALMI ({len(_unique_to_yerushalmi)}) - OMITTED FROM TRAINING:")
    print("---------------------------------------------------------")
    for code in sorted(_unique_to_yerushalmi):
        print(f"  - Code: {code:<5} | File: {_yer_map[code]}")

print("=========================================================\n")

all_dfs = []

for filename in BAVLI_TRACTATES:
    full_path = os.path.join(DIR_BAVLI, filename)
    if os.path.exists(full_path):
        all_dfs.append(pd.read_csv(full_path))

for filename in YERUSHALMI_TRACTATES:
    full_path = os.path.join(DIR_YERUSHALMI, filename)
    if os.path.exists(full_path):
        all_dfs.append(pd.read_csv(full_path))

df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# Extract all lexicon text, normalize to lowercase and split into individual tokens
all_lex_text = " ".join(df['merged_lexicon'].fillna('').astype(str).tolist()).lower()
all_tokens = all_lex_text.split()

# Convert the token list to a set to remove duplicates, then sort alphabetically
unique_tags = sorted(list(set(all_tokens)))
total_unique_count = len(unique_tags)

# Map the unique tags into their respective configurations
m_verbs = [t for t in unique_tags if t in VERB_TAGS]
m_passive = [t for t in unique_tags if t in PASSIVE_VERB_TAGS]
m_nouns = [t for t in unique_tags if t in NOUN_TAGS]
m_preps = [t for t in unique_tags if t in PREPOSITION_TAGS]
m_conjs = [t for t in unique_tags if t in CONJUNCTION_TAGS]
m_emph = [t for t in unique_tags if t in EMPHATIC_STATE_TAGS]
m_abs = [t for t in unique_tags if t in ABSOLUTE_STATE_TAGS]
m_const = [t for t in unique_tags if t in CONSTRUCT_STATE_TAGS]
m_plur = [t for t in unique_tags if t in PLURAL_TAGS]
m_sing = [t for t in unique_tags if t in SINGULAR_TAGS]
m_adj = [t for t in unique_tags if t in ADJECTIVE_TAGS]
m_adv = [t for t in unique_tags if t in ADVERB_TAGS]
m_pron = [t for t in unique_tags if t in PERSONAL_PRONOUN_TAGS]
m_suff = [t for t in unique_tags if t in PRONOMINAL_SUFFIX_TAGS]
m_num = [t for t in unique_tags if t in NUMERAL_TAGS]
m_inter = [t for t in unique_tags if t in INTERJECTION_TAGS]
m_unres = [t for t in unique_tags if t in UNRESOLVED_TEXT_TAGS]
m_gaps = [t for t in unique_tags if t in MANUSCRIPT_GAP_TAGS]
m_irrelevant = [t for t in unique_tags if t in IRRELEVANT_TAGS]

total_mapped_tags = (
    len(m_verbs) + len(m_nouns) + len(m_preps) + len(m_conjs) +
    len(m_emph) + len(m_abs) + len(m_const) + len(m_plur) +
    len(m_sing) + len(m_adj) + len(m_adv) + len(m_pron) +
    len(m_suff) + len(m_num) + len(m_inter) + len(m_unres) +
    len(m_gaps) + len(m_irrelevant)
)

# Compile all configurations into a single list to find unmapped leftovers
all_lists = (
    VERB_TAGS + NOUN_TAGS + PREPOSITION_TAGS + CONJUNCTION_TAGS +
    EMPHATIC_STATE_TAGS + ABSOLUTE_STATE_TAGS + CONSTRUCT_STATE_TAGS +
    PLURAL_TAGS + SINGULAR_TAGS + ADJECTIVE_TAGS + ADVERB_TAGS +
    PERSONAL_PRONOUN_TAGS + PRONOMINAL_SUFFIX_TAGS + NUMERAL_TAGS +
    INTERJECTION_TAGS + UNRESOLVED_TEXT_TAGS + MANUSCRIPT_GAP_TAGS +
    IRRELEVANT_TAGS
)
unmapped_tags = [t for t in unique_tags if t not in all_lists]

# Print the comprehensive summary and sanity check to the console
print("========================================================")
print("ATOMIC GRAMMAR TAGS EXHAUSTIVE REPORT")
print("========================================================")
print(f"Total Unique Tags Found in Database: {total_unique_count}")
print(f"Total Tags Successfully Mapped:      {total_mapped_tags}")
print("-----------------------------------------------------------")
print(f" -> Verbs:               {len(m_verbs)} (Passive: {len(m_passive)}) | Nouns:               {len(m_nouns)}")
print(f" -> Prepositions:        {len(m_preps)} | Conjunctions:        {len(m_conjs)}")
print(f" -> Emphatic States:     {len(m_emph)} | Absolute States:     {len(m_abs)} | Construct States: {len(m_const)}")
print(f" -> Plurals:             {len(m_plur)} | Singulars:           {len(m_sing)}")
print(f" -> Adjectives:          {len(m_adj)} | Adverbs:             {len(m_adv)}")
print(f" -> Personal Pronouns:   {len(m_pron)} | Pronominal Suffixes: {len(m_suff)}")
print(f" -> Numerals:            {len(m_num)} | Interjections:       {len(m_inter)}")
print(f" -> Unresolved Text (X): {len(m_unres)} | Manuscript Gaps (B): {len(m_gaps)}")
print(f" -> Irrelevant Noise:    {len(m_irrelevant)}")
print("-----------------------------------------------------------")

if total_unique_count == total_mapped_tags:
    print("SANITY CHECK PASSED: 100% of tags were mapped!")
else:
    print(f"SANITY CHECK WARNING: There are {len(unmapped_tags)} tags left unmapped.")
    print(unmapped_tags)

print("\nFull Alphabetical List of Existing Tags:")
print(unique_tags)