from ROOT import TFile, TCanvas, TLegend, gROOT,RooRealVar,RooFormulaVar,RooCBShape,RooAddPdf,RooExponential,RooStats,RooGaussian,RooDataSet,RooArgSet,RooArgList,RooArgusBG,RooFFTConvPdf,kRed,kGreen,kDashed,kCyan,kBlue,TLine,TChain,RooKeysPdf,kYellow,kTRUE, TTree
from ROOT import RooFit
from array import array
from math import sqrt
from ROOT import Math


mDp=1869.66
mD0b=1864.84
mK0=497.611
xlow=5220
xup=5600

def gen_charmless(input_files, input_tree_name, vars, output_file, output_tree_name, mode):
    output = TFile(output_file, "recreate")
    
    mmm=array('f',[0.])
    varnames=["D1_M","D2_M","B_M","BDT","D1_ENDVERTEX_Z","D2_ENDVERTEX_Z","B_ENDVERTEX_Z","D1_ENDVERTEX_ZERR","D2_ENDVERTEX_ZERR","B_ENDVERTEX_ZERR"]
    vardict={}
    for var in varnames:
        vardict[var]=array('f',[0.])

    tr={}
    cat=["ss","sb","bs","bb"]

    for i in cat:
        tr[i]=TTree("tr"+i,"")
        for var in vardict:
            tr[i].Branch(var,vardict[var],var+"/F")




if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-files', nargs='+',
                        help='Path to the input file')
    parser.add_argument('--input-tree-name',
                        default='DecayTree', help='Name of the tree')
    parser.add_argument('--output-file', help='Output ROOT file')
    parser.add_argument('--output-tree-name',
                        default='DecayTree', help='Name of the tree')
    parser.add_argument('--mode', help='Name of the selection in yaml')

    args = parser.parse_args()
    gen_charmless(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))

