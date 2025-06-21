import requests
import feedparser
import numpy as np
import string
import os

class ArxivPaper:
    def __init__(self, identifier=None, title=None, cache_dir="./cache"):
        assert identifier or title, "Either identifier or title must be provided"
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

        if identifier:
            self.paper = self.init_from_id(identifier)
        elif title:
            self.paper = self.init_from_title(title)

    def init_from_id(self, identifier):
        base_url = "http://export.arxiv.org/api/query?id_list="
        query_url = base_url + identifier
        
        feed = feedparser.parse(query_url)
        if not feed.entries:
            print("No results found.")
            return None
        
        entry = feed.entries[0]
        return {
            "id": entry.id,
            "title": entry.title,
            "summary": entry.summary,
            "published": entry.published,
            "arxiv_url": entry.id,
            "pdf_url": next((link.href for link in entry.links if link.type == 'application/pdf'), None)
        }

    def init_from_title(self, title):
        # Construct the search query
        base_url = "http://export.arxiv.org/api/query?"
        # remove non-alphanumeric characters from title
        search_title = ''.join(e for e in title if e.isalnum() or e.isspace())
        search_query = f"search_query={'+'.join(search_title.split())}&searchtype=all"
        
        # Make the request
        response = requests.get(base_url + search_query)
        
        feed = feedparser.parse(response.text)
        if not feed.entries:
            print("No results found.")
            return None
        
        entry = feed.entries[0]
        return {
            "id": entry.id,
            "title": entry.title,
            "summary": entry.summary,
            "published": entry.published,
            "arxiv_url": entry.id,
            "pdf_url": next((link.href for link in entry.links if link.type == 'application/pdf'), None)
        }

    def download_pdf(self, filename):
        response = requests.get(self.paper['pdf_url'])
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Failed to download. Status code: {response.status_code}")

if __name__ == "__main__":
    paper = ArxivPaper(title="Repurposing Pre-trained Video Diffusion Models for Event-based Video Interpolation")
    print(paper.paper)
    # seed_paper_id = "2412.11284v1"
    # seed_paper = ArxivPaper(identifier=seed_paper_id)
    # print(seed_paper.paper)
    # print(paper.paper)
    # toc = paper.get_main_text()