import json
import pandas as pd
import json
import pandas as pd
import re
import nltk # pour stopword
from nltk.corpus import stopwords

# Parser le fichier JSONL

data_input= pd.read_json('products.jsonl', lines=True)
print(data_input.columns())

# ID produit (numéro après la tld)
def id_produit_url(data_input):
    pattern = r'(product|products)/((\d+))'
    data_input['id_product'] = data_input['url'].apply(lambda x : re.search(pattern,x).group(2) if re.search(pattern,x) else None)
    return data_input

id_produit_url(data_input)

# Variante (si présente)

def variant_url(data_input):
    pattern = r'variant=([^&]+)'
    data_input['variant'] = data_input['url'].apply(lambda x : re.search(pattern,x).group(1) if re.search(pattern,x) else None)
    return data_input

variant_url(data_input)

# Utiliser la tokenization par espace | Supprimer les stopwords et la ponctuation
nltk.download("stopwords")

stopwords_en = stopwords.words("english")

def nettoyage(texte):
    token_propre=[]
    texte_tokens= texte.lower().split(' ')
    for tok in texte_tokens:
        tok = re.sub(r'[^a-zA-Z0-9]', '', tok)
        if tok not in stopwords_en:
            token_propre.append(tok)
    return token_propre

# Création des index inversés

def index_inverse(data_input,colonne):
    """    
    colonne (str) : 'title' ou 'description'
    """
    index_inv = {}
    for index, row in data_input.iterrows():
        title_tokens = nettoyage(row[colonne])
        for token in title_tokens:
            if token not in index_inv:
                index_inv[token] = set()
            index_inv[token].update(set(row['links']))
    return index_inv

# Créer un index pour les reviews 

def parametres_reviews(row):
    print(row)
    reviews=row['product_reviews']
    nb_total_reviews = len(reviews)
    if nb_total_reviews>0:
        s = 0
        for rev in reviews:
            s += int(rev['rating'])
        note_moyenne = s/nb_total_reviews
    else:
        note_moyenne=0
    derniere_note=reviews[-1]['rating'] if nb_total_reviews>0 else None
    return nb_total_reviews, note_moyenne, derniere_note

def index_reviews(data_input):
    index_rev = {}
    for index, row in data_input.iterrows():
        nb_total_reviews, note_moyenne, derniere_note = parametres_reviews(row)
        index_rev[row['url']] = {
            'nb_total_reviews': nb_total_reviews,
            'note_moyenne': note_moyenne,
            'derniere_note': derniere_note
        }
    return index_rev

index_reviews_data = index_reviews(data_input)
print(index_reviews_data)

