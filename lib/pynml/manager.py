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

from .nml import Topology


class NMLManager(object):

    def __init__(self, **kwargs):
        self.root = Topology(kwargs)    # main nml topology
        self.namespace = OrderedDict()  # owns all nml objects

        self.nodes = OrderedDict()
        self.biports = OrderedDict()
        self.bilinks = OrderedDict()

    def register_object(self, obj):
        if obj.identifier in self.namespace:
            raise Exception(
                'Object already in namespace {}'.format(obj.identifier)
            )
        self.namespace[obj.identifier] = obj

    def create_node(self, **kwargs):
        node = None
        self.register_object(node)
        return node

    def create_biport(self, node, **kwargs):
        biport = None
        self.register_object(biport)
        self.biports[node.identifier] = biport
        return biport

    def create_bilink(self, biport_a, biport_b, **kwargs):
        bilink = None
        self.register_object(bilink)
        self.bilinks[(biport_a.identifier, biport_b.identifier)] = bilink
        return bilink

    def nodes(self):
        for node in self.nodes.values():
            yield node

    def biports(self):
        for nodeid, biport in self.ports.items():
            yield (self.nodes[nodeid], biport)

    def bilinks(self):
        for (biport_aid, biport_bid), bilink in self.bilinks.items():
            yield (self.biports[biport_aid], self.biports[biport_bid], bilink)

    def export_nml(self):
        pass

    def export_graphviz(self):
        pass


__all__ = [
    'NMLManager'
]
