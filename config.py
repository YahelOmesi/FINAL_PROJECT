import os

DIR_BAVLI = os.path.join('Data', 'csv_Bavli')
DIR_YERUSHALMI = os.path.join('Data', 'csv_Yerushalmi')

# GLOBAL CONFIGURATION: Global mapping of tags, each language definition is isolated to its own dedicated set of constants.
VERB_TAGS = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', '(h)aphel', 'ethpay/w', 'ethpolal,', 'quad','ethpalpal', 'ettaphal', 'palpel', 'pay/w', 'polel,', 'v04'] # פעלים
NOUN_TAGS = ['noun', 'n', 'nou', 'name', 'proper', 'geographic', 'geographical'] # שמות עצם
PASSIVE_VERB_TAGS = ['ethpeel', 'ethpaal', 'ettaphal', 'ethpay/w', 'ethpolal,', 'ethpalpal', 'pay/w', 'polel,'] # פעלים סבילים

PREPOSITION_TAGS = ['prep', 'preposition', 'p', 'proclitic'] # מילות יחס ואותיות יחס
CONJUNCTION_TAGS = ['conj', 'conjunction'] # מילות קישור וחיבור

EMPHATIC_STATE_TAGS = ['determined', 'emphatic', 'emphatic"unrecognizable', 'emphaticno'] # מצב מיודע - המלך
ABSOLUTE_STATE_TAGS = ['abs.', 'absolute'] # מצב מוחלט - מלך
CONSTRUCT_STATE_TAGS = ['construct', 'construct"unrecognizable', 'constructno'] # מצב סמיכות - מלכות שמיים

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
    '0', 't', 'is', 'in', 'of', 'above', 'like', 'such', 'babylon','(571–610)', '(died', '2', '610)', '[pky', 'a03', 'adiabene', 'alexander', 
    'and', 'antioch', 'asia', 'c01', 'c02', 'ca', 'center', 'christian', 'church', 'cn', 'divine', 'dly{{)y}}', 'east', 'form', 'fragmentary', 
    'headmaster', 'henana', 'main', 'minor', 'nisibis,', 'p002', 'p05', 'p32', 'r01', 's01', 'school', 'the', 'theologian,', 'theological', 'was'
]