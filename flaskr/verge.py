import requests
import urllib.request
import time
from bs4 import BeautifulSoup

url = 'https://www.theverge.com/film'

result = {}
def get_content(title,link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, 'html.parser')
    # contents = soup.find_all("div", {"class": "c-entry-content"})
    for a in soup.find_all("div", {"class": "c-entry-content"}):
        return a.text

def get_links_and_title():
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    links = soup.findAll('a')
    mydivs = soup.find_all("h2", {"class": "c-entry-box--compact__title"})
    for div in mydivs[:5]:
        # print(div.findAll("a")[1])
        link = (div.find("a")['href'])
        title = (div.find("a").text)
        content = get_content(title,link)
        result[title]=content
    return result    
        


