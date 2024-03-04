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

import numpy as np
import tensorflow as tf
import sys
import math

from numpy.lib.recfunctions import append_fields

from root_numpy import fill_hist, rec2array, root2array, array2root
from rootpy.plotting import Hist2D, Hist1D

import rootpy.ROOT as ROOT
from rootpy.io.pickler import dump

from TensorFlowAnalysis.Interface import *
from TensorFlowAnalysis.Extras import SplitArray, LoadTransformArray, TransformArray


def CreateWeightsBiases(n_input, layers, sigma=1., n_output = 1):
    """
      Create arrays of weights and vectors of biases for the multilayer perceptron 
      if a given configuration (with a single output neuron). 
        n_input : number of input neurons
        layers  : list of numbers of neurons in the hidden layers
      output : 
        weights, biases
    """
    n_hidden = [n_input] + layers
    weights = []
    biases = []
    for i in range(len(n_hidden)-1):
        weights += [tf.Variable(sigma*np.random.normal(
            size=[n_hidden[i], n_hidden[i+1]]), dtype=FPType())]
        biases += [tf.Variable(sigma *
                               np.random.normal(size=[n_hidden[i+1]]), dtype=FPType())]
    weights += [tf.Variable(sigma *
                            np.random.normal(size=[n_hidden[-1], n_output]), dtype=FPType())]
    biases += [tf.Variable(sigma*np.random.normal(size=[n_output]), dtype=FPType())]
    return (weights, biases)


def InitWeightsBiases(init):
    """
      Initialise variable weights and biases from numpy array
    """
    init_weights = init[0]
    init_biases = init[1]
    weights = []
    biases = []
    for i in range(len(init_weights)-1):
        weights += [tf.Variable(init_weights[i], dtype=FPType())]
        biases += [tf.Variable(init_biases[i], dtype=FPType())]
    weights += [tf.Variable(init_weights[-1], dtype=FPType())]
    biases += [tf.Variable(init_biases[-1], dtype=FPType())]
    return (weights, biases)


def InitFixedWeightsBiases(init):
    """
      Initialise constant weights and biases from numpy array
    """
    init_weights = init[0]
    init_biases = init[1]
    weights = []
    biases = []
    for i in range(len(init_weights)-1):
        weights += [tf.constant(init_weights[i], dtype=FPType())]
        biases += [tf.constant(init_biases[i], dtype=FPType())]
    weights += [tf.constant(init_weights[-1], dtype=FPType())]
    biases += [tf.constant(init_biases[-1], dtype=FPType())]
    return (weights, biases)


def MultilayerPerceptron(x, weights, biases, multiple = False):
    """
      Multilayer perceptron with fully connected layers defined by matrices of weights and biases. 
      Use sigmoid function as activation. 
    """
    layer = x
    for i in range(len(weights)):
        layer = tf.nn.sigmoid(tf.add(tf.matmul(layer, weights[i]), biases[i]))
    if multiple : 
      return layer
    else : 
      return layer[:, 0]

def L2Regularisation(weights):
    """
      L2 regularisation term for a list of weight matrices
    """
    penalty = 0.
    for w in weights:
        penalty += tf.reduce_sum(tf.square(w))
    return penalty


def TrainSelection(
    sig_file_name,
    bkg_file_name,
    variables,
    path="./",
    learning_rate=0.002,
    training_epochs=10000,
    print_step=50,
    save_step=1000,
    weight_penalty=1.,
    seed=1,
    n_hidden=[32, 8],
    sig_selection="",
    bkg_selection="",
    output="tmp",
    n_bkg=1000.,
    n_sig=1., 
    sig_tree="tree",
    bkg_tree="tree",
    nn_transform=lambda x: x,
    plot=True, 
    fom=lambda x : x[0]/math.sqrt(x[1] + 5./2.)
):
    """
      Train classifier based on multilayer perceptron
    """

    hists = []

    bkg_var_names = [i.bkg_name for i in variables]
    sig_var_names = [i.sig_name for i in variables]
    bkg_transform = {i.bkg_name: i.transform for i in variables}
    sig_transform = {i.sig_name: i.transform for i in variables}

    np.random.seed(seed)
    tf.set_random_seed(seed)

    sig_array = LoadTransformArray(
        sig_file_name, sig_tree, sig_var_names, sig_selection, sig_transform)
    bkg_array = LoadTransformArray(
        bkg_file_name, bkg_tree, bkg_var_names, bkg_selection, bkg_transform)

    sig_array = np.nan_to_num(rec2array(sig_array))
    bkg_array = np.nan_to_num(rec2array(bkg_array))

    sig_train, sig_test = SplitArray(sig_array)
    bkg_train, bkg_test = SplitArray(bkg_array)

    print('Signal sample size = ', sig_train.shape[0])
    print('Backgr sample size = ', bkg_train.shape[0])

    n_input = len(variables)

    (weights, biases) = CreateWeightsBiases(n_input, n_hidden)

    sig_ph = tf.placeholder(FPType(), shape=(None, None))
    bkg_ph = tf.placeholder(FPType(), shape=(None, None))

    bkg_response = MultilayerPerceptron(bkg_ph, weights, biases)
    sig_response = MultilayerPerceptron(sig_ph, weights, biases)
    cost = tf.reduce_sum(tf.square(bkg_response-0.)) + \
        tf.reduce_sum(tf.square(sig_response-1.))
    reg = weight_penalty*L2Regularisation(weights)
    cost += reg

    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(cost)
    init = tf.global_variables_initializer()

    if plot:
        cnv = ROOT.TCanvas("c", "", 1200, 400)
        cnv.Divide(3, 1)

    with tf.Session() as sess:
        sess.run(init)

        print(sig_array, np.any(np.isnan(sig_array)), np.any(np.isinf(sig_array)))
        print(bkg_array, np.any(np.isnan(bkg_array)), np.any(np.isinf(bkg_array)))

        best_cost = 1e10

        for epoch in range(training_epochs):

            _, c, bkg_train_a, sig_train_a = sess.run([train_op, cost, bkg_response, sig_response], feed_dict={
                                                      sig_ph: sig_train, bkg_ph: bkg_train})

            if epoch % print_step == 0:
                ct, r, bkg_test_a, sig_test_a = sess.run(
                    [cost, reg, bkg_response, sig_response], feed_dict={sig_ph: sig_test, bkg_ph: bkg_test})
                s = "epoch=%04d train=%.9f test=%.9f reg=%.9f diff=%.9f ot=%.9f" % (
                    epoch+1, c, ct, r, ct-r, ct-c)
                print(s)
                sys.stdout.flush()

                if plot:
                    sig_train_h = ROOT.Hist(50, 0., 1.)
                    fill_hist(sig_train_h, nn_transform(sig_train_a))
                    bkg_train_h = ROOT.Hist(50, 0., 1.)
                    fill_hist(bkg_train_h, nn_transform(bkg_train_a))
                    sig_test_h = ROOT.Hist(50, 0., 1.)
                    fill_hist(sig_test_h,  nn_transform(sig_test_a))
                    bkg_test_h = ROOT.Hist(50, 0., 1.)
                    fill_hist(bkg_test_h,  nn_transform(bkg_test_a))

                    sig_train_c = sig_train_h.GetCumulative(False)
                    bkg_train_c = bkg_train_h.GetCumulative(False)
                    sig_test_c = sig_test_h.GetCumulative(False)
                    bkg_test_c = bkg_test_h.GetCumulative(False)

                    sig_train_c.Scale(1./sig_train_c.GetMaximum())
                    bkg_train_c.Scale(1./bkg_train_c.GetMaximum())
                    sig_test_c.Scale(1./sig_test_c.GetMaximum())
                    bkg_test_c.Scale(1./bkg_test_c.GetMaximum())

                    bkg_train_h.Scale(1./bkg_train_h.GetSumOfWeights())
                    bkg_test_h.Scale(1./bkg_test_h.GetSumOfWeights())
                    sig_train_h.Scale(1./sig_train_h.GetSumOfWeights())
                    sig_test_h.Scale(1./sig_test_h.GetSumOfWeights())

                    maximum = max(max(sig_train_h.GetMaximum(), sig_test_h.GetMaximum()), max(
                        bkg_train_h.GetMaximum(), bkg_test_h.GetMaximum()))
                    sig_train_h.SetMaximum(maximum*1.2)
                    sig_test_h.SetMaximum(maximum*1.2)
                    bkg_train_h.SetMaximum(maximum*1.2)
                    bkg_test_h.SetMaximum(maximum*1.2)

                    cnv.cd(1)
                    sig_train_h.GetXaxis().SetTitle("NN response")
                    sig_train_h.SetLineWidth(2)
                    sig_train_h.Draw("e")
                    bkg_train_h.SetLineColor(2)
                    bkg_train_h.SetLineWidth(2)
                    bkg_train_h.Draw("hist same")
                    l = ROOT.TLegend(0.55, 0.70, 0.95, 0.9)
                    l.SetFillStyle(0)
                    l.AddEntry(sig_train_h, "Signal", "p")
                    l.AddEntry(bkg_train_h, "Background", "l")
                    l.Draw()

                    cnv.cd(2)
                    sig_train_c.GetXaxis().SetTitle("NN response cut")
                    sig_train_c.GetYaxis().SetTitle("Selection efficiency")
                    sig_train_c.SetMaximum(1.4)
                    sig_train_c.SetLineWidth(2)
                    sig_train_c.SetLineStyle(2)
                    sig_train_c.Draw("l")
                    sig_test_c.SetLineWidth(2)
                    sig_test_c.Draw("l same")
                    bkg_train_c.SetLineColor(2)
                    bkg_train_c.SetLineWidth(2)
                    bkg_train_c.SetLineStyle(2)
                    bkg_train_c.Draw("l same")
                    bkg_test_c.SetLineColor(2)
                    bkg_test_c.SetLineWidth(2)
                    bkg_test_c.Draw("l same")
                    l = ROOT.TLegend(0.55, 0.60, 0.95, 0.9)
                    l.SetFillStyle(0)
                    l.AddEntry(sig_train_c, "Signal train", "l")
                    l.AddEntry(bkg_train_c, "Backgr. train", "l")
                    l.AddEntry(sig_test_c, "Signal test", "l")
                    l.AddEntry(bkg_test_c, "Backgr. test", "l")
                    l.Draw()

                    cnv.cd(3)
                    fom_train = ROOT.Hist(50, 0., 1.)
                    fom_test = ROOT.Hist(50, 0., 1.)
                    for i in range(1, 50+1):
                        try : 
                          fom_train[i] = fom( (n_sig*sig_train_c[i], n_bkg*bkg_train_c[i]) )
                          fom_test[i] = fom( (n_sig*sig_test_c[i], n_bkg*bkg_test_c[i]) )
                        except : 
                          fom_train[0] = 0.
                          fom_test[0] = 0.
                    fom_train.SetLineWidth(2)
                    fom_train.GetXaxis().SetTitle("NN response cut")
                    fom_train.GetYaxis().SetTitle("FoM")
                    fom_train.SetLineColor(4)
                    fom_train.Draw("l")
                    fom_test.SetLineStyle(2)
                    fom_test.SetLineWidth(2)
                    fom_test.SetLineColor(4)
                    fom_test.Draw("l same")
                    l = ROOT.TLegend(0.20, 0.70, 0.46, 0.9)
                    l.SetFillStyle(0)
                    l.AddEntry(fom_train, "Train", "l")
                    l.AddEntry(fom_test, "Test", "l")
                    l.Draw()

                    cnv.Update()

                    hlist = [sig_train_h, sig_test_h, bkg_train_h, bkg_test_h,
                             sig_train_c, sig_test_c, bkg_train_c, bkg_test_c,
                             fom_train, fom_test]
                    dump(hlist, output + ".root")

                if epoch % save_step == 0:
                    if plot:
                        cnv.Print(output + ".pdf")
                    if c < best_cost:
                        best_cost = c
                        np.save(output, sess.run([weights, biases]))
                        f = open(output + ".txt", "w")
                        f.write(s + "\n")
                        f.close()


def ApplyNN(
    path="./",
    prefix="",
    tree="tree",
    datasets=["input"],
    nns=["train.npy"],
    nn_names=['nn'],
    selection="",
    output="output.root",
    background=False,
    nn_transform=lambda x: x,
    variables=None
):
    """
      Apply trained NN classifier to the input ntuple and save the same tree with added NN response
    """

    if not background:
        exp_var_names = [i.sig_name for i in variables[1:]]
        transform = {i.sig_name: i.transform for i in variables[1:]}
    else:
        exp_var_names = [i.bkg_name for i in variables[1:]]
        transform = {i.bkg_name: i.transform for i in variables[1:]}

    wbs = [InitWeightsBiases(np.load(nn, allow_pickle = True)) for nn in nns]

    exp_ph = tf.placeholder(FPType(), shape=(None, None))
    outs = [nn_transform(MultilayerPerceptron(exp_ph, wb[0], wb[1]))
            for wb in wbs]

    init = tf.global_variables_initializer()

    with tf.Session() as sess:

        sess.run(init)

        first = True

        for dataset in datasets:

            exp_file_name = path + prefix + dataset + ".root"

            exp_struct_array = LoadTransformArray(
                exp_file_name, tree, variables = None, selection = selection, transform = None)
            exp_array = TransformArray(
                exp_struct_array, exp_var_names, transform)

            print("Read dataset ", dataset, ", shape ", exp_struct_array.shape)

            nna = sess.run(outs, feed_dict={exp_ph: exp_array})
            for i in range(len(nna)):
                nna[i] = nna[i].astype(dtype=np.float64)
            nn_array = append_fields(exp_struct_array, nn_names, nna)
            if first:
                mode = "recreate"
                first = False
            else:
                mode = "update"
            array2root(nn_array, path + output, mode=mode)


class MultidimDisplay:

    def __init__(self, data_sample, titles, bounds, bins1d=40, bins2d=20, fitbins1d=None, fitbins2d=None, 
                 plots=None, pull=False, adjust_limits = True, normalise_to_data = True, 
                 zrange = None ):

        self.n_input = len(bounds)
        self.plots = plots
        self.n1arr = {}
        self.n2arr = {}
        self.pull = pull

        if not plots:
            self.can = ROOT.TCanvas("c", "c", 1000, 850)
            self.can.Divide(self.n_input, self.n_input, 0.003, 0.003)
        else:
            self.can = {}
            for i in plots:
                if isinstance(i, tuple):
                    self.can[i] = ROOT.TCanvas(
                        "c_%d_%d" % (i[0], i[1]), "", 900, 400)
                    self.can[i].Divide(2, 1)
                else:
                    self.can[i] = ROOT.TCanvas("c_%d" % i, "", 450, 400)

        self.t1 = ROOT.TPaveLabel(0.68, 0.83, 0.85, 0.93, "Data", "NDC")
        self.t1.SetBorderSize(0)
        self.t1.SetFillColor(0)
        self.t2 = ROOT.TPaveLabel(0.65, 0.83, 0.85, 0.93, "Fit", "NDC")
        self.t2.SetBorderSize(0)
        self.t2.SetFillColor(0)

        self.b = ROOT.TBox()
        self.b.SetFillStyle(0)
        self.b.SetLineWidth(1)
        self.b.SetLineColor(2)

        self.hists2d = []
        self.hists1d = []
        self.hists2d_f = []
        self.hists1d_f = []
        self.hists1d_fc = []
        self.pulls = []

        if fitbins2d == None:
            fitbins2d = bins2d
        if fitbins1d == None:
            fitbins1d = bins1d

        self.fitbins1d = fitbins1d
        self.fitbins2d = fitbins2d
        self.bins1d = bins1d
        self.bins2d = bins2d
        self.adjust_limits = adjust_limits
        self.normalise_to_data = normalise_to_data
        self.zrange = zrange

        for i1 in range(self.n_input):
            print(bounds[i1])
            h = ROOT.Hist(bins1d, bounds[i1][0],  bounds[i1][1])
            hf = ROOT.Hist(fitbins1d, bounds[i1][0],  bounds[i1][1])
            hfc = ROOT.Hist(fitbins1d, bounds[i1][0],  bounds[i1][1])
            hp = ROOT.Hist(bins1d, bounds[i1][0],  bounds[i1][1])
            hf.GetXaxis().SetTitle(titles[i1])
            hf.GetYaxis().SetTitle("Entries")
            hf.GetYaxis().SetTitleOffset(1.2)
            hp.GetXaxis().SetTitle(titles[i1])
            hp.GetYaxis().SetTitle("Pull")
            hp.GetYaxis().SetTitleOffset(1.2)
            h.SetMarkerSize(0.6)
            hf.SetLineWidth(3)
            hfc.SetLineWidth(3)
            self.hists1d_f += [hf]
            self.hists1d_fc += [hfc]
            self.hists1d += [h]
            self.pulls += [hp]
            for i2 in range(i1+1, self.n_input):
                h = ROOT.Hist2D(
                    bins2d, bounds[i1][0],  bounds[i1][1], bins2d, bounds[i2][0],  bounds[i2][1])
                hf = ROOT.Hist2D(
                    fitbins2d, bounds[i1][0],  bounds[i1][1], fitbins2d, bounds[i2][0],  bounds[i2][1])
                h.GetXaxis().SetTitle(titles[i1])
                h.GetYaxis().SetTitle(titles[i2])
#        h.GetZaxis().SetTitle("Entries")
                hf.GetXaxis().SetTitle(titles[i1])
                hf.GetYaxis().SetTitle(titles[i2])
#        hf.GetZaxis().SetTitle("Entries")
                self.hists2d_f += [hf]
                self.hists2d += [h]

        n = 0
        for n1 in range(self.n_input):
            self.hists1d[n1].fill_array(data_sample[:, n1])
            for n2 in range(n1+1, self.n_input):
                self.hists2d[n].fill_array(data_sample[:, (n1, n2)])
                self.n1arr[n] = n1
                self.n2arr[n] = n2
                n += 1

        # Draw 2D data projections
        for n in range(len(self.hists2d)):
            self.hists2d[n].Scale(bins2d**2/self.hists2d[n].GetSumOfWeights())
            self.hists2d[n].SetMinimum(0)
            if not plots:
                if self.n_input % 2 == 0:
                    self.can.cd(2*n+1)
                else:
                    self.can.cd(n+1+(n//self.n_input)*self.n_input)
                self.hists2d[n].Draw("zcol")
                self.t1.Draw()
            else:
                n1 = self.n1arr[n]
                n2 = self.n2arr[n]
                if (n1, n2) in self.can.keys():
                    self.can[(n1, n2)].cd(1)
                    self.hists2d[n].Draw("zcol")
                    self.t1.Draw()

    def draw(self, norm_sample, norm_pdf, outfile):

        subpads = []
        l = ROOT.TLine()

        for i in self.hists1d_f:
            i.Reset()
        for i in self.hists2d_f:
            i.Reset()
        n = 0
        for n1 in range(self.n_input):
            self.hists1d_f[n1].fill_array(norm_sample[:, n1], norm_pdf)
            for n2 in range(n1+1, self.n_input):
                self.hists2d_f[n].fill_array(
                    norm_sample[:, (n1, n2)], norm_pdf)
                n += 1

        # Draw 2D fit projections
        for n in range(len(self.hists2d_f)):
            if self.normalise_to_data : 
                self.hists2d_f[n].Scale(self.hists2d[n].GetSumOfWeights()/self.hists2d_f[n].GetSumOfWeights()*(float(self.fitbins2d)/float(self.bins2d))**2)
                if self.adjust_limits : 
                    self.hists2d_f[n].SetMinimum(0.)
                    self.hists2d_f[n].SetMaximum(self.hists2d[n].GetMaximum())
            else : 
                self.hists2d_f[n].Scale(1./self.hists2d_f[n].GetBinContent(self.hists2d_f[n].GetMaximumBin()))
                if self.zrange : 
                    self.hists2d_f[n].SetMinimum(self.zrange[0])
                    self.hists2d_f[n].SetMaximum(self.zrange[1])
                else : 
                    self.hists2d_f[n].SetMaximum(1.)
            if not self.plots:
                if self.n_input % 2 == 0:
                    self.can.cd(2*n + 2)
                else:
                    self.can.cd(n+1+(n//self.n_input) *
                                self.n_input+self.n_input)
                self.hists2d_f[n].Draw("zcol")
                self.t2.Draw()
            else:
                n1 = self.n1arr[n]
                n2 = self.n2arr[n]
                if (n1, n2) in self.can.keys():
                    self.can[(n1, n2)].cd(2)
                    self.hists2d_f[n].Draw("zcol")
                    self.t2.Draw()

        # Draw 1D fit projections
        for n in range(self.n_input):
            #      can.cd(n + 2*len(hists2d)+1)
            self.hists1d_f[n].Scale(self.hists1d[n].GetSumOfWeights(
            )/self.hists1d_f[n].GetSumOfWeights()*float(self.fitbins1d)/float(self.bins1d))
            self.hists1d[n].SetMinimum(0.)
#      self.hists1d_f[n].SetMarkerColor(2)
            self.hists1d_f[n].SetLineColor(2)
            self.hists1d_f[n].SetMinimum(0.)
            if not self.plots:
                self.can.cd(n + 2*len(self.hists2d)+1)
                pad1 = None
                pad2 = None
                if self.pull:
                    pad1 = ROOT.TPad("subpad1", "This is pad1",
                                     0.01, 0.26, 0.99, 0.99)
                    pad2 = ROOT.TPad("subpad2", "This is pad2",
                                     0.01, 0.01, 0.99, 0.25)
                    pad2.SetTopMargin(0.03)
                    pad2.SetBottomMargin(0.4)
                    pad1.Draw()
                    pad2.Draw()
                    pad1.cd()
                self.hists1d[n].Draw("e")
                self.hists1d_f[n].Draw("hist l same")
                self.hists1d[n].Draw("e same")
                if self.pull:
                    pad2.cd()
                    self.pulls[n] = (self.hists1d_f[n] -
                                     self.hists1d[n])/(self.hists1d_f[n]**0.5)
                    self.pulls[n].GetXaxis().SetTitleSize(
                        3.*self.hists1d_f[n].GetXaxis().GetTitleSize())
                    self.pulls[n].GetYaxis().SetTitleSize(
                        3.*self.hists1d_f[n].GetYaxis().GetTitleSize())
                    self.pulls[n].GetXaxis().SetLabelSize(
                        3.*self.hists1d_f[n].GetXaxis().GetLabelSize())
                    self.pulls[n].GetYaxis().SetLabelSize(
                        3.*self.hists1d_f[n].GetYaxis().GetLabelSize())
                    self.pulls[n].GetYaxis().SetTitleOffset(
                        1./3.*self.hists1d_f[n].GetYaxis().GetTitleOffset())
                    self.pulls[n].GetYaxis().SetTitle("Pull")
                    self.pulls[n].Draw("e")
                    l.DrawLine(self.pulls[n].GetXaxis().GetXmin(
                    ), 0., self.pulls[n].GetXaxis().GetXmax(), 0.)
                subpads += [pad1, pad2]
            else:
                if n in self.can.keys():
                    self.can[n].cd()
                    self.hists1d[n].Draw("e")
                    self.hists1d_f[n].Draw("hist l same")
                    self.hists1d[n].Draw("e same")

        if not self.plots:
            self.can.cd()
            if self.n_input > 2 : 
                for i in range(self.n_input):
                    for j in range(self.n_input//2):
                        if self.n_input % 2 == 1:
                            self.b.DrawBox(float(i)/float(self.n_input)+0.002,
                                           float(2*j+1)/float(self.n_input)+0.002,
                                           float(i+1)/float(self.n_input)-0.002,
                                           float(2*j+3)/float(self.n_input)-0.002)
                        else:
                            self.b.DrawBox(float(2*j)/float(self.n_input)+0.002,
                                           float(i+1)/float(self.n_input)+0.002,
                                           float(2*j+2)/float(self.n_input)-0.002,
                                           float(i+2)/float(self.n_input)-0.001)

            self.can.Update()
            self.can.Print(outfile)
        else:
            n = 0
            for i in self.can.keys():
                self.can[i].Update()
                self.can[i].Print(outfile.split(".")[0] +
                                  ("_%d." % n) + outfile.split(".")[1])
                n += 1

    def drawComponents(self, norm_sample, norm_pdfs, outfile):

        subpads = []
        l = ROOT.TLine()

        for i in self.hists1d_f:
            i.Reset()
        for i in self.hists1d_fc:
            i.Reset()
        for i in self.hists2d_f:
            i.Reset()
        n = 0
        for n1 in range(self.n_input):
            self.hists1d_f[n1].fill_array(norm_sample[:, n1], norm_pdfs[0])
            self.hists1d_fc[n1].fill_array(norm_sample[:, n1], norm_pdfs[1])
            for n2 in range(n1+1, self.n_input):
                self.hists2d_f[n].fill_array(
                    norm_sample[:, (n1, n2)], norm_pdfs[0])
                n += 1

        # Draw 2D fit projections
        for n in range(len(self.hists2d_f)):
            self.hists2d_f[n].Scale(self.hists2d[n].GetSumOfWeights(
            )/self.hists2d_f[n].GetSumOfWeights()*(float(self.fitbins2d)/float(self.bins2d))**2)
            self.hists2d_f[n].SetMinimum(0.)
            self.hists2d_f[n].SetMaximum(self.hists2d[n].GetMaximum())
            if not self.plots:
                if self.n_input % 2 == 0:
                    self.can.cd(2*n + 2)
                else:
                    self.can.cd(n+1+(n//self.n_input) *
                                self.n_input+self.n_input)
                self.hists2d_f[n].Draw("zcol")
                self.t2.Draw()
            else:
                n1 = self.n1arr[n]
                n2 = self.n2arr[n]
                if (n1, n2) in self.can.keys():
                    self.can[(n1, n2)].cd(2)
                    self.hists2d_f[n].Draw("zcol")
                    self.t2.Draw()

        # Draw 1D fit projections
        for n in range(self.n_input):
            #      can.cd(n + 2*len(hists2d)+1)
            scale = self.hists1d[n].GetSumOfWeights(
            )/self.hists1d_f[n].GetSumOfWeights()*float(self.fitbins1d)/float(self.bins1d)
            self.hists1d_f[n].Scale(scale)
            self.hists1d_fc[n].Scale(scale)
            self.hists1d[n].SetMinimum(0.)
#      self.hists1d_f[n].SetMarkerColor(2)
            self.hists1d_f[n].SetLineColor(2)
            self.hists1d_fc[n].SetLineColor(4)
            self.hists1d_f[n].SetMinimum(0.)
            if not self.plots:
                self.can.cd(n + 2*len(self.hists2d)+1)
                pad1 = None
                pad2 = None
                if self.pull:
                    pad1 = ROOT.TPad("subpad1", "This is pad1",
                                     0.01, 0.26, 0.99, 0.99)
                    pad2 = ROOT.TPad("subpad2", "This is pad2",
                                     0.01, 0.01, 0.99, 0.25)
                    pad2.SetTopMargin(0.03)
                    pad2.SetBottomMargin(0.4)
                    pad1.Draw()
                    pad2.Draw()
                    pad1.cd()
                self.hists1d_f[n].Draw("hist l")
                self.hists1d_fc[n].Draw("hist l same")
                self.hists1d[n].Draw("e same")
                if self.pull:
                    pad2.cd()
                    self.pulls[n] = (self.hists1d_f[n] -
                                     self.hists1d[n])/(self.hists1d_f[n]**0.5)
                    self.pulls[n].GetXaxis().SetTitleSize(
                        3.*self.hists1d_f[n].GetXaxis().GetTitleSize())
                    self.pulls[n].GetYaxis().SetTitleSize(
                        3.*self.hists1d_f[n].GetYaxis().GetTitleSize())
                    self.pulls[n].GetXaxis().SetLabelSize(
                        3.*self.hists1d_f[n].GetXaxis().GetLabelSize())
                    self.pulls[n].GetYaxis().SetLabelSize(
                        3.*self.hists1d_f[n].GetYaxis().GetLabelSize())
                    self.pulls[n].GetYaxis().SetTitleOffset(
                        1./3.*self.hists1d_f[n].GetYaxis().GetTitleOffset())
                    self.pulls[n].GetYaxis().SetTitle("Pull")
                    self.pulls[n].Draw("e")
                    l.DrawLine(self.pulls[n].GetXaxis().GetXmin(
                    ), 0., self.pulls[n].GetXaxis().GetXmax(), 0.)
                subpads += [pad1, pad2]
            else:
                if n in self.can.keys():
                    self.can[n].cd()
                    self.hists1d_f[n].Draw("hist l")
                    self.hists1d_fc[n].Draw("hist l same")
                    self.hists1d[n].Draw("e same")

        if not self.plots:
            self.can.cd()
            for i in range(self.n_input):
                for j in range(self.n_input//2):
                    if self.n_input % 2 == 1:
                        self.b.DrawBox(float(i)/float(self.n_input)+0.002,
                                       float(2*j+1)/float(self.n_input)+0.002,
                                       float(i+1)/float(self.n_input)-0.002,
                                       float(2*j+3)/float(self.n_input)-0.002)
                    else:
                        self.b.DrawBox(float(2*j)/float(self.n_input)+0.002,
                                       float(i+1)/float(self.n_input)+0.002,
                                       float(2*j+2)/float(self.n_input)-0.002,
                                       float(i+2)/float(self.n_input)-0.001)

            self.can.Update()
            self.can.Print(outfile)
        else:
            n = 0
            for i in self.can.keys():
                self.can[i].Update()
                self.can[i].Print(outfile.split(".")[0] +
                                  ("_%d." % n) + outfile.split(".")[1])
                n += 1


def EstimateDensity(
    phsp,
    calibfile,
    variables,
    bounds,
    titles,
    weight=None,
    treename="tree",
    learning_rate=0.001,
    training_epochs=100000,
    norm_size=1000000,
    print_step=50,
    display_step=500,
    weight_penalty=1.,
    n_hidden=[32, 8],
    path="./",
    initfile="init.npy",
    outfile="train",
    selection="",
    seed=1,
    plots=None
):

    sample = root2array(path + calibfile, treename=treename,
                        branches=variables, selection=selection)
    data_sample = rec2array(sample, variables)

    n_input = len(variables)

    data_ph = phsp.data_placeholder
    norm_ph = phsp.norm_placeholder

    try:
        init_w = np.load(initfile, allow_pickle = True)
    except:
        init_w = None

    if isinstance(init_w, np.ndarray):
        print("Loading saved weights")
        (weights, biases) = InitWeightsBiases(init_w)
    else:
        print("Creating random weights")
        (weights, biases) = CreateWeightsBiases(n_input, n_hidden)

    def model(x):
        # to make sure PDF is always strictly positive
        return MultilayerPerceptron(x, weights, biases) + 1e-20

    np.random.seed(seed)
    tf.set_random_seed(seed)

    data_model = model(data_ph)
    norm_model = model(norm_ph)

    # Define loss and optimizer
    nll = UnbinnedNLL(data_model, Integral(norm_model)) + \
        L2Regularisation(weights)*weight_penalty

    optimizer = tf.train.AdamOptimizer(learning_rate=learning_rate)
    train_op = optimizer.minimize(nll)

    # Initializing the variables
    init = tf.global_variables_initializer()

    if display_step != 0:
        display = MultidimDisplay(data_sample, titles, bounds, plots=plots)

    with tf.Session() as sess:
        sess.run(init)

        norm_sample = sess.run(phsp.UniformSample(norm_size))
        print("Normalisation sample size = ", len(norm_sample))
        print(norm_sample)
        print("Data sample size = ", len(data_sample))
        print(data_sample)

        # Training cycle
        best_cost = 1e10
        for epoch in range(training_epochs):

            if display_step != 0 and (epoch % display_step == 0):

                norm_pdf = sess.run(norm_model, feed_dict={
                                    norm_ph: norm_sample})
                display.draw(norm_sample, norm_pdf, outfile + ".pdf")

            # Run optimization op (backprop) and cost op (to get loss value)
            _, c = sess.run([train_op, nll], feed_dict={
                            data_ph: data_sample, norm_ph: norm_sample})
            # Display logs per epoch step
            if epoch % print_step == 0:
                s = "Epoch %d, cost %.9f" % (epoch+1, c)
                print(s)
                if c < best_cost:
                    best_cost = c
                    np.save(outfile, sess.run([weights, biases]))
                    f = open(outfile + ".txt", "w")
                    f.write(s + "\n")
                    f.close()

        print("Optimization Finished!")
