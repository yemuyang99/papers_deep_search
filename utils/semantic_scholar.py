import requests
import time

class SemanticScholarCitation:
    @staticmethod
    def get_paper_id(title):
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": title,
            "fields": "paperId",
            "limit": 1
        }
        status_code = 0
        while status_code != 200:
            response = requests.get(url, params=params)
            status_code = response.status_code
            time.sleep(5)
        
        data = response.json()
        if data['data']:
            return data['data'][0]['paperId']
        else:
            return None

    @staticmethod
    def get_citations_from_id(paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations"
        params = {
            "fields": "title,paperId,externalIds,abstract"
        }
        status_code = 0
        while status_code != 200:
            citation_response = requests.get(url, params=params)
            status_code = citation_response.status_code
            time.sleep(1)
        return citation_response.json()['data']
    
    @staticmethod
    def get_reference_from_id(paper_id):
        url = f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/references"
        params = {
            "fields": "title,paperId,externalIds,abstract"
        }
        status_code = 0
        while status_code != 200:
            response = requests.get(url, params=params)
            status_code = response.status_code
            time.sleep(1)
        return response.json()['data']
