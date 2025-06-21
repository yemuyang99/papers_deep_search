import textwrap
import networkx as nx
from tqdm import tqdm
from typing import List
from rapidfuzz import fuzz
from pyvis.network import Network
from utils.arxiv import ArxivPaper
from utils.custom_js import custom_js
from utils.relevance import RelevanceChecker
from utils.semantic_scholar import SemanticScholarCitation

class CitationGraph:
    def __init__(self, seed_papers_id: List[str], topic_description: str, api_key: str):
        self.topic_description = topic_description
        self.relevance_checker = RelevanceChecker(api_key)
        self.G = nx.DiGraph()

        self.node_id_list = []
        self.expand_agenda = [] 
        for seed_paper_id in seed_papers_id:
            seed_paper = ArxivPaper(identifier=seed_paper_id)
            if not seed_paper.paper:
                raise ValueError(f"Paper with ID {seed_paper_id} not found.")
            
            self.G.add_node(
                seed_paper.paper["id"], 
                title=seed_paper.paper['title'], 
                abstract=seed_paper.paper['summary'],
                sem_id=SemanticScholarCitation.get_paper_id(seed_paper.paper['title'])
            )
            self.node_id_list.append(seed_paper.paper["id"])
            self.expand_agenda.append(1)                                        # this tells the plan for expansion. 
                                                                                # 1 means to be expanded; 
                                                                                # 0 means not to be expanded; 
                                                                                # -1 means already expanded.

    def main(self, max_expand: int, max_relevant: int, save_path: str):
        if not save_path.endswith(".graphml"):
            raise ValueError("The save path must end with .graphml")
        while self.expand_agenda.count(-1) < max_expand and len(self.expand_agenda) < max_relevant:
            pagerank = nx.pagerank(self.G)
            for idx in range(len(self.node_id_list)):
                if self.expand_agenda[idx] == -1:
                    pagerank[self.node_id_list[idx]] = -99999999999
            to_be_expanded_id = max(pagerank, key=pagerank.get)
            to_be_expanded    = self.node_id_list.index(to_be_expanded_id)
            print(f"\n\n##### Expanding node: {to_be_expanded_id} - {self.G.nodes[to_be_expanded_id]['title']} #####")
            self.expand(to_be_expanded_id)
            self.expand_agenda[to_be_expanded] = -1
            self.complete_citation_edges()
            self.save(save_path)
            print(f"##### Saved current graph to {save_path} #####")

    def expand(self, node_id: str):
        node_sem_id = self.G.nodes[node_id]['sem_id']
        node_citations = SemanticScholarCitation.get_citations_from_id(node_sem_id)
        for citation in node_citations:
            if 'ArXiv' in citation['citingPaper']['externalIds']:
                arxiv_id = citation['citingPaper']['externalIds']['ArXiv']
                arxiv = ArxivPaper(identifier=arxiv_id)
            else:
                arxiv = ArxivPaper(title=citation['citingPaper']['title'])
                arxiv_title = arxiv.paper['title']
                wantt_title = citation['citingPaper']['title']
                score = fuzz.ratio(arxiv_title, wantt_title)
                if score < 80:
                    arxiv.paper = None

            if arxiv.paper:
                paper_id = arxiv.paper["id"]
                title    = arxiv.paper['title']
                abstract = arxiv.paper['summary']
                sem_id   = citation['citingPaper']['paperId']
            else:
                paper_id = citation['citingPaper']['paperId']
                title    = citation['citingPaper']['title']
                abstract = citation['citingPaper']['abstract'] if citation['citingPaper']['abstract'] else ""
                sem_id   = citation['citingPaper']['paperId']

            success = self.add_new_node(paper_id, title, abstract, sem_id)
            if success and not self.G.has_edge(node_id, paper_id):
                self.G.add_edge(paper_id, node_id)

        node_reference = SemanticScholarCitation.get_reference_from_id(node_sem_id)
        for reference in node_reference:
            if reference['citedPaper']['paperId'] is None:
                continue
            if 'ArXiv' in reference['citedPaper']['externalIds']:
                arxiv_id = reference['citedPaper']['externalIds']['ArXiv']
                arxiv = ArxivPaper(identifier=arxiv_id)
            else:
                arxiv = ArxivPaper(title=reference['citedPaper']['title'])
                arxiv_title = arxiv.paper['title']
                wantt_title = reference['citedPaper']['title']
                score = fuzz.ratio(arxiv_title, wantt_title)
                if score < 80:
                    arxiv.paper = None

            if arxiv.paper:
                paper_id = arxiv.paper["id"]
                title    = arxiv.paper['title']
                abstract = arxiv.paper['summary']
                sem_id   = reference['citedPaper']['paperId']
            else:
                paper_id = reference['citedPaper']['paperId']
                title    = reference['citedPaper']['title']
                abstract = reference['citedPaper']['abstract'] if reference['citedPaper']['abstract'] else ""
                sem_id   = reference['citedPaper']['paperId']

            success = self.add_new_node(paper_id, title, abstract, sem_id)
            if success and not self.G.has_edge(paper_id, node_id):
                self.G.add_edge(node_id, paper_id)

    def add_new_node(self, paper_id: str, title: str, abstract: str, sem_id: str):
        title = title.replace("\n", "")
        if paper_id in self.node_id_list:
            return True
        if not self.relevance_checker.check_relevance(title, abstract, self.topic_description):
            print(f"NO : {title}")
            return False
        self.G.add_node(
            paper_id,
            title=title,
            abstract=abstract,
            sem_id=sem_id
        )
        self.expand_agenda.append(1)
        self.node_id_list.append(paper_id)
        print(f"YES: {title}")
        return True

    def complete_citation_edges(self):
        for node_id in tqdm(self.node_id_list, desc="Completing citation edges"):
            node_sem_id = self.G.nodes[node_id]['sem_id']
            node_reference = SemanticScholarCitation.get_reference_from_id(node_sem_id)
            for reference in node_reference:
                if reference['citedPaper']['paperId'] in self.node_id_list:
                    if not self.G.has_edge(node_id, reference['citedPaper']['paperId']):
                        self.G.add_edge(node_id, reference['citedPaper']['paperId'])

    def save(self, filename: str):
        nx.write_graphml(self.G, filename)

    @staticmethod
    def export_graphml_as_html(graphml_path: str, html_path: str):
        if not graphml_path.endswith(".graphml"):
            raise ValueError("The graphml path must end with .graphml")
        if not html_path.endswith(".html"):
            raise ValueError("The html path must end with .html")
        
        
        G = nx.read_graphml(graphml_path)

        net = Network(notebook=True, directed=True)
        net.from_nx(G)
        
        net.barnes_hut()  # Optional: more stable initial layout
        net.set_options("""
            var options = {
                "physics": {
                    "enabled": true,
                    "stabilization": {
                    "enabled": true,
                    "iterations": 1000,
                    "updateInterval": 25,
                    "onlyDynamicEdges": false,
                    "fit": true
                    },
                    "solver": "forceAtlas2Based",
                    "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08,
                    "damping": 0.4,
                    "avoidOverlap": 1
                    }
                }
            }
        """)

        # Add metadata tooltips
        for node in net.nodes:
            node['abbrv'] = textwrap.fill(node['title'], width=20)
            node['title'] = f"{node['title']}"
            node['label'] = f"{node['abbrv']}"
            node['font']  = {'size': 8}

        net.show(html_path)

        # Inject into the HTML
        with open(html_path, "r") as f:
            html = f.read()

        # Add the JS just before </body>
        html = html.replace("</body>", custom_js + "\n</body>")

        # Overwrite with the enhanced HTML
        with open(html_path, "w") as f:
            f.write(html)
