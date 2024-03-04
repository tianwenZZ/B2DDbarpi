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

from TensorFlowAnalysis.Interface import *
from ROOT import TVirtualFitter, TNtuple, TH1, TH2, TH3,TMath
import math
import numpy as np
import array
import tensorflow as tf
import tensorflow.compat.v1 as tf1

version = tf.__version__.split(".")
if int(version[0]) == 1 and int(version[1]) < 10:
    from tensorflow import Variable as VariableClass
else:
    from tensorflow.python.ops.resource_variable_ops import ResourceVariable as VariableClass


cacheable_tensors = []


class FitParameter(VariableClass):
    """ 
      Class for fit parameters, derived from TF Variable class. 
    """

    def __init__(self, name, init_value, lower_limit=0., upper_limit=0., step_size=1e-6):
        """
          Constructor. 
            name : name of the parameter (passed on to MINUIT)
            init_value : starting value
            lower_limit : lower limit
            upper_limit : upper limit
            step_size : step size (set to 0 for fixed parameters)
        """
        VariableClass.__init__(self, init_value, dtype=FPType())
        self.init_value = init_value
        self.par_name = name
        self.step_size = step_size
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.placeholder = tf1.placeholder(self.dtype, shape=self.get_shape())
        self.update_op = self.assign(self.placeholder)
        self.prev_value = None
        self.error = 0.
        self.positive_error = 0.
        self.negative_error = 0.
        self.fitted_value = init_value
        self.fixed = False

    def update(self, session, value):
        """
          Update the value of the parameter. Previous value is remembered in self.prev_value
          and TF update is called only if the value is changed. 
            session : TF session
            value   : new value
        """
        if value != self.prev_value:
            session.run(self.update_op, {self.placeholder: value})
            self.prev_value = value

    def fix(self):
        self.fixed = True

    def float(self):
        self.fixed = False

    def setFixed(self, fixed):
        self.fixed = fixed

    def floating(self):
        """
          Return True if the parameter is floating (step size>0)
        """
        return self.step_size > 0 and not self.fixed

    def randomise(self, session, minval=None, maxval=None, seed=None):
        """
          Randomise the initial value and update the tf variable value
        """
        if seed:
            np.random.seed(seed)
        if minval == None:
            minval = self.lower_limit
        if maxval == None:
            maxval = self.upper_limit
        val = np.random.uniform(minval, maxval)
        self.init_value = val
        self.update(session, val)


def Switches(size):
    """
      Create the list of switches (flags that control the components of the PDF for use with e.g. fit fractions)
        size : number of components of the PDF
    """
    p = [tf1.placeholder_with_default(Const(1.), shape=()) for i in range(size)]
    return p


def FillNTuple(tupname, data, names):
    """
      Create and fill ROOT NTuple with the data sample. 
        tupname : name of the NTuple
        data : data sample
        names : names of the NTuple variables
      WARNING: This function is SLOW! Better use similar functionality in root_numpy package
        (functions array2tree or array2root)
    """
    variables = ""
    for n in names:
        variables += "%s:" % n
    variables = variables[:-1]
    values = len(names)*[0.]
    avalues = array.array('f', values)
    nt = TNtuple(tupname, "", variables)
    for d in data:
        for i in range(len(names)):
            avalues[i] = d[i]
        nt.Fill(avalues)
    nt.Write()


def ReadNTuple(ntuple, variables, nevents=-1):
    """
      Return a numpy array with the values from TNtuple. 
        ntuple : input TNtuple
        variables : list of ntuple variables to read
        nevents : number of events to read, if -1 all events are read
        WARNING: This function is SLOW! Better use similar functionality in root_numpy package
        (functions tree2array or root2array)

    """
    data = []
    code_list = []
    for v in variables:
        code_list += [compile("i.%s" % v, '<string>', 'eval')]
    if nevents < 0:
        nentries = ntuple.GetEntries()
    else:
        if nevents > ntuple.GetEntries():
            nentries = ntuple.GetEntries()
        else:
            nentries = nevents
    nvars = len(variables)
    array = np.zeros((nentries, nvars))
    for n, i in enumerate(ntuple):
        if n == nentries:
            break
        for m, v in enumerate(code_list):
            array[n][m] = eval(v)
        if n % 100000 == 0:
            print(n, "/", nentries)
    return array


def Gradient(function):
    """
      Returns TF graph for analytic gradient of the input function wrt all floating variables
    """
    tfpars = tf1.trainable_variables()                      # Create TF variables
    # List of floating parameters
    float_tfpars = [p for p in tfpars if p.floating()]
    # Get analytic gradient
    return tf.gradients(function, float_tfpars)


def LoadData(sess, phsp, name, data):
    """
      Load data to TF machinery and return a TF variable corresponding to it
      (to be further used for model fitting). 
        sess   : TF session
        phsp   : phase space object for data
        name   : name for the variable and placeholder
        data   : 2D numpy array with data to be loaded
        return value : TF variable containing data
    """
    placeholder = phsp.Placeholder(name)
    shape = data.shape
    variable = tf.get_variable(name, shape=shape, dtype=FPType(), 
                            initializer=tf.constant_initializer(0.0), trainable=False)
    initializer = variable.assign(placeholder)
    sess.run(initializer, feed_dict={placeholder: data})
    return variable


def AddCacheableTensor(t):
    global cacheable_tensors
    cacheable_tensors += [t]


def RandomiseFitParameters(session):
    tfpars = tf1.trainable_variables()                      # Create TF variables
    # List of floating parameters
    float_tfpars = [p for p in tfpars if p.floating()]
    for p in float_tfpars:
        p.randomise(session)


def RunMinuit(sess, nll, feed_dict=None, call_limit=50000, useGradient=True,
              gradient=None, printout=50, tmpFile="tmp_result.txt",
              runHesse=False, runMinos=False,
              options=None, run_metadata=None):
    """
      Perform MINUIT minimisation of the negative likelihood. 
        sess         : TF session
        nll          : graph for negitive likelihood to be minimised
        feed_dict    : Dictionary of feeds for placeholders (or None if data is already loaded by LoadData)
        call_limit   : limit on number of calls for MINUIT
        gradient     : external gradient graph. If None and useGradient is not False, will be 
                       calculated internally
        useGradient  : flag to control the use of analytic gradient while fitting: 
                       None or False   : gradient is not used
                       True or "CHECK" : analytic gradient will be checked with finite elements, 
                                         and will be used if they match
                       "FORCE"         : analytic gradient will be used regardless. 
        printout     : Printout frequency 
        tmpFile      : Name of the file with temporary results (updated every time printout is called)
        runHesse     ; Run HESSE after minimisation
        runMinos     : Run MINOS after minimisation
        options      : additional options to pass to TF session run
        run_metadata : metadata to pass to TF session run
    """

    global cacheable_tensors

    tfpars = tf1.trainable_variables()     # Create TF variables
    # List of floating parameters
    float_tfpars = [p for p in tfpars if p.floating()]

    if useGradient and gradient is None:
        # Get analytic gradient
        gradient = tf.gradients(nll, float_tfpars)

    cached_data = {}

    fetch_list = []
    for i in cacheable_tensors:
        if i not in cached_data:
            fetch_list += [i]
    if feed_dict:
        feeds = dict(feed_dict)
    else:
        feeds = None
    for i in cacheable_tensors:
        if i in cached_data:
            feeds[i] = cached_data[i]

    # Calculate tensors to be cached
    fetch_data = sess.run(fetch_list, feed_dict=feeds)

    for i, d in zip(fetch_list, fetch_data):
        cached_data[i] = d

    if feed_dict:
        feeds = dict(feed_dict)
    else:
        feeds = None
    for i in cacheable_tensors:
        if i in cached_data:
            feeds[i] = cached_data[i]

    def fcn(npar, gin, f, par, istatus):                  # MINUIT fit function
        for i in range(len(float_tfpars)): float_tfpars[i].update(sess, par[i])

        f.value = sess.run(nll, feed_dict=feeds, options=options,
                        run_metadata=run_metadata)  # Calculate log likelihood

        if istatus == 2:            # If gradient calculation is needed
            dnll = sess.run(gradient, feed_dict=feeds, options=options,
                            run_metadata=run_metadata)  # Calculate analytic gradient
            for i in range(len(float_tfpars)):
                gin[i] = dnll[i]  # Pass gradient to MINUIT
        #fcn.n += 1
        #if fcn.n % printout == 0:
        #    print("  Iteration ", fcn.n, ", Flag=", istatus,
        #          " NLL=", f[0], ", pars=", sess.run(float_tfpars))
        #    tmp_results = {'loglh': f[0], "status": -1}
        #    for n, p in enumerate(float_tfpars):
        #        tmp_results[p.par_name] = (p.prev_value, 0.)
        #    WriteFitResults(tmp_results, tmpFile)

    #fcn.n = 0
    minuit = TVirtualFitter.Fitter(
        0, len(tfpars))        # Create MINUIT instance
    minuit.Clear()
    minuit.SetFCN(fcn)
    # Auxiliary array for MINUIT parameters
    arglist = array.array('d', 10*[0.])

    for n, p in enumerate(float_tfpars):  # Declare fit parameters in MINUIT
        step_size = p.step_size
        lower_limit = p.lower_limit
        upper_limit = p.upper_limit
        if not step_size:
            step_size = 1e-6
        if not lower_limit:
            lower_limit = 0.
        if not upper_limit:
            upper_limit = 0.
        minuit.SetParameter(n, p.par_name, p.init_value,
                            step_size, lower_limit, upper_limit)

    arglist[0] = 0.5
    # Set error definition for neg. likelihood fit
    minuit.ExecuteCommand("SET ERR", arglist, 1)
    if useGradient == True or useGradient == "CHECK":
        minuit.ExecuteCommand("SET GRA", arglist, 0)  # Ask analytic gradient
    elif useGradient == "FORCE":
        arglist[0] = 1
        minuit.ExecuteCommand("SET GRA", arglist, 1)  # Ask analytic gradient
    arglist[0] = call_limit                       # Set call limit
    minuit.ExecuteCommand("MIGRAD", arglist, 1)   # Perform minimisation
    #  minuit.ExecuteCommand("IMP", arglist, 1)   # Perform minimisation
    #  minuit.ExecuteCommand("SIMPLEX", arglist, 1)   # Perform minimisation

    minuit.ExecuteCommand("SET NOG", arglist, 0)  # Ask no analytic gradient

    if runHesse:
        minuit.ExecuteCommand("HESSE", arglist, 1)

    if runMinos:
        minuit.ExecuteCommand("MINOS", arglist, 1)

    results = {}                                  # Get fit results and update parameters
    for n, p in enumerate(float_tfpars):
        p.update(sess, minuit.GetParameter(n))
        p.fitted_value = minuit.GetParameter(n)
        p.error = minuit.GetParError(n)
        if runMinos:
            eplus = array.array("d", [0.])
            eminus = array.array("d", [0.])
            eparab = array.array("d", [0.])
            globcc = array.array("d", [0.])
            minuit.GetErrors(n, eplus, eminus, eparab, globcc)
            p.positive_error = eplus[0]
            p.negative_error = eminus[0]
            results[p.par_name] = (
                p.fitted_value, p.error, p.positive_error, p.negative_error)
        else:
            results[p.par_name] = (p.fitted_value, p.error)

    # Get status of minimisation and NLL at the minimum
    maxlh = array.array("d", [0.])
    edm = array.array("d", [0.])
    errdef = array.array("d", [0.])
    nvpar = array.array("i", [0])
    nparx = array.array("i", [0])
    fitstatus = minuit.GetStats(maxlh, edm, errdef, nvpar, nparx)

    # return fit results
    results["loglh"] = maxlh[0]
    results["status"] = fitstatus
    #results["iterations"] = fcn.n
    return results


def InitialValues():
    """
      Return initial values of free parameters in the same structure 
      as for the fit result. 
    """
    tfpars = tf1.trainable_variables()                      # Create TF variables
    # List of floating parameters
    float_tfpars = [p for p in tfpars if p.floating()]
    results = {}
    for n, p in enumerate(float_tfpars):
        results[p.par_name] = (p.init_value, p.step_size)
    results["loglh"] = 0.
    results["status"] = 0
    results["iterations"] = 0
    return results


def WriteFitResults(results, filename):
    """
      Write the dictionary of fit results to text file
        results : fit results as returned by MinuitFit
        filename : file name
    """
    tfpars = tf1.trainable_variables()  # Create TF variables
    float_tfpars = [p for p in tfpars if p.floating()]
    f = open(filename, "w")
    for p in float_tfpars:
        s = "%s " % p.par_name
        for i in results[p.par_name]:
            s += "%f " % i
        f.write(s + "\n")
    s = "loglh %f %d" % (results["loglh"], results["status"])
    f.write(s + "\n")
    f.close()


def ReadFitResults(sess, filename):
    """
      Read the dictionary of fit results from text file
        sess     : TF session
        filename : file name
    """
    print("Reading results from ", filename)
    tfpars = tf1.trainable_variables()  # Create TF variables
    float_tfpars = [p for p in tfpars if p.floating()]
    par_dict = {}
    for i in float_tfpars:
        par_dict[i.par_name] = i
    try:
        f = open(filename, "r")
    except:
        print("Input file not found!")
        return
    for l in f:
        ls = l.split()
        name = ls[0]
        value = float(ls[1])
        error = float(ls[2])
        if name in par_dict.keys():
            print(name, " = ", value)
            par_dict[name].update(sess, value)
            par_dict[name].init_value = value
            par_dict[name].step_size = error/10.
    f.close()


def CalculateFitFractions(sess, pdf, x, switches, norm_sample):
    """
      Calculate fit fractions for PDF components
        sess        : TF session
        pdf         : PDF graph
        x           : phase space placeholder used for PDF definition
        switches    : list of switches
        norm_sample : normalisation sample. Not needed if external integral is provided
    """
    pdf_norm = sess.run(pdf, feed_dict={x: norm_sample})
    total_int = np.sum(pdf_norm)
    fit_fractions = []
    #print("(CalculateFitFractions) Total number of switches:=",len(switches))
    for i in range(len(switches)):
        fdict = {}
        for j in range(len(switches)):
            fdict[switches[j]] = 0.
        fdict[switches[i]] = 1.
        fdict[x] = norm_sample
        pdf_norm = sess.run(pdf, feed_dict=fdict)
        part_int = np.sum(pdf_norm)
        #print("(CalculateFitFractions) component ",i,"integral:=",part_int,"total:=",total_int)
        fit_fractions += [part_int/total_int]
    return fit_fractions

def CalculateFitFractionsIJ(sess, pdf, x, switches, norm_sample):
    """
      Calculate fit fractions for PDF components
        sess        : TF session
        pdf         : PDF graph
        x           : phase space placeholder used for PDF definition
        switches    : list of switches
        norm_sample : normalisation sample. Not needed if external integral is provided
    """
    pdf_norm = sess.run(pdf, feed_dict={x: norm_sample})
    total_int = np.sum(pdf_norm)
    fit_fractions = []
    #print("(CalculateFitFractions) Total number of switches:=",len(switches))
    for i in range(len(switches)):
        for j in range(len(switches)):
            fdict = {}
            for k in range(len(switches)):
                fdict[switches[k]] = 0.
            fdict[switches[i]] = 1.
            fdict[switches[j]] = 1.
            fdict[x] = norm_sample
            pdf_norm = sess.run(pdf, feed_dict=fdict)
            part_int = np.sum(pdf_norm)
            #print("(CalculateFitFractions) component ",i,"integral:=",part_int,"total:=",total_int)
            fit_fractions += [part_int/total_int]
    return fit_fractions



def CalculateCPFitFractions(sess, pdf_particle, pdf_antiparticle, x, switches, norm_sample):
    """
      Calculate CPC and CPV fit fractions for PDF components
        sess              : TF session
        pdf_particle      : PDF of particle decay
        pdf_antiparticle  : PDF of anti-particle decay
        x                 : phase space placeholder used for PDF definition
        switches          : list of switches
        norm_sample       : normalisation sample. Not needed if external integral is provided
    """

    norm_part = np.sum(sess.run(pdf_particle,     feed_dict={x: norm_sample}))
    norm_anti = np.sum(sess.run(pdf_antiparticle, feed_dict={x: norm_sample}))

    integral = norm_part + norm_anti
    cpv_int = norm_part - norm_anti

    cpc_fit_fractions = []
    cpv_fit_fractions = []
    for i in range(len(switches)):
        fdict = {x: norm_sample}
        for j in range(len(switches)):
            fdict[switches[j]] = 0.
        fdict[switches[i]] = 1.

        norm_part = np.sum(sess.run(pdf_particle,     feed_dict=fdict))
        norm_anti = np.sum(sess.run(pdf_antiparticle, feed_dict=fdict))

        cpc_fit_fractions += [(norm_part + norm_anti)/integral]
        cpv_fit_fractions += [(norm_part - norm_anti)/integral]
    return cpc_fit_fractions, cpv_fit_fractions


def CalculateInterferenceFitFractions(sess, pdf, x, switches, norm_sample):
    """
      Calculate interference fit fractions between pairs of PDF components
        sess        : TF session
        pdf         : PDF graph
        x           : phase space placeholder used for PDF definition
        switches    : list of switches
        norm_sample : normalisation sample. Not needed if external integral is provided
    """
    interference_fit_fractions = {}
    pdf_norm = sess.run(pdf, feed_dict={x: norm_sample})
    total_int = np.sum(pdf_norm)
    for i in range(len(switches)):
        fdict = {}
        # switch everything off
        for j in range(len(switches)):
            fdict[switches[j]] = 0.
        # switch only comp1 on and calc |A1|^2
        fdict[switches[i]] = 1.
        fdict[x] = norm_sample
        part_int_1 = np.sum(sess.run(pdf, feed_dict=fdict))
        # switch everything off
        fdict[switches[i]] = 0.
        for k in range(len(switches)):
            if i != k and tuple(sorted([i, k])) not in interference_fit_fractions:
                # switch only comp2 on and calculate |A2!^2
                fdict[switches[k]] = 1.
                part_int_2 = np.sum(sess.run(pdf, feed_dict=fdict))
                # switch both comp1 and comp2 on and rest off to calc |A1+A2|^2
                fdict[switches[i]] = 1.
                part_int_12 = np.sum(sess.run(pdf, feed_dict=fdict))
                # calculate 2*Re(A1conj*A2) = |A1+A2|^2 - |A1|^2 - |A2!^2
                interference_fit_fractions[(i, k)] = (
                    part_int_12 - part_int_1 - part_int_2)/total_int
                # switch everything off
                fdict[switches[i]] = 0.
                fdict[switches[k]] = 0.
    return interference_fit_fractions


def WriteFitFractions(fit_fractions, names, filename):
    """
      Write fit fractions to text file
        fit_fractions : list of fit fractions returned by FitFractions
        names : list of component names
        filename : file name
    """
    f = open(filename, "w")
    sum_fit_fractions = 0.
    for n, ff in zip(names, fit_fractions):
        s = "%s %f" % (n, ff)
        print(s)
        f.write(s + "\n")
        sum_fit_fractions += ff
    s = "Sum %f" % sum_fit_fractions
    print(s)
    f.write(s + "\n")
    f.close()

def WriteFitFractionsIJ(fit_fractions, filename):
    """
      Write fit fractions to text file
        fit_fractions : list of fit fractions returned by FitFractions
        names : list of component names
        filename : file name
    """
    f = open(filename, "w")
    row_col = TMath.Sqrt(len(fit_fractions))
    for ii in range(len(fit_fractions)):
        s = "%0.5f\t" % (fit_fractions[ii])
        if (ii+1)%row_col==0: s+="\n"
        f.write(s )
    f.close()



def LoadNormSample(nt, var, nevents=-1, majorant=-1):
    """
      Return a normalization sample, thinked for efficiency folding using reconstructed simulation
      No filtering at this stage, this method corresponds to DalitzPhaseSpace.UnfilteredSample
        nt  : ROOT ntuple
        var : list of tree branches to be read
        nevents : number of events to load
    """
    sample = ReadNTuple(nt, var, nevents)
    if majorant > 0:
        sample = np.transpose(np.array(sample))
        sample = np.vstack([sample, np.random.uniform(
            0., majorant, sample.size/len(var)).astype('d')])
        sample = np.transpose(np.array(sample))

    return sample
