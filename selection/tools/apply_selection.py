from constants import C_LIGHT, P_MASS, K_MASS, BU_MASS, DU_MASS, D0_MASS, PI_MASS
import time
import argparse
import yaml

from ROOT import (
    vector,
    gInterpreter,
    ROOT,
    RDataFrame,
    TObject
)




def read_from_yaml(mode, selection_files):
    selection_dict = dict()
    for file in selection_files:
        with open(file, 'r') as stream:
            selection_dict.update(yaml.safe_load(stream)[mode])
    return selection_dict


def apply_cuts(cuts, dataframe):
    for key in cuts.keys():
        cut = cuts[key]
        if cut:
            dataframe = dataframe.Filter(cut, key)
    # check efficiencies
    report = dataframe.Report()
    report.Print()
    return dataframe



def apply_selection(input_files, input_tree_name, output_file, output_tree_name,
                    mode, cut_keys, cut_string, selection_files, branches_files,
                    keep_all_original_branches):
    # enable multithreading
    ROOT.EnableImplicitMT()

    input_files = [input_files] if type(
        input_files) != type([]) else input_files
    names = vector('string')()
    for n in input_files:
        names.push_back(n if n.endswith('.root') else n+'*.root')
    dataframe = RDataFrame(input_tree_name, names)
    # read cuts from all input files
    cuts = read_from_yaml(mode, selection_files) if selection_files else {}
    # if cut keys are specified apply only desired cuts for given mode
    if cut_keys:
        cuts = {cut_key: cuts[cut_key] for cut_key in cut_keys}
    if cut_string:
        cuts = {'cut': cut_string}
    # read branches from all input files
    branches_to_add = read_from_yaml(
        mode, branches_files) if branches_files else {}
    if branches_to_add:
        # get list of existing branches
        branches_in_df = dataframe.GetColumnNames()
        # define new branches and keep original branches if specified
        branches = vector('string')()
        if keep_all_original_branches:
            branches = branches_in_df

        # in case helicity angles and/or docaz are specified in branches
        #gInterpreter.LoadMacro('tools/calculateHelicityPolarAngle.cpp')
        #gInterpreter.LoadMacro('tools/calculatePlaneAngle.cpp')
        #gInterpreter.LoadMacro('tools/calculateclone.cpp')
        gInterpreter.LoadMacro('tools/calculateEta.cpp')
        gInterpreter.LoadMacro('tools/find2Min.cpp')
        gInterpreter.LoadMacro('tools/find3Min.cpp')
        gInterpreter.LoadMacro('tools/find4Min.cpp')

        # add new branches
        for branch in branches_to_add.keys():
            branch_value = branches_to_add[branch].format(
                C_LIGHT=C_LIGHT, DU_MASS=DU_MASS, PI_MASS=PI_MASS, K_MASS=K_MASS)
            if branch not in branches_in_df:
                if branch == branch_value:
                    print(
                        'WARNING: {} branch is not present in the original tree. Setting value to -99999.'.format(branch))
                    dataframe = dataframe.Define(branch, "-99999.0")
                elif not branch_value:
                    print('Skipping branch ', branch)
                    continue
                else:
                    dataframe = dataframe.Define(branch, branch_value)
            elif not branch_value:
                print('Skipping branch ', branch)
                continue
            branches.push_back(branch)
        # apply all cuts
        if cuts:
            dataframe = apply_cuts(cuts, dataframe)
        # save new tree
        print('Branches kept in the pruned tree:', branches)
        dataframe.Snapshot(output_tree_name, output_file, branches)
    else:
        # apply all cuts
        if cuts:
            dataframe = apply_cuts(cuts, dataframe)
        # save new tree
        print('All branches are kept in the tree')
        dataframe.Snapshot(output_tree_name, output_file)



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
    parser.add_argument('--cut-keys', default='', nargs='+',
                        help='Specify which cuts for the mode should be applied, if not all')
    parser.add_argument('--cut-string', default=None,
                        help='Alternatively, specify cut string directly')
    parser.add_argument('--selection-files', nargs='+',
                        help='Yaml files with selection')
    parser.add_argument('--branches-files', nargs='+',
                        help='Yaml files with branches')
    parser.add_argument('--keep-all-original-branches', default=True,
                        help='Keeps all original branches if True, only adds specified branches if False') #always want to keep all original branches
    args = parser.parse_args()
    apply_selection(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))

