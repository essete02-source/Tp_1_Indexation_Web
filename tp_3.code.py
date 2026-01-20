import json 
import os
import pandas as pd 
import re
import nltk # pour stopword
from nltk.corpus import stopwords
nltk.download("stopwords")

stopwords_en = stopwords.words("english")

# Lecture et préparation (15 min)
# Charger les index

def load_json_file(folder):
    dict_indexes={}
    for file in os.listdir(folder):
        if file.endswith(".json") and file!="products.jsonl":
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                name_file = file[:-5] 
                dict_indexes[name_file]= json.load(f)
    return dict_indexes

# Mettre en place les fonctions de tokenization (identiques au TP précédent)

def clean_texte(texte):
    token_propre=[]
    texte_tokens= texte.lower().split(' ')
    for tok in texte_tokens:
        tok = re.sub(r'[^a-zA-Z0-9]', '', tok)
        if tok and tok not in stopwords_en:
            token_propre.append(tok)
    return token_propre

def input_text(texte):
    liste_token = clean_texte(texte)
    return liste_token

# Implémenter la lecture des synonymes

def get_synonyme(dict_synonyme,word):
    if word in dict_synonyme:
        return [word] +dict_synonyme[word]
    for k,v in dict_synonyme.items():
        if word in v:
            return [k]+v
    return [word] # pas de synonyme trouvé


# Filtrage des documents (45 min)
# • Augmentation de la requête par synonymes (applicable par exemple pour l’origine desproduits)

def augment_data(liste_token,data_synonyme):
    liste_token_augmente =set(liste_token.copy())
    for token in liste_token:
        liste_synonyme = get_synonyme(data_synonyme,token) 
        liste_token_augmente.update(liste_synonyme)
    return list(liste_token_augmente)

# Créer une fonction qui vérifie si au moins un des tokens est présent

def check_at_least_one_token(liste_tokens,texte):
    for token in liste_tokens:
        token = token.lower()
        if re.search(token,texte.lower()):
            return True 
    return False

def check_all_tokens(liste_tokens,texte):
    for token in liste_tokens:
        token = token.lower()
        if not re.search(token,texte.lower()):
            return False
    return True


# Ranking (30 min)

# Analyser les données disponibles pour identifier les signaux pertinents

def rank(texte_input,liste_token):
    n = len(liste_token)


def bm25_title():
    pass

def bm25_description():
    pass




