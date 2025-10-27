import os
import shutil
import nltk

# List of NLTK resources with proper paths
corpora = [
    "corpora/stopwords",
    "corpora/wordnet",
    "corpora/omw-1.4",
    "tokenizers/punkt",
    "taggers/averaged_perceptron_tagger",
]

# Central folder where all NLTK data will be bundled
bundle_path = "nltk_bundle"
os.makedirs(bundle_path, exist_ok=True)

for corpus in corpora:
    try:
        src_path = nltk.data.find(corpus)  # full path within NLTK data
    except LookupError:
        nltk.download(corpus.split("/")[1])
        src_path = nltk.data.find(corpus)
        
    dest_path = os.path.join(bundle_path, os.path.basename(corpus))
    
    if os.path.isdir(src_path):
        shutil.copytree(src_path, dest_path, dirs_exist_ok=True)
    else:  # some data may be a single file
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copy2(src_path, dest_path)

print(f"NLTK corpora bundled into {bundle_path}")
