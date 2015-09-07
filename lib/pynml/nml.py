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
    """
    Abstract class abstract class for most other classes.

    This class cannot be instantiated directly.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, **kwargs):
        self.exists_during_lifetimes = []
        self.is_alias_network_objects = []
        self.located_at_location = None
        self._id = None
        self._name = None
        self._version = None
        self._kwargs = kwargs

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        if is_valid_uri(id, require_scheme=True):
            self._id = id
        else:
            raise IdError()

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, version):
        self._version = version

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
        if self._id:
            this.attrib['id'] = self._id
        if self._name:
            this.attrib['name'] = self._name
        if self._version:
            this.attrib['version'] = self._version

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
    """
    This class represents a device in a network topology.

    Any device can be represented by this class. Take into consideration that
    a Node instance does not necesarily represents a physical device.
    """
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
    """
    A Port object allows a Network Object to connect to the rest of a network.

    Ports connect to other ports by using Link objects. A Port object does not
    necesarily represents a physical interface.
    """

    def __init__(self, **kwargs):
        super(Port, self).__init__(kwargs)
        self.has_label_label = None
        self.has_service_services = []
        self.is_sink_links = []
        self.is_source_links = []
        self._encoding = None

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

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

        if self._encoding:
            this.attrib['encoding'] = self._encoding

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
    """
    A Link object defines unidirectional communication.

    It communicates source objects to sink ones. A Link object can represent
    any connection between individual or grouped sources and sinks.
    """
    def __init__(self, **kwargs):
        super(Link, self).__init__(kwargs)
        self.has_label_labels = None
        self.is_serial_compound_link_links = []
        self._encoding = None
        self._no_return_traffic = False

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    @property
    def no_return_traffic(self):
        return self._no_return_traffic

    @no_return_traffic.setter
    def no_return_traffic(self, no_return_traffic):
        self._no_return_traffic = no_return_traffic

    def has_label(self, label):
        self.has_label_label = label

    def is_serial_compound_link(self, ordered_links):
        self.is_serial_compound_link_links = ordered_links

    def getNML(self, parent=None):
        this = super(Link, self).getNML(parent)

        if self._encoding:
            this.attrib['encoding'] = self._encoding

        if self._no_return_traffic:
            this.attrib['no_return_traffic'] = str(self._no_return_traffic)

        return this


class Service(NetworkObject):
    """
    Abstract class that defines an ability of a network.

    Service inherits from Network Object.
    This class cannot be instantiated directly.
    """
    __meta_class__ = ABCMeta


class SwitchingService(Service):
    """
    This class describes the ability to create new Links between its Ports.

    These Links can connect inbound ports to outbound ones.
    """

    def __init__(self, **kwargs):
        super(SwitchingService, self).__init__(kwargs)
        self.has_inbound_port_ports = []
        self.has_outbound_port_ports = []
        self.provides_link_links = []
        self._encoding = None
        self._label_swapping = False

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    @property
    def label_swapping(self):
        return self._label_swapping

    @label_swapping.setter
    def label_swapping(self, label_swapping):
        self._label_swapping = label_swapping

    def has_inbound_port(self, port):
        self.has_inbound_port_ports.append(port)

    def has_outbound_port(self, port):
        self.has_outbound_port_ports.append(port)

    def provides_link(self, link):
        self.provides_link_links.append(link)

    def getNML(self, parent=None):
        this = super(SwitchingService, self).getNML(parent)

        if self._encoding:
            this.attrib['encoding'] = self._encoding

        if self._label_swapping:
            this.attrib['label_swapping'] = str(self._label_swapping)

        for port in self.has_inbound_port_ports:
            port.getNML(this)

        for port in self.has_outbound_port_ports:
            port.getNML(this)

        for link in self.provides_link_links:
            link.getNML(this)

        return this


class AdaptationService(Service):
    """
    This class describes the ability to embed data from one port into another.

    Commonly referred to adding data from the higher layer into the lower one.
    A multiplexing adaptation function is defined, so different channels can
    be embedded in a sinle data stream.
    """
    def __init__(self, **kwargs):
        super(AdaptationService, self).__init__(kwargs)
        self.adaptation_function = None
        self.can_provide_port_ports = []
        self.provides_port_ports = []

    @property
    def adaptation_function(self):
        return self._adaptation_function

    @adaptation_function.setter
    def adaptation_function(self, adaptation_function):
        self._adaptation_function = adaptation_function

    def can_provide_port(self, port):
        if port.__class__.__name__ not in ['Port', 'PortGroup']:
            raise CanProvidePortError()
        self.can_provide_port_ports.append(port)

    def provides_port(self, port):
        self.provides_port.append(port)

    def getNML(self, parent=None):
        this = super(AdaptationService, self).getNML(parent)

        if self._adaptation_function:
            this.attrib['adaptation_function'] = self._adaptation_function

        for port in self.can_provide_port_ports:
            port.getNML(this)

        for port in self.provides_port_ports:
            port.getNML(this)

        return this


class DeadaptationService(Service):
    """
    Inverse of the AdaptationService class.

    This class describes the ability to extract data of one port from the
    encoding of another.
    A demultiplexing adaptation function is defined, so different channels can
    be extracted from a single data stream.
    """
    def __init__(self, **kwargs):
        super(DeadaptationService, self).__init__(kwargs)
        self.adaptation_function = None
        self.can_provide_port_ports = []
        self.provides_port_ports = []

    @property
    def adaptation_function(self):
        return self._adaptation_function

    @adaptation_function.setter
    def adaptation_function(self, adaptation_function):
        self._adaptation_function = adaptation_function

    def can_provide_port(self, port):
        self.can_provide_port_ports.append(port)

    def provides_port(self, port):
        self.provides_port.append(port)

    def getNML(self, parent=None):
        this = super(DeadaptationService, self).getNML(parent)

        if self._adaptation_function:
            this.attrib['adaptation_function'] = self._adaptation_function

        for port in self.can_provide_port_ports:
            port.getNML(this)

        for port in self.provides_port_ports:
            port.getNML(this)

        return this


class Group(NetworkObject):
    """
    Abstract class that describes a collection of objects.

    Groups inherits from Network Object.
    Groups can be part of other groups and an object can be part of several
    different groups.
    """
    __meta_class__ = ABCMeta


class Topology(Group):
    """
    A set of connected Network Objects.

    Connected means that the objects in the Topology object can communicate
    between them or means for their communication can be created.
    """
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
    """An unordered set of Ports."""

    def __init__(self, **kwargs):
        super(PortGroup, self).__init__(kwargs)
        self.has_label_group_group = None
        self.has_port_ports = []
        self.is_sink_link_groups = []
        self.is_source_link_groups = []
        self._encoding = None

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    def has_label_group(self, label_group):
        self.has_label_group_group = label_group

    def has_port(self, port):
        self.has_port_ports.append(port)

    def is_sink(self, link_group):
        self.is_sink_link_groups.append(link_group)

    def is_source(self, link_group):
        self.is_source_link_groups.append(link_group)


class LinkGroup(Group):
    """An unordered set of Links"""

    def __init__(self, **kwargs):
        super(LinkGroup, self).__init__(kwargs)
        self.has_label_group_group = None
        self.has_link_links = []
        self.is_serial_compound_link_link_groups = []
        self._encoding = None

    def has_label_group(self, label_group):
        self.has_label_group_group = label_group

    def has_link(self, link):
        self.has_link_links.append(link)

    def is_serial_compound_link(self, link_group):
        self.is_serial_compound_link_link_groups.append(link_group)


class BidirectionalPort(Group):
    """
    A pair of unidirectional Ports.

    A BidirectionalPort object represents a bidirectional physical or virtual
    port.
    """

    def __init__(self, **kwargs):
        super(BidirectionalPort, self).__init__(kwargs)
        self.has_port_ports = []
        self._encoding = None

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    def has_port(self, port0, port1):
        self.has_port_ports.append(port0)
        self.has_port_ports.append(port1)


class BidirectionalLink(Group):
    """
    A pair of unidirectional Links.

    A BidirectionalLink object form a bidirectional physical or virtual link.
    """
    def __init__(self, **kwargs):
        super(BidirectionalLink, self).__init__()
        self.has_link_links = []
        self._encoding = None

    @property
    def encoding(self):
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        self._encoding = encoding

    def has_link(self, link0, link1):
        self.has_link_links.append(link0)
        self.has_link_links.append(link1)


class Location(object):
    """
    A reference to a geographical location.

    A Location object describes where a NetworkObject is.
    """
    def __init__(self, **kwargs):
        self._id = None
        self._name = None
        self._long = None
        self._lat = None
        self._alt = None
        self._unlocode = None
        self._address = None
        self._kwargs = kwargs

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id):
        self._id = id

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def long(self):
        return self._long

    @long.setter
    def long(self, long):
        self._long = long

    @property
    def lat(self):
        return self._lat

    @lat.setter
    def lat(self, lat):
        self._lat = lat

    @property
    def alt(self):
        return self._alt

    @alt.setter
    def alt(self, alt):
        self._alt = alt

    @property
    def unlocode(self):
        return self._unlocode

    @unlocode.setter
    def unlocode(self, unlocode):
        self._unlocode = unlocode

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, address):
        self._address = address

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
        if self._alt:
            this.attrib['alt'] = self.alt
        if self.unlocode:
            this.attrib['unlocode'] = self.unlocode
        if self._address:
            this.attrib['address'] = self.address

        return this


class Lifetime(object):
    """
    A time interval where a NetworkObject is active.

    If an object has several Lifetimes associated with it, then its lifetime is
    the union of all its Lifetimes time intervals.
    """
    def __init__(self, **kwargs):
        self._start = None
        self._end = None
        self._kwargs = kwargs

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        self._end = end

    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(self.__class__.__name__)
        else:
            this = etree.SubElement(parent, self.__class__.__name__)
        if self.start:
            this.attrib['start'] = self._start
        if self.end:
            this.attrib['end'] = self._end

        return this


class Label(object):
    """
    A value that describes a single data stream embedded in a larger one.

    A Label can have one value for labeling its single data stream.
    A VLAN number can be represented using a Label object, for example.
    """
    def __init__(self, **kwargs):
        self._labeltype = None
        self._value = None
        self._kwargs = kwargs

    @property
    def labeltype(self):
        return self._labeltype

    @labeltype.setter
    def labeltype(self, labeltype):
        self._labeltype = labeltype

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def getNML(self, parent=None):
        if parent is None:
            this = etree.Element(self.__class__.__name__)
        else:
            this = etree.SubElement(parent, self.__class__.__name__)
        if self.labeltype:
            this.attrib['labeltype'] = self._labeltype
        if self.value:
            this.attrib['value'] = self._value

        return this


class LabelGroup(object):
    """An unordered set of Labels."""
    def __init__(self, **kwargs):
        self._labeltype = ''
        self._values = ''
        self._kwargs = kwargs


class OrderedList(object):
    """An ordered list of NetworkObjects."""
    def __init__(self, **kwargs):
        self._kwargs = kwargs


class ListItem(object):
    """
    A syntactical construct which may be used to create Ordered Lists.

    Its exact usage depends of the specific syntax.
    """
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
