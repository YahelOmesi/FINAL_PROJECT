import pandas as pd
import os

# Import all 17 atomically isolated configuration lists from config.py
from config import (
    VERB_TAGS, NOUN_TAGS, PREPOSITION_TAGS, CONJUNCTION_TAGS,
    EMPHATIC_STATE_TAGS, ABSOLUTE_STATE_TAGS, CONSTRUCT_STATE_TAGS,
    PLURAL_TAGS, SINGULAR_TAGS, ADJECTIVE_TAGS, ADVERB_TAGS,
    PERSONAL_PRONOUN_TAGS, PRONOMINAL_SUFFIX_TAGS, NUMERAL_TAGS,
    INTERJECTION_TAGS, UNRESOLVED_TEXT_TAGS, MANUSCRIPT_GAP_TAGS,
    CAL_SYSTEM_METADATA_TAGS,BAVLI_TRACTATES, YERUSHALMI_TRACTATES
)

# 1. Load ONLY the explicitly listed files for the audit
dir_bavli = os.path.join('Data', 'csv_Bavli')
dir_yerushalmi = os.path.join('Data', 'csv_Yerushalmi')

all_dfs = []

for filename in BAVLI_TRACTATES:
    full_path = os.path.join(dir_bavli, filename)
    if os.path.exists(full_path):
        all_dfs.append(pd.read_csv(full_path))

for filename in YERUSHALMI_TRACTATES:
    full_path = os.path.join(dir_yerushalmi, filename)
    if os.path.exists(full_path):
        all_dfs.append(pd.read_csv(full_path))

df = pd.concat(all_dfs, ignore_index=True) if all_dfs else pd.DataFrame()

# 2. Extract all lexicon text, normalize to lowercase, and split into individual tokens
all_lex_text = " ".join(df['merged_lexicon'].fillna('').astype(str).tolist()).lower()
all_tokens = all_lex_text.split()

# 3. Convert the token list to a set to remove duplicates, then sort alphabetically
unique_tags = sorted(list(set(all_tokens)))
total_unique_count = len(unique_tags)

# 4. Map the unique tags into their respective configurations
m_verbs = [t for t in unique_tags if t in VERB_TAGS]
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
m_meta = [t for t in unique_tags if t in CAL_SYSTEM_METADATA_TAGS]

total_mapped_tags = (
    len(m_verbs) + len(m_nouns) + len(m_preps) + len(m_conjs) +
    len(m_emph) + len(m_abs) + len(m_const) + len(m_plur) +
    len(m_sing) + len(m_adj) + len(m_adv) + len(m_pron) +
    len(m_suff) + len(m_num) + len(m_inter) + len(m_unres) +
    len(m_gaps) + len(m_meta)
)

# 5. Compile all configurations into a single list to find unmapped leftovers
all_lists = (
    VERB_TAGS + NOUN_TAGS + PREPOSITION_TAGS + CONJUNCTION_TAGS +
    EMPHATIC_STATE_TAGS + ABSOLUTE_STATE_TAGS + CONSTRUCT_STATE_TAGS +
    PLURAL_TAGS + SINGULAR_TAGS + ADJECTIVE_TAGS + ADVERB_TAGS +
    PERSONAL_PRONOUN_TAGS + PRONOMINAL_SUFFIX_TAGS + NUMERAL_TAGS +
    INTERJECTION_TAGS + UNRESOLVED_TEXT_TAGS + MANUSCRIPT_GAP_TAGS +
    CAL_SYSTEM_METADATA_TAGS
)
unmapped_tags = [t for t in unique_tags if t not in all_lists]

# 6. Print the comprehensive summary and sanity check to the console
print("📊 ========================================================")
print("📊 ATOMIC GRAMMAR TAGS EXHAUSTIVE REPORT")
print("📊 ========================================================")
print(f"Total Unique Tags Found in Database: {total_unique_count}")
print(f"Total Tags Successfully Mapped:      {total_mapped_tags}")
print("-----------------------------------------------------------")
print(f" -> Verbs:              {len(m_verbs)} | Nouns:               {len(m_nouns)}")
print(f" -> Prepositions:        {len(m_preps)} | Conjunctions:        {len(m_conjs)}")
print(f" -> Emphatic States:     {len(m_emph)} | Absolute States:     {len(m_abs)} | Construct States: {len(m_const)}")
print(f" -> Plurals:             {len(m_plur)} | Singulars:           {len(m_sing)}")
print(f" -> Adjectives:          {len(m_adj)} | Adverbs:             {len(m_adv)}")
print(f" -> Personal Pronouns:   {len(m_pron)} | Pronominal Suffixes: {len(m_suff)}")
print(f" -> Numerals:            {len(m_num)} | Interjections:       {len(m_inter)}")
print(f" -> Unresolved Text (X): {len(m_unres)} | Manuscript Gaps (B): {len(m_gaps)}")
print(f" -> CAL System Metadata: {len(m_meta)}")
print("-----------------------------------------------------------")

if total_unique_count == total_mapped_tags:
    print("✅ SANITY CHECK PASSED: 100% of tags are perfectly isolated and accounted for!")
else:
    print(f"⚠️ SANITY CHECK WARNING: There are {len(unmapped_tags)} tags left unmapped.")
    print(unmapped_tags)

print("\n📋 Full Alphabetical List of Existing Tags:")
print(unique_tags)