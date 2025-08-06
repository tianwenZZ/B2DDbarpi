import argparse
import subprocess
import sys

parser = argparse.ArgumentParser()
parser.add_argument('--input-files',
                    nargs='+',
                    help='Path to the input file')
parser.add_argument('--input-tree-name',
                    default='DecayTree',
                    help='Name of the tree')
parser.add_argument('--mode',
                    help='Mode of the decay')
parser.add_argument('--out-func',
                    help='Output func file of parameters ')
parser.add_argument('--output-files',
                    help='Output file of fit plots')
parser.add_argument("--method",
                    help='Fit python codes for different signal pdf: gaus, DCB, ...')
args = parser.parse_args()

# 构造命令
cmd = [
        "python", "tools/fit/fit_MC_"+args.method+".py",
        "--input-files", ' '.join(args.input_files),
        "--out-func", args.out_func,
        "--output-files", args.output_files,
        "--mode", args.mode,
        ]
if args.method == "2gaus":
    cmd.append("--frac")
    cmd.append("0.3")


print(f"[INFO] Running: {' '.join(cmd)}")
ret = subprocess.run(cmd)

if ret.returncode != 0:
    sys.exit(f"[ERROR] Fit failed with code {ret.returncode}")

