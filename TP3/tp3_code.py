import json 
import os
import pandas as pd 
import re
import nltk # pour stopword
from nltk.corpus import stopwords
nltk.download("stopwords")
import math

stopwords_en = stopwords.words("english")

from utils import clean_texte, input_text, augment_data

# Lecture et préparation (15 min)
# Charger les index

def load_all_indexes(folder="output_professeur"):
    """
    Returns:
        dict: Dictionnaire contenant tous les index chargés depuis des fichiers JSON dans le dossier
    """
    dict_indexes={}

    if not os.path.exists(folder):
        raise FileNotFoundError(f"Index folder '{folder}' not found")
    
    for file in os.listdir(folder):
        if file.endswith(".json") and file!="products.jsonl":
            with open(os.path.join(folder, file), 'r', encoding='utf-8') as f:
                name_file = file[:-5] 
                dict_indexes[name_file]= json.load(f)
    return dict_indexes

def load_products(filepath="output_professeur/products.jsonl"):
    products = {}

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            product = json.loads(line)
            url = product["url"]

            products[url] = {
                "title": product["title"],
                "description": product["description"]
            }

    return products

# Filtrage des documents (45 min)
# Créer une fonction qui vérifie si au moins un des tokens est présent

def check_at_least_one_token(query_tokens, title_index, description_index):
    """
    Filtre les sites contenant au moins un des tokens de la requête dans le titre ou la description"
    
    Returns:
        set: Ensemble des urls correspondant au critère
    
    """
    match_elements =set()
    for token in query_tokens:
        if token in title_index:
            match_elements.update(title_index[token].keys())
        if token in description_index:
            match_elements.update(description_index[token].keys())
    return match_elements

def check_all_tokens(query_tokens, champ_index): 
    """
    Filtre les sites contenant tous les tokens de la requête dans le champ spécifié (titre ou description)
    
    Args:
        champ_index (dict): Index inversé du champ (titre ou description)
    
    """
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

# Implémenter la fonction bm25 ainsi qu’une fonction de match exact

def get_all_urls(field_index):
    """
    Extrait toutes les urls présentes dans un index inversé positionnel.
    
    Returns:
        set: Ensemble des urls
    
    """
    all_urls = set()
    for urls in field_index.values():
        all_urls.update(urls.keys())
    return all_urls

def compute_document_lengths(index):
    lengths = {}

    for token in index:
        for url in index[token]:
            if url not in lengths:
                lengths[url] = 0
            lengths[url] += len(index[token][url])

    return lengths

def compute_idf(token, index, N):
    df = len(index[token]) if token in index else 0
    if df == 0:
        return 0
    return math.log(1 + (N - df + 0.5) / (df + 0.5))



def calculate_bm25(query_tokens, url, index, k1=1.2, b=0.75):

    N = len(get_all_urls(index))
    doc_lengths = compute_document_lengths(index)

    if url not in doc_lengths: # si le doc n'exitse pas dans l'index
        return 0
    
    doc_len = doc_lengths[url]
    avgdl = sum(doc_lengths.values()) / len(doc_lengths)

    score = 0
    for token in query_tokens:
        if token in index and url in index[token]:
            tf = len(index[token][url])
            idf = compute_idf(token, index, N)
            num = tf * (k1 + 1)
            den = tf + k1 * (1 - b + b * doc_len / avgdl)
            score += idf * (num / den)

    return score

# Match exact

def is_exact_match(query_tokens, doc_url, index):
    if not query_tokens:
        return False

    # tous les tokens doivent être dans le document
    for t in query_tokens:
        if t not in index or doc_url not in index[t]:
            return False

    # positions possibles du premier mot
    for start in index[query_tokens[0]][doc_url]:
        ok = True
        for i, t in enumerate(query_tokens):
            if start + i not in index[t][doc_url]:
                ok = False
                break
        if ok:
            return True

    return False

# Scoring 

WEIGHTS = {
    "bm25_title": 10,      # plus important car plus informatif
    "bm25_desc": 1,        
    "exact_match": 50,     # très pertinent si match exact
    "position_0": 20,      # très pertinent si la requête est au début
    "reviews_avg": 2,      # pour la qualité
    "reviews_count": 0.1   # pour la poularité
}

def linear_scoring(query_tokens, query_tokens_augmented, url, 
                   title_index, description_index, reviews_index):
    score = 0

    score += WEIGHTS["bm25_title"] * calculate_bm25(query_tokens_augmented, url, title_index)
    score += WEIGHTS["bm25_desc"] * calculate_bm25(query_tokens_augmented, url, description_index)

    if is_exact_match(query_tokens, url, title_index) or is_exact_match(query_tokens, url, description_index):
        score += WEIGHTS["exact_match"]

    if query_tokens and is_exact_match(query_tokens, url, title_index):
        if 0 in title_index[query_tokens[0]][url]:
            score += WEIGHTS["position_0"]

    if url in reviews_index:
        score += WEIGHTS["reviews_avg"] * reviews_index[url]["mean_mark"]
        score += WEIGHTS["reviews_count"] * reviews_index[url]["total_reviews"]

    return score

# Créer une fonction de recherche complète qui combine les étapes précédentes

def search(query, title_index, description_index, reviews_index, synonym_dict=None):
    query_tokens_phrase = input_text(query)     # garde l'ordre (pour exact match)
    
    if synonyms:
        tokens_aug = augment_data(query_tokens_phrase, synonyms)
    else:
        tokens_aug = query_tokens_phrase[:]

    urls = check_at_least_one_token(tokens_aug, title_index, description_index)

    results = []
    for url in urls:
        score = linear_scoring(query_tokens_phrase, tokens_aug, url,
                               title_index, description_index, reviews_index)
        results.append((url, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


def format_results_to_json(scored_results, query, products_data, total_docs):
    results = {
        "query": query,
        "metadata": {
            "total_documents": total_docs,
            "filtered_documents": len(scored_results),
            "returned_results": min(len(scored_results), 20)
        },
        "results": []
    }
    
    for url, score in scored_results[:20]:
        if url in products_data:
            product_info = products_data[url]
        else:
            continue

        results["results"].append({
            "url": url,
            "title": product_info["title"],
            "description": product_info["description"],
            "score": round(score, 2)
        })
    
    return results

# Testing (30 min)

def run_tests(title_index, description_index, reviews_index, synonyms, products):
    test_queries = [
        "smartphone usa",
        "chocolat white italy",
        "running shoes",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        results = search(query, title_index, description_index, reviews_index, synonyms)
        
        print(f"Found {len(results)} results")
        for i, (url, score) in enumerate(results[:5], 1):
            if url in products:
                title = products[url]["title"]
            else:
                title = ""

            print(f"{i}. [{score:.2f}] {title[:70]}...")


if __name__ == "__main__":

    indexes = load_all_indexes()
    products = load_products()

    title_index = indexes["title_index"]
    description_index = indexes["description_index"]
    reviews_index = indexes["reviews_index"]
    synonyms = indexes["origin_synonyms"]

    run_tests(title_index, description_index, reviews_index, synonyms, products)

    all_docs = get_all_urls(title_index) | get_all_urls(description_index)

    while True:
        query = input("\nQuery or 'quit': ")
        if query == "quit":
            break

        results = search(query, title_index, description_index, reviews_index, synonyms)
        formatted = format_results_to_json(results, query, products, len(all_docs))

        for i, r in enumerate(formatted["results"][:10], 1):
            print(f"{i}. {r['title']} ({r['score']})")

        if input("Save? (y/n): ") == "y":
            os.makedirs("TP3", exist_ok=True)
            filename = f"TP3/results_{query.replace(' ', '_')}.json"
            with open(filename, "w") as f:
                json.dump(formatted, f, indent=2)
