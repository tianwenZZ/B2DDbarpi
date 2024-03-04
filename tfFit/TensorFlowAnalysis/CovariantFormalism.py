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
from TensorFlowAnalysis.Interface import *
from TensorFlowAnalysis.Kinematics import *
from TensorFlowAnalysis.QFT import *
import TensorFlowAnalysis.Optimisation as Optimisation


def CovariantBaryonDecayAmplitude(p4a, p4b, p4c, p4d, spinor_a, spinor_d, spin_r, parity_r, parity_d, cache=False):
    """
      Covariant amplitude for the decay D->ABC, where D and A are spin-1/2 particles, 
      and the decay proceeds via a resonance R in the AB channel (so that R is a baryon 
      with spin up to 7/2). 
    """

    p4r = p4a + p4b
    mr = Mass(p4r)
    spinor_r = DiracSpinors(spin_r, p4r, mr)
    p4a_t = QFTObject(1, 0, tf.cast(p4a, dtype=CType()))
    p4d_t = QFTObject(1, 0, tf.cast(p4d, dtype=CType()))
    sab = Bar(spinor_a)
    sd = spinor_d

    if parity_r == -1:
        sab = sab*DiracGamma5()
    if parity_d*parity_r == -1:
        sd = DiracGamma5()*sd

    ampl = Complex(Const(0.), Const(0.))
    for pol_r in range(len(spinor_r)):
        sr = spinor_r[pol_r]
        srb = Bar(spinor_r[pol_r])

        if spin_r == 1:
            ampl += ((sab*sr)*(srb*sd)).tensor
        if spin_r == 3:
            ampl += (((sab*sr)*p4a_t)*((srb*sd)*p4d_t)).tensor
        if spin_r == 5:
            ampl += ((((sab*sr)*p4a_t)*p4a_t)*(((srb*sd)*p4d_t)*p4d_t)).tensor
        if spin_r == 7:
            ampl += (((((sab*sr)*p4a_t)*p4a_t)*p4a_t) *
                     ((((srb*sd)*p4d_t)*p4d_t)*p4d_t)).tensor

    a = ampl/(2.*tf.cast(mr, dtype=CType()))

    if cache:
        Optimisation.cacheable_tensors += [a]

    return a


def CovariantBaryonBCDecayAmplitude(p4a, p4b, p4c, p4d, spinor_a, spinor_d, spin_r, cache=False):
    """
      Covariant amplitude for the decay D->ABC, where D and A are spin-1/2 particles, 
      and the decay proceeds via a (integral-spin) resonance R in the BC channel 
      (so that R is a meson with spin 0 or 1). 
    """
    p4r = p4b + p4c
    p4diff = p4b - p4c
    mr = Mass(p4r)

#  p4a_t    = QFTObject(1, 0, tf.cast(p4a, dtype = CType()))
#  p4d_t    = QFTObject(1, 0, tf.cast(p4d, dtype = CType()))
    p4diff_t = QFTObject(1, 0, tf.cast(p4diff, dtype=CType()))

    ampl = Complex(Const(0.), Const(0.))

    sab = Bar(spinor_a)
    sd = spinor_d

    if spin_r == 0:
        ampl += (sab*sd).tensor
    if spin_r == 2:
        #    sab2 = sab * DiracGamma() * DiracGamma5()
        sab2 = sab * DiracGamma()
        proj = BosonProjector(2, p4r, mr)
        ampl += (((sab2 % sd)*proj)*p4diff_t).tensor

#  a = ampl/(2.*tf.cast(mr, dtype = CType()))
    a = ampl

    if cache:
        Optimisation.cacheable_tensors += [a]

    return a
