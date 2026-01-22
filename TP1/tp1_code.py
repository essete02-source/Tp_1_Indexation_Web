import urllib.request, urllib.robotparser
from bs4 import BeautifulSoup
import json
import requests
import re
from urllib.parse import urlparse, urljoin
import time


#  Configuration initiale et Extraction du contenu
# Développer une fonction qui s’assure que le crawler a le droit de parser une page

""" Je voulais stocker les robots.txt déjà lus pour éviter de les relire à chaque fois, mais je suis consciente
qu'ils peuvent être mis à jour donc je ne l'ai pas fait. Pour un TP ça risque de ne pas être aggressif mais
dans la vraie vie, on pourrait consulter une fois de temps en temps le robots.txt pour voir s'il a changé. """

def check_politess(url):
    """ 
    Vérifie si le crawling est autorisé selon le fichier robots.txt de l'url 
    
    Returns:
        bool: True si le crawling est autorisé, False sinon
    """
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt" # on part à la racine de l'url
    print(robots_url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
    except Exception as e:
        print(f"Impossible de lire robots.txt: {e}")
        return True  # si pas de robots.txt alors on autorise
    
    time.sleep(1)  # permet au serveur de ne pas être surchargé 
    return rp.can_fetch("*", url)


# Développer une fonction pour parser le HTML

def html_parser(url):
    """
    
    Returns:
        None ou Objet BeautifulSoup si autorisé"""
    if check_politess(url):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except Exception as e:
            print(f"Erreur parsing {url} : {e}")
            return None
    else:
        print(f"Crawl non autorisé pour {url}")
        return None

    
# Extraire titre, premier paragraphe et liens et l’information d’où viennent les liens

def nettoyer_url(url,url_depart):
    # Il y'a des liens qui sont relatifs
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return url
    return urljoin(url_depart, url)
    
def get_link(soup_detail, url_base,visited):
    """
    Extrait tous les liens internes.

    Args:
        soup_detail (BeautifulSoup): Objet soup en sortie de htmlparse.
        url_base (str)
        visited (set): Set des urls déjà visitées.

    Returns:
        list: Liste des nouveaux liens internes non visités.
    """
    body = soup_detail.find('body')
    if not body:
        return []
    
    balises_avec_link = body.find_all('a', href=True)
    links = []
    
    for content in balises_avec_link:
        link_nettoye = nettoyer_url(content['href'], url_base)
        
        if urlparse(link_nettoye).netloc == urlparse(url_base).netloc:
            if link_nettoye not in visited:
                links.append(link_nettoye)
    
    links = list(set(links))
    return links

def get_title(soup):
    title = soup.find('title')
    if title:
        return title.text.strip()
    return ""

def get_description(soup):
    description = soup.find('p',class_="product-description")
    if description is not None:
       return description.text
    return ""

def extraire_information(url,url_base,visited):
    # donnees dans les meta property
    # og:url , og:title  ou <title>, og:description 
    # pour les links, tous les 'href' dans les body
    try: 
        soup = html_parser(url)

        if soup is None:
            return None, []
        
        links = get_link(soup, url_base, visited)
        title = get_title(soup)
        description = get_description(soup)

        dict_sortie = {"url":url,
                "title":title,
                "description":description,
                "links":links
                }
        return dict_sortie, links
    
    except Exception as e:
        print(f"Erreur pour la page : {url}: {e}")
        return None, []


# Logique de crawling 
# Implémenter une file d'attente des URLs à visiter

def ordre_de_priorite(liste_url):
    """
    Trie les urls pour prioriser celles contenant 'product' ou 'products'.

    Args:
        liste_url (list): Liste des urls à trier
        
    Returns:
        list: Liste triée avec urls prioritaires en premier
    """
    liste_prioritaire=[url for url in liste_url if re.search(r'product(s)?',url)]
    liste_non_prioritaire=[url for url in liste_url if not re.search(r'product(s)?',url)]
    return liste_prioritaire + liste_non_prioritaire

# ---
def main(url_depart, url_base, nb_max):
    """
    Args:
        url_depart (str): URL de départ du crawl
        url_base (str): URL de base du site (pour les liens relatifs, robots.txt, etc)
        nb_max (int): Nombre maximum de pages à visiter
        
    Returns:
        list: Liste des dictionnaires avec les données extraites
    """
    liste_url = [url_depart]
    visited = set()
    data_frame_json = []
    pages_visitees = 0

    while liste_url and pages_visitees < nb_max:
        url = liste_url.pop(0)

        if url in visited:
            continue # on évite de revister une page
        
        print(f' Crawl de la page {url}') 
        visited.add(url)  
        data, new_links = extraire_information(url, url_base, visited)
        
        if data:
            data_frame_json.append(data)
        
        liste_url.extend(new_links)

        liste_url=ordre_de_priorite(liste_url) 
        pages_visitees+=1

    return data_frame_json

# Stockage des urls crawlées (10 min)- Sortir les résultats dans un fichier json

def construire_fichier_json(df):
    with open('output_json_tp1.json','w',encoding='utf-8') as f:
        json.dump(df,f,indent=4,ensure_ascii=False)

# Tests et optimisation (30 min)

# Il manque à la fin du script :
if __name__ == "__main__":

    url_depart = "https://web-scraping.dev/products"
    url_base = "https://web-scraping.dev"
    nb_max = 50

    result = main(url_depart, url_base, nb_max)

    construire_fichier_json(result)