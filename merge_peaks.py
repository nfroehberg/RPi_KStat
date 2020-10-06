# Small scrip to merge peak detection and O2 measurement results created by the KStat GUI
# runs on all files with the appropriate file name found in the same directory as the script
# Nico Fröhberg, 2020
# nico.froehberg@gmx.de

from glob import glob
import pandas as pd
import os

dir = os.path.basename(os.getcwd())

all_files = glob('*')
peak_files = []
o2_files = []
for file in all_files:
    if '-peaks.txt' in file:
        peak_files.append(file)
    if '-o2_measurement.txt' in file:
        o2_files.append(file)

if len(peak_files) == 0:
    print('No peak file found, no merge possible')
elif len(peak_files) == 1:
    print('Only one peak file found, no merge possible')
else:
    df = pd.read_csv(peak_files[0])
    print(peak_files[0])
    for peak_file in peak_files[1:]:
        print(peak_file)
        df = df.append(pd.read_csv(peak_file))
    df=df.drop(columns=df.columns[-1],axis=1)
    df.to_csv(dir+'-peaks.csv',index=False)
    
if len(o2_files) == 0:
    print('No peak file found, no merge possible')
elif len(o2_files) == 1:
    print('Only one peak file found, no merge possible')
else:
    df = pd.read_csv(o2_files[0])
    print(o2_files[0])
    for o2_file in o2_files[1:]:
        print(o2_file)
        df = df.append(pd.read_csv(o2_file))
    df=df.drop(columns=df.columns[-1],axis=1)
    df.to_csv(dir+'-o2_measurement.csv',index=False)