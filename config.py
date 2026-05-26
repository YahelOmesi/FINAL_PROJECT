# ==============================================================================
# GLOBAL CONFIGURATION: Exhaustive and Atomically Isolated Tag Mapping (46 tags)
# Every linguistic definition is isolated into its own dedicated constant array.
# ==============================================================================

# --- 1. CORE VARIABLES (Hypotheses 4, 8) ---
VERB_TAGS = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', '(h)aphel', 'ethpay/w', 'ethpolal,', 'quad'] # פעלים
NOUN_TAGS = ['noun', 'n', 'nou', 'name', 'proper', 'geographic', 'geographical'] # שמות עצם

# --- 2. FUNCTION WORDS SEPARATION (Hypothesis 2) ---
PREPOSITION_TAGS = ['prep', 'preposition', 'p', 'proclitic'] # מילות יחס ואותיות יחס
CONJUNCTION_TAGS = ['conj', 'conjunction'] # מילות קישור וחיבור

# --- 3. MORPHOLOGICAL STATES SEPARATION (Hypothesis 1) ---
EMPHATIC_STATE_TAGS = ['determined', 'emphatic'] # מצב מיודע - המלך
ABSOLUTE_STATE_TAGS = ['abs.', 'absolute'] # מצב מוחלט - מלך
CONSTRUCT_STATE_TAGS = ['construct'] # מצב סמיכות - מלכות שמיים

# --- 4. PLURALITY SEPARATION (Hypothesis 6) ---
PLURAL_TAGS = ['pl.', 'plural'] # לשון רבים
SINGULAR_TAGS = ['sg.', 'singular'] # לשון יחיד

# --- 5. MODIFIERS SEPARATION ---
ADJECTIVE_TAGS = ['adjective'] # תואר השם
ADVERB_TAGS = ['adverb'] # תואר הפועל

# --- 6. PRONOUNS SEPARATION ---
PERSONAL_PRONOUN_TAGS = ['independent', 'personal'] # כינויי גוף עצמאיים
PRONOMINAL_SUFFIX_TAGS = ['pronominal', 'suffix'] # כינויים חבורים\סיומות

# --- 7. SECONDARY SPEECH SEPARATION ---
NUMERAL_TAGS = ['numeral'] # מספרים
INTERJECTION_TAGS = ['interjection'] # מילות קריאה והתרגשות

# --- 8. STRUCTURAL AND DATA GAPS SEPARATION ---
UNRESOLVED_TEXT_TAGS = ['x'] # מילים שלא פוענחו
MANUSCRIPT_GAP_TAGS = ['b'] # חורים פיזיים או קטעים חסרים
CAL_SYSTEM_METADATA_TAGS = ['a01', 'data', 'i01', 'no', 'or', 'r', 'with', '|'] # סימונים טכניים פנימיים של אתר CAL