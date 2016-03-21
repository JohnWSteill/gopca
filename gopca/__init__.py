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

import pkg_resources

from .config import GOPCAConfig
from .signature import GOPCASignature
from .result import GOPCAResult
from .run import GOPCARun
from .go_pca import GOPCA
from .plotter import GOPCAPlotter

__version__ = pkg_resources.require('gopca')[0].version

__all__ = ['GOPCAInput','GOPCA','GOPCAResult', 'GOPCARun', 'GOPCAPlot']
