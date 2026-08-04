import os

# Input directories containing the processed Bavli and Yerushalmi CSV files.
DIR_BAVLI = os.path.join('Data', 'csv_Bavli')
DIR_YERUSHALMI = os.path.join('Data', 'csv_Yerushalmi')

# Global mapping of grammatical and textual tags.
# Each linguistic category is maintained in a separate dedicated list.
VERB_TAGS = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', '(h)aphel', 'ethpay/w', 'ethpolal,', 'quad','ethpalpal', 'ettaphal', 'palpel', 'pay/w', 'polel,', 'v04'] # Verb forms
NOUN_TAGS = ['noun', 'n', 'nou', 'name', 'proper', 'geographic', 'geographical'] # Common, proper, and geographical nouns
PASSIVE_VERB_TAGS = ['ethpeel', 'ethpaal', 'ettaphal', 'ethpay/w', 'ethpolal,', 'ethpalpal', 'pay/w', 'polel,'] # Passive verb forms

PREPOSITION_TAGS = ['prep', 'preposition', 'p', 'proclitic'] # Independent and proclitic prepositions
CONJUNCTION_TAGS = ['conj', 'conjunction'] # Conjunctions and connective particles

EMPHATIC_STATE_TAGS = ['determined', 'emphatic', 'emphatic"unrecognizable', 'emphaticno'] # Emphatic or determined nominal state
ABSOLUTE_STATE_TAGS = ['abs.', 'absolute'] # Absolute nominal state
CONSTRUCT_STATE_TAGS = ['construct', 'construct"unrecognizable', 'constructno'] # Construct nominal state

PLURAL_TAGS = ['pl.', 'plural'] # Plural number
SINGULAR_TAGS = ['sg.', 'singular'] # Singular number

ADJECTIVE_TAGS = ['adjective'] # Adjectives
ADVERB_TAGS = ['adverb'] # Adverbs

PERSONAL_PRONOUN_TAGS = ['independent', 'personal'] # Independent personal pronouns
PRONOMINAL_SUFFIX_TAGS = ['pronominal', 'suffix'] # Pronominal suffixes and attached pronouns

NUMERAL_TAGS = ['numeral'] # Numerals
INTERJECTION_TAGS = ['interjection'] # Interjections and exclamatory expressions

UNRESOLVED_TEXT_TAGS = ['x'] # Words or textual units that could not be deciphered
MANUSCRIPT_GAP_TAGS = ['b'] # Physical manuscript gaps or missing textual sections

# Tags currently treated as irrelevant metadata or parsing noise.
# This classification should be reviewed with Liad.
IRRELEVANT_TAGS = [
    'a01', 'a02', 'b02', 'i01', 'i02', '”p01', 'no', 'or', 'r', 'with', '|', ':',
    '"unrecognizable', 'absolute"unrecognizable', 'data', 'data,', 'found"', 'previous', 'query', 'rows', 'lemma', 'word', 'number', 'single',
    '0', 't', 'is', 'in', 'of', 'above', 'like', 'such', 'babylon','(571–610)', '(died', '2', '610)', '[pky', 'a03', 'adiabene', 'alexander', 
    'and', 'antioch', 'asia', 'c01', 'c02', 'ca', 'center', 'christian', 'church', 'cn', 'divine', 'dly{{)y}}', 'east', 'form', 'fragmentary', 
    'headmaster', 'henana', 'main', 'minor', 'nisibis,', 'p002', 'p05', 'p32', 'r01', 's01', 'school', 'the', 'theologian,', 'theological', 'was'
]