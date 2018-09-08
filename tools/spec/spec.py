# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2018 Hewlett Packard Enterprise Development LP
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
NML specification definition.
"""


NML_SPEC = {
    'classes': [
        {
            'name': 'Network Object',
            'parent': None,
            'brief': 'The basic class from other instances inherit from',
            'doc': (
                'No NetworkObject instances can be created because '
                'this class is abstract'
            ),
            'abstract': True,
            'attributes': [
                {
                    'name': 'name',
                    'property': True,
                    'nml_attribute': 'name',
                    'semantic_type': 'string',
                    'type': 'str',
                    'default': (
                        '\'{}({})\'.format(\n'
                        '                '
                        'self.__class__.__name__, str(id(self))\n'
                        '            '
                        ')'
                    ),
                    'default_arg': 'None',
                    'validation': '%s',
                    'doc': 'Human readable string name'
                },
                {
                    'name': 'identifier',
                    'property': True,
                    'nml_attribute': 'id',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'str(id(self))',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': 'Persistent globally unique URI'
                },
                {
                    'name': 'version',
                    'property': True,
                    'nml_attribute': 'version',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME
                    'doc': 'Time stamp formatted as ISO 8601'
                },
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'isAlias',
                    'with': ['Network Object'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isAlias relation'
                },
                {
                    'name': 'locatedAt',
                    'with': ['Location'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document locatedAt relation'
                },
            ]
        },
        {
            'name': 'Node',
            'parent': 'Network Object',
            'brief': 'A Node object represents a device in a network',
            'doc': (
                'Physical or virtual devices can be represented '
                'by instances of this class'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'implementedBy',
                    'with': ['Node'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document implementedBy relation'
                },
            ]
        },
        {
            'name': 'Port',
            'parent': 'Network Object',
            'brief': 'Endpoint of an unidirectional connection',
            'doc': (
                'Can represent physical or virtual ports. Needs a proper '
                'linking instance to connect to other ports'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the port as an '
                        'URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasLabel',
                    'with': ['Label'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabel relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Adaptation Service', 'De-adaptation Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'isSink',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSink relation'
                },
                {
                    'name': 'isSource',
                    'with': ['Link'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSource relation'
                },
            ]
        },
        {
            'name': 'Link',
            'parent': 'Network Object',
            'brief': 'Connects a source object with a sink one',
            'doc': (
                'Sources and sinks have specified isSource or isSink '
                'relations with the Link instance but not vice versa'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the link as an '
                        'URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasLabel',
                    'with': ['Label'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabel relation'
                },
            ]
        },
        {
            'name': 'Service',
            'parent': 'Network Object',
            'brief': 'Base class for services that a network may provide',
            'doc': (
                'No Service instances can be created because '
                'this class is abstract'
            ),
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Switching Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can create new links between '
                'certain ports'
            ),
            'doc': (
                'An instance of this class shows that the network is capable '
                'of creating new Links or LinkGroups between its inbound and '
                'outbound ports. These Links or LinkGroups are identified by '
                'being related to the SwitchingService instance with a '
                'providesLink relation'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'encoding',
                    'property': True,
                    'nml_attribute': 'encoding',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': (
                        'Format of the data streaming through the service as '
                        'an URI'
                    )
                },
            ],
            'relations': [
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'providesLink',
                    'with': ['Link', 'Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesLink relation'
                },
            ]
        },
        {
            'name': 'Adaptation Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can embed data from one or more '
                'Ports or PortGroups into other Ports or PortGroups'
            ),
            'doc': (
                'An instance of this class shows that data from one or more '
                'Ports can be embedded in the data encoding of other Port or '
                'Ports. This class has an adaptationFunction attribute that '
                'should describe the kind of embedding that is used by the '
                'AdaptationService instance'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'adaptation_function',
                    'property': False,
                    'nml_attribute': 'adaptationFunction',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'Function for multiplexing'
                }
            ],
            'relations': [
                {
                    'name': 'canProvidePort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document canProvidePort relation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesPort relation'
                }
            ]
        },
        {
            'name': 'De-adaptation Service',
            'parent': 'Service',
            'brief': (
                'Shows that the network can extract data from one or more '
                'Ports or PortGroups encoding'
            ),
            'doc': (
                'An instance of this class shows that data from one or more '
                'Ports can be extracted from the data encoding of other Port '
                'or Ports. This class has an adaptationFunction attribute '
                'that should describe the kind of extraction that is used by '
                'the DeadaptationService instance'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'adaptation_function',
                    'property': False,
                    'nml_attribute': 'adaptationFunction',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'Function for multiplexing'
                }
            ],
            'relations': [
                {
                    'name': 'canProvidePort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document canProvidePort relation'
                },
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'providesPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document providesPort relation'
                }
            ]
        },
        {
            'name': 'Group',
            'parent': 'Network Object',
            'brief': 'A collection of objects',
            'doc': (
                'Any object can be part of a Group, even another Group. '
                'An object can be part of multiple Groups'
            ),
            'abstract': True,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Topology',
            'parent': 'Group',
            'brief': 'A set of connected or connectable Network objects',
            'doc': (
                'One or more Link or LinkGroup objects can provide the '
                'connection between the Topology Network Objects'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasNode',
                    'with': ['Node'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasNode relation'
                },
                {
                    'name': 'hasInboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasInboundPort relation'
                },
                {
                    'name': 'hasOutboundPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasOutboundPort relation'
                },
                {
                    'name': 'hasService',
                    'with': ['Switching Service'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasService relation'
                },
                {
                    'name': 'hasEnvironment',
                    'with': ['Environment'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasEnvironment relation'
                },
                {
                    'name': 'hasTopology',
                    'with': ['Topology'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasTopology relation'
                }
            ]
        },
        {
            'name': 'Port Group',
            'parent': 'Group',
            'brief': 'A unordered set of Ports',
            'doc': 'FIXME: Document PortGroup',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabelGroup relation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasPort relation'
                },
                {
                    'name': 'isSink',
                    'with': ['Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSink relation'
                },
                {
                    'name': 'isSource',
                    'with': ['Link Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSource relation'
                },
            ]
        },
        {
            'name': 'Link Group',
            'parent': 'Group',
            'brief': 'A unordered set of Links',
            'doc': 'FIXME: Document LinkGroup',
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLabelGroup',
                    'with': ['Lifetime'],
                    'cardinality': '1',
                    'doc': 'FIXME: Document hasLabelGroup relation'
                },
                {
                    'name': 'hasLink',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document hasLink relation'
                },
                {
                    'name': 'isSerialCompoundLink',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document isSerialCompoundLink relation'
                }
            ]
        },
        {
            'name': 'Bidirectional Port',
            'parent': 'Group',
            'brief': 'A group of two unidirectional Ports or PortGroups',
            'doc': (
                'The purpose of this class is to provide a convenient '
                'representation of a bidirectional Port. This is needed '
                'because NML is a unidirectional specification'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasPort',
                    'with': ['Port', 'Port Group'],
                    'cardinality': '2',
                    'doc': 'FIXME: Document hasPort relation'
                }
            ]
        },
        {
            'name': 'Bidirectional Link',
            'parent': 'Group',
            'brief': 'A group of two unidirectional Links or LinkGroups',
            'doc': (
                'The purpose of this class is to provide a convenient '
                'representation of a bidirectional Link. This is needed '
                'because NML is a unidirectional specification'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
                {
                    'name': 'existsDuring',
                    'with': ['Lifetime'],
                    'cardinality': '+',
                    'doc': 'FIXME: Document existsDuring relation'
                },
                {
                    'name': 'hasLink',
                    'with': ['Link', 'Link Group'],
                    'cardinality': '2',
                    'doc': 'FIXME: Document hasLink relation'
                }
            ]
        },
        {
            'name': 'Environment',
            'parent': 'NetworkObject',
            'brief': 'Describes attributes inherent to the environment',
            'doc': (
                'Attributes to be attached to the environment the topology is '
                'in'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'Location',
            'parent': None,
            'brief': 'Describes where the object is physically located',
            'doc': (
                'An instance of this class can be related to other objects '
                'that are to be represented as being present in the same '
                'place'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'name',
                    'property': True,
                    'nml_attribute': 'name',
                    'semantic_type': 'string',
                    'type': 'str',
                    'default': (
                        '\'{}<{}>\'.format(\n'
                        '                '
                        'self.__class__.__name__, str(id(self))\n'
                        '            '
                        ')'
                    ),
                    'default_arg': 'None',
                    'validation': '%s',
                    'doc': 'Human readable string name'
                },
                {
                    'name': 'identifier',
                    'property': True,
                    'nml_attribute': 'id',
                    'semantic_type': 'URI',
                    'type': 'str',
                    'default': 'str(id(self))',
                    'default_arg': 'None',
                    'validation': 'is_valid_uri(%s)',
                    'doc': 'Persistent globally unique URI'
                },
                {
                    'name': 'longitude',
                    'property': True,
                    'nml_attribute': 'long',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Longitude in WGS84 and in decimal degrees'
                },
                {
                    'name': 'latitude',
                    'property': True,
                    'nml_attribute': 'lat',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Latitude in WGS84 and in decimal degrees'
                },
                {
                    'name': 'altitude',
                    'property': True,
                    'nml_attribute': 'alt',
                    'semantic_type': 'WGS84',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add WGS84 validation
                    'doc': 'Altitude in WGS84 and in decimal meters'
                },
                {
                    'name': 'unlocode',
                    'property': True,
                    'nml_attribute': 'unlocode',
                    'semantic_type': 'UN/LOCODE',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add UN/LOCODE validation
                    'doc': 'UN/LOCODE location identifier'
                },
                {
                    'name': 'address',
                    'property': True,
                    'nml_attribute': 'address',
                    'semantic_type': 'vCard ADR',
                    'type': 'str',
                    'default': 'unset',
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add vCard ADR validation
                    'doc': 'A vCard ADR property'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Lifetime',
            'parent': None,
            'brief': 'A time interval where the object is active',
            'doc': (
                'An object can have multiple Lifetimes, if so, it will be '
                'active in a time interval equivalent to the union of all '
                'its Lifetimes time intervals'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'start',
                    'property': True,
                    'nml_attribute': 'start',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add ISO 8601 validation
                    'doc': (
                        'Date and time formatted as ISO 8601 calendar date '
                        'compact representation with UTC timezone '
                        '(YYYYMMDDThhmmssZ)'
                    )
                },
                {
                    'name': 'end',
                    'property': True,
                    'nml_attribute': 'end',
                    'semantic_type': 'timestamp',
                    'type': 'str',
                    'default': (
                        'datetime.now().replace(microsecond=0).isoformat()'
                    ),
                    'default_arg': 'None',
                    'validation': None,  # FIXME Add ISO 8601 validation
                    'doc': (
                        'Date and time formatted as ISO 8601 calendar date '
                        'compact representation with UTC timezone '
                        '(YYYYMMDDThhmmssZ)'
                    )
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label',
            'parent': None,
            'brief': 'A value that specifies a single data stream among many',
            'doc': (
                'A Label is technology-specific, so a Label used to identify '
                'a VLAN would be different from a Label used to identify a '
                'wavelength'
            ),
            'abstract': False,
            'attributes': [
                {
                    'name': 'labeltype',
                    'property': False,
                    'nml_attribute': 'labeltype',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A technology-specific labelset'
                },
                {
                    'name': 'value',
                    'property': False,
                    'nml_attribute': 'value',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A specific value taken from a labelset'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Label Group',
            'parent': None,
            'brief': 'A unordered set of Labels',
            'doc': 'FIXME: Document LabelGroup',
            'abstract': False,
            'attributes': [
                {
                    'name': 'labeltype',
                    'property': False,
                    'nml_attribute': 'labeltype',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A technology-specific labelset'
                },
                {
                    'name': 'value',
                    'property': False,
                    'nml_attribute': 'value',
                    'semantic_type': None,
                    'type': None,
                    'default': None,
                    'default_arg': None,
                    'validation': None,
                    'doc': 'A specific value taken from a labelset'
                }
            ],
            'relations': [
            ]
        },
        {
            'name': 'Ordered List',
            'parent': None,
            'brief': 'An ordered list of Network Objects',
            'doc': (
                'Instances of this class are used to describe a path in the '
                'network along with the isSerialCompoundLink relation'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
        {
            'name': 'List Item',
            'parent': None,
            'brief': 'An element of an OrderedList',
            'doc': (
                'Is a syntax-dependent object used to represent elements in '
                'an OrderedList'
            ),
            'abstract': False,
            'attributes': [
            ],
            'relations': [
            ]
        },
    ]
}
"""NML Specification as a Python dictionary"""


__all__ = ['NML_SPEC']
