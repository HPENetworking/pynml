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
Test suite for module pynml.manager.

See http://pythontesting.net/framework/pytest/pytest-introduction/#fixtures
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from distutils.spawn import find_executable

import pytest  # noqa

from pynml.manager import NMLManager, ExtendedNMLManager


def common_mgr():
    """
    Create a base topology.

    This uses the ExtendedNMLManager for it's helpers.
    """
    # Create base topology
    mgr = ExtendedNMLManager(name='Graphviz Namespace')

    sw1 = mgr.create_node(identifier='sw1', name='My Switch 1')
    sw2 = mgr.create_node(identifier='sw2', name='My Switch 2')

    assert mgr.get_object('sw1') is not None
    assert mgr.get_object('sw2') is not None

    sw1p1 = mgr.create_biport(sw1)
    sw1p2 = mgr.create_biport(sw1)
    sw1p3 = mgr.create_biport(sw1)  # noqa
    sw2p1 = mgr.create_biport(sw2)
    sw2p2 = mgr.create_biport(sw2)
    sw2p3 = mgr.create_biport(sw2)  # noqa

    sw1p1_sw2p1 = mgr.create_bilink(sw1p1, sw2p1)  # noqa
    sw1p2_sw2p2 = mgr.create_bilink(sw1p2, sw2p2)  # noqa

    return mgr


def test_xml_nml(tmpdir):
    """
    Check that the NML XML export work.
    """
    # Create base topology
    mgr = common_mgr()

    # Save XML file
    xmlfile = tmpdir.join('topology.xml')
    mgr.save_nml(str(xmlfile))

    assert xmlfile.check(file=1)

    # FIXME: When parser is implemented, reparse in new namespace and assert


def test_graphviz(tmpdir):
    """
    Check that the graphviz export work.
    """
    # Skip if dot is missing
    dot_exec = find_executable('dot')
    if dot_exec is None:
        pytest.skip('Missing Graphviz "dot" executable')

    # Create base topology
    cmgr = common_mgr()
    mgr = NMLManager()
    # FIXME: Don't be lazy
    mgr.namespace = cmgr.namespace  # Hack, because I'm lazy

    # Plot graphviz file
    srcfile = tmpdir.join('graph.gv')
    plotfile = tmpdir.join('graph.svg')
    print('Ploting graphviz file to {} ...'.format(str(plotfile)))
    mgr.save_graphviz(str(plotfile), keep_gv=True)

    # Check files were created
    assert plotfile.check(file=1)
    assert srcfile.check(file=1)


def test_graphviz_extended(tmpdir):
    """
    Check that the graphviz export work.
    """
    # Skip if dot is missing
    dot_exec = find_executable('dot')
    if dot_exec is None:
        pytest.skip('Missing Graphviz "dot" executable')

    # Create base topology
    mgr = common_mgr()

    # Plot graphviz file
    srcfile = tmpdir.join('graph.gv')
    plotfile = tmpdir.join('graph.svg')
    print('Ploting graphviz file to {} ...'.format(str(plotfile)))
    mgr.save_graphviz(str(plotfile), keep_gv=True)

    # Check files were created
    assert plotfile.check(file=1)
    assert srcfile.check(file=1)
