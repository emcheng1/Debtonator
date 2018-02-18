# debtonator

Debtonator is designed to resolve a network of debts using the least number of transactions possible. Given a graph as an adjacency list, 
debtonator will return an adjacency list describing the final debt network setup.

This repo contains two files: hi.py and gui.pyw.

1. hi.py
  hi.py computes debt resolution using two methods: graph traversal and bipartite graph construction. The latter has outperformed the 
  former in all dense testcases thus far, and about half of sparse cases. 

2. gui.pyw
   gui.pyw provides a tkinter GUI in order for users to interface with the program without editing the source code.
