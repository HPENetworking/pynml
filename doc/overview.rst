.. toctree::

===============
Developer Guide
===============

BidirectionalLink and BidirectionalPort relation
================================================

.. digraph:: BiportBilink

   graph [fontname="Verdana" fontsize=8]
   node [fontname="Verdana" fontsize=7]
   edge [fontname="Verdana" fontsize=7]
   graph [layout=neato, nodesep=0.05 pad=0.0 margin=0.0 ranksep=0.25]
   node [style=filled shape=box margin=0.05 width=0.25 height=0.25]
   edge [arrowhead=vee];

   // Nodes
   node_a [label="Node:A"]
   pai [label="Port:PAi"]
   pao [label="Port:PAo"]
   pa [label="BidirectionalPort:PA"]

   node_b [label="Node:B"]
   pbi [label="Port:PBi"]
   pbo [label="Port:PBo"]
   pb [label="BidirectionalPort:PB"]

   link_b_a [label="Link:B-A"]
   link_a_b [label="Link:A-B"]
   bilink [label="BidirectionalLink:AB"]

   // Relations
   node_a -> pai [label="hasInboundPort"]
   node_a -> pao [label="hasOutboundPort"]
   pai -> link_b_a [label="isSink"]
   pao -> link_a_b [label="isSource"]

   node_b -> pbi [label="hasInboundPort"]
   node_b -> pbo [label="hasOutboundPort"]
   pbi -> link_a_b [label="isSink"]
   pbo -> link_b_a [label="isSource"]

   pa -> pai [label="hasPort"]
   pa -> pao [label="hasPort"]
   pb -> pbi [label="hasPort"]
   pb -> pbo [label="hasPort"]

   bilink -> link_a_b [label="hasLink"]
   bilink -> link_b_a [label="hasLink"]
