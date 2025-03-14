import requests
from bs4 import BeautifulSoup

class SearchAgent:
    def __init__(self, query):
        self.query = query

    def search(self):
        # ...existing code...
        response = requests.get(f"https://www.google.com/search?q={self.query}")
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        for g in soup.find_all(class_='g'):
            link = g.find('a')['href']
            results.append(link)
        return results
