from ConfigSpace import Configuration
from os import system,remove,getcwd
from os.path import basename,exists,join
import random,time
import numpy as np
import multiprocessing
import pandas as pd

current_path = getcwd()
def format_instance(config: Configuration):
    
    return f'-bms_num {config["bms_num"]} -hard_sp {config["hard_sp"]} \
            -soft_weight_threshold {config["soft_weight_threshold"]} -h_inc {config["h_inc"]}'


def set_cpu_time(c):
    global cpu_time
    cpu_time = c
  
def set_target_folder(folder):
    global target_folder
    target_folder = folder

def set_pre_tag(Tag):
    global pre_Tag
    pre_Tag = Tag

def read_targets(target_file,output_file):
    if not exists(join(current_path,target_file)):
        f = open(join(current_path,output_file))
        lines = f.readlines()
        max_f = int(lines[0].strip().split(' ')[0])
        min_f = int(lines[len(lines) - 1].strip().split(' ')[0])

        if max_f - min_f < 5:
            targets = list(range(min_f, max_f + 1))[::-1]
        else:
            targets = list(np.linspace(max_f,min_f,5))
            targets = [int(t) for t in targets]

        f.close()
        f = open(join(current_path,target_file),'w+')
        for t in targets:
            f.write(f'{t}\n')
        f.close()
        return targets
    else:
        f = open(join(current_path,output_file))
        f1 = open(join(current_path,target_file),"a+")
        lines = f.readlines()
        f1.seek(0)
        lines1 = f1.readlines()
        targets = [int(line1) for line1 in lines1]
        best_found =  int(lines[len(lines)-1].strip().split(' ')[0])
        if best_found < targets[len(targets) - 1]:
            targets.append(best_found)
            f1.write(f'{best_found}\n')
        f.close()
        f1.close()
        return targets

def ecdf(config: Configuration, ins: str, seed: int = 0, rand_tag: int = 0):
    ''' target_file: target/ins.target
        output_file tmp_{random_number}.out'''
    rand_ins = list(ins)
    random.seed(time.time() + float(config["bms_num"]) + rand_tag)
    random.shuffle(rand_ins)
    random_number = random.randint(1, 10000000)
    
    system(f"./SATLike3.0-ecdf {ins} 1 -cpu_time {cpu_time} {format_instance(config)} > ./{pre_Tag}_tmp_{random_number}.out" )

    with open(join(current_path,f'./{pre_Tag}_tmp_{random_number}.out')) as out_file:
        lines = out_file.readlines()
    if len(lines) == 0:
        remove(join(current_path,f"./{pre_Tag}_tmp_{random_number}.out"))
        return 0

    targets = read_targets(f'{target_folder}/{basename(ins)}-{cpu_time}.target',f'./{pre_Tag}_tmp_{random_number}.out')
    budgets =  np.logspace(np.log(0.1),np.log(cpu_time),50,base=np.e)
    budgets = [cpu_time + 0.1 - b for b in budgets]
    budgets.sort()
    ecdf = 0
    index = 0
    f, t = lines[index].strip().split(' ')
    f = int(f)
    t = float(t)
    for b in budgets:
        if t < b:
            while(True):
                index += 1
                if index >= len(lines):
                    break
                f, t = lines[index].strip().split(' ')
                f = int(f)
                t = float(t)
                if t >= b:
                    break
        for target in targets:
            if f <= target:
                ecdf += 1
    out_file.close()
    remove(join(current_path,f"./{pre_Tag}_tmp_{random_number}.out"))
    return -ecdf

def found_f(config: Configuration, ins: str, seed: int = 0, rand_tag: int = 0):
    ''' target_file: target/ins.target
        output_file {pre_Tag}_tmp_{random_number}.out'''
    
    r = pd.read_csv('best_mse23-w.csv')
    best_r = r[r['Instance'] == basename(ins)]['Best-Sol'].values[0]
    
    rand_ins = list(ins)
    random.seed(time.time() + float(config["bms_num"]) + rand_tag)
    random.shuffle(rand_ins)
    random_number = random.randint(1, 10000000)
    system(f"./SATLike3.0-best-f {ins} 1 -cpu_time {cpu_time} {format_instance(config)} > ./{pre_Tag}_tmp_{random_number}.out" )

    with  open(join(current_path,f'./{pre_Tag}_tmp_{random_number}.out')) as out_file:
        r = out_file.read()
        if pd.isna(best_r):
            result = 1
        else:
            if r == '':
                result = 0
            else:
                result = (float(best_r) + 1.0) / (float(r.strip()) + 1.0)
    remove(join(current_path,f"./{pre_Tag}_tmp_{random_number}.out"))
    return -result


def multi_ecdf(config: Configuration, ins: str, seed: int = 0):
    ''' target_file: target/ins.target
        output_file tmp_{random_number}.out'''
    instances = ins.split('|')
    argus = [(config, instances[i], seed, i) for i in range(len(instances))] 
    pool = multiprocessing.Pool(processes=20)
    results = pool.starmap(ecdf,argus)
    pool.close()
    pool.join()
    return np.mean(results)


def PAR2(config: Configuration, ins: str, seed: int = 0):
    ''' target_file: target/ins.target
        output_file {pre_Tag}_tmp_{random_number}.out'''
    instances = ins.split('|')
    argus = [(config, instances[i], seed, i) for i in range(len(instances))] 
    pool = multiprocessing.Pool(processes=20)
    results = pool.starmap(found_f,argus)
    pool.close()
    pool.join()
    return np.mean(results)