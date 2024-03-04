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


def PartialIntegral(pdf, size):
    """
    """
    pdf2 = tf.reshape(pdf, [-1, size])
    return tf.reduce_mean(pdf2, axis=1)


def Integral(pdf):
    """
      Return the graph for the integral of the PDF
        pdf : PDF
    """
    return tf.reduce_mean(pdf)


def WeightedIntegral(pdf, weight_func):
    """
      Return the graph for the integral of the PDF
        pdf : PDF
        weight_func : weight function
    """
    return tf.reduce_mean(pdf*weight_func)


def UnbinnedNLL(pdf, integral):
    """
      Return unbinned negative log likelihood graph for a PDF
        pdf      : PDF 
        integral : precalculated integral
    """
    return -tf.reduce_sum(Log(pdf/integral))


def UnbinnedWeightedNLL(pdf, integral, weight_func):
    """
      Return unbinned weighted negative log likelihood graph for a PDF
        pdf         : PDF
        integral    : precalculated integral
        weight_func : weight function
    """
    return -tf.reduce_sum(Log(pdf/integral)*weight_func)
