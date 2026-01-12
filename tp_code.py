import urllib.request, urllib.robotparser
from bs4 import BeautifulSoup
import json
import requests

url_depart = "https://web-scraping.dev/products"

dict_sortie = {"url":"",
               "title":"",
               "description":"",
               "product_feature":{},
               "links":[]
               } # convertir avec json.dumps, indent


def fonction_de_sortie(url_depart,nb_maximum_docs):
    pass


# Développer une fonction qui s’assure que le crawler a le droit de parser une page

def check_politess(url):
    url_robots = url + fr"robots.txt"
    # headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    response = requests.get(url_robots) # ,headers
    liste = response.text.split('\n\n')
    nos_permissions = [ el for el in liste if el.startswith('User-Agent: *')]
    print(nos_permissions[0].split('\n'))
    print(response.text)
    return True # pour l'instant

# Développer une fonction pour parser le HTML

def html_parser(url):
    if check_politess(url):
        response = requests.get(url)
        soup = BeautifulSoup( response.text , 'html.parser')
        print(soup.prettify())


# Extraire titre, premier paragraphe et liens et l’information d’où viennent les liens

def get_link(soup_detail):
    body = soup_detail.find('body')
    balises_avec_link_interessant = body.find_all('a',href=True)
    links=[]
    for content in balises_avec_link_interessant:
        links.append(content['href'])
    return links

def get_title(soup):
    title = soup.find('meta',property="og:title")
    return title['content']

def get_description(soup):
    title = soup.find('p',class_="product-description")
    return title.text

def extraire_information(url):
    # donnees dans les meta property
    # og:url , og:title , og:description 
    # pour les links, tous les 'href' dans les body
    soup = html_parser(url)
    links = get_link(soup)
    title = get_title(soup)
    description = get_description(soup)


def html_parser(url):
    if check_politess(url):
        response = requests.get(url+rf'/products')
        soup = BeautifulSoup( response.text , 'html.parser')
        return soup 
        