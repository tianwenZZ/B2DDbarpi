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

from root_numpy import array2tree, root2array, rec2array
import rootpy.ROOT as ROOT
import numpy as np


def array2dataset(arr, variables, name='dataset'):
    """
    Create RooFit dataset from the numpy array
      arr : 2D numpy array (first dimension corresponds to "event", second dimension to "variable")
      variables : list of variable names. The length should be equal to the 2nd dimension of "arr"
    """
    tree = array2tree(arr)
    varset = ROOT.RooArgSet(name + "_argset")
    for var in variables:
        varset.add(var)
    ds = ROOT.RooDataSet(name, name, tree, varset)
    return ds


def SplitArray(arr, frac=0.5):
    """
    Split numpy array into two parts in the 1st dimension (e.g. split the dataset)
      arr  : 2D numpy array. 1st dimension corresponds to "event"
      frac : fraction of events in the first part (the second part will have (1-frac) events). 0.<frac<1.
    """
    l = arr.shape[0]
    m = int(round(frac*l))
    np.random.shuffle(arr)
    return (arr[:m, :], arr[m:, :])


def LoadTransformArray(filename, treename, variables=None, selection=None, transform=None, nan = None):
    """
    Load array from ROOT file and optionally apply transformation of variables. 
    This function extends the "root2array" function from root_numpy library
      filename : name of ROOT file
      treename : name of ROOT tree in the file (if None, defaults to "tree")
      variables : list of variables to read
      selection : selection string in root_numpy format
      transform : dictionary of transformations to apply. 
        keys are variables names
        values are lambda functions for transformation (should work with 1D numpy arrays, e.g. "lambda x : np.cos(x)")
    """
    print('Loading array from file ', filename)
    array = root2array(filename, treename,
                       branches=variables, selection=selection)
    if transform:
        for v, func in transform.items():
            print('Transforming variable ', v)
            array[v] = func(array[v])
    if nan : 
      return np.nan_to_num(array, nan = nan)
    else : 
      return array


def TransformArray(rec, fields=None, transforms=None):
    """
    Apply transformation of variables to numpy array.
      rec       : numpy recarray
      fields    : list of variables to extract from recarray and optionally transform
      selection : selection string in root_numpy format
      transform : dictionary of transformations to apply. 
        keys are variables names
        values are lambda functions for transformation (should work with 1D numpy arrays, e.g. "lambda x : np.cos(x)")
    """
    array = rec2array(rec, fields)
    print('Extracting variables ', str(fields), " from array")
    if transforms:
        for v, func in transforms.items():
            i = fields.index(v)
            print('Transforming variable ', v, ' index ', i)
            if i:
                array[:, i] = func(array[:, i])
    return array


def PlotArrayComparison(arrays, variables, ranges, vartitles, size, splits, colors, options, canvasname, weights=None):
    """
    Compare 1D distributions from a list of arrays
    """
    import rootpy.ROOT as ROOT
    from root_numpy import fill_hist

    c = ROOT.TCanvas(canvasname.replace("/", "_"), "", size[0], size[1])
    c.Divide(splits[0], splits[1])

    hists = []

    for n, v in enumerate(variables):

        hh = []

        for m, a in enumerate(arrays):
            h = ROOT.Hist(50, ranges[n][0], ranges[n][1])
            arr = a[v[m]]
            w = None
            if weights and weights[m]:
                w = a[weights[m]]
            fill_hist(h, arr, w)
            hh += [h]

        maximum = hh[0].GetMaximum()
        for m, h in enumerate(hh[1:]):
            h.Scale(hh[0].GetSumOfWeights()/h.GetSumOfWeights())
            h.SetLineColor(colors[m+1])
            h.SetMarkerColor(colors[m+1])
            h.SetMarkerSize(0.05)
            maximum = max(maximum, h.GetMaximum())

        c.cd(n+1)
        hh[0].SetMaximum(maximum*1.2)
        hh[0].Draw(options[0])
        hh[0].SetLineColor(colors[0])
        hh[0].SetMarkerColor(colors[0])
        hh[0].GetXaxis().SetTitle(vartitles[n])
        for m, h in enumerate(hh[1:]):
            h.Draw(options[m+1] + " same")

        hists += [hh]
    c.Print(canvasname + ".pdf")
    return (c, hists)


def FillRootFile(filename, array, variables, tree="tree", mode="recreate"):
    """
      Convenience function to store the unstructured array (e.g. from session.run() ) 
      into a ROOT tree
      Same  syntax as FillNTuple, but using root_numpy, so much faster
    """
    from root_numpy import array2root
    struct = [(name, float) for name in variables]
    recarray = np.rec.fromarrays(array.transpose(), dtype=struct)
    array2root(recarray, filename, mode=mode, treename=tree)
