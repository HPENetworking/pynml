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
Test suite for module pynml.manager.

See http://pythontesting.net/framework/pytest/pytest-introduction/#fixtures
"""

from __future__ import unicode_literals, absolute_import
from __future__ import print_function, division

from os.path import join
from shutil import rmtree
from tempfile import mkdtemp
from subprocess import check_call
from distutils.spawn import find_executable

import pytest  # noqa

from pynml.manager import ExtendedNMLManager


def test_graphviz():
    """
    Check that the graphviz export work.
    """
    # Skip if dot is missing
    dot_exec = find_executable('dot')
    if dot_exec is None:
        pytest.skip('Missing Graphviz "dot" executable')

    # Create base topology
    mgr = ExtendedNMLManager(name='Graphviz Namespace')

    sw1 = mgr.create_node(name='My Switch 1')
    sw2 = mgr.create_node(name='My Switch 2')

    sw1p1 = mgr.create_biport(sw1)
    sw1p2 = mgr.create_biport(sw1)
    sw1p3 = mgr.create_biport(sw1)  # noqa
    sw2p1 = mgr.create_biport(sw2)
    sw2p2 = mgr.create_biport(sw2)
    sw2p3 = mgr.create_biport(sw2)  # noqa

    sw1p1_sw2p1 = mgr.create_bilink(sw1p1, sw2p1)  # noqa
    sw1p2_sw2p2 = mgr.create_bilink(sw1p2, sw2p2)  # noqa

    # Render graphviz and write output
    graph = mgr.export_graphviz()

    tmpdir = mkdtemp(prefix='pynml_test_')
    srcfile = join(tmpdir, 'graph.dot')
    outfile = join(tmpdir, 'graph.png')

    print('Saving graphviz file to {} ...'.format(srcfile))
    print(graph)
    with open(srcfile, 'w') as fd:
        fd.write(graph)

    check_call([dot_exec, '-Tpng', srcfile, '-o', outfile])

    rmtree(tmpdir)