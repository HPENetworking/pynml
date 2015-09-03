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
pynml exceptions module.
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division


class NMLException(Exception):
    """
    Base NML Exception class.
    """
    def __str__(self):
        return self.__class__.__doc__.strip().replace('\n', ' ')

    def __repr__(self):
        return repr(str(self))


class VersionError(NMLException):
    """
    Version should be used only for objects of the Topology class.
    """


class CanProvidePortError(NMLException):
    """
    A Service canProvidePort relation must relate it with an object of type
    Port or PortGroup.
    """


class ExistsDuringError(NMLException):
    """
    A NetworkObject existsDuring relation must relate it with an object of
    type Lifetime.
    """


class HasInboundPortError(NMLException):
    """
    A NetworkObject hasInboundPort relation must relate it with an object of
    type Port or PortGroup.
    """


class HasLabelError(NMLException):
    """
    A Link hasLabel relation must relate it with an object of type Label or
    Label.
    """


class HasLabelGroupError(NMLException):
    """
    A LinkGroup hasLabelGroup relation must relate it with an object of type
    LabelGroup or LabelGroup.
    """


class HasLinkError(NMLException):
    """
    A Group hasLink relation must relate it with an object of type Link or
    LinkGroup.
    """


class HasNodeError(NMLException):
    """
    A NetworkObject hasNode relation must relate it with an object of type
    Node.
    """


class HasOutboundPortError(NMLException):
    """
    A NetworkObject hasOutboundPort relation must relate it with an object of
    type Port or PortGroup.
    """


class HasPortError(NMLException):
    """
    A Group hasPort relation must relate it with an object of type Port or
    PortGroup.
    """


class HasServiceError(NMLException):
    """
    A NetworkObject hasService relation must relate it with an object of type
    Service.
    """


class HasTopologyError(NMLException):
    """
    A NetworkObject hasTopology relation must relate it with an object of type
    Topology.
    """


class ImplementedByError(NMLException):
    """
    A NetworkObject implementedBy relation must relate it with an object of
    type NetworkObject.
    """


class IsAliasError(NMLException):
    """
    A isAlias relation must relate an object with one of the same type.
    """


class IsSinkError(NMLException):
    """
    A NetworkObject isSink relation must relate it with an object of type Link
    or LinkGroup.
    """


class IsSourceError(NMLException):
    """
    A NetworkObject isSource relation must relate it with an object of type
    Link or LinkGroup.
    """


class LocatedAtError(NMLException):
    """
    A NetworkObject locatedAt relation must relate it with an object of type
    Location.
    """


class ProvidesLinkError(NMLException):
    """
    A Service providesLink relation must relate it with an object of type Link
    or LinkGroup.
    """


class ProvidesPortError(NMLException):
    """
    A Service providesPort relation must relate it with an object of type Port
    or PortGroup.
    """


class IdError(NMLException):
    """
    Id must be a valid URI.
    """


__all__ = [
    'VersionError',
    'CanProvidePortError',
    'ExistsDuringError',
    'HasInboundPortError',
    'HasLabelError',
    'HasLabelGroupError',
    'HasLinkError',
    'HasNodeError',
    'HasOutboundPortError',
    'HasPortError',
    'HasServiceError',
    'HasTopologyError',
    'ImplementedByError',
    'IsAliasError',
    'IsSinkError',
    'IsSourceError',
    'LocatedAtError',
    'ProvidesLinkError',
    'ProvidesPortError',
    'IdError'
]
