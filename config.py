import os

# 1. הגדרת נתיבים לתיקיות הנתונים
_dir_bavli = os.path.join('Data', 'csv_Bavli')
_dir_yerushalmi = os.path.join('Data', 'csv_Yerushalmi')

# 2. סריקת כל קבצי ה-CSV הקיימים בפועל בתיקיות
_files_bavli = [f for f in os.listdir(_dir_bavli) if f.endswith('.csv')] if os.path.exists(_dir_bavli) else []
_files_yerushalmi = [f for f in os.listdir(_dir_yerushalmi) if f.endswith('.csv')] if os.path.exists(_dir_yerushalmi) else []

# 3. פונקציות עזר לחילוץ קוד המסכת הנקי (למשל: 'df_az_csv.csv' -> 'az')
def _get_bavli_code(filename):
    return filename.replace('df_', '').replace('_csv.csv', '')

def _get_yer_code(filename):
    return filename.replace('df_yer_', '').replace('_csv.csv', '')

# 4. מיפוי קודים לקבצים המקוריים
_bavli_map = {_get_bavli_code(f): f for f in _files_bavli}
_yer_map = {_get_yer_code(f): f for f in _files_yerushalmi}

_bavli_codes = set(_bavli_map.keys())
_yer_codes = set(_yer_map.keys())

# 5. חישוב קבוצות: משותפות מול ייחודיות
_shared_codes = _bavli_codes & _yer_codes
_unique_to_bavli = _bavli_codes - _yer_codes
_unique_to_yerushalmi = _yer_codes - _bavli_codes

# 6. בניית הרשימות הגלובליות עבור המודל (רק המשותפות)
BAVLI_TRACTATES = [_bavli_map[code] for code in _shared_codes]
YERUSHALMI_TRACTATES = [_yer_map[code] for code in _shared_codes]

# 7. הדפסות מפורטות לביקורת הדאטה
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


# GLOBAL CONFIGURATION: Global mapping of tags, each language definition is isolated to its own dedicated set of constants.
VERB_TAGS = ['verb', 'v', 'peal', 'pael', 'ethpeel', 'ethpaal', '(h)aphel', 'ethpay/w', 'ethpolal,', 'quad','ethpalpal', 'ettaphal', 'palpel'] # פעלים
NOUN_TAGS = ['noun', 'n', 'nou', 'name', 'proper', 'geographic', 'geographical'] # שמות עצם
PASSIVE_VERB_TAGS = ['ethpeel', 'ethpaal', 'ettaphal', 'ethpay/w', 'ethpolal,', 'ethpalpal'] # פעלים סבילים

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