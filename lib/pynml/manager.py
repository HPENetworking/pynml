# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP <asicapi@hp.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

"""
topology manager module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from collections import OrderedDict

from .nml import Node, Port, BidirectionalPort, Link, BidirectionalLink


class NMLManager(object):
    """
    NML namespace manager.

    :var namespace: :py:class:`OrderedDict` with all NML objects registered.
     Use :meth:`register_object` to register new objects.
    :var metadata: Store all kwargs passed to the constructor.
    """

    def __init__(self, **kwargs):
        self.namespace = OrderedDict()

        self.nodes = OrderedDict()
        self.biports = OrderedDict()
        self.bilinks = OrderedDict()

        self.metadata = kwargs

    def register_object(self, obj):
        """
        Register a NML object into the namespace managed by this Manager.

        :param NetworkObject obj: Object to register into the namespace.
        :raises Exception: If object already in namespace.
        """
        if obj.identifier in self.namespace:
            raise Exception(
                'Object already in namespace {}'.format(obj.identifier)
            )
        self.namespace[obj.identifier] = obj

    def create_node(self, **kwargs):
        """
        Helper to create and register a :class:`Node`.

        All keyword arguments are passed as is to the :class:`Node`
        constructor.

        :rtype: :class:`Node`
        :return: A new :class:`Node` already registered into the namespace.
        """
        node = Node(**kwargs)
        self.register_object(node)
        return node

    def create_biport(self, node, **kwargs):
        """
        Helper to create and register a :class:`BidirectionalPort`.

        All keyword arguments are passed as is to the
        :class:`BidirectionalPort` constructor. This helper also creates all
        intermediate directed inbound and outbound subports and relates them
        to the node. The `node` argument is related to those subports too.

        :rtype: :class:`BidirectionalPort`
        :return: A new :class:`BidirectionalPort` already registered into the
         namespace and with subports already related.
        """
        # Create objects
        biport = BidirectionalPort(**kwargs)
        in_port = Port(name=biport.name + '_in')
        out_port = Port(name=biport.name + '_out')

        # Register objects
        self.register_object(biport)
        self.register_object(in_port)
        self.register_object(out_port)

        # Relate objects
        biport.set_has_port(in_port, out_port)

        node.add_has_inbound_port(in_port)
        node.add_has_outbound_port(out_port)

        self.biports[node.identifier] = biport
        return biport

    def create_bilink(self, biport_a, biport_b, **kwargs):
        """
        Helper to create and register a :class:`BidirectionalLink`.

        All keyword arguments are passed as is to the
        :class:`BidirectionalLink` constructor. This helper also creates all
        intermediate directed sink and source sublinks and relates them
        to the inbound and outbound subports.

        :rtype: :class:`BidirectionalLink`
        :return: A new :class:`BidirectionalLink` already registered into the
         namespace and with sublinks already related.
        """
        # Create objects
        bilink = BidirectionalLink(**kwargs)
        link_a_b = Link(name=bilink.name + '_link_a_b')
        link_b_a = Link(name=bilink.name + '_link_b_a')

        # Register objects
        self.register_object(bilink)
        self.register_object(link_a_b)
        self.register_object(link_b_a)

        # Relate objects
        bilink.set_has_link(link_a_b, link_b_a)

        biport_a._has_port_ports[0].add_is_sink(link_b_a)  # inbound port
        biport_a._has_port_ports[1].add_is_source(link_a_b)  # outbound port

        biport_b._has_port_ports[0].add_is_sink(link_a_b)  # inbound port
        biport_b._has_port_ports[1].add_is_source(link_b_a)  # outbound port

        self.bilinks[(biport_a.identifier, biport_b.identifier)] = bilink
        return bilink

    def nodes(self):
        """
        Iterate over all registered :class:`Node`s in the namespace.

        This iterates the nodes in the order as they were added into the
        namespace.

        :return: An iterator to all nodes in the namespace.
        """
        for node in self.nodes.values():
            yield node

    def biports(self):
        """
        Iterate over all registered :class:`BidirectionalPort`s in the
        namespace.

        This iterates the biports in the order as they were added into the
        namespace.

        :return: An iterator to all biports in the namespace. The iterator is
         a tuple (:class:`Node`, :class:`BidirectionalPort`).
        """
        for nodeid, biport in self.ports.items():
            yield (self.nodes[nodeid], biport)

    def bilinks(self):
        """
        Iterate over all registered :class:`BidirectionalLink`s in the
        namespace.

        This iterates the bilinks in the order as they were added into the
        namespace.

        :return: An iterator to all bilinks in the namespace. The iterator is
         a tuple (:class:`Node`, :class:`BidirectionalPort`,
         :class:`BidirectionalLink`).
        """
        for (biport_aid, biport_bid), bilink in self.bilinks.items():
            yield (self.biports[biport_aid], self.biports[biport_bid], bilink)

    def export_nml(self):
        """
        Export current namespace as a NML XML format.

        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The current NML namespace in NML XML format.
        """
        pass

    def export_graphviz(self):
        """
        Export current namespace as a Graphviz graph.

        :rtype: str
        :return: The current NML namespace in Graphviz graph notation.
        """
        pass


__all__ = [
    'NMLManager'
]
