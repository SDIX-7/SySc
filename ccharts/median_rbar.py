# Copyright (C) 2016  Carlos Henrique Silva <carlosqsilva@outlook.com>
#
# This library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from .ccharts import ccharts
from .tables import A6, D3, D4
import numpy as np


class median_rbar(ccharts):
    
    _title = "Median Chart (X~)"
    
    def plot(self, data, size, newdata=None):
        assert size >= 2
        assert size <= 10
        
        medians = np.median(data, axis=1)
        
        if newdata is not None:
            newvalues = np.median(newdata, axis=1)
        else:
            newvalues = None
        
        median_bar = np.mean(medians)
        
        ranges = np.ptp(data, axis=1)
        rbar = np.mean(ranges)
        
        ucl = median_bar + A6[size] * rbar
        lcl = median_bar - A6[size] * rbar
        
        return (medians, median_bar, lcl, ucl, self._title)


class rbar_median(ccharts):
    
    _title = "R Chart (for Median)"
    
    def plot(self, data, size, newdata=None):
        assert size >= 2
        assert size <= 10
        
        ranges = np.ptp(data, axis=1)
        
        if newdata is not None:
            newvalues = np.ptp(newdata, axis=1)
        else:
            newvalues = None
        
        rbar = np.mean(ranges)
        
        ucl = D4[size] * rbar
        lcl = D3[size] * rbar
        
        return (ranges, rbar, lcl, ucl, self._title)
