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
    parsed = urlparse(url)
    robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt" # on part à la racine de l'url
    print(robots_url)
    rp = urllib.robotparser.RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    time.sleep(1) 
    return rp.can_fetch("*", url)

# Développer une fonction pour parser le HTML

def html_parser(url):
    if check_politess(url):
        response = requests.get(url)
        soup = BeautifulSoup( response.text , 'html.parser')
        return soup 
    
# Extraire titre, premier paragraphe et liens et l’information d’où viennent les liens

def nettoyer_url(url,url_depart='https://web-scraping.dev'):
    # Il y'a des liens qui sont relatifs
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return url
    return urljoin(url_depart, url)
    
def get_link(soup_detail):
    global liste_url 
    body = soup_detail.find('body')
    balises_avec_link_interessant = body.find_all('a',href=True)
    links=[]
    for content in balises_avec_link_interessant:
        links.append(content['href'])

    links=[nettoyer_url(link) for link in links]
    liste_url.extend(links)
    liste_url=list(set(liste_url))
    print(f"Nombre d'urls à visiter : {len(liste_url)}")
    return links

def get_title(soup):
    return soup.find('title').text

def get_description(soup):
    title = soup.find('p',class_="product-description")
    if title is not None:
       return title.text
    return ""

def extraire_information(url):
    # donnees dans les meta property
    # og:url , og:title  ou <title>, og:description 
    # pour les links, tous les 'href' dans les body
    global data_frame_json 
    try: 
        soup = html_parser(url)
        links = get_link(soup)
        title = get_title(soup)
        description = get_description(soup)
        dict_sortie = {"url":url,
                "title":title,
                "description":description,
                "links":links
                }
        data_frame_json.append(dict_sortie)
        return data_frame_json
    except Exception as e:
        print(f"Erreur pour la page : {url}: {e}")
        return data_frame_json


# Logique de crawling 
# Implémenter une file d'attente des URLs à visiter

def ordre_de_priorite(liste_url):
    # on va mettre ceux qui ont 'product' ou 'prodcuts' dans une liste et le reste dans une autre , pour prioriser les url 'product' 
    liste_prioritaire=[url for url in liste_url if re.search(r'product(s)?',url)]
    liste_non_prioritaire=[url for url in liste_url if not re.search(r'product(s)?',url)]
    return liste_prioritaire + liste_non_prioritaire

def main(liste_url_param,nb_max):
    global liste_url
    liste_url = liste_url_param

    pages_visitees = 0
    while liste_url and pages_visitees < nb_max:
        url = liste_url.pop(0)
        if url in visited:
            continue
        print(f' Crawl de la page {url}') 
        extraire_information(url)
        visited.add(url)   
        liste_url=ordre_de_priorite(liste_url) 
        pages_visitees+=1

    print(f'fin {pages_visitees} pages visitées')
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

    liste_url=[]
    visited = set()
    liste_url.append(url_depart)

    data_frame_json = []

    result = main(liste_url, 50)
    construire_fichier_json(result)