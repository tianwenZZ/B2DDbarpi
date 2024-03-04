from math import sqrt
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('s1', type=float, help='sigma1')
parser.add_argument('s1e', type=float, help='sigma1 err')
parser.add_argument('a1', type=float, help='a1')

args = parser.parse_args()

f=0.3
reso=sqrt(f+(1-f)*args.a1**2)*args.s1
reso_err=sqrt(f+(1-f)*args.a1**2)*args.s1e

print("reso=%f +- %f"%(reso, reso_err))
