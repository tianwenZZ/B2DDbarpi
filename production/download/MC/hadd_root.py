import json
import time
import argparse
import yaml
import subprocess

def hadd(target, source_map):
    root = target.split('/')[-1].split('.')[0]
    mode = root.split('_')[0]
    year = root.split('_')[1]
    mag = root.split('_')[2]
    # Do some transformations 
    year = year[-2:]
    if mag == "mu":
        mag = "up"
    if mag == "md":
        mag = "down"
    jobname = f"{mode}-sqDalitz-dv{year}-{mag}"
    with open(source_map, "r") as f:
        mapJobidNames = json.load(f)
    jobids = [mapJobidNames[jobname]]
    if jobname+"_splitted" in mapJobidNames.keys():
        jobids.append(mapJobidNames[jobname+"_splitted"])
    
    # Run the hadd.
    command = f'lb-run DaVinci/v44r10p5 hadd {target} '
    for i in jobids:
        command += f'output/download/MC/split/{i}/* '
    subprocess.Popen(command, shell=True)


if __name__ == '__main__':
    time_start = time.time()    # time start
    print('INFO: time start:', time.asctime(time.localtime(time_start)))
    parser = argparse.ArgumentParser()
    parser.add_argument('--target', 
                        help='Path to the output file')
    parser.add_argument('--source-map', 
                        help='Path to the jobid-name map in json file')
    args = parser.parse_args()
    hadd(**vars(args))
    time_end = time.time()  # time end
    print('INFO: time end:', time.asctime(time.localtime(time_end)))
    time_sum = time_end - time_start  # time cost, unit: second
    print('INFO: the program cost: {} min.'.format(round(time_sum/60, 2)))
