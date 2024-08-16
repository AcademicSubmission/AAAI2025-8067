
from os import listdir
import sys
from os.path import isfile, join
from ConfigSpace import ConfigurationSpace
from ConfigSpace import Integer,Float
from contextlib import redirect_stdout
from smac import AlgorithmConfigurationFacade as ACFacade
from smac import Scenario
import random

ins_path = '/the/path/of/maxsat/ins'

seed = int(sys.argv[1])
files = [join(ins_path,f) for f in listdir(ins_path) if isfile(join(ins_path, f))]
random.seed(seed)
instances = random.sample(files,int(len(files) * 0.2))

bms_num = Integer("bms_num",(10,100))
hard_sp = Float("hard_sp",(0.00000001,0.1))
soft_weight_threshold = Float("soft_weight_threshold",(100,1000))
h_inc = Float("h_inc",(1,500))
cs = ConfigurationSpace(seed=seed)
cs.add_hyperparameters([bms_num, hard_sp, soft_weight_threshold, h_inc])

# Scenario object specifying the optimization "environment"
scenario = Scenario(cs, instances=instances, deterministic=True, cputime_limit=60000, n_workers=1,n_trials=1000,seed = seed)

# Now we use SMAC to find the best hyperparameters
smac = ACFacade(
    scenario,
    "./satlike-tune.sh",  # We pass the filename of our script here
    overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
)

incumbent = smac.optimize()

# Let's calculate the cost of the incumbent
incumbent_cost = smac.validate(incumbent)


with open("smac_out.log","a") as f:
    with redirect_stdout(f):
        print(f"Incumbent result: {incumbent}\nIncumbent cost: {incumbent_cost}")
