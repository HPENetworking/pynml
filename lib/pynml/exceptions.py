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
pynml exceptions module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division


class NMLException(Exception):
    """
    Base NML Exception class.
    """
    def __str__(self):
        return ' '.join(self.__class__.__doc__.split())

    def __repr__(self):
        return repr(str(self))


class RelationExistsDuringError(NMLException):
    """
    A existsDuring relation must relate with objects of type Lifetime.
    """


class RelationIsAliasError(NMLException):
    """
    A isAlias relation must relate with objects of type NetworkObject.
    """


class RelationLocatedAtError(NMLException):
    """
    A locatedAt relation must relate with objects of type Location.
    """


class RelationHasInboundPortError(NMLException):
    """
    A hasInboundPort relation must relate with objects of type Port or
    PortGroup.
    """


class RelationHasOutboundPortError(NMLException):
    """
    A hasOutboundPort relation must relate with objects of type Port or
    PortGroup.
    """


class RelationHasServiceError(NMLException):
    """
    A hasService relation must relate with objects of type SwitchingService.
    """


class RelationImplementedByError(NMLException):
    """
    A implementedBy relation must relate with objects of type Node.
    """


class RelationHasLabelError(NMLException):
    """
    A hasLabel relation must relate with objects of type Label.
    """


class RelationIsSinkError(NMLException):
    """
    A isSink relation must relate with objects of type LinkGroup.
    """


class RelationIsSourceError(NMLException):
    """
    A isSource relation must relate with objects of type LinkGroup.
    """


class RelationProvidesLinkError(NMLException):
    """
    A providesLink relation must relate with objects of type Link or LinkGroup.
    """


class RelationCanProvidePortError(NMLException):
    """
    A canProvidePort relation must relate with objects of type Port or
    PortGroup.
    """


class RelationProvidesPortError(NMLException):
    """
    A providesPort relation must relate with objects of type Port or PortGroup.
    """


class RelationHasNodeError(NMLException):
    """
    A hasNode relation must relate with objects of type Node.
    """


class RelationHasEnvironmentError(NMLException):
    """
    A hasEnvironment relation must relate with objects of type Environment.
    """


class RelationHasTopologyError(NMLException):
    """
    A hasTopology relation must relate with objects of type Topology.
    """


class RelationHasLabelGroupError(NMLException):
    """
    A hasLabelGroup relation must relate with objects of type Lifetime.
    """


class RelationHasPortError(NMLException):
    """
    A hasPort relation must relate with objects of type Port or PortGroup.
    """


class RelationHasLinkError(NMLException):
    """
    A hasLink relation must relate with objects of type Link or LinkGroup.
    """


class RelationIsSerialCompoundLinkError(NMLException):
    """
    A isSerialCompoundLink relation must relate with objects of type Port or
    PortGroup.
    """


class AttributeNameError(NMLException):
    """
    Attribute `name` must be a human readable string name.
    """


class AttributeIdError(NMLException):
    """
    Attribute `identifier` must be a persistent globally unique URI.
    """


class AttributeEncodingError(NMLException):
    """
    Attribute `encoding` must be a format of the data streaming through the
    service as an URI.
    """


__all__ = [
    'RelationExistsDuringError',
    'RelationIsAliasError',
    'RelationLocatedAtError',
    'RelationHasInboundPortError',
    'RelationHasOutboundPortError',
    'RelationHasServiceError',
    'RelationImplementedByError',
    'RelationHasLabelError',
    'RelationIsSinkError',
    'RelationIsSourceError',
    'RelationProvidesLinkError',
    'RelationCanProvidePortError',
    'RelationProvidesPortError',
    'RelationHasNodeError',
    'RelationHasEnvironmentError',
    'RelationHasTopologyError',
    'RelationHasLabelGroupError',
    'RelationHasPortError',
    'RelationHasLinkError',
    'RelationIsSerialCompoundLinkError',
    'AttributeNameError',
    'AttributeIdError',
    'AttributeEncodingError'
]
