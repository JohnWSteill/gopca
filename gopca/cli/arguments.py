# Copyright (c) 2015, 2016 Florian Wagner
#
# This file is part of GO-PCA.
#
# GO-PCA is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License, Version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

"""Functions for configuring command-line parameters of GO-PCA scripts.
"""

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import *

# import sys
import argparse
import textwrap

import gopca

file_mv = '<file>'
int_mv = '<int>'
float_mv = '<float>'
name_mv = '<name>'
str_mv = '<str>'

# str_type = lambda s: str(s, sys.getfilesystemencoding())


def get_argument_parser(prog=None, desc=None, formatter_class=None):
    """Create an argument parser.

    Parameters
    ----------
    prog: str, optional
        The program name.
    desc: str, optinoal
        The program description.
    formatter_class: argparser formatter class, optional
        The argparse formatter class to use.

    Returns
    -------
    `argparse.ArgumentParser`
        The arguemnt parser created.
    """
    if formatter_class is None:
        formatter_class = argparse.RawTextHelpFormatter

    parser = argparse.ArgumentParser(
        prog=prog, description=desc,
        formatter_class=formatter_class, add_help=False)

    g = parser.add_argument_group('Help')
    g.add_argument('-h', '--help', action='help',
                   help='Show this help message and exit.')

    v = gopca.__version__
    g.add_argument('--version', action='version', version='GO-PCA ' + v,
                   help='Output the GO-PCA version and exit.')

    return parser


def add_reporting_args(parser):
    """Add reporting arguments to an argument parser.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Reporting options')

    g.add_argument(
        '-l', '--log-file', type=str, metavar=file_mv, default=None,
        help=textwrap.dedent("""\
            Path of log file (if specified, report to stdout AND
            file)."""))

    g.add_argument(
        '-q', '--quiet', action='store_true',
        help='Only output errors and warnings.')

    g.add_argument(
        '-v', '--verbose', action='store_true',
        help='Enable verbose output. Ignored if --quiet is specified.')

    return parser


def add_io_args(parser):
    """Add input/output arguments to an argument parser.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Input and output files (required)')

    g.add_argument(
        '-g', '--gopca-file', type=str, required=True, metavar=file_mv,
        help='The GO-PCA result file.')

    g.add_argument(
        '-o', '--output-file', type=str, required=True, metavar=file_mv,
        help='The output file.')

    return g


def add_go_term_args(parser):
    """Add GO term arguments to an argument parser.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('GO term options')

    g.add_argument(
        '--term-reverse-order', action='store_true',
        help='Reverse the order of the GO terms.')

    g.add_argument(
        '--term-max-len', type=int, metavar=int_mv, default=50,
        help='The maximal length of GO term labels.')

    return g


def add_signature_args(parser):
    """Add signature arguments to an argument parser.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Signature options')

    g.add_argument(
        '--sig-reverse-order', action='store_true',
        help='Reverse the order of the signatures.')

    g.add_argument(
        '--sig-max-len', type=int, metavar=int_mv, default=50,
        help='The maximal length of signature labels.')

    g.add_argument(
        '--sig-filter-corr', type=float, metavar=float_mv, default=1.0,
        help='Correlation threshold for filtering signatures (1.0 = off).')

    return g


def add_sample_args(parser):
    """Add sample arguments to an argument parser.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Sample options')

    g.add_argument(
        '--sample-no-clustering', action='store_true',
        help='Disable clustering of the samples.')

    g.add_argument(
        '--sample-cluster-metric', default='euclidean', metavar=name_mv,
        help='The metric used in the hierarchical clustering algorithm.')

    return g


def add_fig_args(parser):
    """Add shared figure parameters.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Figure options')

    g.add_argument(
        '-s', '--fig-size', type=float, nargs=2, default=[18, 18],
        metavar=(float_mv, float_mv),
        help='Figure width and height (in inches).')

    g.add_argument(
        '-r', '--fig-resolution', type=float, default=150,
        metavar=float_mv,
        help='Figure resolution (in dpi).')

    g.add_argument(
        '-f', '--fig-font-size', type=int, default=24,
        metavar=float_mv,
        help='Figure font size (in pt).')

    g.add_argument(
        '-m', '--fig-font-family', default='serif',
        metavar=name_mv,
        help='Figure font family.')

    g.add_argument(
        '-t', '--fig-use-tex', action='store_true',
        help='Use LaTeX for typesetting figure text.')

    g.add_argument(
        '-b', '--fig-mpl-backend', default=None,
        metavar=name_mv,
        help='Matplotlib backend.')

    return g


def add_heatmap_args(parser):
    """Add shared heat map parameters.

    Parameters
    ----------
    parser: `argparse.ArgumentParser`

    Returns
    -------
    `argparse.ArgumentGroup`
        The argument group created.
    """
    g = parser.add_argument_group('Heat map color and colorbar options')

    g.add_argument(
        '-cm', '--colormap', default='RdBu_r',
        metavar=name_mv,
        help='The colormap used.')

    g.add_argument(
        '-vc', '--val-coolest', type=float, default=-3.0,
        metavar=float_mv,
        help='The value corresponding to the "coolest" color.')

    g.add_argument(
        '-vh', '--val-hottest', type=float, default=3.0,
        metavar=float_mv,
        help='The value corresponding to the "hottest" color.')

    g.add_argument(
        '-co', '--cbar-orient',  default='horizontal',
        metavar=name_mv,
        help='The orientation of the colorbar.')

    g.add_argument(
        '-ca', '--cbar-anchor', type=float, nargs=2,
        default=(0.96, 1.0),
        metavar=(float_mv, float_mv),
        help='The colorbar anchoring position (x and y).')

    g.add_argument(
        '-cs', '--cbar-scale', type=float, default=0.3,
        metavar=float_mv,
        help='Scaling factor to adjust the size of the colorbar.')

    g.add_argument(
        '-cp', '--cbar-pad', type=float, default=0.015,
        metavar=float_mv,
        help='The colorbar padding.')

    g.add_argument(
        '-ct', '--cbar-ticks', nargs='*', default=None,
        metavar='<float>',
        help='The colorbar ticks.')

    g.add_argument(
        '--show-sample-labels', action='store_true',
        help='Show sample labels.')

    g.add_argument(
        '--sample-label-font-size', type=float, default=None,
        metavar=float_mv,
        help='Sample label font size (in points).')

    return g
