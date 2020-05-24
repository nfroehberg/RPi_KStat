from pandas import read_csv
parafile = 'test-parameters.txt'
params = read_csv(parafile, delim_whitespace=True, engine='python', names=['0','1','2','3'], index_col=0)
f = open(parafile,'r')
type=f.readline()
f.close()
if 'Cyclic' in type:
    print('cyclic')
print(type)
print(params)
print(params['2']['n_scans'])
