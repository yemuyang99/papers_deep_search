# Paper Deep Search
### TL'DR
`main.py` illustrates the usage of this package. Inputs are 
1) a topic description that you want to search;
2) a list of seed papers that are relevant to the topic. (1-2 papers are sufficient) Currently only ArXiv paper id is supported.
3) your deepseek API key.

The package will 
1) look at the paper's reference (who this paper cites) and citation (who cites this paper), 
2) determine whether those papers are relevant by checking your topic description, empowered by deepseek.
3) recursively do the above step on the newly discovered papers. The order is determined by the page rank algorithm.
4) the algorithm stops when either i) No. discovered papers exceed `max_expand` or ii) No. relevant papers exceed `max_relevant` or iii) you stop it manually.

Output:
1) a list of papers. (printed to the console)
2) a citation graph that is relevant to your topic description. (`*.graphml`)
3) a visualization of the graph. (`*.html`)
See `example_outputs/`.

### Python Environment Setup
```
conda create -n papers python=3.11 -y
conda activate papers
pip install networkx tqdm rapidfuzz pyvis requests feedparser numpy openai scipy
```

### Run the Code
Open `main.py` and set your 
* `seed_papers_id` (Arxiv), 
* `topic_description`, 
* `api_key`, 
* `max_expand`: maximum number of papers that are checked reference and citations.
* `max_relevant`: maximum number of relevant papers.