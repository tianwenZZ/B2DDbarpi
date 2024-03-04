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
from math import sqrt


class QFTObject:
    """
      Class representing QFT object: a multidimensional TF tensor which represents a list of 
      tensors (in a mathematical sense) with several Lorentz and one or two spinor indices. 
      The first (outermost) dimension corresponds to the "event" or a "candidate" (unless the 
      tensor is declared "constant" in the constructor), followed by an arbitrary number (0-...) 
      of Lorentz dimensions and 0-2 Dirac spinor dimensions. 
    """

    def __init__(self, lorentzRank, spinorStructure, tensor, const=False):
        """
          Constructor for QFT object. 
            lorentzRank : Number of Lorentz indices
            spinorStructure : code representing a spinor structure of the tensor: 
              0 - Dirac scalar (no spinor degrees of freedom)
              1 - Dirac 4-spinor (1 spinor index)
              2 - Dirac anti-4-spinor (1 spinor index)
              3 - Dirac 4x4 matrix (2 spinor indices)
            tensor : TF tensor used for initialisation. Should be of rank (1+lorentzRank+spinorRank). 
                     The first dimension (if const==False) corresponds to "event" and can be of arbitrary size, 
                     while all other dimensions should be of the size 4 (Lorentz space-time or Dirac
                     spinor components). For Lorentz dimensions, x-z correspond to indices 0-2, 
                     time has index 3
            const : Boolean flag, if True, the tensor does not depend on "event" (is constant), 
                    otherwise the first (innermost) dimension corresponds to "event". 
        """
        self.lorentzRank = lorentzRank
        self.spinorStructure = spinorStructure
        if lorentzRank < 0:
            raise(ValueError, "Number of Lorentz indices must be positive")
        if spinorStructure not in [0, 1, 2, 3]:
            raise(ValueError, "Spinor structure must be an integer in range 0-3")
        self.tensor = tensor
        self.const = const

    def spinorRank(self):
        """
          Return spinor rank depending on spinor structure 
          (rank 0 for structure 0, rank 1 for structures 1,2, rank 2 for structure 3). 
        """
        srank = 0
        if self.spinorStructure == 1 or self.spinorStructure == 2:
            srank = 1
        if self.spinorStructure == 3:
            srank = 2
        return srank

    def rank(self):
        """
          Return overall rank of the tensor including Lorentz and spinor degrees of freedom, 
          but excluding "event" dimension. 
        """
        return self.lorentzRank + self.spinorRank()

    def einsum(self, formula, *args):
        """
          Extension of tf.einsum to support ellipsis ("..." for an arbitrary number of indices 
          which should not be contracted). 
        """
        index_names = "bcdefghuvwxyz"  # Pool of indices to be used to replace ellipsis
        nindex = 0
        replacements = ""  # list of indices actually used
        (left, right) = formula.split("->")
        inputs = left.split(",")
        new_formula = ""
        for i, a in zip(inputs, args):
            if i.find("...") >= 0:
                explicit_dims = len(i)-3
                rank = len(a.get_shape())
                nrepl = rank - explicit_dims
                repl = index_names[nindex:nindex + nrepl]
                nindex += nrepl
                replacements += repl
                imod = i.replace("...", repl)
                new_formula += imod + ","
#        print "Replaced ... with %s, new input is %s, all replacements is %s" % (repl, imod, replacements)
            else:
                new_formula += i + ","
        new_formula = new_formula[:-1] + "->" + \
            right.replace("...", replacements)
        return tf.einsum(new_formula, *args)

    def __mod__(self, p2):
        """
          Outer product. p1 and p2 can have arbitrary number of Lorentz indices. 
        """
        lrank1 = self.lorentzRank
        lrank2 = p2.lorentzRank

        if self.spinorStructure == 1 and p2.spinorStructure == 3:
            raise(ValueError, "Cannot multiply spinor by matrix")
        if self.spinorStructure == 3 and p2.spinorStructure == 2:
            raise(ValueError, "Cannot multiply matrix by anti-spinor")

        m1 = self.tensor
        m2 = p2.tensor

        if self.spinorStructure == 0 and p2.spinorStructure == 0:
            # Multiply two Dirac scalars
            f1 = "..."
            f2 = "..."
            r = "..."
            spinor = 0

        if self.spinorStructure in [1, 2] and p2.spinorStructure == 0:
            # Multiply Dirac (anti)spinor by Dirac scalar
            f1 = "...i"
            f2 = "..."
            r = "...i"
            spinor = self.spinorStructure

        if self.spinorStructure == 0 and p2.spinorStructure in [1, 2]:
            # Multiply Dirac scalar by Dirac (anti)spinor
            f1 = "..."
            f2 = "...i"
            r = "...i"
            spinor = p2.spinorStructure

        if self.spinorStructure == 3 and p2.spinorStructure == 0:
            # Multiply Dirac matrix by Dirac scalar
            f1 = "...ij"
            f2 = "..."
            r = "...ij"
            spinor = 3

        if self.spinorStructure == 0 and p2.spinorStructure == 3:
            # Multiply Dirac scalar by Dirac matrix
            f1 = "..."
            f2 = "...ij"
            r = "...ij"
            spinor = 3

        if self.spinorStructure == 1 and p2.spinorStructure == 2:
            # Multiply spinor by antispinor (-> matrix)
            f1 = "..."
            f2 = "..."
            r = "..."
            spinor = 3

        if self.spinorStructure == 2 and p2.spinorStructure == 1:
            # Multiply antispinor by spinor (-> Dirac scalar)
            f1 = "...i"
            f2 = "...i"
            r = "..."
            spinor = 0

        if self.spinorStructure == 3 and p2.spinorStructure == 1:
            # Multiply matrix by spinor (-> Dirac spinor)
            f1 = "...ij"
            f2 = "...j"
            r = "...i"
            spinor = 1

        if self.spinorStructure == 2 and p2.spinorStructure == 3:
            # Multiply antispinor by matrix (-> Dirac antispinor)
            f1 = "...i"
            f2 = "...ij"
            r = "...j"
            spinor = 2

        if self.spinorStructure == 3 and p2.spinorStructure == 3:
            # Multiply antispinor by matrix (-> Dirac antispinor)
            f1 = "...ij"
            f2 = "...jk"
            r = "...ik"
            spinor = 3

        # Add "candidate" index if either of tensors is not constant
        if not self.const:
            f1 = "a" + f1
        if not p2.const:
            f2 = "a" + f2
        if not self.const or not p2.const:
            r = "a" + r

        m = self.einsum("%s,%s->%s" % (f1, f2, r), m1, m2)

        return QFTObject(lrank1+lrank2, spinor, m, const=self.const and p2.const)

    def __rmul__(self, p2):
        """
          Right-product, should only be called if left-hand side is not a QFT object. 
        """
        if not isinstance(p2, QFTObject):
            return QFTObject(self.lorentzRank, self.spinorStructure, self.tensor*p2, const=self.const)
        else:
            return None  # This should not happen

    def __mul__(self, p2):
        """
          Product with contraction of 1st Lorentz indices of the two operands. 
        """
        if not isinstance(p2, QFTObject):
            return QFTObject(self.lorentzRank, self.spinorStructure, self.tensor*p2, const=self.const)

        lrank1 = self.lorentzRank
        lrank2 = p2.lorentzRank
        if lrank1 == 0 or lrank2 == 0:
            return (self % p2)

        if self.spinorStructure == 1 and p2.spinorStructure == 3:
            raise(ValueError, "Cannot multiply spinor by matrix")
        if self.spinorStructure == 3 and p2.spinorStructure == 2:
            raise(ValueError, "Cannot multiply matrix by anti-spinor")

        m1 = self.tensor
        m2 = p2.tensor

        if self.spinorStructure == 0 and p2.spinorStructure == 0:
            # Multiply two Dirac scalars
            f1 = "...m"
            f2 = "...n"
            r = "..."
            spinor = 0

        if self.spinorStructure in [1, 2] and p2.spinorStructure == 0:
            # Multiply Dirac (anti)spinor by Dirac scalar
            f1 = "...mi"
            f2 = "...n"
            r = "...i"
            spinor = self.spinorStructure

        if self.spinorStructure == 0 and p2.spinorStructure in [1, 2]:
            # Multiply Dirac (anti)spinor by Dirac scalar
            f1 = "...m"
            f2 = "...ni"
            r = "...i"
            spinor = p2.spinorStructure

        if self.spinorStructure == 3 and p2.spinorStructure == 0:
            # Multiply Dirac (anti)spinor by Dirac scalar
            f1 = "...mij"
            f2 = "...n"
            r = "...ij"
            spinor = 3

        if self.spinorStructure == 0 and p2.spinorStructure == 3:
            # Multiply Dirac (anti)spinor by Dirac scalar
            f1 = "...m"
            f2 = "...nij"
            r = "...ij"
            spinor = 3

        if self.spinorStructure == 1 and p2.spinorStructure == 2:
            # Multiply spinor by antispinor (-> matrix)
            f1 = "...mi"
            f2 = "...nj"
            r = "...ij"
            spinor = 3

        if self.spinorStructure == 2 and p2.spinorStructure == 1:
            # Multiply antispinor by spinor (-> Dirac scalar)
            f1 = "...mi"
            f2 = "...ni"
            r = "..."
            spinor = 0

        if self.spinorStructure == 3 and p2.spinorStructure == 1:
            # Multiply matrix by spinor (-> Dirac spinor)
            f1 = "...mij"
            f2 = "...nj"
            r = "...i"
            spinor = 1

        if self.spinorStructure == 2 and p2.spinorStructure == 3:
            # Multiply antispinor by matrix (-> Dirac antispinor)
            f1 = "...mi"
            f2 = "...nij"
            r = "...j"
            spinor = 2

        if self.spinorStructure == 3 and p2.spinorStructure == 3:
            # Multiply antispinor by matrix (-> Dirac antispinor)
            f1 = "...mij"
            f2 = "...njk"
            r = "...ik"
            spinor = 3

        # Add "candidate" index if either of tensors is not constant
        if not self.const:
            f1 = "a" + f1
        if not p2.const:
            f2 = "a" + f2
        if not self.const or not p2.const:
            r = "a" + r

        m = self.einsum("%s,mn,%s->%s" % (f1, f2, r),
                        m1, self.metricTensor(), m2)

        return QFTObject(lrank1+lrank2-2, spinor, m, const=self.const and p2.const)

    def __or__(self, p2):
        """
          Product with contraction of all Lorentz indices of the two operands. 
        """
        raise(TypeError, "Not implemented. ")
        return self

    def __sub__(self, p2):
        """
          Difference of two operands. If one of the operands is a Dirac matrix and another is a 
          Dirac scalar, assume unit matrix in spinor space. 
        """
        if p2 == 0.:
            return self
        if not isinstance(p2, QFTObject) and self.lorentzRank == 0:
            return self - p2*QFTObject(0, 2, self.spinorUnity(0))
        lrank1 = self.lorentzRank
        lrank2 = p2.lorentzRank
        srank1 = self.spinorRank()
        srank2 = p2.spinorRank()
        if lrank1 != lrank2:
            raise(ValueError, "Tensors should have the same Lorentz structure")
        if not (srank1 != srank2 or not (srank1 == 0 and srank2 == 3) or not (srank2 == 0 and srank1 == 3)):
            raise(ValueError, "Tensors should have consistent spinor structure")
        m1 = self.tensor
        m2 = p2.tensor
        sstruct = self.spinorStructure
        if self.const:
            m1 = tf.expand_dims(m1, 0)
        if p2.const:
            m2 = tf.expand_dims(m2, 0)
        if srank1 != srank2:
            if srank1 == 0:
                m1 = tf.expand_dims(m1, 1 + lrank1)
                m1 = tf.expand_dims(m1, 1 + lrank1)
                m1 *= self.spinorUnity(lrank1)
                sstruct = p2.spinorStructure
            if srank2 == 0:
                m2 = tf.expand_dims(m2, 1 + lrank2)
                m2 = tf.expand_dims(m2, 1 + lrank2)
                m2 *= self.spinorUnity(lrank2)
        m = m1 - m2
        const = self.const and p2.const
        if const:
            m = tf.squeeze(m, 0)
        return QFTObject(lrank1, sstruct, m, const=const)

    def __add__(self, p2):
        """
          Sum of two operands. If one of the operands is a Dirac matrix and another is a 
          Dirac scalar, assume unit matrix in spinor space. 
        """
        if p2 == 0.:
            return self
        if not isinstance(p2, QFTObject) and self.lorentzRank == 0:
            return self + p2*QFTObject(0, 2, self.spinorUnity(0))
        lrank1 = self.lorentzRank
        lrank2 = p2.lorentzRank
        srank1 = self.spinorRank()
        srank2 = p2.spinorRank()
        if lrank1 != lrank2:
            raise(ValueError, "Tensors should have the same Lorentz structure")
        if not (srank1 != srank2 or not (srank1 == 0 and srank2 == 3) or not (srank2 == 0 and srank1 == 3)):
            raise(ValueError, "Tensors should have consistent spinor structure")
        m1 = self.tensor
        m2 = p2.tensor
        sstruct = self.spinorStructure
        if self.const:
            m1 = tf.expand_dims(m1, 0)
        if p2.const:
            m2 = tf.expand_dims(m2, 0)
        if srank1 != srank2:
            if srank1 == 0:
                m1 = tf.expand_dims(m1, 1 + lrank1)
                m1 = tf.expand_dims(m1, 1 + lrank1)
                m1 *= self.spinorUnity(lrank1)
                sstruct = p2.spinorStructure
            if srank2 == 0:
                m2 = tf.expand_dims(m2, 1 + lrank2)
                m2 = tf.expand_dims(m2, 1 + lrank2)
                m2 *= self.spinorUnity(lrank2)
        m = m1 + m2
        const = self.const and p2.const
        if const:
            m = tf.squeeze(m, 0)
        return QFTObject(lrank1, sstruct, m, const=const)

    def metricTensor(self):
        """
          Return Lorentz metric tensor. 
        """
        Z = complex(0., 0.)
        pU = complex(1., 0.)
        mU = complex(-1., 0.)
        return tf.constant([[mU, Z, Z, Z], [Z, mU, Z, Z], [Z, Z, mU, Z], [Z, Z, Z, pU]], dtype=CType())

    def spinorUnity(self, lorentzRank):
        """
          Auxiliary function, return unit tensor in spinor space with the "lorentzRank" additional Lorentz indices
        """
        Z = complex(0., 0.)
        pU = complex(1., 0.)
        unity = tf.constant([[pU, Z, Z, Z], [Z, pU, Z, Z], [
                            Z, Z, pU, Z], [Z, Z, Z, pU]], dtype=CType())
        shape = (lorentzRank+1)*[1] + [4, 4]
        return tf.reshape(unity, shape)

    def transpose(self):
        """
          Return transposed QFT object (in spinor space). 
        """
        if self.spinorStructure == 1:
            return QFTObject(self.lorentzRank, 2, self.tensor, const=self.const)
        if self.spinorStructure == 2:
            return QFTObject(self.lorentzRank, 1, self.tensor, const=self.const)
        if self.spinorStructure == 3:
            rank = self.rank()
            if self.const:
                rank += 1
            perm = range(rank)
            # Swap last two indices corresponding to spinor structure
            perm[-2], perm[-1] = perm[-1], perm[-2]
            print("Transpose perm", perm)
            return QFTObject(self.lorentzRank, 3, tf.transpose(self.tensor, perm), const=self.const)
#      return QFTObject(self.lorentzRank, 3, self.tensor )
        return self

    def conjugate(self):
        """
          Return conjugate QFT object
        """
        return QFTObject(self.lorentzRank, self.spinorStructure, tf.conj(self.tensor), const=self.const)

    def adjoint(self):
        """
          Return adjoint QFT object (transposed and conjugated)
        """
        return self.transpose().conjugate()


def LorentzBoostTensor(p4):
    """
      Lorentz boost tensor. 
        p4 - boost vector. The transformation will boost into the rest frame of this vector
    """
    bx = XComponent(p4)/TimeComponent(p4)
    by = YComponent(p4)/TimeComponent(p4)
    bz = ZComponent(p4)/TimeComponent(p4)
    gamma = 1./Sqrt(1. - bx**2 - by**2 - bz**2)
    gamma2 = gamma**2/(gamma + 1.)
    return QFTObject(2, 0, tf.cast(tf.stack([
        tf.stack([bx*bx*gamma2 + 1, bx*by*gamma2,
                  bx*bz*gamma2,     bx*gamma], axis=1),
        tf.stack([bx*by*gamma2,     by*by*gamma2 + 1,
                  by*bz*gamma2,     by*gamma], axis=1),
        tf.stack([bx*bz*gamma2,     by*bz*gamma2,
                  bz*bz*gamma2 + 1, bz*gamma], axis=1),
        tf.stack([bx*gamma,         by*gamma,
                  bz*gamma,         gamma], axis=1)
    ], axis=2), dtype=CType()))


def QFTMetricTensor():
    """
      Return QFT object representing metric tensor in Lorentz space
    """
    Z = complex(0., 0.)
    pU = complex(1., 0.)
    mU = complex(-1., 0.)
    metric = tf.constant([[mU, Z, Z, Z], [Z, mU, Z, Z], [
                         Z, Z, mU, Z], [Z, Z, Z, pU]], dtype=CType())
    return QFTObject(2, 0, metric, const=True)


def DiracGamma():
    """
      Vector of Dirac gamma matrices
    """
    Z = complex(0., 0.)
    pU = complex(1., 0.)
    mU = complex(-1., 0.)
    pI = complex(0., 1.)
    mI = complex(0., -1.)

    gamma0 = [[pU, Z, Z, Z], [Z, pU, Z, Z], [Z, Z, mU, Z], [Z, Z, Z, mU]]
    gamma1 = [[Z, Z, Z, pU], [Z, Z, pU, Z], [Z, mU, Z, Z], [mU, Z, Z, Z]]
    gamma2 = [[Z, Z, Z, mI], [Z, Z, pI, Z], [Z, pI, Z, Z], [mI, Z, Z, Z]]
    gamma3 = [[Z, Z, pU, Z], [Z, Z, Z, mU], [mU, Z, Z, Z], [Z, pU, Z, Z]]

    return QFTObject(1, 3, tf.constant([gamma1, gamma2, gamma3, gamma0], dtype=CType()), const=True)


def DiracGamma5():
    """
      Dirac gamma5 matrix
    """
    Z = complex(0., 0.)
    pU = complex(1., 0.)
    gamma5 = [[Z, Z, pU, Z], [Z, Z, Z, pU], [pU, Z, Z, Z], [Z, pU, Z, Z]]
    return QFTObject(0, 3, tf.constant(gamma5, dtype=CType()), const=True)


def DiracGamma0():
    """
      Dirac gamma0 matrix
    """
    Z = complex(0., 0.)
    pU = complex(1., 0.)
    mU = complex(-1., 0.)
    gamma0 = [[pU, Z, Z, Z], [Z, pU, Z, Z], [Z, Z, mU, Z], [Z, Z, Z, mU]]
    return QFTObject(0, 3, tf.constant(gamma0, dtype=CType()), const=True)


def Bar(spinor):
    """
      Dirac conjugation for an (anti)spinor (adjoint and multiplied by gamma0). 
    """
    if spinor.spinorStructure == 1:
        return spinor.adjoint()*DiracGamma0()
    if spinor.spinorStructure == 2:
        return DiracGamma0()*spinor.adjoint()
    return None


def PolarisationVectors(spin, p4, mass):
    """
      Create basis of polarisation vectors
        spin : spin of the state
        p4   : 4-momentum of the state 
        mass : mass of the state. If mass=0, make sure that there
               is no longitudinal polarisation 
    """
    if spin % 2 == 1:
        raise(ValueError, "Spin should be integer")
    if spin == 2:
        if not isinstance(mass, float) or mass > 0.:
            boost = LorentzBoostTensor(p4)
            eps1 = QFTObject(1, 0, tf.constant([complex(1./sqrt(2.), 0.), complex(
                0., -1./sqrt(2.)), complex(0., 0.), complex(0., 0.)], dtype=CType()), const=True)
            eps2 = QFTObject(1, 0, tf.constant([complex(0., 0.), complex(
                0., 0.), complex(1., 0.), complex(0., 0.)], dtype=CType()), const=True)
            eps3 = QFTObject(1, 0, tf.constant([complex(-1./sqrt(2.), 0.), complex(
                0., -1./sqrt(2.)), complex(0., 0.), complex(0., 0.)], dtype=CType()), const=True)
            eps1 = eps1 * boost
            eps2 = eps2 * boost
            eps3 = eps3 * boost
        else:
            bx = XComponent(p4)/TimeComponent(p4)
            by = YComponent(p4)/TimeComponent(p4)
            bz = ZComponent(p4)/TimeComponent(p4)
            x = -by/Sqrt(bx**2 + by**2)
            y = bx/Sqrt(bx**2 + by**2)
            c = ZComponent(p4)/Sqrt(XComponent(p4)**2 +
                                    YComponent(p4)**2 + ZComponent(p4)**2)
            s = Sin(Acos(c))
            eps1 = QFTObject(1, 0, tf.stack([Complex(-x*x*(1-c)+c, -x*y*(1-c))/sqrt(2.),
                                             Complex(-x*y*(1-c),   -
                                                     y*y*(1-c)+c)/sqrt(2.),
                                             Complex(y*s,         -
                                                     x*s)/sqrt(2.),
                                             Complex(Zeros(x), Zeros(x))], axis=1))
            eps2 = QFTObject(1, 0, tf.constant([complex(0., 0.), complex(0., 0.), complex(
                0., 0.), complex(0., 0.)], dtype=CType()), const=True)  # No m=0 polarisation
            eps3 = QFTObject(1, 0, tf.stack([Complex(x*x*(1-c)+c, -x*y*(1-c))/sqrt(2.),
                                             Complex(x*y*(1-c),   -y *
                                                     y*(1-c)+c)/sqrt(2.),
                                             Complex(-y*s,         -
                                                     x*s)/sqrt(2.),
                                             Complex(Zeros(x), Zeros(x))], axis=1))
        return [eps1, eps2, eps3]
    else:
        # Recursion with J' = 1 and J' = J-1
        eps1 = PolarisationVectors(2, p4, mass)
        epsJ = PolarisationVectors(spin-2, p4, mass)
        eps = []
        for m in range(-spin, spin+1, 2):
            eps += [None]
            for m1 in [-2, 0, 2]:
                for mJ in range(-spin+2, spin-1, 2):
                    #          print m, mJ, m1
                    deps = complex(Clebsch(2, m1, spin-2, mJ, spin, m),
                                   0.)*(eps1[m1//2+1] % epsJ[mJ//2+spin//2-1])
                    if eps[-1] == None:
                        eps[-1] = deps
                    else:
                        eps[-1] += deps
        return eps


def DiracSpinors(spin, p4, mass):
    if spin % 2 == 0:
        raise(ValueError, "Spin should be half-integer")
    if spin == 1:
        epm = TimeComponent(p4) + mass
        norm = Sqrt(epm)
        zeros = Zeros(norm)
        ne = Complex(norm/epm, zeros)
        psigma1a = Complex(ZComponent(p4),  zeros)
        psigma2a = Complex(XComponent(p4),  YComponent(p4))
        psigma1b = Complex(XComponent(p4), -YComponent(p4))
        psigma2b = Complex(-ZComponent(p4),  zeros)

        spinor_a = QFTObject(0, 1, tf.stack([Complex(norm, zeros), Complex(
            zeros, zeros), psigma1a*ne, psigma2a*ne], axis=1))
        spinor_b = QFTObject(0, 1, tf.stack([Complex(zeros, zeros), Complex(
            norm, zeros), psigma1b*ne, psigma2b*ne], axis=1))
        return [spinor_a, spinor_b]
    else:
        j = spin-1
        ds1 = DiracSpinors(1, p4, mass)
        eps = PolarisationVectors(j, p4, mass)
        ds = []
        for m in range(-spin, spin+1, 2):
            ds += [None]
            for m1 in [-1, 1]:
                im1 = (m1+1)//2
                for mj in range(-j, j+1, 2):
                    imj = (mj+j)//2
#          print m, mj, m1, im1, imj
                    dds = complex(Clebsch(1, m1, spin-1, mj, spin,
                                          m), 0.)*(ds1[im1] % eps[imj])
                    if ds[-1] == None:
                        ds[-1] = dds
                    else:
                        ds[-1] += dds
        return ds


def BosonProjector(spin, p4, m):
    if spin % 2 == 1:
        raise(ValueError, "Spin should be integer")
    if spin == 2:
        if isinstance(m, float) and m > 0.:
            p4t = QFTObject(1, 0, tf.cast(p4, dtype=CType()))
            return (p4t % p4t)*(1./m**2) - QFTMetricTensor()
        else:
            return -1.*QFTMetricTensor()
    else:
        pol = PolarisationVectors(spin, p4, m)
        proj = None
        for p in pol:
            if proj == None:
                proj = p % (p.conjugate())
            else:
                proj += p % (p.conjugate())
        return proj


def FermionProjector(spin, p4, m):
    if spin % 2 == 0:
        raise(ValueError, "Spin should be half-integer")
    if spin == 1:
        p4t = QFTObject(1, 0, tf.cast(p4, dtype=CType()))
        return (p4t*DiracGamma() + m)*(1./(2.*m))
    else:
        pol = DiracSpinors(spin, p4, m)
        proj = None
        for p in pol:
            if proj == None:
                proj = p % Bar(p)
            else:
                proj += p % Bar(p)
        return proj*(1./(2.*m))
