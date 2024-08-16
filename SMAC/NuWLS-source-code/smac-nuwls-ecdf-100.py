
from genericpath import exists
from os import listdir,system,mkdir
from os.path import isfile, join, basename
from ConfigSpace import Categorical, ConfigurationSpace
from ConfigSpace import Integer,Float, Configuration
from contextlib import redirect_stdout
from smac import HyperparameterOptimizationFacade as HPOFacade
from smac import AlgorithmConfigurationFacade as ACFacade
from smac import Scenario
import random
from nuwls_ecdf import ecdf,set_cpu_time,set_target_folder

ins_path = '/the/path/of/maxsat/ins'
set_cpu_time(100)

files = [join(ins_path,f) for f in listdir(ins_path) if isfile(join(ins_path, f))]
random.seed(100)
instances = random.sample(files,int(len(files) * 0.2))
target_folder = 'target-100'
tmp_d = random.randint(1,10000000)
set_target_folder('target-100-'+str(tmp_d))
if not exists('target-100-'+str(tmp_d)):
    mkdir('target-100-'+str(tmp_d))

class NuWLsfunction:
    @property
    def configspace(self) -> ConfigurationSpace:
        cs = ConfigurationSpace(seed=0)
        bms_num = Integer("bms_num",(10,100))
        hard_sp = Float("hard_sp",(0.00000001,0.1))
        soft_sp = Float("soft_sp",(0.00000001,0.1))
        soft_weight_threshold = Float("soft_weight_threshold",(100,1000))
        h_inc = Float("h_inc",(1,100))
        s_inc = Float("s_inc",(1,100))
        coe = Integer("coe",(100,10000))
        cs.add_hyperparameters([bms_num, hard_sp, soft_sp, soft_weight_threshold, h_inc, s_inc, coe])
        return cs

    def train(self, config: Configuration, instance: str, seed: int = 0) -> float:
        """Returns the y value of a quadratic function with a minimum we know to be at x=0."""
        y = ecdf(config, instance, seed)
        return y

# Scenario object specifying the optimization "environment"

model = NuWLsfunction()
scenario = Scenario(model.configspace, instances=instances, deterministic=True, cputime_limit=60000, n_workers=1,n_trials=1000)

# Now we use SMAC to find the best hyperparameters
smac = ACFacade(
    scenario,
    model.train,
    overwrite=True,  # Overrides any previous results that are found that are inconsistent with the meta-data
)

incumbent = smac.optimize()


# Let's calculate the cost of the incumbent
incumbent_cost = smac.validate(incumbent)


with open("smac_out.log","a") as f:
    with redirect_stdout(f):
        print(f"Incumbent result: {incumbent}\nIncumbent cost: {incumbent_cost}")
