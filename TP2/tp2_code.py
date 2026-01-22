import json
import pandas as pd
import json
import pandas as pd
import re
import os
import nltk # pour stopword
from nltk.corpus import stopwords
nltk.download("stopwords")

stopwords_en = stopwords.words("english")


# ID produit (numéro après la tld)
def extract_id_produit_url(data_input):
    """
    Extrait l'id produit qui suit 'product' ou 'products' dans l'URL et qui se trouve dans la section 'path' de l'url
    
    Args:
        data_input (pd.DataFrame): Dataframe de l'input contenant une colonne 'url'
    
    Returns:
        pd.DataFrame: Dataframe avec une nouvelle colonne 'id_product' 
    """
    pattern = r'(product|products)/((\d+))'
    data_input['id_product'] = data_input['url'].apply(lambda x : re.search(pattern,x).group(2) if re.search(pattern,x) else None)
    return data_input


# Variante (si présente)

def extract_variant_url(data_input):
    """
    
    Returns:
        pd.DataFrame: Dataframe avec une nouvelle colonne 'variant'
    """
    pattern = r'variant=([^&]+)'
    data_input['variant'] = data_input['url'].apply(lambda x : re.search(pattern,x).group(1) if re.search(pattern,x) else None)
    return data_input


# Utiliser la tokenization par espace | Supprimer les stopwords et la ponctuation

def clean_texte(texte):
    """
    Tokenize, nettoie et supprime les stopwords d'un texte donné.
    
    Returns:
        list: Liste des tokens nettoyés
    """
    token_propre=[]
    texte_tokens= texte.lower().split(' ')
    for tok in texte_tokens:
        tok = re.sub(r'[^a-zA-Z0-9]', '', tok)
        if tok and tok not in stopwords_en:
            token_propre.append(tok)
    return token_propre

# Création des index inversés

def index_inverse(data_input,colonne):
    """    
    Crée un index inversé simple pour une colonne donnée ('title' ou 'description')

    Args:
        colonne (str) : 'title' ou 'description'

    Returns:
        dict: index inversé {token: [url1, url2, ...]}
    """
    index_inv = {}
    for index, row in data_input.iterrows():
        url=row['url']
        title_tokens = clean_texte(row[colonne])
        for token in title_tokens:
            if token not in index_inv:
                index_inv[token] = []
            if url not in index_inv[token]:
                index_inv[token].append(url)
    return index_inv

# Créer un index pour les reviews 

def parametres_reviews(row):
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
    """
    Crée un index des reviews pour chaque url. Ce n'est pas un index inversé.
    
    Returns:
        dict: {url: {total_reviews, average_rating, last_rating}}
    """
    index_rev = {}
    for index, row in data_input.iterrows():
        nb_total_reviews, note_moyenne, derniere_note = parametres_reviews(row)
        index_rev[row['url']] = {
            'nb_total_reviews': nb_total_reviews,
            'note_moyenne': note_moyenne,
            'derniere_note': derniere_note
        }
    return index_rev


# Index des features

def index_inv_brand(data_input):
    index_inv={}
    for index, row in data_input.iterrows():
        if 'brand' not in row['product_features']:
            continue
        brand=row['product_features']['brand']
        if brand not in index_inv:
            index_inv[brand] = []
        if row['url'] not in index_inv[brand]:
            index_inv[brand].append(row['url'])
    return index_inv

def index_inv_origin(data_input):
    index_inv={}
    for index, row in data_input.iterrows():
        if 'made in' not in row['product_features']:
            continue
        origin=row['product_features']['made in'].lower()
        if origin not in index_inv:
            index_inv[origin] = []
        if row['url'] not in index_inv[origin]:
            index_inv[origin].append(row['url'])
    return index_inv

# Index de position

def index_inv_title_pos(data_input):
    """
    Crée un index inversé positionnel pour les titres
    
    Returns:
        dict: {token: {url: [positions]}}
        
    """
    index_inv={}
    for index,row in data_input.iterrows():
        liste_token_title = clean_texte(row['title'])
        for pos, token in enumerate(liste_token_title):
            if token not in index_inv:
                index_inv[token] = {}
            if row['url'] not in index_inv[token]:
                index_inv[token][row["url"]] = []
            index_inv[token][row["url"]].append(pos)
    return index_inv

def index_inv_description(data_input):
    index_inv={}
    for index,row in data_input.iterrows():
        liste_token_description = clean_texte(row['description'])
        for pos, token in enumerate(liste_token_description):
            if token not in index_inv:
                index_inv[token] = {}
            if row['url'] not in index_inv[token]:
                index_inv[token][row["url"]] = []
            index_inv[token][row["url"]].append(pos)
    return index_inv

# Sauvegarde des index

def save_index(data_input,output_dir):
    """
    Crée et sauvegarde les index dans des fichiers JSON.
    
    """

    os.makedirs(output_dir, exist_ok=True)

    index_inv_title_position = index_inv_title_pos(data_input)
    index_inv_description_position = index_inv_description(data_input)
    index_brand = index_inv_brand(data_input)
    index_origin = index_inv_origin(data_input)
    reviews_index = index_reviews(data_input)
    
    with open(os.path.join(output_dir, 'title_index.json'),'w') as f:
        json.dump(index_inv_title_position, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, 'description_index.json'),'w') as f:
        json.dump(index_inv_description_position, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, 'brand_index.json'),'w') as f:
        json.dump(index_brand, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, 'origin_index.json'),'w') as f:
        json.dump(index_origin, f, indent=4, ensure_ascii=False)
    with open(os.path.join(output_dir, 'reviews_index.json'),'w') as f:
        json.dump(reviews_index, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Parser le fichier JSONL

    input_file = 'products.jsonl'
    output_directory = 'indexes'

    data_input = pd.read_json(input_file, lines=True)

    data_input = extract_id_produit_url(data_input)
    data_input = extract_variant_url(data_input)
    save_index(data_input, output_directory)