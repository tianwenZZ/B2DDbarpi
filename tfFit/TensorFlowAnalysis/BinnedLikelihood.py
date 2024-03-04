# Copyright 2017 CERN for the benefit of the LHCb collaboration
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import tensorflow as tf
import array
import numpy as np
import math

from TensorFlowAnalysis.Interface import *


def MakeHistogram(phsp, sample, bins, weights=None, normed=False):
    hist = np.histogramdd(
        sample, bins=bins, range=phsp.Bounds(), weights=weights, normed=normed)
    return hist[0]  # Only return the histogram itself, not the bin boundaries


def HistogramNorm(hist):
    return np.sum(hist)


def BinnedChi2(hist1, hist2, err):
    return tf.reduce_sum(((hist1-hist2)/err)**2)
