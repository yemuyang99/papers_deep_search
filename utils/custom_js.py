custom_js = """
<script type="text/javascript">
function highlightInOut(network, nodesDS, edgesDS, inEdgesMap, outEdgesMap) {
    network.on("click", function(params) {
        // Batch reset of all nodes
        const allNodes = nodesDS.get().map(node => ({
            id: node.id,
            color: 'rgba(128,128,128,0.3)',
            size: 10,
            label: node.abbrv
        }));
        nodesDS.update(allNodes);

        // Batch reset of all edges
        const allEdges = edgesDS.get().map(edge => ({
            id: edge.id,
            color: 'rgba(128,128,128,0.3)'
        }));
        edgesDS.update(allEdges);

        if (params.nodes.length === 0) return;

        const clickedNode = params.nodes[0];
        const connectedIn = inEdgesMap[clickedNode] || [];
        const connectedOut = outEdgesMap[clickedNode] || [];
        const loop = connectedIn.filter(item => connectedOut.includes(item));

        // Batch update for highlighted nodes
        const highlightUpdates = [];

        highlightUpdates.push({
            id: clickedNode,
            color: 'black',
            size: 15,
            label: nodesDS.get(clickedNode).abbrv
        });

        connectedIn.forEach(nodeId => {
            highlightUpdates.push({ id: nodeId, color: 'cyan' });
        });

        connectedOut.forEach(nodeId => {
            highlightUpdates.push({ id: nodeId, color: 'green' });
        });

        loop.forEach(nodeId => {
            highlightUpdates.push({ id: nodeId, color: 'orange' });
        });

        nodesDS.update(highlightUpdates);
    });

    network.on("doubleClick", function(params) {
        if (params.nodes.length === 0) return;

        const clickedNode = params.nodes[0];
        const node = nodesDS.get(clickedNode);

        if (node && node.title) {
            navigator.clipboard.writeText(node.title)
                .then(() => {
                    console.log("Title copied:", node.title);
                })
                .catch(err => {
                    console.error("Failed to copy:", err);
                });
        }
    });
}

window.addEventListener("load", () => {
    const inEdgesMap = {};
    const outEdgesMap = {};

    edges.forEach(edge => {
        if (!inEdgesMap[edge.to]) inEdgesMap[edge.to] = [];
        inEdgesMap[edge.to].push(edge.from);
        if (!outEdgesMap[edge.from]) outEdgesMap[edge.from] = [];
        outEdgesMap[edge.from].push(edge.to);
    });

    highlightInOut(network, nodes, edges, inEdgesMap, outEdgesMap);

    network.once("stabilizationIterationsDone", function () {
        network.setOptions({ physics: false });
    });
});
</script>
"""

# for node_id in tqdm(self.node_id_list, desc="Completing citation edges step 1"):
#     if self.G.nodes[node_id]['is_relevant'] == False:
#         continue
#     node_sem_id = self.G.nodes[node_id]['sem_id']
#     node_citations = SemanticScholarCitation.get_citations_from_id(node_sem_id)
#     for citation in node_citations:
#         if citation['citingPaper']['paperId'] in self.node_id_list:
#             if not self.G.has_edge(citation['citingPaper']['paperId'], node_id):
#                 self.G.add_edge(citation['citingPaper']['paperId'], node_id)