#%%
from pandas.core.frame import DataFrame
from pydoc import describe

from random import randint
from typing import Any
from kvittering import class_defs as sim
from kvittering import simulate_util as su
import pandas as pd

#%%

sim_config: sim.SimConfig = sim.SimConfig(
    sim_pop=10000,
    default_shop_n_year=150,
    eats_healthy_prob=0.5,
    organized_prob=0.3,
    rural_prob=0.2,
    education_effect=0,
    household_size_effect=0.1,
    rural_effect=-0.1,
    organized_effect=-0.5
)

sim_object: su.HouseholdSim = su.simulate(sim_config, printout=True)

#%%
su.compare_health_by_group(sim_object.sampled_data, "education")


#%%
print(sim_object)
assert sim_object.sampled_data is not None
#%%

temp_full : pd.DataFrame = sim_object.sampled_data.all_households
temp_hush : pd.DataFrame = sim_object.sampled_data.sampled_households
temp_kvitt : pd.DataFrame = sim_object.sampled_data.sampled_receipts
print(len(temp_kvitt))
print(len(temp_hush))


#%%
temp_full.groupby("education")["shopped_healthy"].mean()

#%%
temp_hush.groupby("education")["shopped_healthy"].mean()

#%%
su.compare_sampling(sim_object.sampled_data, "shopped_healthy")


#%%

def sim_and_compare(utdanning_effekt: int, sim_pop: int = 10000, colname : str = "") -> DataFrame:
    params = sim.SimConfig(
        sim_pop=sim_pop,
        utdanning_effekt=utdanning_effekt
    )

    simulation = su.lag_husholdnings_handle_sim(params, printout=False)
    sampled = su.SampledData(simulation)

    return su.compare_sampling(sampled, colname)

#%%
default: pd.DataFrame = sim_and_compare(utdanning_effekt=0, sim_pop= 1000, colname="utdanning")
sjelden: pd.DataFrame = sim_and_compare(utdanning_effekt=-5, sim_pop= 1000,colname= "utdanning")
ofte: pd.DataFrame = sim_and_compare(utdanning_effekt=5, sim_pop= 1000,colname= "utdanning")

#%%
print("Default 0")
default
#%%
print("Sjelden : 5")
sjelden

#%%
print("Ofte : -5")
ofte





#%%
#%%
#%%
#%%



# DEFAULT

params: sim.SimHandleFrekvensParams = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    strukturert_effekt= 0,
    strukturert_prob=0.2)

default_sim: su.HusholdningsHandleSim = su.lag_husholdnings_handle_sim(sim_config=params, printout=False)
default_sampled_data : su.SampledData = su.SampledData(sim_object=default_sim)
default_comp_str: DataFrame = su.compare_sampling(sampled_data=su.SampledData(sim_object=default_sim), column="er_strukturert")
default_comp_utd: DataFrame = su.compare_sampling(sampled_data=su.SampledData(sim_object=default_sim), column="utdanning")
#%%
params_sjelden = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    strukturert_effekt= -5,
    strukturert_prob=0.2)

sjelden_sim = su.lag_husholdnings_handle_sim(sim_config=params_sjelden,printout=False)
sjelden_sampled_data = su.SampledData(sjelden_sim)
sjelden_comp_str = su.compare_sampling(sampled_data=sjelden_sampled_data,column="er_strukturert")
sjelden_comp_utd = su.compare_sampling(sampled_data=sjelden_sampled_data,column="utdanning")
#%%
# Høyere utdanning = handler oftere

params_ofte = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    strukturert_effekt= 5,
    strukturert_prob=0.2)

ofte_sim = su.lag_husholdnings_handle_sim(sim_config=params_ofte,printout=False)
ofte_sampled_data = su.SampledData(ofte_sim)
ofte_comp_str = su.compare_sampling(sampled_data=ofte_sampled_data,column="er_strukturert")
ofte_comp_utd = su.compare_sampling(sampled_data=ofte_sampled_data,column="utdanning")


#%%
default_comp_utd
#%%
default_comp_str
#%%
sjelden_comp_str
#%%
sjelden_comp_utd
#%%
ofte_comp_str
#%%
ofte_comp_utd

#%%
## Checking multiple values

pd.crosstab(
    ofte_sampled_data.sampled_husholdninger["utdanning"],
    ofte_sampled_data.sampled_husholdninger["er_strukturert"],
    normalize="index"
).mul(100).round(2)


#%%
pd.crosstab(
    ofte_sampled_data.sampled_kvitteringer["utdanning"],
    ofte_sampled_data.sampled_kvitteringer["er_strukturert"],
    normalize="index"
).mul(100).round(2)

#%%


#%%


#%%
## lag sample data

#%%
#%%
