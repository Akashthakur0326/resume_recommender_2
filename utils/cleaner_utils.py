import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from textblob import TextBlob
import emoji
from symspellpy.symspellpy import SymSpell, Verbosity

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()
# Stopwords
stop_words = set(stopwords.words('english'))

# Optional: SymSpell setup for typo correction
sym_spell = SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
# You may load dictionary here if needed: sym_spell.load_dictionary("frequency_dictionary_en_82_765.txt", 0, 1)

# ---------------- Cleaning Functions ---------------- #

def lowercase_text(text: str) -> str:
    return text.lower()

def remove_digits(text: str, replace_with_tag=False) -> str:
    if replace_with_tag:
        return re.sub(r'\d+', '<NUM>', text)
    return re.sub(r'\d+', '', text)

def remove_urls(text: str) -> str:
    return re.sub(r'http\S+|www\S+|https\S+', '', text)

def strip_newlines_whitespace(text: str) -> str:
    return re.sub(r'\s+', ' ', text).strip()

def remove_special_characters(text: str) -> str:
    return re.sub(r'[^A-Za-z0-9\s]+', '', text)

def remove_punctuation(text: str) -> str:
    return text.translate(str.maketrans('', '', string.punctuation))

def lemmatize_text(text: str) -> str:
    tokens = nltk.word_tokenize(text)
    return ' '.join([lemmatizer.lemmatize(t) for t in tokens])

def remove_stopwords(text: str, custom_keep=None) -> str:
    custom_keep = custom_keep or []
    tokens = nltk.word_tokenize(text)
    return ' '.join([t for t in tokens if t not in stop_words or t in custom_keep])

def correct_typos(text: str) -> str:
    blob = TextBlob(text)
    return str(blob.correct())

def expand_contractions(text: str) -> str:
    contractions = {
        "don't": "do not",
        "i'm": "i am",
        "it's": "it is",
        "can't": "cannot",
        "won't": "will not",
    }
    pattern = re.compile(r'\b(' + '|'.join(contractions.keys()) + r')\b')
    return pattern.sub(lambda x: contractions[x.group()], text)

def normalize_elongated_words(text: str) -> str:
    return re.sub(r'(.)\1{2,}', r'\1\1', text)

def handle_repeated_symbols(text: str) -> str:
    text = re.sub(r'([!?.]){2,}', r'\1', text)
    return text

def manage_emojis(text: str) -> str:
    return emoji.demojize(text)

def remove_non_english_chars(text: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\s]+', '', text)

def remove_duplicates(texts: list) -> list:
    return list(set(texts))

def replace_multiple_spaces(text: str) -> str:
    return re.sub(r'\s+', ' ', text)

def remove_whitespace(text):
    return " ".join(text.split())


def clean_text(text, lowercase=True, remove_ws=True, special_char=True, lemmatize=True, remove_sw=True):
    if lowercase: text = lowercase_text(text)
    if remove_ws: text = remove_whitespace(text)
    if special_char: text = remove_special_characters(text)
    if lemmatize: text = lemmatize_text(text)
    if remove_sw: text = remove_stopwords(text)
    return text