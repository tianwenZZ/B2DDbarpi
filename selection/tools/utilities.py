import yaml

import ROOT
from ROOT import TChain

def get_val(tree,item):
    '''
    return the value of expression for given treen and entry
    '''
    pieces = item.split()
    if len(pieces)==1:
        return getattr(tree,pieces[0])
    else:
        pieces = pieces[2:]
        for ii,p in enumerate(pieces):
            # reply on upper case to find the variable
            if any(c.isupper() for c in p):
                    p = getattr(tree,p)
            pieces[ii] = str(p)
        expr = ' '.join(pieces)
        code_obj = compile(expr,'','eval')
        return eval(code_obj)


def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict


def load_data(treename, files):
    '''
    load data files to a TChain
    '''
    names = []
    for n in files:
        names.append(n if n.endswith('.root') else n+'*.root')
    tree = TChain(treename)
    for n in names:
        tree.Add(n)
    return tree


def draw_pull(plot, xx, data_name, fit_name, xtitle):
    hpull = plot.pullHist(data_name, fit_name)
    hpull.SetFillColor(1)
    
    frame = xx.frame(ROOT.RooFit.Title("pull"))
    frame.GetXaxis().SetTitle(xtitle)
    frame.GetYaxis().SetTitle("pull")
    frame.GetYaxis().SetRangeUser(-5, 5)
    frame.GetXaxis().SetTitleSize(0.15)
    frame.GetXaxis().SetTitleOffset(1.10)
    frame.GetXaxis().SetLabelSize(0.15)
    frame.GetYaxis().SetTitleSize(0.2)
    frame.GetYaxis().SetTitleOffset(0.22)
    frame.GetYaxis().SetNdivisions(502)
    frame.GetYaxis().SetLabelSize(0.15)
    frame.GetXaxis().CenterTitle()
    frame.GetYaxis().CenterTitle()

    frame.addPlotable(hpull, "BX")
    return frame


class DalitzPhaseSpace:
    def __init__(self, m0, m1, m2, m3):
        self.m0 = m0
        self.m1 = m1
        self.m2 = m2
        self.m3 = m3
    def M0(self):
        return self.m0
    def M1(self):
        return self.m1
    def M2(self):
        return self.m2
    def M3(self):
        return self.m3
    def upperLimit(self, index):
        if index=="12":
            return (self.m0-self.m3)**2
        elif index=="13":
            return (self.m0-self.m2)**2
        elif index=="23":
            return (self.m0-self.m1)**2
        else:
            print("Error: Invalid input phsp index!")
    def lowerLimit(self, index):
        if index=="12":
            return (self.m1+self.m2)**2
        elif index=="13":
            return (self.m1+self.m3)**2
        elif index=="23":
            return (self.m2+self.m3)**2
        else:
            print("Error: Invalid input phsp index!")
