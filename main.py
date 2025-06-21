from citation_graph import CitationGraph

topic_description = """
Identify research papers related to synthetic financial data generation. Financial data includes credit card transactions, stock prices, trading volumes, economical indicators, and so on.
Make sure the paper is relevant to **synthesize** the financial data, not just analyzing or predicting the financial data.
If it is only about analyzing or predicting the financial data, it is not relevant.
"""
cg = CitationGraph(
    seed_papers_id=["2011.01843", "2109.12546"],
    topic_description=topic_description,
    api_key="YOUR_API_KEY"
)
cg.main(max_expand=50, max_relevant=200, save_path='financial_data.graphml')

CitationGraph.export_graphml_as_html("financial_data.graphml", "financial_data.html")