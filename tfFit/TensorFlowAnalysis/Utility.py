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
from TensorFlowAnalysis.Optimisation import *


def MultivariateGauss(x, norm, mean, invCov):
    print(norm)
    dx = x-mean
#  expArg = tf.einsum("ij,aj,ai->a", invCov, dx, dx)
    res = tf.matmul(dx, invCov, transpose_b=True)
    expArg = tf.reduce_sum(tf.multiply(res, dx), 1)
    return (norm**2)*Exp(-0.5*expArg)


def Gauss2D(x, norm, xmean, ymean, xsigma, ysigma, corr):
    print(norm)
    offdiag = abs(xsigma*ysigma)*corr
    array = [[xsigma**2, offdiag], [offdiag, ysigma**2]]
    cov = tf.stack(array)
    mean = tf.stack([xmean, ymean])
    invcov = tf.matrix_inverse(cov, name="MatInv")
    return MultivariateGauss(x, norm, mean, invcov)


def Gauss4D(x, params):
    norm = params[0]
    mean = tf.stack(params[1:5])
    sigma = tf.stack(params[5:9])
    corr = tf.stack([[Const(1.),  params[9],  params[10], params[11]],
                     [params[9],  Const(1.),  params[12], params[13]],
                     [params[10], params[12], Const(1.),  params[14]],
                     [params[11], params[13], params[14], Const(1.)]])

    cov = tf.einsum("i,ij,j->ij", sigma, corr, sigma)
    invcov = tf.matrix_inverse(cov)
    return MultivariateGauss(x, norm, mean, invcov)


class GaussianMixture2D:
    def __init__(self, prefix, n, x_range, y_range):
        self.params = []
        for i in range(n):
            sn = 1.
            if i > 0:
                sn = 0.
            norm = FitParameter(prefix + "n%d" % i, sn, 0., 2.)
            xmean = FitParameter(
                prefix + "xm%d" % i, np.random.uniform(x_range[0], x_range[1], 1)[0], -1., 1.)
            ymean = FitParameter(
                prefix + "ym%d" % i, np.random.uniform(y_range[0], y_range[1], 1)[0], -1., 1.)
            xsigma = FitParameter(prefix + "xs%d" %
                                  i, (x_range[1] - x_range[0])/4., 0.1, 2.)
            ysigma = FitParameter(prefix + "ys%d" %
                                  i, (y_range[1] - y_range[0])/4., 0.1, 2.)
            corr = FitParameter(prefix + "c%d" % i, 0., -0.9, 0.9)
            self.params += [(norm, xmean, ymean, xsigma, ysigma, corr)]
#    self.params[0][0].step_size = 0. # Fix first normalisation term

    def fix(self):
        for par in self.params:
            for var in par:
                var.init_value = var.fitted_value
                var.fix()

    def float(self, n):
        for var in self.params[n]:
            var.float()
#    self.params[0][0].step_size = 0. # Fix first normalisation term

    def add(self, n):
        i = len(self.params)
        p = self.params[n]
        prefix = p[0].par_name[:-len("n%d" % n)]
        norm = FitParameter(
            prefix + "n%d" % i, p[0].fitted_value, p[0].lower_limit, p[0].upper_limit, p[0].step_size)
        xmean = FitParameter(
            prefix + "xm%d" % i, p[1].fitted_value, p[1].lower_limit, p[1].upper_limit, p[1].step_size)
        ymean = FitParameter(
            prefix + "ym%d" % i, p[2].fitted_value, p[2].lower_limit, p[2].upper_limit, p[2].step_size)
        xsigma = FitParameter(
            prefix + "xs%d" % i, p[3].fitted_value, p[3].lower_limit, p[3].upper_limit, p[3].step_size)
        ysigma = FitParameter(
            prefix + "ys%d" % i, p[4].fitted_value, p[4].lower_limit, p[4].upper_limit, p[4].step_size)
        corr = FitParameter(
            prefix + "c%d" % i, p[5].fitted_value, p[5].lower_limit, p[5].upper_limit, p[5].step_size)
        self.params += [(norm, xmean, ymean, xsigma, ysigma, corr)]

    def model(self, x):
        d = Const(0.)
        for i in self.params:
            d += Gauss2D(x, i[0], i[1], i[2], i[3], i[4], i[5])
        return d


class GaussianMixture4D:
    def __init__(self, prefix, n, ranges):
        self.params = []
        for i in range(n):
            norm = FitParameter(prefix + "n%d" % i, 1./(1. + float(i)), 0., 2.)
            xmean = FitParameter(
                prefix + "xm%d" % i, np.random.uniform(x_range[0], x_range[1], 1)[0], -1., 1.)
            ymean = FitParameter(
                prefix + "ym%d" % i, np.random.uniform(y_range[0], y_range[1], 1)[0], -1., 1.)
            xsigma = FitParameter(prefix + "xs%d" %
                                  i, (x_range[1] - x_range[0])/4., 0., 2.)
            ysigma = FitParameter(prefix + "ys%d" %
                                  i, (x_range[1] - x_range[0])/4., 0., 2.)
            corr = FitParameter(prefix + "c%d" % i, 0., -0.9, 0.9)
            self.params += [(norm, xmean, ymean, xsigma, ysigma, corr)]
        self.params[0][0].step_size = 0.  # Fix first normalisation term

    def model(self, x):
        d = Const(0.)
        for i in self.params:
            d += Gauss2D(x, i[0], i[1], i[2], i[3], i[4], i[5])
        return d
