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

def load_json_file(folder="output_indexes"):
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

def check_at_least_one_token(query_tokens, title_index, description_index):
    match_elements =set()
    for token in query_tokens:
        if token in title_index:
            match_elements.update(title_index[token].keys())
        if token in description_index:
            match_elements.update(description_index[token].keys())
    return match_elements

def check_all_tokens(query_tokens, champ_index): 
    """ champ = title or description"""
    listes_url =[]
    for token in query_tokens:
        if token in champ_index:
            listes_url.append(set(champ_index[token].keys()))
        else:
            return set() # si au moins un token n'est pas trouvé
    if listes_url:
        return set.intersection(*listes_url) # on conserve les urls qui contiennenr tous les tokens
    else:
        return set()

# Ranking (30 min)

# Analyser les données disponibles pour identifier les signaux pertinents
"""

On donnera plus d'importance aux titres qu'aux descriptions car ils sont moins bruités.
On donnera également plus d'importance aux urls qui contiennet la requete dans le même ordre.
On pourra aussi utiliser les notes des reviews pour favoriser ceux avec de bonnes notes.
On peut également essayer de voir la popularité pour les priviligers.

"""
dict_indexes = load_json_file()

# Titre
title_indexes = dict_indexes['title_index']

all_urls_title= set()

for docs in title_indexes.values():
    all_urls_title.update(docs.keys())
print(f"{len(all_urls_title)} urls")
print(f"{len(title_indexes)} tokens uniques\n\n")

# Description

description_indexes = dict_indexes['description_index']

all_urls_description = set()

for docs in description_indexes.values():
    all_urls_description.update(docs.keys())
print(f"{len(all_urls_description)} urls")
print(f"{len(description_indexes)} tokens uniques\n\n")

# Reviews

reviews_indexes = dict_indexes['reviews_index']
print(reviews_indexes.values())
mark = [r['mean_mark'] for r in reviews_indexes.values() if r['total_reviews'] > 0]
nb_reviews = [r['total_reviews'] for r in reviews_indexes.values()]

if mark:
        print(f"Note moyenne: {sum(mark)/len(mark):.2f}/5")
        print(f"Avis moyen: {sum(nb_reviews)/len(nb_reviews):.2f}\n\n")

WEIGHTS = {
    "bm25_title": 10,      # plus important car plus informatif
    "bm25_desc": 1,        
    "exact_match": 50,     # très pertinent si match exact
    "position_0": 20,      # très pertinent si la requête est au début
    "reviews_avg": 2,      # pour la qualité
    "reviews_count": 0.1   # pour la poularité
}

# Implémenter la fonction bm25 ainsi qu’une fonction de match exact


def bm25_title(query_token,title_index,matching_urls):
    for tok in query_token:
        nb_url_with_token = len(title_index.get(tok,{}))
    pass

def bm25_description(query,description_index):
    pass


# Implémenter une fonction de scoring linéaire 
""" Combinant :
* Fréquence des tokens dans les documents
• Présence dans le titre vs description
• Les avis
• Autres signaux identifiés comme pertinents
• Utilisez l’information de position quand vous y avez accès
"""

