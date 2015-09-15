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

from datetime import datetime
from collections import OrderedDict
from abc import ABCMeta, abstractmethod
from xml.etree import ElementTree as etree  # noqa

from rfc3986 import is_valid_uri

from .exceptions import (
    RelationExistsDuringError,
    RelationIsAliasError,
    RelationLocatedAtError,
    RelationHasInboundPortError,
    RelationHasOutboundPortError,
    RelationHasServiceError,
    RelationImplementedByError,
    RelationHasLabelError,
    RelationIsSinkError,
    RelationIsSourceError,
    RelationProvidesLinkError,
    RelationCanProvidePortError,
    RelationProvidesPortError,
    RelationHasNodeError,
    RelationHasTopologyError,
    RelationHasLabelGroupError,
    RelationHasPortError,
    RelationHasLinkError,
    RelationIsSerialCompoundLinkError,
    AttributeNameError,
    AttributeIdError,
    AttributeEncodingError
)


NAMESPACES = {'nml': 'http://schemas.ogf.org/nml/2013/05/base'}


def tree_element(self, this, parent):
    """
    Helper function to identify an XML node to modify in a inheritance and
    multi-node tree.
    """
    if this is None:
        if parent is None:
            this = etree.Element(
                self.__class__.__name__, nsmap=NAMESPACES
            )
        else:
            this = etree.SubElement(
                parent, self.__class__.__name__, nsmap=NAMESPACES
            )
    return this


class NetworkObject(object):
    """
    The basic class from other instances inherit from.

    No NetworkObject instances can be created because this class is abstract.

    :param str name: Human readable string name.
    :param str identifier: Persistent globally unique URI.
    :param str version: Time stamp formatted as ISO 8601.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self, name=None, identifier=None, version=None, **kwargs):
        # Attributes
        if name is None:
            name = '{}<{}>'.format(
                self.__class__.__name__, str(id(self))
            )
        self.name = name

        if identifier is None:
            identifier = str(id(self))
        self.identifier = identifier

        if version is None:
            version = datetime.now().replace(microsecond=0).isoformat()
        self.version = version

        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._is_alias_network_objects = OrderedDict()
        self._located_at_locations = (None, )

        self.metadata = kwargs

    @property
    def name(self):
        """
        Get attribute name.

        :return: Human readable string name.
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """
        Set attribute name.

        :param str name: Human readable string name.
        """
        if not name:
            raise AttributeNameError()
        self._name = name

    @property
    def identifier(self):
        """
        Get attribute identifier.

        :return: Persistent globally unique URI.
        :rtype: str
        """
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        """
        Set attribute identifier.

        :param str identifier: Persistent globally unique URI.
        """
        if not is_valid_uri(identifier):
            raise AttributeIdError()
        self._identifier = identifier

    @property
    def version(self):
        """
        Get attribute version.

        :return: Time stamp formatted as ISO 8601.
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """
        Set attribute version.

        :param str version: Time stamp formatted as ISO 8601.
        """
        self._version = version

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def is_alias(self, network_object):
        """
        Check `isAlias` relation with given `network_object` object.

        FIXME: Document isAlias relation..

        :param network_object: Object to validate relation `isAlias` with.
        :type network_object: NetworkObject
        :return: True if `network_object` is related to `self` with `isAlias`.
        :rtype: bool
        """
        if network_object.__class__ not in (
                NetworkObject, ):
            raise RelationIsAliasError()

        return network_object.identifier in \
            self._is_alias_network_objects

    def add_is_alias(self, network_object):
        """
        Add given `network_object` to this object `isAlias` relations.

        :param network_object: Object to add to the `isAlias` relation.
        :type network_object: NetworkObject
        """
        if network_object.__class__ not in (
                NetworkObject, ):
            raise RelationIsAliasError()

        self._is_alias_network_objects[network_object.identifier] = \
            network_object

    def located_at(self, location):
        """
        Check `locatedAt` relation with given `location` object.

        FIXME: Document locatedAt relation..

        :param location: Object to validate relation `locatedAt` with.
        :type location: Location
        :return: True if `location` is related to `self` with `locatedAt`.
        :rtype: bool
        """
        if location.__class__ not in (
                Location, ):
            raise RelationLocatedAtError()

        return location in \
            self._located_at_locations

    def set_located_at(self, location):
        """
        Set the `locatedAt` relation to given objects.

        :param location: Object to set to the `locatedAt` relation.
        :type location: Location
        """
        arg_tuple = (location, )

        for arg in arg_tuple:
            if arg.__class__ not in (Location, ):
                raise RelationLocatedAtError()

        self._located_at_locations = arg_tuple

    @abstractmethod
    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['name'] = self._name
        this.attrib['id'] = self._identifier
        this.attrib['version'] = self._version

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isAlias'
        for network_object in self._network_objects:
            reference = etree.SubElement(
                relation, network_object.__class__.__name__
            )
            reference.attrib['id'] = network_object.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'locatedAt'
        for location in self._locations:
            reference = etree.SubElement(
                relation, location.__class__.__name__
            )
            reference.attrib['id'] = location.identifier

        return this


class Node(NetworkObject):
    """
    A Node object represents a device in a network.

    Physical or virtual devices can be represented by instances of this class.
    """

    def __init__(
            self, **kwargs):
        super(Node, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._has_inbound_port_ports = OrderedDict()
        self._has_outbound_port_ports = OrderedDict()
        self._has_service_switching_services = OrderedDict()
        self._implemented_by_nodes = OrderedDict()

    def has_inbound_port(self, port):
        """
        Check `hasInboundPort` relation with given `port` object.

        FIXME: Document hasInboundPort relation..

        :param port: Object to validate relation `hasInboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasInboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        return port.identifier in \
            self._has_inbound_port_ports

    def add_has_inbound_port(self, port):
        """
        Add given `port` to this object `hasInboundPort` relations.

        :param port: Object to add to the `hasInboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        self._has_inbound_port_ports[port.identifier] = \
            port

    def has_outbound_port(self, port):
        """
        Check `hasOutboundPort` relation with given `port` object.

        FIXME: Document hasOutboundPort relation..

        :param port: Object to validate relation `hasOutboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasOutboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        return port.identifier in \
            self._has_outbound_port_ports

    def add_has_outbound_port(self, port):
        """
        Add given `port` to this object `hasOutboundPort` relations.

        :param port: Object to add to the `hasOutboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        self._has_outbound_port_ports[port.identifier] = \
            port

    def has_service(self, switching_service):
        """
        Check `hasService` relation with given `switching_service` object.

        FIXME: Document hasService relation..

        :param switching_service: Object to validate relation `hasService`
         with.
        :type switching_service: SwitchingService
        :return: True if `switching_service` is related to `self` with
         `hasService`.
        :rtype: bool
        """
        if switching_service.__class__ not in (
                SwitchingService, ):
            raise RelationHasServiceError()

        return switching_service.identifier in \
            self._has_service_switching_services

    def add_has_service(self, switching_service):
        """
        Add given `switching_service` to this object `hasService` relations.

        :param switching_service: Object to add to the `hasService` relation.
        :type switching_service: SwitchingService
        """
        if switching_service.__class__ not in (
                SwitchingService, ):
            raise RelationHasServiceError()

        self._has_service_switching_services[switching_service.identifier] = \
            switching_service

    def implemented_by(self, node):
        """
        Check `implementedBy` relation with given `node` object.

        FIXME: Document implementedBy relation..

        :param node: Object to validate relation `implementedBy` with.
        :type node: Node
        :return: True if `node` is related to `self` with `implementedBy`.
        :rtype: bool
        """
        if node.__class__ not in (
                Node, ):
            raise RelationImplementedByError()

        return node.identifier in \
            self._implemented_by_nodes

    def add_implemented_by(self, node):
        """
        Add given `node` to this object `implementedBy` relations.

        :param node: Object to add to the `implementedBy` relation.
        :type node: Node
        """
        if node.__class__ not in (
                Node, ):
            raise RelationImplementedByError()

        self._implemented_by_nodes[node.identifier] = \
            node

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`NetworkObject.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasInboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasOutboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasService'
        for switching_service in self._switching_services:
            reference = etree.SubElement(
                relation, switching_service.__class__.__name__
            )
            reference.attrib['id'] = switching_service.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'implementedBy'
        for node in self._nodes:
            reference = etree.SubElement(
                relation, node.__class__.__name__
            )
            reference.attrib['id'] = node.identifier

        # Parent attributes and relations
        super(Node, self).as_nml(this, parent)

        return this


class Port(NetworkObject):
    """
    Endpoint of an unidirectional connection.

    Can represent physical or virtual ports. Needs a proper linking instance to
    connect to other ports.

    :param str encoding: Format of the data streaming through the port as an
     URI.
    """

    def __init__(
            self, encoding=None, **kwargs):
        super(Port, self).__init__(**kwargs)

        # Attributes
        if encoding is None:
            encoding = 'FIXME: Provide default'
        self.encoding = encoding

        # Relations
        self._has_label_labels = (None, )
        self._has_service_adaptation_services = OrderedDict()
        self._is_sink_links = OrderedDict()
        self._is_source_links = OrderedDict()

    @property
    def encoding(self):
        """
        Get attribute encoding.

        :return: Format of the data streaming through the port as an URI.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Set attribute encoding.

        :param str encoding: Format of the data streaming through the port as
         an URI.
        """
        if not is_valid_uri(encoding):
            raise AttributeEncodingError()
        self._encoding = encoding

    def has_label(self, label):
        """
        Check `hasLabel` relation with given `label` object.

        FIXME: Document hasLabel relation..

        :param label: Object to validate relation `hasLabel` with.
        :type label: Label
        :return: True if `label` is related to `self` with `hasLabel`.
        :rtype: bool
        """
        if label.__class__ not in (
                Label, ):
            raise RelationHasLabelError()

        return label in \
            self._has_label_labels

    def set_has_label(self, label):
        """
        Set the `hasLabel` relation to given objects.

        :param label: Object to set to the `hasLabel` relation.
        :type label: Label
        """
        arg_tuple = (label, )

        for arg in arg_tuple:
            if arg.__class__ not in (Label, ):
                raise RelationHasLabelError()

        self._has_label_labels = arg_tuple

    def has_service(self, adaptation_service):
        """
        Check `hasService` relation with given `adaptation_service` object.

        FIXME: Document hasService relation..

        :param adaptation_service: Object to validate relation `hasService`
         with.
        :type adaptation_service: AdaptationService or DeAdaptationService
        :return: True if `adaptation_service` is related to `self` with
         `hasService`.
        :rtype: bool
        """
        if adaptation_service.__class__ not in (
                AdaptationService,
                DeAdaptationService, ):
            raise RelationHasServiceError()

        return adaptation_service.identifier in \
            self._has_service_adaptation_services

    def add_has_service(self, adaptation_service):
        """
        Add given `adaptation_service` to this object `hasService` relations.

        :param adaptation_service: Object to add to the `hasService` relation.
        :type adaptation_service: AdaptationService or DeAdaptationService
        """
        if adaptation_service.__class__ not in (
                AdaptationService,
                DeAdaptationService, ):
            raise RelationHasServiceError()

        self._has_service_adaptation_services[adaptation_service.identifier] = \
            adaptation_service

    def is_sink(self, link):
        """
        Check `isSink` relation with given `link` object.

        FIXME: Document isSink relation..

        :param link: Object to validate relation `isSink` with.
        :type link: Link
        :return: True if `link` is related to `self` with `isSink`.
        :rtype: bool
        """
        if link.__class__ not in (
                Link, ):
            raise RelationIsSinkError()

        return link.identifier in \
            self._is_sink_links

    def add_is_sink(self, link):
        """
        Add given `link` to this object `isSink` relations.

        :param link: Object to add to the `isSink` relation.
        :type link: Link
        """
        if link.__class__ not in (
                Link, ):
            raise RelationIsSinkError()

        self._is_sink_links[link.identifier] = \
            link

    def is_source(self, link):
        """
        Check `isSource` relation with given `link` object.

        FIXME: Document isSource relation..

        :param link: Object to validate relation `isSource` with.
        :type link: Link
        :return: True if `link` is related to `self` with `isSource`.
        :rtype: bool
        """
        if link.__class__ not in (
                Link, ):
            raise RelationIsSourceError()

        return link.identifier in \
            self._is_source_links

    def add_is_source(self, link):
        """
        Add given `link` to this object `isSource` relations.

        :param link: Object to add to the `isSource` relation.
        :type link: Link
        """
        if link.__class__ not in (
                Link, ):
            raise RelationIsSourceError()

        self._is_source_links[link.identifier] = \
            link

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`NetworkObject.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['encoding'] = self._encoding

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLabel'
        for label in self._labels:
            reference = etree.SubElement(
                relation, label.__class__.__name__
            )
            reference.attrib['id'] = label.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasService'
        for adaptation_service in self._adaptation_services:
            reference = etree.SubElement(
                relation, adaptation_service.__class__.__name__
            )
            reference.attrib['id'] = adaptation_service.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isSink'
        for link in self._links:
            reference = etree.SubElement(
                relation, link.__class__.__name__
            )
            reference.attrib['id'] = link.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isSource'
        for link in self._links:
            reference = etree.SubElement(
                relation, link.__class__.__name__
            )
            reference.attrib['id'] = link.identifier

        # Parent attributes and relations
        super(Port, self).as_nml(this, parent)

        return this


class Link(NetworkObject):
    """
    Connects a source object with a sink one.

    Sources and sinks have specified isSource or isSink relations with the Link
    instance but not vice versa.

    :param str encoding: Format of the data streaming through the link as an
     URI.
    """

    def __init__(
            self, encoding=None, **kwargs):
        super(Link, self).__init__(**kwargs)

        # Attributes
        if encoding is None:
            encoding = 'FIXME: Provide default'
        self.encoding = encoding

        # Relations
        self._has_label_labels = (None, )

    @property
    def encoding(self):
        """
        Get attribute encoding.

        :return: Format of the data streaming through the link as an URI.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Set attribute encoding.

        :param str encoding: Format of the data streaming through the link as
         an URI.
        """
        if not is_valid_uri(encoding):
            raise AttributeEncodingError()
        self._encoding = encoding

    def has_label(self, label):
        """
        Check `hasLabel` relation with given `label` object.

        FIXME: Document hasLabel relation..

        :param label: Object to validate relation `hasLabel` with.
        :type label: Label
        :return: True if `label` is related to `self` with `hasLabel`.
        :rtype: bool
        """
        if label.__class__ not in (
                Label, ):
            raise RelationHasLabelError()

        return label in \
            self._has_label_labels

    def set_has_label(self, label):
        """
        Set the `hasLabel` relation to given objects.

        :param label: Object to set to the `hasLabel` relation.
        :type label: Label
        """
        arg_tuple = (label, )

        for arg in arg_tuple:
            if arg.__class__ not in (Label, ):
                raise RelationHasLabelError()

        self._has_label_labels = arg_tuple

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`NetworkObject.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['encoding'] = self._encoding

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLabel'
        for label in self._labels:
            reference = etree.SubElement(
                relation, label.__class__.__name__
            )
            reference.attrib['id'] = label.identifier

        # Parent attributes and relations
        super(Link, self).as_nml(this, parent)

        return this


class Service(NetworkObject):
    """
    Base class for services that a network may provide.

    No Service instances can be created because this class is abstract.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self, **kwargs):
        super(Service, self).__init__(**kwargs)

        # Attributes
        # Relations

    @abstractmethod
    def as_nml(self, this=None, parent=None):
        """
        See :meth:`NetworkObject.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        # Parent attributes and relations
        super(Service, self).as_nml(this, parent)

        return this


class SwitchingService(Service):
    """
    Shows that the network can create new links between certain ports.

    An instance of this class shows that the network is capable of creating new
    Links or LinkGroups between its inbound and outbound ports. These Links or
    LinkGroups are identified by being related to the SwitchingService instance
    with a providesLink relation.

    :param str encoding: Format of the data streaming through the service as an
     URI.
    """

    def __init__(
            self, encoding=None, **kwargs):
        super(SwitchingService, self).__init__(**kwargs)

        # Attributes
        if encoding is None:
            encoding = 'FIXME: Provide default'
        self.encoding = encoding

        # Relations
        self._has_inbound_port_ports = OrderedDict()
        self._has_outbound_port_ports = OrderedDict()
        self._provides_link_links = OrderedDict()

    @property
    def encoding(self):
        """
        Get attribute encoding.

        :return: Format of the data streaming through the service as an URI.
        :rtype: str
        """
        return self._encoding

    @encoding.setter
    def encoding(self, encoding):
        """
        Set attribute encoding.

        :param str encoding: Format of the data streaming through the service
         as an URI.
        """
        if not is_valid_uri(encoding):
            raise AttributeEncodingError()
        self._encoding = encoding

    def has_inbound_port(self, port):
        """
        Check `hasInboundPort` relation with given `port` object.

        FIXME: Document hasInboundPort relation..

        :param port: Object to validate relation `hasInboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasInboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        return port.identifier in \
            self._has_inbound_port_ports

    def add_has_inbound_port(self, port):
        """
        Add given `port` to this object `hasInboundPort` relations.

        :param port: Object to add to the `hasInboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        self._has_inbound_port_ports[port.identifier] = \
            port

    def has_outbound_port(self, port):
        """
        Check `hasOutboundPort` relation with given `port` object.

        FIXME: Document hasOutboundPort relation..

        :param port: Object to validate relation `hasOutboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasOutboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        return port.identifier in \
            self._has_outbound_port_ports

    def add_has_outbound_port(self, port):
        """
        Add given `port` to this object `hasOutboundPort` relations.

        :param port: Object to add to the `hasOutboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        self._has_outbound_port_ports[port.identifier] = \
            port

    def provides_link(self, link):
        """
        Check `providesLink` relation with given `link` object.

        FIXME: Document providesLink relation..

        :param link: Object to validate relation `providesLink` with.
        :type link: Link or LinkGroup
        :return: True if `link` is related to `self` with `providesLink`.
        :rtype: bool
        """
        if link.__class__ not in (
                Link,
                LinkGroup, ):
            raise RelationProvidesLinkError()

        return link.identifier in \
            self._provides_link_links

    def add_provides_link(self, link):
        """
        Add given `link` to this object `providesLink` relations.

        :param link: Object to add to the `providesLink` relation.
        :type link: Link or LinkGroup
        """
        if link.__class__ not in (
                Link,
                LinkGroup, ):
            raise RelationProvidesLinkError()

        self._provides_link_links[link.identifier] = \
            link

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Service.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['encoding'] = self._encoding

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasInboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasOutboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'providesLink'
        for link in self._links:
            reference = etree.SubElement(
                relation, link.__class__.__name__
            )
            reference.attrib['id'] = link.identifier

        # Parent attributes and relations
        super(SwitchingService, self).as_nml(this, parent)

        return this


class AdaptationService(Service):
    """
    Shows that the network can embed data from one or more Ports or PortGroups
    into other Ports or PortGroups.

    An instance of this class shows that data from one or more Ports can be
    embedded in the data encoding of other Port or Ports. This class has an
    adaptationFunction attribute that should describe the kind of embedding
    that is used by the AdaptationService instance.

    :param None adaptation_function: Function for multiplexing.
    """

    def __init__(
            self, adaptation_function=None, **kwargs):
        super(AdaptationService, self).__init__(**kwargs)

        # Attributes
        self.adaptation_function = adaptation_function

        # Relations
        self._can_provide_port_ports = OrderedDict()
        self._exists_during_lifetimes = OrderedDict()
        self._provides_port_ports = OrderedDict()

    def can_provide_port(self, port):
        """
        Check `canProvidePort` relation with given `port` object.

        FIXME: Document canProvidePort relation..

        :param port: Object to validate relation `canProvidePort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `canProvidePort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationCanProvidePortError()

        return port.identifier in \
            self._can_provide_port_ports

    def add_can_provide_port(self, port):
        """
        Add given `port` to this object `canProvidePort` relations.

        :param port: Object to add to the `canProvidePort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationCanProvidePortError()

        self._can_provide_port_ports[port.identifier] = \
            port

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def provides_port(self, port):
        """
        Check `providesPort` relation with given `port` object.

        FIXME: Document providesPort relation..

        :param port: Object to validate relation `providesPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `providesPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationProvidesPortError()

        return port.identifier in \
            self._provides_port_ports

    def add_provides_port(self, port):
        """
        Add given `port` to this object `providesPort` relations.

        :param port: Object to add to the `providesPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationProvidesPortError()

        self._provides_port_ports[port.identifier] = \
            port

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Service.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['adaptationFunction'] = self._adaptation_function

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'canProvidePort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'providesPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        # Parent attributes and relations
        super(AdaptationService, self).as_nml(this, parent)

        return this


class DeAdaptationService(Service):
    """
    Shows that the network can extract data from one or more Ports or
    PortGroups encoding.

    An instance of this class shows that data from one or more Ports can be
    extracted from the data encoding of other Port or Ports. This class has an
    adaptationFunction attribute that should describe the kind of extraction
    that is used by the DeadaptationService instance.

    :param None adaptation_function: Function for multiplexing.
    """

    def __init__(
            self, adaptation_function=None, **kwargs):
        super(DeAdaptationService, self).__init__(**kwargs)

        # Attributes
        self.adaptation_function = adaptation_function

        # Relations
        self._can_provide_port_ports = OrderedDict()
        self._exists_during_lifetimes = OrderedDict()
        self._provides_port_ports = OrderedDict()

    def can_provide_port(self, port):
        """
        Check `canProvidePort` relation with given `port` object.

        FIXME: Document canProvidePort relation..

        :param port: Object to validate relation `canProvidePort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `canProvidePort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationCanProvidePortError()

        return port.identifier in \
            self._can_provide_port_ports

    def add_can_provide_port(self, port):
        """
        Add given `port` to this object `canProvidePort` relations.

        :param port: Object to add to the `canProvidePort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationCanProvidePortError()

        self._can_provide_port_ports[port.identifier] = \
            port

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def provides_port(self, port):
        """
        Check `providesPort` relation with given `port` object.

        FIXME: Document providesPort relation..

        :param port: Object to validate relation `providesPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `providesPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationProvidesPortError()

        return port.identifier in \
            self._provides_port_ports

    def add_provides_port(self, port):
        """
        Add given `port` to this object `providesPort` relations.

        :param port: Object to add to the `providesPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationProvidesPortError()

        self._provides_port_ports[port.identifier] = \
            port

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Service.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['adaptationFunction'] = self._adaptation_function

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'canProvidePort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'providesPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        # Parent attributes and relations
        super(DeAdaptationService, self).as_nml(this, parent)

        return this


class Group(NetworkObject):
    """
    A collection of objects.

    Any object can be part of a Group, even another Group. An object can be
    part of multiple Groups.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(
            self, **kwargs):
        super(Group, self).__init__(**kwargs)

        # Attributes
        # Relations

    @abstractmethod
    def as_nml(self, this=None, parent=None):
        """
        See :meth:`NetworkObject.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        # Parent attributes and relations
        super(Group, self).as_nml(this, parent)

        return this


class Topology(Group):
    """
    A set of connected or connectable Network objects.

    One or more Link or LinkGroup objects can provide the connection between
    the Topology Network Objects.
    """

    def __init__(
            self, **kwargs):
        super(Topology, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._has_node_lifetimes = OrderedDict()
        self._has_inbound_port_ports = OrderedDict()
        self._has_outbound_port_ports = OrderedDict()
        self._has_service_switching_services = OrderedDict()
        self._has_topology_topologies = OrderedDict()

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def has_node(self, lifetime):
        """
        Check `hasNode` relation with given `lifetime` object.

        FIXME: Document hasNode relation..

        :param lifetime: Object to validate relation `hasNode` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `hasNode`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationHasNodeError()

        return lifetime.identifier in \
            self._has_node_lifetimes

    def add_has_node(self, lifetime):
        """
        Add given `lifetime` to this object `hasNode` relations.

        :param lifetime: Object to add to the `hasNode` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationHasNodeError()

        self._has_node_lifetimes[lifetime.identifier] = \
            lifetime

    def has_inbound_port(self, port):
        """
        Check `hasInboundPort` relation with given `port` object.

        FIXME: Document hasInboundPort relation..

        :param port: Object to validate relation `hasInboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasInboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        return port.identifier in \
            self._has_inbound_port_ports

    def add_has_inbound_port(self, port):
        """
        Add given `port` to this object `hasInboundPort` relations.

        :param port: Object to add to the `hasInboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasInboundPortError()

        self._has_inbound_port_ports[port.identifier] = \
            port

    def has_outbound_port(self, port):
        """
        Check `hasOutboundPort` relation with given `port` object.

        FIXME: Document hasOutboundPort relation..

        :param port: Object to validate relation `hasOutboundPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasOutboundPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        return port.identifier in \
            self._has_outbound_port_ports

    def add_has_outbound_port(self, port):
        """
        Add given `port` to this object `hasOutboundPort` relations.

        :param port: Object to add to the `hasOutboundPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasOutboundPortError()

        self._has_outbound_port_ports[port.identifier] = \
            port

    def has_service(self, switching_service):
        """
        Check `hasService` relation with given `switching_service` object.

        FIXME: Document hasService relation..

        :param switching_service: Object to validate relation `hasService`
         with.
        :type switching_service: SwitchingService
        :return: True if `switching_service` is related to `self` with
         `hasService`.
        :rtype: bool
        """
        if switching_service.__class__ not in (
                SwitchingService, ):
            raise RelationHasServiceError()

        return switching_service.identifier in \
            self._has_service_switching_services

    def add_has_service(self, switching_service):
        """
        Add given `switching_service` to this object `hasService` relations.

        :param switching_service: Object to add to the `hasService` relation.
        :type switching_service: SwitchingService
        """
        if switching_service.__class__ not in (
                SwitchingService, ):
            raise RelationHasServiceError()

        self._has_service_switching_services[switching_service.identifier] = \
            switching_service

    def has_topology(self, topology):
        """
        Check `hasTopology` relation with given `topology` object.

        FIXME: Document hasTopology relation..

        :param topology: Object to validate relation `hasTopology` with.
        :type topology: Topology
        :return: True if `topology` is related to `self` with `hasTopology`.
        :rtype: bool
        """
        if topology.__class__ not in (
                Topology, ):
            raise RelationHasTopologyError()

        return topology.identifier in \
            self._has_topology_topologies

    def add_has_topology(self, topology):
        """
        Add given `topology` to this object `hasTopology` relations.

        :param topology: Object to add to the `hasTopology` relation.
        :type topology: Topology
        """
        if topology.__class__ not in (
                Topology, ):
            raise RelationHasTopologyError()

        self._has_topology_topologies[topology.identifier] = \
            topology

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Group.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasNode'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasInboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasOutboundPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasService'
        for switching_service in self._switching_services:
            reference = etree.SubElement(
                relation, switching_service.__class__.__name__
            )
            reference.attrib['id'] = switching_service.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasTopology'
        for topology in self._topologies:
            reference = etree.SubElement(
                relation, topology.__class__.__name__
            )
            reference.attrib['id'] = topology.identifier

        # Parent attributes and relations
        super(Topology, self).as_nml(this, parent)

        return this


class PortGroup(Group):
    """
    A unordered set of Ports.

    FIXME: Document PortGroup.
    """

    def __init__(
            self, **kwargs):
        super(PortGroup, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._has_label_group_lifetimes = (None, )
        self._has_port_ports = OrderedDict()
        self._is_sink_link_groups = OrderedDict()
        self._is_source_link_groups = OrderedDict()

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def has_label_group(self, lifetime):
        """
        Check `hasLabelGroup` relation with given `lifetime` object.

        FIXME: Document hasLabelGroup relation..

        :param lifetime: Object to validate relation `hasLabelGroup` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `hasLabelGroup`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationHasLabelGroupError()

        return lifetime in \
            self._has_label_group_lifetimes

    def set_has_label_group(self, lifetime):
        """
        Set the `hasLabelGroup` relation to given objects.

        :param lifetime: Object to set to the `hasLabelGroup` relation.
        :type lifetime: Lifetime
        """
        arg_tuple = (lifetime, )

        for arg in arg_tuple:
            if arg.__class__ not in (Lifetime, ):
                raise RelationHasLabelGroupError()

        self._has_label_group_lifetimes = arg_tuple

    def has_port(self, port):
        """
        Check `hasPort` relation with given `port` object.

        FIXME: Document hasPort relation..

        :param port: Object to validate relation `hasPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasPortError()

        return port.identifier in \
            self._has_port_ports

    def add_has_port(self, port):
        """
        Add given `port` to this object `hasPort` relations.

        :param port: Object to add to the `hasPort` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasPortError()

        self._has_port_ports[port.identifier] = \
            port

    def is_sink(self, link_group):
        """
        Check `isSink` relation with given `link_group` object.

        FIXME: Document isSink relation..

        :param link_group: Object to validate relation `isSink` with.
        :type link_group: LinkGroup
        :return: True if `link_group` is related to `self` with `isSink`.
        :rtype: bool
        """
        if link_group.__class__ not in (
                LinkGroup, ):
            raise RelationIsSinkError()

        return link_group.identifier in \
            self._is_sink_link_groups

    def add_is_sink(self, link_group):
        """
        Add given `link_group` to this object `isSink` relations.

        :param link_group: Object to add to the `isSink` relation.
        :type link_group: LinkGroup
        """
        if link_group.__class__ not in (
                LinkGroup, ):
            raise RelationIsSinkError()

        self._is_sink_link_groups[link_group.identifier] = \
            link_group

    def is_source(self, link_group):
        """
        Check `isSource` relation with given `link_group` object.

        FIXME: Document isSource relation..

        :param link_group: Object to validate relation `isSource` with.
        :type link_group: LinkGroup
        :return: True if `link_group` is related to `self` with `isSource`.
        :rtype: bool
        """
        if link_group.__class__ not in (
                LinkGroup, ):
            raise RelationIsSourceError()

        return link_group.identifier in \
            self._is_source_link_groups

    def add_is_source(self, link_group):
        """
        Add given `link_group` to this object `isSource` relations.

        :param link_group: Object to add to the `isSource` relation.
        :type link_group: LinkGroup
        """
        if link_group.__class__ not in (
                LinkGroup, ):
            raise RelationIsSourceError()

        self._is_source_link_groups[link_group.identifier] = \
            link_group

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Group.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLabelGroup'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isSink'
        for link_group in self._link_groups:
            reference = etree.SubElement(
                relation, link_group.__class__.__name__
            )
            reference.attrib['id'] = link_group.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isSource'
        for link_group in self._link_groups:
            reference = etree.SubElement(
                relation, link_group.__class__.__name__
            )
            reference.attrib['id'] = link_group.identifier

        # Parent attributes and relations
        super(PortGroup, self).as_nml(this, parent)

        return this


class LinkGroup(Group):
    """
    A unordered set of Links.

    FIXME: Document LinkGroup.
    """

    def __init__(
            self, **kwargs):
        super(LinkGroup, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._has_label_group_lifetimes = (None, )
        self._has_link_ports = OrderedDict()
        self._is_serial_compound_link_ports = OrderedDict()

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def has_label_group(self, lifetime):
        """
        Check `hasLabelGroup` relation with given `lifetime` object.

        FIXME: Document hasLabelGroup relation..

        :param lifetime: Object to validate relation `hasLabelGroup` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `hasLabelGroup`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationHasLabelGroupError()

        return lifetime in \
            self._has_label_group_lifetimes

    def set_has_label_group(self, lifetime):
        """
        Set the `hasLabelGroup` relation to given objects.

        :param lifetime: Object to set to the `hasLabelGroup` relation.
        :type lifetime: Lifetime
        """
        arg_tuple = (lifetime, )

        for arg in arg_tuple:
            if arg.__class__ not in (Lifetime, ):
                raise RelationHasLabelGroupError()

        self._has_label_group_lifetimes = arg_tuple

    def has_link(self, port):
        """
        Check `hasLink` relation with given `port` object.

        FIXME: Document hasLink relation..

        :param port: Object to validate relation `hasLink` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasLink`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasLinkError()

        return port.identifier in \
            self._has_link_ports

    def add_has_link(self, port):
        """
        Add given `port` to this object `hasLink` relations.

        :param port: Object to add to the `hasLink` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasLinkError()

        self._has_link_ports[port.identifier] = \
            port

    def is_serial_compound_link(self, port):
        """
        Check `isSerialCompoundLink` relation with given `port` object.

        FIXME: Document isSerialCompoundLink relation..

        :param port: Object to validate relation `isSerialCompoundLink` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with
         `isSerialCompoundLink`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationIsSerialCompoundLinkError()

        return port.identifier in \
            self._is_serial_compound_link_ports

    def add_is_serial_compound_link(self, port):
        """
        Add given `port` to this object `isSerialCompoundLink` relations.

        :param port: Object to add to the `isSerialCompoundLink` relation.
        :type port: Port or PortGroup
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationIsSerialCompoundLinkError()

        self._is_serial_compound_link_ports[port.identifier] = \
            port

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Group.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLabelGroup'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLink'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'isSerialCompoundLink'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        # Parent attributes and relations
        super(LinkGroup, self).as_nml(this, parent)

        return this


class BidirectionalPort(Group):
    """
    A group of two unidirectional Ports or PortGroups.

    The purpose of this class is to provide a convenient representation of a
    bidirectional Port. This is needed because NML is a unidirectional
    specification.
    """

    def __init__(
            self, **kwargs):
        super(BidirectionalPort, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._has_port_ports = (None, None, )

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def has_port(self, port):
        """
        Check `hasPort` relation with given `port` object.

        FIXME: Document hasPort relation..

        :param port: Object to validate relation `hasPort` with.
        :type port: Port or PortGroup
        :return: True if `port` is related to `self` with `hasPort`.
        :rtype: bool
        """
        if port.__class__ not in (
                Port,
                PortGroup, ):
            raise RelationHasPortError()

        return port in \
            self._has_port_ports

    def set_has_port(self, port1, port2):
        """
        Set the `hasPort` relation to given objects.

        :param port1: One of the objects to set the `hasPort` relation.
        :type port1: Port or PortGroup
        :param port2: One of the objects to set the `hasPort` relation.
        :type port2: Port or PortGroup
        """
        arg_tuple = (port1, port2, )

        for arg in arg_tuple:
            if arg.__class__ not in (Port, PortGroup, ):
                raise RelationHasPortError()
        if len(set(arg_tuple)) != len(arg_tuple):
            raise Exception('Non unique objects')  # FIXME

        self._has_port_ports = arg_tuple

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Group.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasPort'
        for port in self._ports:
            reference = etree.SubElement(
                relation, port.__class__.__name__
            )
            reference.attrib['id'] = port.identifier

        # Parent attributes and relations
        super(BidirectionalPort, self).as_nml(this, parent)

        return this


class BidirectionalLink(Group):
    """
    A group of two unidirectional Links or LinkGroups.

    The purpose of this class is to provide a convenient representation of a
    bidirectional Link. This is needed because NML is a unidirectional
    specification.
    """

    def __init__(
            self, **kwargs):
        super(BidirectionalLink, self).__init__(**kwargs)

        # Attributes
        # Relations
        self._exists_during_lifetimes = OrderedDict()
        self._has_link_links = (None, None, )

    def exists_during(self, lifetime):
        """
        Check `existsDuring` relation with given `lifetime` object.

        FIXME: Document existsDuring relation..

        :param lifetime: Object to validate relation `existsDuring` with.
        :type lifetime: Lifetime
        :return: True if `lifetime` is related to `self` with `existsDuring`.
        :rtype: bool
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        return lifetime.identifier in \
            self._exists_during_lifetimes

    def add_exists_during(self, lifetime):
        """
        Add given `lifetime` to this object `existsDuring` relations.

        :param lifetime: Object to add to the `existsDuring` relation.
        :type lifetime: Lifetime
        """
        if lifetime.__class__ not in (
                Lifetime, ):
            raise RelationExistsDuringError()

        self._exists_during_lifetimes[lifetime.identifier] = \
            lifetime

    def has_link(self, link):
        """
        Check `hasLink` relation with given `link` object.

        FIXME: Document hasLink relation..

        :param link: Object to validate relation `hasLink` with.
        :type link: Link or LinkGroup
        :return: True if `link` is related to `self` with `hasLink`.
        :rtype: bool
        """
        if link.__class__ not in (
                Link,
                LinkGroup, ):
            raise RelationHasLinkError()

        return link in \
            self._has_link_links

    def set_has_link(self, link1, link2):
        """
        Set the `hasLink` relation to given objects.

        :param link1: One of the objects to set the `hasLink` relation.
        :type link1: Link or LinkGroup
        :param link2: One of the objects to set the `hasLink` relation.
        :type link2: Link or LinkGroup
        """
        arg_tuple = (link1, link2, )

        for arg in arg_tuple:
            if arg.__class__ not in (Link, LinkGroup, ):
                raise RelationHasLinkError()
        if len(set(arg_tuple)) != len(arg_tuple):
            raise Exception('Non unique objects')  # FIXME

        self._has_link_links = arg_tuple

    def as_nml(self, this=None, parent=None):
        """
        See :meth:`Group.as_nml`.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'existsDuring'
        for lifetime in self._lifetimes:
            reference = etree.SubElement(
                relation, lifetime.__class__.__name__
            )
            reference.attrib['id'] = lifetime.identifier

        relation = etree.SubElement(this, 'Relation')
        relation.attrib['type'] = 'hasLink'
        for link in self._links:
            reference = etree.SubElement(
                relation, link.__class__.__name__
            )
            reference.attrib['id'] = link.identifier

        # Parent attributes and relations
        super(BidirectionalLink, self).as_nml(this, parent)

        return this


class Location(object):
    """
    Describes where the object is physically located.

    An instance of this class can be related to other objects that are to be
    represented as being present in the same place.

    :param str longitude: Longitude in WGS84 and in decimal degrees.
    :param str latitude: Latitude in WGS84 and in decimal degrees.
    :param str altitude: Altitude in WGS84 and in decimal meters.
    :param str unlocode: UN/LOCODE location identifier.
    :param str address: A vCard ADR property.
    """

    def __init__(
            self, longitude=None, latitude=None, altitude=None, unlocode=None,
            address=None, **kwargs):
        # Attributes
        if longitude is None:
            longitude = 'FIXME: Provide default'
        self.longitude = longitude

        if latitude is None:
            latitude = 'FIXME: Provide default'
        self.latitude = latitude

        if altitude is None:
            altitude = 'FIXME: Provide default'
        self.altitude = altitude

        if unlocode is None:
            unlocode = 'FIXME: Provide default'
        self.unlocode = unlocode

        if address is None:
            address = 'FIXME: Provide default'
        self.address = address

        # Relations

        self.metadata = kwargs

    @property
    def longitude(self):
        """
        Get attribute longitude.

        :return: Longitude in WGS84 and in decimal degrees.
        :rtype: str
        """
        return self._longitude

    @longitude.setter
    def longitude(self, longitude):
        """
        Set attribute longitude.

        :param str longitude: Longitude in WGS84 and in decimal degrees.
        """
        self._longitude = longitude

    @property
    def latitude(self):
        """
        Get attribute latitude.

        :return: Latitude in WGS84 and in decimal degrees.
        :rtype: str
        """
        return self._latitude

    @latitude.setter
    def latitude(self, latitude):
        """
        Set attribute latitude.

        :param str latitude: Latitude in WGS84 and in decimal degrees.
        """
        self._latitude = latitude

    @property
    def altitude(self):
        """
        Get attribute altitude.

        :return: Altitude in WGS84 and in decimal meters.
        :rtype: str
        """
        return self._altitude

    @altitude.setter
    def altitude(self, altitude):
        """
        Set attribute altitude.

        :param str altitude: Altitude in WGS84 and in decimal meters.
        """
        self._altitude = altitude

    @property
    def unlocode(self):
        """
        Get attribute unlocode.

        :return: UN/LOCODE location identifier.
        :rtype: str
        """
        return self._unlocode

    @unlocode.setter
    def unlocode(self, unlocode):
        """
        Set attribute unlocode.

        :param str unlocode: UN/LOCODE location identifier.
        """
        self._unlocode = unlocode

    @property
    def address(self):
        """
        Get attribute address.

        :return: A vCard ADR property.
        :rtype: str
        """
        return self._address

    @address.setter
    def address(self, address):
        """
        Set attribute address.

        :param str address: A vCard ADR property.
        """
        self._address = address

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['long'] = self._longitude
        this.attrib['lat'] = self._latitude
        this.attrib['alt'] = self._altitude
        this.attrib['unlocode'] = self._unlocode
        this.attrib['address'] = self._address

        # Relations
        return this


class Lifetime(object):
    """
    A time interval where the object is active.

    An object can have multiple Lifetimes, if so, it will be active in a time
    interval equivalent to the union of all its Lifetimes time intervals.

    :param str start: Date and time formatted as ISO 8601 calendar date compact
     representation with UTC timezone (YYYYMMDDThhmmssZ).
    :param str end: Date and time formatted as ISO 8601 calendar date compact
     representation with UTC timezone (YYYYMMDDThhmmssZ).
    """

    def __init__(
            self, start=None, end=None, **kwargs):
        # Attributes
        if start is None:
            start = datetime.now().replace(microsecond=0).isoformat()
        self.start = start

        if end is None:
            end = datetime.now().replace(microsecond=0).isoformat()
        self.end = end

        # Relations

        self.metadata = kwargs

    @property
    def start(self):
        """
        Get attribute start.

        :return: Date and time formatted as ISO 8601 calendar date compact
         representation with UTC timezone (YYYYMMDDThhmmssZ).
        :rtype: str
        """
        return self._start

    @start.setter
    def start(self, start):
        """
        Set attribute start.

        :param str start: Date and time formatted as ISO 8601 calendar date
         compact representation with UTC timezone (YYYYMMDDThhmmssZ).
        """
        self._start = start

    @property
    def end(self):
        """
        Get attribute end.

        :return: Date and time formatted as ISO 8601 calendar date compact
         representation with UTC timezone (YYYYMMDDThhmmssZ).
        :rtype: str
        """
        return self._end

    @end.setter
    def end(self, end):
        """
        Set attribute end.

        :param str end: Date and time formatted as ISO 8601 calendar date
         compact representation with UTC timezone (YYYYMMDDThhmmssZ).
        """
        self._end = end

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['start'] = self._start
        this.attrib['end'] = self._end

        # Relations
        return this


class Label(object):
    """
    A value that specifies a single data stream among many.

    A Label is technology-specific, so a Label used to identify a VLAN would be
    different from a Label used to identify a wavelength.

    :param None labeltype: A technology-specific labelset.
    :param None value: A specific value taken from a labelset.
    """

    def __init__(
            self, labeltype=None, value=None, **kwargs):
        # Attributes
        self.labeltype = labeltype

        self.value = value

        # Relations

        self.metadata = kwargs

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['labeltype'] = self._labeltype
        this.attrib['value'] = self._value

        # Relations
        return this


class LabelGroup(object):
    """
    A unordered set of Labels.

    FIXME: Document LabelGroup.

    :param None labeltype: A technology-specific labelset.
    :param None value: A specific value taken from a labelset.
    """

    def __init__(
            self, labeltype=None, value=None, **kwargs):
        # Attributes
        self.labeltype = labeltype

        self.value = value

        # Relations

        self.metadata = kwargs

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes
        this.attrib['labeltype'] = self._labeltype
        this.attrib['value'] = self._value

        # Relations
        return this


class OrderedList(object):
    """
    An ordered list of Network Objects.

    Instances of this class are used to describe a path in the network along
    with the isSerialCompoundLink relation.
    """

    def __init__(
            self, **kwargs):
        # Attributes
        # Relations

        self.metadata = kwargs

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        return this


class ListItem(object):
    """
    An element of an OrderedList.

    Is a syntax-dependent object used to represent elements in an OrderedList.
    """

    def __init__(
            self, **kwargs):
        # Attributes
        # Relations

        self.metadata = kwargs

    def as_nml(self, this=None, parent=None):
        """
        Build NML representation of this node.

        :param this: Node to modify. If `None`, a new node is created.
        :type this: :py:class:`xml.etree.ElementTree`
        :param parent: Parent node to hook to. If `None`, a root node is
         created.
        :type parent: :py:class:`xml.etree.ElementTree`
        :rtype: :py:class:`xml.etree.ElementTree`
        :return: The NML representation of this node.
        """
        this = tree_element(self, this, parent)

        # Attributes

        # Relations
        return this


__all__ = [
    'NetworkObject',
    'Node',
    'Port',
    'Link',
    'Service',
    'SwitchingService',
    'AdaptationService',
    'DeAdaptationService',
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
