#!/usr/bin/python
import json
import sys,os
import shutil

# python _ alg_name func_id filename penalty

penalty = int(sys.argv[4])

def copy_dat(ori_file, copy_file):
    r = 0
    ori_f = open(ori_file)
    cpy_f = open(copy_file,'w')
    runs = []

    ori_lines = ori_f.readlines()
    for ol in ori_lines:
        if ol[0] ==  'e':
            r += 1
            cpy_f.write("evaluations raw_y hard_unsat_nb soft_unsat_weight distance_to_the_last_best\n")
            if (r > 1):
                best =  {"instance" : 1, "evals" : evaluations, "best": {"evals": evaluations, "y": best_f}}
                runs.append(best)
            continue
        else:
            info = ol.split(' ')
            evaluations = int(info[0])
            best_f = int(info[1]) * penalty + int(info[2])
            cpy_f.write("{} {} {} {} {}\n".format(info[0], best_f, info[1], info[2], info[3]))
            dim = info[4]
    best =  {"instance" : 1, "evals" : evaluations, "best": {"evals": evaluations, "y": best_f}}
    runs.append(best)

    ori_f.close()
    cpy_f.close()
    return dim, runs
        
alg_name = sys.argv[1]
func_id = sys.argv[2]
suite_name = "maxSAT"
filename = sys.argv[3]
save_path = "data_"+filename[:-4]
folder_name = "data"

f_c = 1
tfolder_name = folder_name
while os.path.exists(tfolder_name):
    tfolder_name = folder_name + str(f_c)
    f_c += 1

os.mkdir(tfolder_name)
os.mkdir(tfolder_name +'/' + save_path)

copy_dat(filename, tfolder_name +'/' + save_path + "/" + filename)

data = {}
data["version"] = "0.3.5" 
data["suite"] = "maxSAT"
data["function_id"] = func_id
data["function_name"] = filename
data["maximization"] = False
data["algorithm"] =  {"name": alg_name, "info": alg_name}
data["attributes"] = ["evaluations","hard_unsat_nb","soft_unsat_weight","distance_to_the_last_best"]


run = {"dimension" : 0,"path" : save_path + '/' + filename  ,"runs": []}

dimension, runs = copy_dat(filename,tfolder_name +'/' + save_path + '/' + filename)

run["dimension"] = int(dimension)
run["runs"] = runs
data["scenarios"] = [run]

with open(tfolder_name+"/data_"+filename[:-4] + ".json",'w') as f:
    json.dump(data,f,indent=1)