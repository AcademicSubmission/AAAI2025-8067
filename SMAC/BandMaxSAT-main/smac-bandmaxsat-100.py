
from os import listdir
import sys
from os.path import isfile, join
from ConfigSpace import ConfigurationSpace
from ConfigSpace import Integer,Float
from contextlib import redirect_stdout
from smac import HyperparameterOptimizationFacade as HPOFacade
from smac import AlgorithmConfigurationFacade as ACFacade
from smac import Scenario
import random

ins_path = '/the/path/of/maxsat/ins'

seed = int(sys.argv[1])
files = [join(ins_path,f) for f in listdir(ins_path) if isfile(join(ins_path, f))]
random.seed(seed)
instances = random.sample(files,int(len(files) * 0.2))

bms_num = Integer("bms_num",(5,25))
lambda_ = Float("lambda_",(0.1,2))
gamma = Float("gamma",(0.8,1.0))
armnum = Integer("armnum",(10,30))
backward_step = Integer("backward_step",(10,30))
cs = ConfigurationSpace(seed=seed)
cs.add_hyperparameters([bms_num, lambda_, gamma, armnum, backward_step])

# Scenario object specifying the optimization "environment"
scenario = Scenario(cs, instances=instances, deterministic=True, cputime_limit=60000, n_workers=1,n_trials=1000,seed=seed)

# Now we use SMAC to find the best hyperparameters
smac = ACFacade(
    scenario,
    "./BandMaxSAT-100.sh",  # We pass the filename of our script here
    overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
)

incumbent = smac.optimize()

# Let's calculate the cost of the incumbent
incumbent_cost = smac.validate(incumbent)


with open("smac_out.log","a") as f:
    with redirect_stdout(f):
        print(f"Incumbent result: {incumbent}\nIncumbent cost: {incumbent_cost}")
