import fitz
import re
import pandas as pd
import nltk
import spacy
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams
from PARSER import constant
from utils import cleaner_utils


nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


def parse_resume(uploaded_file):
    doc = open_pdf(uploaded_file)
    raw_text = extract_text(doc)
    cleaned_text = cleaner_utils.clean_text(raw_text)

    # Extract features
    name = None  # placeholder
    email = extract_email(cleaned_text)
    skills = extract_skills(cleaned_text)
    experience = extract_experience(cleaned_text)

    return {
        "Name": name,
        "Email": email,
        "Skills": skills,
        "Experience": experience
    }




def open_pdf(uploaded_file):
    """Open PDF once and return PyMuPDF doc object."""
    return fitz.open(stream=uploaded_file.read(), filetype="pdf")

def extract_text(doc, as_pages=False):
    if as_pages:
        return [page.get_text("text") for page in doc]
    else:
        return "\n".join([page.get_text("text") for page in doc])#return palin text

def extract_links(doc):
    links = []
    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                links.append(link["uri"])
    return links

def get_number_of_pages(doc):
    return len(doc)

"""def process_pdf(file):
    with fitz.open(file) as doc:
        return {
            "text": extract_text(doc),
            "links": extract_links(doc),
            "num_pages": get_number_of_pages(doc)
    }
"""
"""
    1-->Split the resume into lines → text_split.

    2-->Loop through each line (phrase).

    3-->If the line matches a section header (education, projects, etc.):
        entities[p_key] = []  make a fresh list for that section.

        else key = p_key  change the “active section” pointer.

    4-->For all following non-empty lines → elif key and phrase.strip(): → they get appended under the current key.

    5-->When another section header appears → step 3 runs again, so key is updated to the new section."""


def classify_sections(text):
    """
    Split resume text into sections based on RESUME_SECTION.
    Returns a dict where keys are section names and values are lists of lines.
    """

    # Split lines and strip whitespace
    line_split = [line.strip() for line in text.split("\n") if line.strip()]

    entity = {}
    key = None

    # Lowercase section list for matching
    section_set = set([s.lower() for s in constant.RESUME_SECTION])

    for line in line_split:
        # Skip single-character bullets
        if len(line) == 1:
            continue

        # Case-insensitive match with sections
        line_lower = line.lower()
        curr_key = set(line_lower.split(" ")) & section_set

        try:
            curr_key = list(curr_key)[0]  # convert set to list
        except IndexError:
            curr_key = None

        if curr_key:
            # Standardize key to original RESUME_SECTION casing
            orig_key = next((s for s in constant.RESUME_SECTION if s.lower() == curr_key), curr_key)
            entity[orig_key] = []
            key = orig_key  #start a new section 
        elif key is not None:
            entity[key].append(line) #if the line is not a section header add the current line to the most recent key

    # Remove empty sections
    entity = {k: v for k, v in entity.items() if v}

    return entity


#Then it applies its Named Entity Recognition (NER) model, which predicts BIO tags (Begin, Inside, Outside) for each token.
#Consecutive tokens with the same entity label (following the B/I pattern) are grouped together by spaCy internally.
def spacy_entity(processed_text):#expects a nlp processed text
    entities= {}
    for ent in processed_text.ents:
        if ent.label_ not in entities.keys():
            entities[ent.label_] = [ent.text]
        else:
            entities[ent.label_].append(ent.text)
    for key in entities.keys():#manage redundant entry
        entities[key] = list(set(entities[key]))#converting values of keys to set remove duplicate while list converts it back to list
    return entities



def extract_email(text):

    email = re.findall(r"([^@|\s]+@[^@]+\.[^@|\s]+)", text)
    if email:
        try:
            return email[0].split()[0]
        except IndexError:
            return None
    else : return []


def extract_name(nlp_text, matcher):
    pattern = [constant.NAME_PATTERN]

    # fixed: no None, no unpacking
    matcher.add("NAME", pattern)

    matches = matcher(nlp_text)

    for _, start, end in matches:
        span = nlp_text[start:end]
        if "name" not in span.text.lower():
            return span.text
    return None




def extract_education(nlp_text): #expects clean and tokenized text 
    edu = {}
    # Extract education degree
    try:
        for index, text in enumerate(nlp_text):
            for tex in text.split():
                tex = re.sub(r'[?|$|.|!|,]', r'', tex)
                if tex.upper() in constant.EDUCATION and tex not in constant.STOPWORDS:
                    edu[tex] = text + nlp_text[index + 1]
    except IndexError:
        pass
    return edu

#1.Load skills file (flat list of skills).
#2.Tokenize text (unigrams).
#3.Get noun chunks (bigrams, trigrams).
#4.Match tokens + noun chunks with skills list.
#5.Normalize (lowercase, strip spaces).
#6.Return unique skills.

'''def extract_skills(nlp_text, noun_chunks):
    skill_set=[]
    letter= [token.text for token in nlp_text if token.text not in constant.STOPWORDS]

    df= pd.read_csv('skills.csv')
    skills = list(df.columns.values)

    for l in letter:
        if l.lower() in skills:
            skill_set.append(l)

    #bigram and trigram
    for l in noun_chunks:
        l= l.text.lower().strip()
        if l in skills:
            skill_set.append(l)

    return list(set([i.lower() for i in skill_set]))
'''
def extract_experience(resume_text):
    """
    Extracts experience-related phrases from a resume using hybrid Regex + NER + POS tagging.
    """
    resume_text = resume_text.replace('\n', ' ')
    wordnet_lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))

    # Tokenization & Lemmatization
    word_tokens = nltk.word_tokenize(resume_text)
    filtered_tokens = [w for w in word_tokens if w.lower() not in stop_words]
    lemmatized = [wordnet_lemmatizer.lemmatize(w) for w in filtered_tokens]
    tagged = nltk.pos_tag(lemmatized)

    # POS-based chunking
    cp = nltk.RegexpParser('P: {<NNP>+}')#one or more proper nouns 
    cs = cp.parse(tagged)
    chunks = []
    for vp in cs.subtrees(filter=lambda x: x.label() == 'P'):
        phrase = " ".join([i[0] for i in vp.leaves()])
        if len(phrase.split()) >= 2:
            chunks.append(phrase)

    # Regex for "X years experience" patterns
    regex_matches = re.findall(r'(\d+\+?\s?(?:years|yrs|year)\s(?:of\s)?experience[^.,;]*)', resume_text, flags=re.IGNORECASE)

    # NER context extraction
    doc = nlp(resume_text)
    ner_matches = []
    for ent in doc.ents:
        if ent.label_ in ["DATE", "TIME", "ORG"]:
            context_window = resume_text[max(ent.start_char - 40, 0): ent.end_char + 40]
            if re.search(r'(experience|worked|as|role|position)', context_window, re.IGNORECASE):
                ner_matches.append(ent.text)

    all_exp = set(chunks + regex_matches + ner_matches)
    all_exp = [x.strip() for x in all_exp if len(x.strip()) > 3]

    return list(all_exp)


def extract_skills(text, skills_list=None):
    """
    Extracts skills from cleaned text using n-gram matching.
    """
    if skills_list is None:
        df = pd.read_csv('skills.csv')
        skills_list = [s.lower().strip() for s in df.columns.values]

    text = cleaner_utils.clean_text(text, lowercase=True, remove_ws=True, special_char=True, lemmatize=False, remove_sw=True)
    tokens = nltk.word_tokenize(text)
    found_skills = set()

    # Unigrams
    for token in tokens:
        if token in skills_list:
            found_skills.add(token)

    # Bigrams
    for bg in ngrams(tokens, 2):
        bg_str = " ".join(bg)
        if bg_str in skills_list:
            found_skills.add(bg_str)

    # Trigrams
    for tg in ngrams(tokens, 3):
        tg_str = " ".join(tg)
        if tg_str in skills_list:
            found_skills.add(tg_str)

    return list(found_skills)


def classify_job_sections(text, extra_experience=None):

    if not isinstance(text, str):
        return {}

    line_split = [i.strip() for i in text.split("\n") if i.strip()]

    entity = {}
    key = None

    for line in line_split:
        if len(line) == 1:  # skip bullets
            continue

        curr_key = set(line.lower().split(" ")) & set(constant.JOB_SECTION)

        try:
            curr_key = list(curr_key)[0]  # pick first match
        except IndexError:
            pass

        if curr_key in constant.JOB_SECTION:  # found new section header
            entity[curr_key] = []
            key = curr_key
        elif key is not None and line:  # continue under last found section
            entity[key].append(line)

    # ensure keys exist
    for sec in constant.JOB_SECTION:
        entity.setdefault(sec, [])

    # append extra experience if given
    if extra_experience:
        entity["experience"].append(extra_experience)

    return entity


"""def classify_job_sections(text, extra_experience=None):
    if not isinstance(text, str) or not text.strip():
        return {sec: [] for sec in constant.JOB_SECTION}

    entity = {sec: [] for sec in constant.JOB_SECTION}

    # your parsing logic here
    nlp_text = nlp(text)
    entity["skills"] = extract_skills(text)

    # safely append extra_experience
    if extra_experience is not None:
        # if it's a Series or list, convert to string
        if isinstance(extra_experience, pd.Series) or isinstance(extra_experience, list):
            extra_experience = " ".join(map(str, extra_experience))
        entity["experience"].append(str(extra_experience))

    # naive parsing for experience/education lines
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if "year" in line.lower() or "month" in line.lower():
            entity["experience"].append(line)
        if any(edu in line.lower() for edu in ["bsc", "msc", "bachelor", "master", "phd", "diploma"]):
            entity["education"].append(line)

    return entity
"""
