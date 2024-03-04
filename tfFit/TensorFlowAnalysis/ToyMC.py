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


def AcceptRejectSample(density, sample):
    """
      Return toy MC sample graph using accept-reject method
        density : function to calculate density
        sample  : input uniformly distributed sample
    """
    x = sample[:, 0:-1]
    if density:
        r = sample[:, -1]
        return tf.boolean_mask(x, density(x) > r)
    else:
        return x


def CreateAcceptRejectSample(sess, density, x, sample):
    """
      Create toy MC sample using accept-reject method for a density defined as a graph
        sess    : Tf session
        density : density graph
        x       : phase space placeholder used for density graph definition
        sample  : input uniformly distributed sample
      Returns numpy array of generated points
    """
    p = sample[:, 0:-1]
    print("p shape:",p.shape)
    r = sample[:, -1]
    pdf_data = sess.run(density, feed_dict={x: p})
    return p[pdf_data > r]


def MaximumEstimator(density, phsp, size):
    """
      Return the graph for the estimator of the maximum of density function
        density : density function
        phsp : phase space object (should have UniformSample method implemented)
        size : size of the random sample for maximum estimation
    """
    sample = phsp.UniformSample(size)
    return tf.reduce_max(density(sample))


def EstimateMaximum(sess, pdf, x, norm_sample):
    """
      Estimate the maximum of density function defined as a graph
        sess : TF session
        pdf  : density graph
        x    : phase space placeholder used for the definition of the density function
        size : size of the random sample for maximum estimation
      Returns the estimated maximum of the density
    """
    pdf_data = sess.run(pdf, {x: norm_sample})
    return np.nanmax(pdf_data)


def RunToyMC(sess, pdf, x, phsp, size, majorant, chunk=200000, switches=None, seed=None, norm_sample=[], interferences=False):
    """
      Create toy MC sample. To save memory, the sample is generated in "chunks" of a fixed size inside 
      TF session, which are then concatenated. 
        sess : TF session
        pdf : PDF graph
        x   : phase space placeholder used for PDF definition
        phsp : phase space
        size : size of the target data sample (if >0) or number of chunks (if <0)
        majorant : maximum PDF value for accept-reject method
        chunk : chunk size
        switches : optional list of switches for component weights
        norm_sample : if provided use this sample to produce toy MC instead of generating phase-space events
        interferences : set to True if weights to project interferences between all the components contained in switches should be added (requires switches)
    """
    first = True
    length = 0
    nchunk = 0
    nreadevents = 0
    curr_maximum = majorant
    count=0
    phsp_sample = phsp.Filter(x)

    if seed:
        np.random.seed(seed)
    while length < size or nchunk < -size:
        if (norm_sample != []):
            if nreadevents >= len(norm_sample):
                break
            initsample = norm_sample[nreadevents:nreadevents+chunk]
            len_sample = len(initsample)
            initsample = np.transpose(np.array(initsample))
            initsample = np.vstack(
                [initsample, np.random.uniform(0., majorant, len_sample).astype('d')])
            initsample = np.transpose(np.array(initsample))
            nreadevents += len_sample
        else:
            initsample = phsp.UnfilteredSample(chunk, curr_maximum)
        d1 = sess.run(phsp_sample, feed_dict={x: initsample})
        d = CreateAcceptRejectSample(sess, pdf, x, d1)
        v = sess.run(pdf, feed_dict={x: d})
        over_maximum = v[v > curr_maximum]
        if len(over_maximum) > 0:
            new_maximum = np.amax(over_maximum)*1.5
            print("  Updating maximum: %f -> %f. Starting over. " %
                  (curr_maximum, new_maximum))
            first = True
            length = 0
            nchunk = 0
            curr_maximum = new_maximum
            continue
        print("components switches",switches)
        if switches:
            weights = []
#      v = sess.run(pdf, feed_dict = { x : d } )
            for i in range(len(switches)):
                fdict = {}
                #print("length of switches:",len(switches))
                for j in range(len(switches)):
                    fdict[switches[j]] = 0.
                    #print("fdict :",fdict[switches[j]])
                fdict[switches[i]] = 1.
                fdict[x] = d
                v1 = sess.run(pdf, feed_dict=fdict)
                weights += [v1/v]
                count+=1
            # compute interference weights
            # idea: interference = |A+B|^2-|A|^2-|B|^2
            if interferences:
                # loop over all components
                for i in range(len(switches)):
                    # turn all components off
                    for j in range(len(switches)):
                        fdict[switches[j]] = 0.
                    fdict[switches[i]] = 1. # turn the current component on
                    vi = weights[i] # these are the weights to project the current component
                    # loop over all components that come before the current one in switches
                    for k in range(i):
                        fdict[switches[k]] = 1. # turn the second component on
                        vcomb = sess.run(pdf, feed_dict=fdict) # generate weights for the combination of the two components i and k
                        vk = weights[k] # these are the weights to project the second component
                        weights += [vcomb/v-vk-vi] # save the weights
                        fdict[switches[k]] = 0. # turn the second component off again
            d = np.append(d, np.transpose(
                np.array(weights, dtype=np.dtype('f'))), axis=1)

        if first:
            data = d
        else:
            data = np.append(data, d, axis=0)
        #print("data shape:",data.shape)
        first = False
        length += len(d)
        nchunk += 1
        #print("counts:",count)
        print("  Chunk %d, size=%d, inphsp=%d, total length=%d" % (nchunk, len(d), len(d1), length))
    if size > 0:
        return data[:size]
    else:
        return data


def RunToyMC_weighted(sess, pdf, x, phsp, size, chunk=200000, switches=None, seed=None, norm_sample=[]):
    """
      Create toy MC sample. To save memory, the sample is generated in "chunks" of a fixed size inside 
      TF session, which are then concatenated. 
        sess : TF session
        pdf : PDF graph
        x   : phase space placeholder used for PDF definition
        phsp : phase space
        size : size of the target data sample (if >0) or number of chunks (if <0)
        majorant : maximum PDF value for accept-reject method
        chunk : chunk size
        switches : optional list of switches for component weights
        norm_sample : if provided use this sample to produce toy MC instead of generating phase-space events
    """
    first = True
    length = 0
    nchunk = 0
    nreadevents = 0
    count=0
    phsp_sample = phsp.Filter(x)
    #print("length of norm sample:",len(norm_sample))
    if seed:
        np.random.seed(seed)
    while length < size or nchunk < -size:
        if (norm_sample != []):
            if nreadevents >= len(norm_sample):
                break
            initsample = norm_sample[nreadevents:nreadevents+chunk]
            len_sample = len(initsample)
            nreadevents += len_sample
        else:
            initsample = phsp.UnfilteredSample(chunk, majorant)

        d = sess.run(phsp_sample, feed_dict={x: initsample})

        weights = []
        v = sess.run(pdf, feed_dict={x: d})
        weights += [v]
        count+=1

        if switches:
            for i in range(len(switches)):
                fdict = {}
                #print("switch ",i," :",switches[i])
                for j in range(len(switches)):
                    fdict[switches[j]] = 0.
                    #print("fdict: ",fdict[switches[j]])
                fdict[switches[i]] = 1.
                fdict[x] = d
                v1 = sess.run(pdf, feed_dict=fdict)
                weights += [v1]
                count+=1
            d = np.append(d, np.transpose(
                np.array(weights, dtype=np.dtype('f'))), axis=1)

        if first:
            data = d
        else:
            data = np.append(data, d, axis=0)
        #print("data shape:",data.shape)
        first = False
        length += len(d)
        nchunk += 1
        #print("counts:",count)
        #print("size:",size)
        #print("length of weight:",len(data))
        print("  Chunk %d, size=%d, total length=%d" % (nchunk, len(d), length))
    if size > 0:
        return data[:size]
    else:
        return data

def RunFastToyMC(sess, pdf, phsp, size, majorant, chunk=200000, seed=1):
    """
      Create toy MC sample. To save memory, the sample is generated in "chunks" of a fixed size 
            sess : TF session
             pdf : Function returning PDF graph for a given sample as an agrument
            phsp : phase space
            size : size of the target data sample (if >0) or number of chunks (if <0)
        majorant : maximum PDF value for accept-reject method
           chunk : chunk size
            seed : initial random seed. Not initalised if None
    """
    length, nchunk, curr_maximum = 0, 0, majorant
    data = np.empty((0, phsp.Dimensionality()))

    if seed != None : 
        tf.set_random_seed(seed)

    rndsample = AcceptRejectSample(pdf, phsp.Filter(phsp.UnfilteredSampleGraph(chunk, curr_maximum) ))
    vsample = pdf(rndsample)

    def condition(length, size, nchunk):
      return length < size or nchunk < -size

    print(type(length), type(size), type(nchunk))
    while condition(length, size, nchunk):
        d, v = sess.run((rndsample, vsample))
        over_maximum = v[v > curr_maximum]
        if len(over_maximum) > 0:
            new_maximum = sess.run(tf.reduce_max(over_maximum))*1.5
            print(f'  Updating maximum: {curr_maximum} -> {new_maximum}. Starting over.')
            length, nchunk, curr_maximum = 0, 0, new_maximum
            rndsample = AcceptRejectSample(pdf, phsp.Filter(phsp.UnfilteredSampleGraph(chunk, curr_maximum) ))
            vsample = pdf(rndsample)
            data = np.empty((0, phsp.Dimensionality()))
            continue
        data = np.concatenate([data, d], axis=0)
        length += len(d)
        nchunk += 1
        print(f'  Chunk {nchunk}, size={len(d)}, total length={length}')
    return data[:size] if size > 0 else data

def RunToyMC_weightedInter(sess, pdf, x, phsp, size, chunk=200000, switches=None, seed=None, norm_sample=[]):
    """
      Create toy MC sample. To save memory, the sample is generated in "chunks" of a fixed size inside 
      TF session, which are then concatenated. 
        sess : TF session
        pdf : PDF graph
        x   : phase space placeholder used for PDF definition
        phsp : phase space
        size : size of the target data sample (if >0) or number of chunks (if <0)
        majorant : maximum PDF value for accept-reject method
        chunk : chunk size
        switches : optional list of switches for component weights
        norm_sample : if provided use this sample to produce toy MC instead of generating phase-space events
    """
    first = True
    length = 0
    nchunk = 0
    nreadevents = 0
    count=0
    phsp_sample = phsp.Filter(x)
    print("--> length of norm sample:",len(norm_sample))
    if seed:
        np.random.seed(seed)
    while length < size or nchunk < -size:
        if (norm_sample != []):
            if nreadevents >= len(norm_sample):
                break
            initsample = norm_sample[nreadevents:nreadevents+chunk]
            len_sample = len(initsample)
            nreadevents += len_sample
        else:
            initsample = phsp.UnfilteredSample(chunk, majorant)

        d = sess.run(phsp_sample, feed_dict={x: initsample})

        weights = []
        v = sess.run(pdf, feed_dict={x: d})
        weights += [v]
        count+=1

        if switches:
            for i in range(len(switches)):
                for j in range(i,len(switches)):
                    fdict = {}
                    #print("switch (",i,j,") :",switches[i],switches[j])
                    for k in range(len(switches)):
                        fdict[switches[k]] = 0.
                        #print("fdict: ",fdict[switches[j]])
                    fdict[switches[i]] = 1.
                    fdict[switches[j]] = 1.
                    fdict[x] = d
                    v1 = sess.run(pdf, feed_dict=fdict)
                    weights += [v1]
                    count+=1
            d = np.append(d, np.transpose(
                np.array(weights, dtype=np.dtype('f'))), axis=1)

        if first:
            data = d
        else:
            data = np.append(data, d, axis=0)
        #print("data shape:",data.shape)
        first = False
        length += len(d)
        nchunk += 1
        #print("counts:",count)
        #print("size:",size)
        #print("length of weight:",len(data))
        print("  Chunk %d, size=%d, total length=%d" % (nchunk, len(d), length))
    if size > 0:
        return data[:size]
    else:
        return data

