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
    def __init__(self):
        self.existsDuringLifetimes = []
        self.isAliasNetworkObjects = []
        self.locatedAtLocation = None
        self.__id = None
        self.__name = None
        self.__version = None

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

    def existsDuring(self, lifetime):
        if lifetime.__class__.__name__ != 'Lifetime':
            raise ExistsDuringError()

        self.existsDuringLifetimes.append(lifetime)

    def isAlias(self, networkObject):
        if self.__class__.__name__ != networkObject.__class__.__name__:
            raise IsAliasError()
        self.isAliasNetworkObjects.append(networkObject)

    def locatedAt(self, location):
        self.locatedAtLocation = location

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

        for networkObject in self.isAliasNetworkObjects:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isAlias'
            networkObject.getNML(relation)

        for lifetime in self.existsDuringLifetimes:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'existsDuring'
            lifetime.getNML(relation)

        if self.locatedAtLocation:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'locatedAt'
            self.locatedAtLocation.getNML(relation)

        return this


class Node(NetworkObject):

    def __init__(self):
        super(Node, self).__init__()
        self.hasInboundPortPorts = []
        self.hasOutboundPortPorts = []
        self.hasServiceServices = []
        self.implementedByNodes = []

    def hasInboundPort(self, port):
        self.hasInboundPortPorts.append(port)

    def hasOutboundPort(self, port):
        self.hasOutboundPortPorts.append(port)

    def hasService(self, service):
        self.hasServiceServices.append(service)

    def implementedBy(self, node):
        self.implementedByNodes.append(node)

    def getNML(self, parent=None):
        this = super(Node, self).getNML(parent)

        for port in self.hasInboundPortPorts:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasInboundPort'
            port.getNML(relation)

        for port in self.hasOutboundPortPorts:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasOutoundPort'
            port.getNML(relation)

        for service in self.hasServiceServices:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for node in self.implementedByNodes:
            node.getNML(this)

        return this


class Port(NetworkObject):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def __init__(self):
        super(Port, self).__init__()
        self.hasLabelLabel = None
        self.hasServiceServices = []
        self.isSinkLinks = []
        self.isSourceLinks = []
        self.__encoding = None

    def hasLabel(self, label):
        self.hasLabelLabel = label

    def hasService(self, service):
        self.hasServiceServices.append(service)

    def isSink(self, link):
        self.isSinkLinks.append(link)

    def isSource(self, link):
        self.isSourceLinks.append(link)

    def getNML(self, parent=None):
        this = super(Port, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.hasLabelLabel:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasLabel'
            self.hasLabelLabel.getNML(relation)

        for service in self.hasServiceServices:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for link in self.isSinkLinks:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isSink'
            link.getNML(relation)

        for link in self.isSourceLinks:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'isSource'
            link.getNML(relation)

        return this


class Link(NetworkObject):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def noReturnTraffic(self):
        return self.__noReturnTraffic

    @noReturnTraffic.setter
    def noReturnTraffic(self, noReturnTraffic):
        self.__noReturnTraffic = noReturnTraffic

    def __init__(self):
        super(Link, self).__init__()
        self.hasLabelLabels = None
        self.isSerialCompoundLinkLinks = []
        self.__encoding = None
        self.__noReturnTraffic = False

    def hasLabel(self, label):
        self.hasLabelLabel = label

    def isSerialCompoundLink(self, orderedLinks):
        self.isSerialCompoundLinkLinks = orderedLinks

    def getNML(self, parent=None):
        this = super(Link, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.__noReturnTraffic:
            this.attrib['noReturnTraffic'] = str(self.__noReturnTraffic)

        return this


class Service(NetworkObject):
    __metaClass__ = ABCMeta


class SwitchingService(Service):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    @property
    def labelSwapping(self):
        return self.__labelSwapping

    @labelSwapping.setter
    def labelSwapping(self, labelSwapping):
        self.__labelSwapping = labelSwapping

    def __init__(self):
        super(SwitchingService, self).__init__()
        self.hasInboundPortPorts = []
        self.hasOutboundPortPorts = []
        self.providesLinkLinks = []
        self.__encoding = None
        self.__labelSwapping = False

    def hasInboundPort(self, port):
        self.hasInboundPortPorts.append(port)

    def hasOutboundPort(self, port):
        self.hasOutboundPortPorts.append(port)

    def providesLink(self, link):
        self.providesLinkLinks.append(link)

    def getNML(self, parent=None):
        this = super(SwitchingService, self).getNML(parent)

        if self.__encoding:
            this.attrib['encoding'] = self.__encoding

        if self.__labelSwapping:
            this.attrib['labelSwapping'] = str(self.__labelSwapping)

        for port in self.hasInboundPortPorts:
            port.getNML(this)

        for port in self.hasOutboundPortPorts:
            port.getNML(this)

        for link in self.providesLinkLinks:
            link.getNML(this)

        return this


class AdaptationService(Service):

    @property
    def adaptationFunction(self):
        return self.__adaptationFunction

    @adaptationFunction.setter
    def adaptationFunction(self, adaptationFunction):
        self.__adaptationFunction = adaptationFunction

    def __init__(self):
        super(AdaptationService, self).__init__()
        self.adaptationFunction = None
        self.canProvidePortPorts = []
        self.providesPortPorts = []

    def canProvidePort(self, port):
        if port.__class__.__name__ not in ['Port', 'PortGroup']:
            raise CanProvidePortError()
        self.canProvidePortPorts.append(port)

    def providesPort(self, port):
        self.providesPort.append(port)

    def getNML(self, parent=None):
        this = super(AdaptationService, self).getNML(parent)

        if self.__adaptationFunction:
            this.attrib['adaptationFunction'] = self.__adaptationFunction

        for port in self.canProvidePortPorts:
            port.getNML(this)

        for port in self.providesPortPorts:
            port.getNML(this)

        return this


class DeadaptationService(Service):

    @property
    def adaptationFunction(self):
        return self.__adaptationFunction

    @adaptationFunction.setter
    def adaptationFunction(self, adaptationFunction):
        self.__adaptationFunction = adaptationFunction

    def __init__(self):
        super(DeadaptationService, self).__init__()
        self.adaptationFunction = None
        self.canProvidePortPorts = []
        self.providesPortPorts = []

    def canProvidePort(self, port):
        self.canProvidePortPorts.append(port)

    def providesPort(self, port):
        self.providesPort.append(port)

    def getNML(self, parent=None):
        this = super(DeadaptationService, self).getNML(parent)

        if self.__adaptationFunction:
            this.attrib['adaptationFunction'] = self.__adaptationFunction

        for port in self.canProvidePortPorts:
            port.getNML(this)

        for port in self.providesPortPorts:
            port.getNML(this)

        return this


class Group(NetworkObject):
    __metaClass__ = ABCMeta


class Topology(Group):

    def __init__(self):
        super(Topology, self).__init__()
        self.hasNodeNodes = []
        self.hasInboundPortPorts = []
        self.hasOutboundPortPorts = []
        self.hasServiceServices = []
        self.hasTopologyTopologies = []

    def hasNode(self, node):
        self.hasNodeNodes.append(node)

    def hasInboundPort(self, port):
        self.hasInboundPortPorts.append(port)

    def hasOutboundPort(self, port):
        self.hasOutboundPortPorts.append(port)

    def hasService(self, service):
        self.hasServiceServices.append(service)

    def hasTopology(self, topology):
        self.hasTopologyTopologies.append(topology)

    def getNML(self, parent=None):
        this = super(Topology, self).getNML(parent)

        for node in self.hasNodeNodes:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasNode'
            node.getNML(relation)

        for port in self.hasInboundPortPorts:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasInboundPort'
            port.getNML(relation)

        for port in self.hasOutboundPortPorts:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasOutboundPort'
            port.getNML(relation)

        for service in self.hasServiceServices:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasService'
            service.getNML(relation)

        for topology in self.hasTopologyTopologies:
            relation = etree.SubElement(this, 'Relation')
            relation.attrib['type'] = 'hasTopology'
            topology.getNML(relation)

        return this


class PortGroup(Group):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def __init__(self):
        super(PortGroup, self).__init__()
        self.hasLabelGroupGroup = None
        self.hasPortPorts = []
        self.isSinkLinkGroups = []
        self.isSourceLinkGroups = []
        self.__encoding = None

    def hasLabelGroup(self, labelGroup):
        self.hasLabelGroupGroup = labelGroup

    def hasPort(self, port):
        self.hasPortPorts.append(port)

    def isSink(self, linkGroup):
        self.isSinkLinkGroups.append(linkGroup)

    def isSource(self, linkGroup):
        self.isSourceLinkGroups.append(linkGroup)


class LinkGroup(Group):

    def __init__(self):
        super(LinkGroup, self).__init__()
        self.hasLabelGroupGroup = None
        self.hasLinkLinks = []
        self.isSerialCompoundLinkLinkGroups = []
        self.__encoding = None

    def hasLabelGroup(self, labelGroup):
        self.hasLabelGroupGroup = labelGroup

    def hasLink(self, link):
        self.hasLinkLinks.append(link)

    def isSerialCompoundLink(self, linkGroup):
        self.isSerialCompoundLinkLinkGroups.append(linkGroup)


class BidirectionalPort(Group):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def __init__(self):
        super(BidirectionalPort, self).__init__()
        self.hasPortPorts = []
        self.__encoding = None

    def hasPort(self, port0, port1):
        self.hasPortPorts.append(port0)
        self.hasPortPorts.append(port1)


class BidirectionalLink(Group):

    @property
    def encoding(self):
        return self.__encoding

    @encoding.setter
    def encoding(self, encoding):
        self.__encoding = encoding

    def __init__(self):
        super(BidirectionalLink, self).__init__()
        self.hasLinkLinks = []
        self.__encoding = None

    def hasLink(self, link0, link1):
        self.hasLinkLinks.append(link0)
        self.hasLinkLinks.append(link1)


class Location(object):

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

    def __init__(self):
        self.__id = None
        self.__name = None
        self.__long = None
        self.__lat = None
        self.__alt = None
        self.__unlocode = None
        self.__address = None

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

    def __init__(self):
        self.__start = None
        self.__end = None

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

    def __init__(self):
        self.__labeltype = None
        self.__value = None

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
    labeltype = ''
    values = ''


class OrderedList(object):
    pass


class ListItem(object):
    pass


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
