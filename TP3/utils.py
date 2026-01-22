import json 
import os
import pandas as pd 
import re
import nltk # pour stopword
from nltk.corpus import stopwords
nltk.download("stopwords")
import math

stopwords_en = stopwords.words("english")

# Mettre en place les fonctions de tokenization (identiques au TP précédent)

def clean_texte(texte):
    """
    Nettoie et tokenize le texte en supprimant la ponctuation et les stopwords.
    Idem que TP2
    
    """
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

def get_synonyms(dict_synonyme,word):
    """
    Récupère les synonymes d'un mot à partir du dictionnaire des synonymes.
    Bi-directionnel : si le mot est une clé ou une valeur, on retourne tous les synonymes associés.
    
    Args:
        dict_synonyme (dict): Dictionnaire des synonymes {mot: [syn1, syn2, ...]}
        word (str): Mot pour lequel on veut les synonymes
    
    Returns:
        list: Liste contant le mot et ses synonymes"""
    if word in dict_synonyme:
        return [word] +dict_synonyme[word]
    for k,value in dict_synonyme.items():
        if word in value:
            return [k]+value
    return [word] # pas de synonyme trouvé


# • Augmentation de la requête par synonymes (applicable par exemple pour l’origine desproduits)

def augment_data(liste_token,data_synonyme):
    """
    Enrichit la liste de tokens avec leurs synonymes
    
    """
    liste_token_augmented =set(liste_token.copy())
    for token in liste_token:
        liste_synonyme = get_synonyms(data_synonyme,token) 
        liste_token_augmented.update(liste_synonyme)
    return list(liste_token_augmented)

