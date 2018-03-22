# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2016 Hewlett Packard Enterprise Development LP
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

from logging import getLogger
from os import makedirs, remove
from os.path import dirname, abspath, splitext, isdir
from collections import OrderedDict
from xml.dom import minidom
from xml.etree import ElementTree as etree  # noqa
from subprocess import check_call, Popen, PIPE
from distutils.spawn import find_executable

from six import StringIO, text_type

from .nml import NAMESPACES
from .nml import (
    Node, Port, BidirectionalPort, Link, BidirectionalLink, Environment
)


log = getLogger(__name__)


GRAPHVIZ_TPL = """\
digraph G {{
    // Style
    graph [fontname="Verdana" fontsize=8]
    node [fontname="Verdana" fontsize=7]
    edge [fontname="Verdana" fontsize=7]
    graph [layout=fdp, nodesep=0.05 pad=0.0 margin=0.0 ranksep=0.25]
    node [style=filled shape=box margin=0.05 width=0.25 height=0.25]

    label="{namespace}"

    // Objects
    {objects}

    // Relations
    {relations}
}}
"""


GRAPHVIZ_TPL_EXTENDED = """\
graph G {{
    // Style
    graph [fontname="Verdana" fontsize=8]
    node [fontname="Verdana" fontsize=7]
    edge [fontname="Verdana" fontsize=7]
    graph [nodesep=0.05 pad=0.0 margin=0.0 ranksep=0.25]
    node [style=filled shape=box margin=0.05 width=0.25 height=0.25]

    label="{namespace}"

    // Nodes
    {nodes}

    // Ports
    {ports}

    // Links
    {links}
}}
"""


class NMLManager(object):
    """
    NML namespace manager.

    :param str name: Name of this namespace.
    :var namespace: :py:class:`OrderedDict` with all NML objects registered.
     Use :meth:`register_object` to register new objects.
    :var metadata: Store all kwargs passed to the constructor.
    """

    def __init__(self, name='NML Namespace', **kwargs):
        self.name = name
        self.namespace = OrderedDict()
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

    def get_object(self, identifier):
        """
        Get an object from this namespace by it's unique identifier.

        :param str identifier: Object unique identifier.
        :rtype: NMLObject
        :return: The object with given identifier, or None if not found.
        """
        return self.namespace.get(identifier, None)

    def export_nml(self, pretty=True):
        """
        Export current namespace as a NML XML format.

        :param pretty: Pretty print the output XML.
        :rtype: str
        :return: The current NML namespace in NML XML format.
        """
        root = etree.Element('Namespace')
        for xmlns, uri in NAMESPACES.items():
            root.attrib['xmlns:{}'.format(xmlns)] = uri

        for obj_id, obj in self.namespace.items():
            obj.as_nml(parent=root)

        xml = etree.tostring(root, encoding='utf-8')
        if pretty:
            infile = StringIO(text_type(xml, 'utf-8'))
            doc = minidom.parse(infile)
            xml = doc.toprettyxml(indent='    ', encoding='utf-8')
        return text_type(xml, 'utf-8')

    def save_nml(self, path, pretty=True):
        """
        Write NML XML file of the current namespace.

        To use this function the following must be considered:

        - The output file will be overriden. If case of permissions or IO error
          and exception is raised.
        - If the output parent directories does not exists this function will
          try to create them using py:func:`os.makedirs`.

        :param str path: Path to save the exported XML of the NML namespace.
        :param bool pretty: Pretty print the output XML.
        """
        # Create parent directories
        path = abspath(path)
        parent = dirname(path)
        if not isdir(parent):
            makedirs(parent)

        # Export namespace
        nml_xml = self.export_nml(pretty=True)
        with open(path, 'w') as fd:
            fd.write(nml_xml)

        log.info('Saved graphviz file {}'.format(path))

    def export_graphviz(self):
        """
        Export current namespace as a Graphviz graph.

        :rtype: str
        :return: The current NML namespace in Graphviz graph notation.
        """
        rdr_objects = []
        rdr_relations = []

        # Gather nodes and relations
        for obj_id, obj in self.namespace.items():
            rdr_objects.append('{} [label="{}"]'.format(obj_id, obj.name))

            for relation_name, related_objs in obj.relations.items():

                # Handle iteration over dictionaries and tuples
                collection = related_objs()
                if hasattr(collection, 'values'):
                    collection = collection.values()

                for related_obj in collection:

                    # Ignore non-setup relations
                    if related_obj is None:
                        continue

                    rdr_relations.append(
                        '{} -> {} [label="{}"]'.format(
                            obj_id, related_obj.identifier, relation_name
                        )
                    )

        # Render template
        graph = GRAPHVIZ_TPL.format(
            namespace=self.name,
            objects='\n    '.join(rdr_objects),
            relations='\n    '.join(rdr_relations)
        )
        return graph

    def save_graphviz(self, path, keep_gv=False):
        """
        Plot this namespace using Graphviz.

        To use this function the following must be considered:

        - The path must be a path to a filename in the format expected, for
          example, if a `.svg` file is expected the `path` must end with a
          `.svg`. If no format is provided an exception is raised.
        - The output file will be overriden. If case of permissions or IO error
          and exception is raised.
        - This function will call the `dot` binary by itself if found
          (using py:func:`distutils.spawn.find_executable`); if not, an
          exception is raised.
        - If the output parent directories does not exists this function will
          try to create them using py:func:`os.makedirs`.

        :param str path: Path to save the rendered graphviz file.
        :param bool keep_gv: Keep the `.gv` file with the source of the graph.
         This file will live in the same directory of the output file with the
         same name but with the `.gv`.
        :rtype: str o None
        :return: Path to `.gv` file is `keep_gv` is True, else `None`.
        """
        # Find dot executable
        dot_exec = find_executable('dot')
        if dot_exec is None:
            raise Exception('Missing Graphviz "dot" executable')

        # Create parent directories
        path = abspath(path)
        parent = dirname(path)
        if not isdir(parent):
            makedirs(parent)

        # Determine and cache supported formats
        # dot -T? stderr is in the format:
        #     Format: "?" not recognized. Use one of: canon cmap cmapx [...]
        if not hasattr(self, '_graphviz_formats_cache'):
            self._graphviz_formats_cache = []
            proc = Popen([dot_exec, '-T?'], stdout=PIPE, stderr=PIPE)
            stdout, stderr = proc.communicate()
            self._graphviz_formats_cache = \
                sorted(text_type(stderr).strip().split(':')[-1].split())

        # Determine plot format
        root, ext = splitext(path)
        format = ext[1:] if ext else ''
        if format not in self._graphviz_formats_cache:
            raise Exception(
                'Unsupported format "{}". '
                'Supported formats are: {}'.format(
                    format, ', '.join(self._graphviz_formats_cache)
                )
            )

        # Export namespace
        graph = self.export_graphviz()
        source = root + '.gv'
        with open(source, 'w') as fd:
            fd.write(graph)

        # Plot graph
        check_call([
            dot_exec, '-T{}'.format(format), source, '-o', path
        ])

        log.info('Saved graphviz file {}'.format(source))

        if keep_gv:
            return source

        remove(source)
        return None


class ExtendedNMLManager(NMLManager):
    """
    Extended NMLManager object.

    This object provides a additional helper interface that allow to easily
    create common objects in a topology, their relations and iterate over them.
    In particular, this object does the following assumptions that are not part
    of the NML specification:

    - A :class:`pynml.nml.BidirectionalPort` is related to a single
      :class:`pynml.nml.Node`.
    - A :class:`pynml.nml.BidirectionalLink` is related to a single
      :class:`pynml.nml.BidirectionalPort`.

    If the above assumptions aren't true for your topologies please use the
    standard :class:`NMLManager` or implement your own subclass.

    The original proposed name for this class was
    ``NMLManagerWithCommonHelpersThatMakeSeveralAssumptions``, but it was too
    long.
    """

    def __init__(self, **kwargs):
        super(ExtendedNMLManager, self).__init__(**kwargs)
        self._environment = None
        self._nodes = OrderedDict()
        self._biport_node_map = OrderedDict()
        self._bilink_biport_map = OrderedDict()

    def create_environment(self, **kwargs):
        """
        Helper to create and register a :class:`pynml.nml.Environment`.

        All keyword arguments are passed as is to the
        :class:`pynml.nml.Environment` constructor.

        :rtype: :class:`pynml.nml.Environment`
        :return: A new :class:`pynml.nml.Environment` already registered into
         the namespace.
        """
        kwargs['identifier'] = 'env'
        environment = Environment(**kwargs)
        self.register_object(environment)
        self.environment = environment
        return environment

    @property
    def environment(self):
        """
        Returns the environment :class: pynml.nml.Environment
        """
        return self._environment

    def create_node(self, **kwargs):
        """
        Helper to create and register a :class:`pynml.nml.Node`.

        All keyword arguments are passed as is to the :class:`pynml.nml.Node`
        constructor.

        :rtype: :class:`pynml.nml.Node`
        :return: A new :class:`pynml.nml.Node` already registered into the
         namespace.
        """
        node = Node(**kwargs)
        self.register_object(node)
        self._nodes[node.identifier] = node
        return node

    def create_biport(self, node, **kwargs):
        """
        Helper to create and register a :class:`pynml.nml.BidirectionalPort`.

        All keyword arguments are passed as is to the
        :class:`pynml.nml.BidirectionalPort` constructor. This helper also
        creates all intermediate directed inbound and outbound subports and
        relates them to the node. The `node` argument is related to those
        subports too.

        :rtype: :class:`pynml.nml.BidirectionalPort`
        :return: A new :class:`pynml.nml.BidirectionalPort` already registered
         into the namespace and with subports already related.
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

        self._biport_node_map[biport.identifier] = node
        return biport

    def create_bilink(self, biport_a, biport_b, **kwargs):
        """
        Helper to create and register a :class:`pynml.nml.BidirectionalLink`.

        All keyword arguments are passed as is to the
        :class:`pynml.nml.BidirectionalLink` constructor. This helper also
        creates all intermediate directed sink and source sublinks and relates
        them to the inbound and outbound subports.

        :rtype: :class:`pynml.nml.BidirectionalLink`
        :return: A new :class:`pynml.nml.BidirectionalLink` already registered
         into the namespace and with sublinks already related.
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

        self._bilink_biport_map[bilink.identifier] = (biport_a, biport_b)
        return bilink

    def nodes(self):
        """
        Iterate over all registered :class:`pynml.nml.Node` s in the namespace.

        This iterates the nodes in the order as they were added into the
        namespace.

        :return: An iterator to all nodes in the namespace.
        """
        for node in self._nodes.values():
            yield node

    def biports(self):
        """
        Iterate over all registered :class:`pynml.nml.BidirectionalPort` s in
        the namespace.

        This iterates the biports in the order as they were added into the
        namespace.

        :return: An iterator to all biports in the namespace. The iterator is
         a tuple
         (:class:`pynml.nml.Node`, :class:`pynml.nml.BidirectionalPort`).
        """
        for biport_id, node in self._biport_node_map.items():
            yield (node, self.namespace[biport_id])

    def bilinks(self):
        """
        Iterate over all registered :class:`pynml.nml.BidirectionalLink` s in
        the namespace.

        This iterates the bilinks in the order as they were added into the
        namespace.

        :return: An iterator to all bilinks in the namespace. The iterator is
         a tuple of the form:
         ((:class:`pynml.nml.Node` A, :class:`pynml.nml.BidirectionalPort` A),
         (:class:`pynml.nml.Node` B, :class:`pynml.nml.BidirectionalPort` B),
         :class:`pynml.nml.BidirectionalLink`).
        """
        for bilink_id, (biport_a, biport_b) in self._bilink_biport_map.items():
            node_a = self._biport_node_map[biport_a.identifier]
            node_b = self._biport_node_map[biport_b.identifier]
            yield (
                (node_a, biport_a),
                (node_b, biport_b),
                self.namespace[bilink_id]
            )

    def export_graphviz(self):
        """
        Graphiz export override. See :meth:`NMLManager.export_graphviz`.
        """
        # Get and index of all nodes
        nodes_idx = list(self._nodes.values())

        # Get an index of all biports
        biports_per_node = OrderedDict()
        for node, biport in self.biports():
            if node.identifier not in biports_per_node:
                biports_per_node[node.identifier] = []
            biports_per_node[node.identifier].append(biport)

        # Render
        rdr_nodes = []
        rdr_ports = []
        rdr_links = []

        # Render nodes and ports
        for node_idx, node in enumerate(nodes_idx, 1):

            # Render node
            rdr_nodes.append('subgraph clusterNode{} {{'.format(node_idx))
            rdr_nodes.append('    label="{}"'.format(node.name))

            # Render ports
            if node.identifier in biports_per_node:
                for port_idx, port in enumerate(
                        biports_per_node[node.identifier], 1):
                    rdr_nodes.append(
                        '    n{}p{}'.format(node_idx, port_idx)
                    )
                    rdr_ports.append(
                        'n{0}p{1} [label="p{1}"]'.format(
                            node_idx, port_idx
                        )
                    )

            rdr_nodes.append('}')
            rdr_nodes.append('')

        # Render links
        for (node_a, biport_a), (node_b, biport_b), bilink in self.bilinks():
            rdr_links.append(
                'n{}p{} -- n{}p{}'.format(
                    nodes_idx.index(node_a) + 1,
                    biports_per_node[node_a.identifier].index(biport_a) + 1,
                    nodes_idx.index(node_b) + 1,
                    biports_per_node[node_b.identifier].index(biport_b) + 1,
                )
            )

        # Render template
        graph = GRAPHVIZ_TPL_EXTENDED.format(
            namespace=self.name,
            nodes='\n    '.join(rdr_nodes),
            ports='\n    '.join(rdr_ports),
            links='\n    '.join(rdr_links)
        )
        return graph


__all__ = [
    'NMLManager',
    'ExtendedNMLManager'
]
