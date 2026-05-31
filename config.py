# TRACTATES SELECTION: Explicitly define which files to include in the research
BAVLI_TRACTATES = ['df_hor_csv.csv', 'df_hag_csv.csv', 'df_yom_csv.csv', 'df_rh_csv.csv']
YERUSHALMI_TRACTATES = ['df_yer_hor_csv.csv', 'df_yer_hag_csv.csv', 'df_yer_yom_csv.csv', 'df_yer_rh_csv.csv']

# GLOBAL CONFIGURATION: Global mapping of tags, each language definition is isolated to its own dedicated set of constants.
VERB_TAGS = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', '(h)aphel', 'ethpay/w', 'ethpolal,', 'quad','ethpalpal', 'ettaphal', 'palpel'] # פעלים
NOUN_TAGS = ['noun', 'n', 'nou', 'name', 'proper', 'geographic', 'geographical'] # שמות עצם

PREPOSITION_TAGS = ['prep', 'preposition', 'p', 'proclitic'] # מילות יחס ואותיות יחס
CONJUNCTION_TAGS = ['conj', 'conjunction'] # מילות קישור וחיבור

EMPHATIC_STATE_TAGS = ['determined', 'emphatic'] # מצב מיודע - המלך
ABSOLUTE_STATE_TAGS = ['abs.', 'absolute'] # מצב מוחלט - מלך
CONSTRUCT_STATE_TAGS = ['construct'] # מצב סמיכות - מלכות שמיים

PLURAL_TAGS = ['pl.', 'plural'] # לשון רבים
SINGULAR_TAGS = ['sg.', 'singular'] # לשון יחיד

ADJECTIVE_TAGS = ['adjective'] # תואר השם
ADVERB_TAGS = ['adverb'] # תואר הפועל

PERSONAL_PRONOUN_TAGS = ['independent', 'personal'] # כינויי גוף עצמאיים
PRONOMINAL_SUFFIX_TAGS = ['pronominal', 'suffix'] # כינויים חבורים\סיומות

NUMERAL_TAGS = ['numeral'] # מספרים
INTERJECTION_TAGS = ['interjection'] # מילות קריאה והתרגשות

UNRESOLVED_TEXT_TAGS = ['x'] # מילים שלא פוענחו
MANUSCRIPT_GAP_TAGS = ['b'] # חורים פיזיים או קטעים חסרים במגילה\בכתב היד

# לשאול את ליעד
IRRELEVANT_TAGS = [
    'a01', 'a02', 'b02', 'i01', 'i02', '”p01', 'no', 'or', 'r', 'with', '|', ':',
    '"unrecognizable', 'absolute"unrecognizable', 'data', 'data,', 'found"', 'previous', 'query', 'rows', 'lemma', 'word', 'number', 'single',
    '0', 't', 'is', 'in', 'of', 'above', 'like', 'such', 'babylon'
]