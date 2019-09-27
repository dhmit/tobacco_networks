# Network Test Data
network_test_data.json has some initial test data to get this project started.

It's a dict with two lists, `nodes` and `links`. 

Each node has the following attributes:
- name: (str) Name of the person
- id: (int) id of the node (not important initially)
- docs: (int) number of documents that they have sent or received (might be used to scale the node size)
- words: (int) number of words in the docs they have sent or received

Each link has the following attributes:
- node1: (str) name of person 1 (each link connects two nodes)
- node2: (str) name of person 2
- id: (int) id of the link (not important initially)
- docs: (str) number of documents exchanged between node1 and node2
- words: (str) number of words in the docs exchanged between node1 and node2

Note: the links are undirected. For the time being we are not distinguishing between documents 
sent and documents received. In the future, we might add two links for each node1/node2 pair, one
with the documents sent from node1 to node2 and one with documents sent from node2 to node1.
