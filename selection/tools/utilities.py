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


def draw_pull(plot, xx, xtitle):
    hpull = plot.pullHist()
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
