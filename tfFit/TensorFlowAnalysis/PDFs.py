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

from ROOT import TVirtualFitter, TNtuple, TH1, TH2, TH3
from TensorFlowAnalysis.Interface import *


class RootHistShape:
    """
      Class that creates a TensorFlow graph for a (multi)linear interpolation of
      ROOT TH{1,2,3} histogram. Useful for e.g. efficiency and background shapes 
      stored in histograms. 
    """

    def __init__(self, hist):
        """
          Constructor.
            hist - ROOT THn object
        """
        if isinstance(hist, TH1):
            nx = hist.GetNbinsX()
            array = np.zeros((nx), dtype=np.dtype('d'))
            self.limits = [
                tf.constant([hist.GetXaxis().GetBinCenter(1)], dtype=FPType()),
                tf.constant([hist.GetXaxis().GetBinCenter(nx)], dtype=FPType()),
            ]
            for x in range(nx):
                array[x] = hist.GetBinContent(x+1)
            self.ns = tf.constant([nx-1], dtype=FPType())

        if isinstance(hist, TH2):
            nx = hist.GetNbinsX()
            ny = hist.GetNbinsY()
            array = np.zeros((nx, ny), dtype=np.dtype('d'))
            self.limits = [
                tf.constant([hist.GetXaxis().GetBinCenter( 1),  hist.GetYaxis().GetBinCenter(1)], dtype=FPType()),
                tf.constant([hist.GetXaxis().GetBinCenter( nx), hist.GetYaxis().GetBinCenter(ny)], dtype=FPType()),
            ]
            for x in range(nx):
                for y in range(ny):
                    array[x][y] = hist.GetBinContent(x+1, y+1)
            self.ns = tf.constant([nx-1, ny-1], dtype=FPType())

        if isinstance(hist, TH3):
            nx = hist.GetNbinsX()
            ny = hist.GetNbinsY()
            nz = hist.GetNbinsZ()
            array = np.zeros((nx, ny, nz), dtype=np.dtype('d'))
            self.limits = [
                tf.constant([hist.GetXaxis().GetBinCenter(1),  hist.GetYaxis().GetBinCenter(
                    1),  hist.GetZaxis().GetBinCenter(1)], dtype=FPType()),
                tf.constant([hist.GetXaxis().GetBinCenter(nx), hist.GetYaxis().GetBinCenter(
                    ny), hist.GetZaxis().GetBinCenter(nz)], dtype=FPType()),
            ]
            for x in range(nx):
                for y in range(ny):
                    for z in range(nz):
                        array[x][y][z] = hist.GetBinContent(x+1, y+1, z+1)
            self.ns = tf.constant([nx-1, ny-1, nz-1], dtype=FPType())

        self.array = tf.constant(array, dtype=FPType())

    def shape(self, x):
        """
          Method that returns a TF graph with the interpolation result for for a set of N M-dimensional points 
            x - TF tensor of shape (N, M)
        """
        c = (x - self.limits[0])/(self.limits[1]-self.limits[0])*self.ns
        return Interpolate(self.array, c)


def CrystalBall(x, mu, sigma, alpha, n):
    t = (x-mu)/sigma*tf.sign(alpha)
    abs_alpha = tf.abs(alpha)
    a = tf.pow((n / abs_alpha), n) * tf.exp(-0.5 * tf.square(alpha))
    b = (n / abs_alpha) - abs_alpha
    cond = tf.less(t, -abs_alpha)
    func = tf.where(cond, tf.exp(-0.5 * tf.square(t)), a*tf.pow(b-t, -n))
    func = tf.where(tf.is_nan(func), tf.ones_like(func), func)
    return func


def DoubleCrystalBall(x, mu, sigma, alpha1, n1, alpha2, n2, frac):
    return CrystalBall(x, mu, sigma, alpha1, n1) + frac*CrystalBall(x, mu, sigma, alpha2, n2)
