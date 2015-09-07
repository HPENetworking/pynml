# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Hewlett Packard Enterprise Development LP
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
pynml main module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree as etree  # noqa

from rfc3986 import is_valid_uri

from .exceptions import (
    IdError, ExistsDuringError, IsAliasError, CanProvidePortError
)


NAMESPACES = {'nml': 'http://schemas.ogf.org/nml/2013/05/base'}


class NetworkObject(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, **kwargs):
        self.exists_during_lifetimes = []
        self.is_alias_network_objects = []
        self.located_at_location = None
        self.__id = None
        self.__name = None
        self.__version = None
        self._kwargs = kwargs

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        if is_valid_uri(id, require_scheme=True):
            self.__id = id
        else:
            raise IdError()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def version(self):
        return self.__version

    @version.setter
    def version(self, version):
        self.__version = version

    def exists_during(self, lifetime):
        if lifetime.__class__.__name__ != 'Lifetime':
            raise ExistsDuringError()

        self.exists_during_lifetimes.append(lifetime)

    def is_alias(self, network_object):
        if self.__class__.__name__ != network_object.__class__.__name__:
            raise IsAliasError()
        self.is_alias_network_objects.append(network_object)

    def locatedAt(self, location):
        self.located_at_location = location

    @abstractmethod
    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(
                self.__class__.__name__, nsmap=NAMESPACES
            )
        else:
            this = etree.SubElement(
                parent, self.__class__.__name__, nsmap=NAMESPACES
            )
        if self.__id:
            this.attrib['id'] = self.__id
        if self.__name:
            this.attrib['name'] = self.__name
        if self.__version:
            this.attrib['version'] = self.__version

        for network_object in self.is_alias_network_objects:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isAlias'
            network_object.getNML(relation)

        for lifetime in self.exists_during_lifetimes:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'existsDuring'
            lifetime.getNML(relation)

        if self.located_at_location:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'locatedAt'
            self.located_at_location.getNML(relation)

        return this


class Node(NetworkObject):

    def __init__(self, **kwargs):
        super(Node, self).__init__(kwargs)
        self.has_inbound_port_ports = []
        self.has_outbound_port_ports = []
        self.has_service_services = []
        self.implemented_by_nodes = []

    def has_inbound_port(self, port):
        self.has_inbound_port_ports.append(port)

    def has_outbound_port(self, port):
        self.has_outbound_port_ports.append(port)

    def has_service(self, service):
        self.has_service_services.append(service)

    def implementedBy(self, node):
        self.implemented_by_nodes.append(node)

    def getNML(self, parent=None):
        this = super(Node, self).getNML(parent)

        for port in self.has_inbound_port_ports:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasInboundPort'
            port.getNML(relation)

        for port in self.has_outbound_port_ports:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasOutoundPort'
            port.getNML(relation)

        for service in self.has_service_services:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for node in self.implemented_by_nodes:
            node.getNML(this)

        return this


class Port(NetworkObject):

    def __init__(self, **kwargs):
        super(Port, self).__init__(kwargs)
        self.has_label_label = None
        self.has_service_services = []
        self.is_sink_links = []
        self.is_source_links = []
        self.__encoding = None

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def has_label(self, label):
        self.has_label_label = label

    def has_service(self, service):
        self.has_service_services.append(service)

    def is_sink(self, link):
        self.is_sink_links.append(link)

    def is_source(self, link):
        self.is_source_links.append(link)

    def getNML(self, parent=None):
        this = super(Port, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.has_label_label:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasLabel'
            self.has_label_label.getNML(relation)

        for service in self.has_service_services:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for link in self.is_sink_links:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isSink'
            link.getNML(relation)

        for link in self.is_source_links:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isSource'
            link.getNML(relation)

        return this


class Link(NetworkObject):

    def __init__(self, **kwargs):
        super(Link, self).__init__(kwargs)
        self.has_label_labels = None
        self.is_serial_compound_link_links = []
        self.__encoding = None
        self.__no_return_traffic = False

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def no_return_traffic(self):
        return self.__no_return_traffic

    @no_return_traffic.setter
    def no_return_traffic(self, no_return_traffic):
        self.__no_return_traffic = no_return_traffic

    def has_label(self, label):
        self.has_label_label = label

    def is_serial_compound_link(self, ordered_links):
        self.is_serial_compound_link_links = ordered_links

    def getNML(self, parent=None):
        this = super(Link, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.__no_return_traffic:
            this.attrib['no_return_traffic'] = str(self.__no_return_traffic)

        return this


class Service(NetworkObject):
    __meta_class__ = ABCMeta


class SwitchingService(Service):

    def __init__(self, **kwargs):
        super(SwitchingService, self).__init__(kwargs)
        self.has_inbound_port_ports = []
        self.has_outbound_port_ports = []
        self.provides_link_links = []
        self.__encoding = None
        self.__label_swapping = False

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def label_swapping(self):
        return self.__label_swapping

    @label_swapping.setter
    def label_swapping(self, label_swapping):
        self.__label_swapping = label_swapping

    def has_inbound_port(self, port):
        self.has_inbound_port_ports.append(port)

    def has_outbound_port(self, port):
        self.has_outbound_port_ports.append(port)

    def provides_link(self, link):
        self.provides_link_links.append(link)

    def getNML(self, parent=None):
        this = super(SwitchingService, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.__label_swapping:
            this.attrib['label_swapping'] = str(self.__label_swapping)

        for port in self.has_inbound_port_ports:
            port.getNML(this)

        for port in self.has_outbound_port_ports:
            port.getNML(this)

        for link in self.provides_link_links:
            link.getNML(this)

        return this


class AdaptationService(Service):

    def __init__(self, **kwargs):
        super(AdaptationService, self).__init__(kwargs)
        self.adaptation_function = None
        self.can_provide_port_ports = []
        self.provides_port_ports = []

    @property
    def adaptation_function(self):
        return self.__adaptation_function

    @adaptation_function.setter
    def adaptation_function(self, adaptation_function):
        self.__adaptation_function = adaptation_function

    def can_provide_port(self, port):
        if port.__class__.__name__ not in ['Port', 'PortGroup']:
            raise CanProvidePortError()
        self.can_provide_port_ports.append(port)

    def provides_port(self, port):
        self.provides_port.append(port)

    def getNML(self, parent=None):
        this = super(AdaptationService, self).getNML(parent)

        if self.__adaptation_function:
            this.attrib['adaptation_function'] = self.__adaptation_function

        for port in self.can_provide_port_ports:
            port.getNML(this)

        for port in self.provides_port_ports:
            port.getNML(this)

        return this


class DeadaptationService(Service):

    def __init__(self, **kwargs):
        super(DeadaptationService, self).__init__(kwargs)
        self.adaptation_function = None
        self.can_provide_port_ports = []
        self.provides_port_ports = []

    @property
    def adaptation_function(self):
        return self.__adaptation_function

    @adaptation_function.setter
    def adaptation_function(self, adaptation_function):
        self.__adaptation_function = adaptation_function

    def can_provide_port(self, port):
        self.can_provide_port_ports.append(port)

    def provides_port(self, port):
        self.provides_port.append(port)

    def getNML(self, parent=None):
        this = super(DeadaptationService, self).getNML(parent)

        if self.__adaptation_function:
            this.attrib['adaptation_function'] = self.__adaptation_function

        for port in self.can_provide_port_ports:
            port.getNML(this)

        for port in self.provides_port_ports:
            port.getNML(this)

        return this


class Group(NetworkObject):
    __meta_class__ = ABCMeta


class Topology(Group):

    def __init__(self, **kwargs):
        super(Topology, self).__init__(kwargs)
        self.has_node_nodes = []
        self.has_inbound_port_ports = []
        self.has_outbound_port_ports = []
        self.has_service_services = []
        self.has_topology_topologies = []

    def has_node(self, node):
        self.has_node_nodes.append(node)

    def has_inbound_port(self, port):
        self.has_inbound_port_ports.append(port)

    def has_outbound_port(self, port):
        self.has_outbound_port_ports.append(port)

    def has_service(self, service):
        self.has_service_services.append(service)

    def has_topology(self, topology):
        self.has_topology_topologies.append(topology)

    def getNML(self, parent=None):
        this = super(Topology, self).getNML(parent)

        for node in self.has_node_nodes:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasNode'
            node.getNML(relation)

        for port in self.has_inbound_port_ports:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasInboundPort'
            port.getNML(relation)

        for port in self.has_outbound_port_ports:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasOutboundPort'
            port.getNML(relation)

        for service in self.has_service_services:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for topology in self.has_topology_topologies:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasTopology'
            topology.getNML(relation)

        return this


class PortGroup(Group):

    def __init__(self, **kwargs):
        super(PortGroup, self).__init__(kwargs)
        self.has_label_group_group = None
        self.has_port_ports = []
        self.is_sink_link_groups = []
        self.is_source_link_groups = []
        self.__encoding = None

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def has_label_group(self, label_group):
        self.has_label_group_group = label_group

    def has_port(self, port):
        self.has_port_ports.append(port)

    def is_sink(self, link_group):
        self.is_sink_link_groups.append(link_group)

    def is_source(self, link_group):
        self.is_source_link_groups.append(link_group)


class LinkGroup(Group):

    def __init__(self, **kwargs):
        super(LinkGroup, self).__init__(kwargs)
        self.has_label_group_group = None
        self.has_link_links = []
        self.is_serial_compound_link_link_groups = []
        self.__encoding = None

    def has_label_group(self, label_group):
        self.has_label_group_group = label_group

    def has_link(self, link):
        self.has_link_links.append(link)

    def is_serial_compound_link(self, link_group):
        self.is_serial_compound_link_link_groups.append(link_group)


class BidirectionalPort(Group):

    def __init__(self, **kwargs):
        super(BidirectionalPort, self).__init__(kwargs)
        self.has_port_ports = []
        self.__encoding = None

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def has_port(self, port0, port1):
        self.has_port_ports.append(port0)
        self.has_port_ports.append(port1)


class BidirectionalLink(Group):

    def __init__(self, **kwargs):
        super(BidirectionalLink, self).__init__()
        self.has_link_links = []
        self.__encoding = None

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def has_link(self, link0, link1):
        self.has_link_links.append(link0)
        self.has_link_links.append(link1)


class Location(object):

    def __init__(self, **kwargs):
        self.__id = None
        self.__name = None
        self.__long = None
        self.__lat = None
        self.__alt = None
        self.__unlocode = None
        self.__address = None
        self._kwargs = kwargs

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, id):
        self.__id = id

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        self.__name = name

    @property
    def long(self):
        return self.__long

    @long.setter
    def long(self, long):
        self.__long = long

    @property
    def lat(self):
        return self.__lat

    @lat.setter
    def lat(self, lat):
        self.__lat = lat

    @property
    def alt(self):
        return self.__alt

    @alt.setter
    def alt(self, alt):
        self.__alt = alt

    @property
    def unlocode(self):
        return self.__unlocode

    @unlocode.setter
    def unlocode(self, unlocode):
        self.__unlocode = unlocode

    @property
    def address(self):
        return self.__address

    @address.setter
    def address(self, address):
        self.__address = address

    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(self.__class__.__name__)
        else:
            this = etree.SubElement(parent, self.__class__.__name__)
        if self.id:
            this.attrib['id'] = self.id
        if self.name:
            this.attrib['name'] = self.name
        if self.long:
            this.attrib['long'] = self.long
        if self.lat:
            this.attrib['lat'] = self.lat
        if self.__alt:
            this.attrib['alt'] = self.alt
        if self.unlocode:
            this.attrib['unlocode'] = self.unlocode
        if self.__address:
            this.attrib['address'] = self.address

        return this


class Lifetime(object):

    def __init__(self, **kwargs):
        self.__start = None
        self.__end = None
        self._kwargs = kwargs

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, start):
        self.__start = start

    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, end):
        self.__end = end

    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(self.__class__.__name__)
        else:
            this = etree.SubElement(parent, self.__class__.__name__)
        if self.start:
            this.attrib['start'] = self.start
        if self.end:
            this.attrib['end'] = self.end

        return this


class Label(object):

    def __init__(self, **kwargs):
        self.__labeltype = None
        self.__value = None
        self._kwargs = kwargs

    @property
    def labeltype(self):
        return self.__labeltype

    @labeltype.setter
    def labeltype(self, labeltype):
        self.__labeltype = labeltype

    @property
    def value(self):
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(self.__class__.__name__)
        else:
            this = etree.SubElement(parent, self.__class__.__name__)
        if self.labeltype:
            this.attrib['labeltype'] = self.labeltype
        if self.value:
            this.attrib['value'] = self.value

        return this


class LabelGroup(object):
    def __init__(self, **kwargs):
        self._labeltype = ''
        self._values = ''
        self._kwargs = kwargs


class OrderedList(object):
    def __init__(self, **kwargs):
        self._kwargs = kwargs


class ListItem(object):
    def __init__(self, **kwargs):
        self._kwargs = kwargs


__all__ = [
    'NetworkObject',
    'Node',
    'Port',
    'Link',
    'Service',
    'SwitchingService',
    'AdaptationService',
    'DeadaptationService',
    'Group',
    'Topology',
    'PortGroup',
    'LinkGroup',
    'BidirectionalPort',
    'BidirectionalLink',
    'Location',
    'Lifetime',
    'Label',
    'LabelGroup',
    'OrderedList',
    'ListItem'
]
