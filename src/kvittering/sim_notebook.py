#%%
from pandas.core.frame import DataFrame
from pydoc import describe

from random import randint
from typing import Any
from kvittering import class_defs as sim
from kvittering import simulate_util as su
import pandas as pd

#%%
## Set the simulation configuration. We can reuse this, then control in the simulation call what effects we want implemented.
sim_config = sim.SimConfig(
    sim_pop=1000,
    eats_healthy_prob=0.5,
    organized_prob=0.3,
    rural_prob=0.2,
    health_education_effect=0.20,
    health_organized_effect=0.40,
    health_rural_effect=-0.20,
    health_hh_size_effect=-0.3,
    freq_education_effect=-0.20,
    freq_organized_effect=-0.4,
    freq_rural_effect=-0.10,
    freq_hh_size_effect=0.0
)

sim_object: su.HouseholdSim = su.simulate(sim_config, sim_affect=sim.ParameterAffects.BOTH, printout=True)

data_report: pd.DataFrame = su.compare_report(sim_object)
full_dat:pd.DataFrame = sim_object.sampled_data.all_households


#%%
data_report

#%%

sim_object2: su.HouseholdSim = su.simulate(sim_config, sim_affect=sim.ParameterAffects.HEALTHINESS,printout=True)

data_report2: pd.DataFrame = su.compare_report(sim_object=sim_object2)
full_dat2:pd.DataFrame = sim_object2.sampled_data.all_households

#%%
data_report2
#su.receipt_count_by_group(sim_object2.sampled_data, "household_type")

#%%

sim_object3: su.HouseholdSim = su.simulate(sim_config,sim_affect=sim.ParameterAffects.NONE, printout=True)
data_report3: pd.DataFrame = su.compare_report(sim_object3)
full_dat3:pd.DataFrame = sim_object3.sampled_data.all_households

#%%
data_report3



#%%
assert sim_object.sampled_data is not None
#%%

temp_full_households : pd.DataFrame = sim_object.sampled_data.all_households.groupby("h_id", as_index=False).first()
temp_full_receipts : pd.DataFrame = sim_object.sampled_data.all_households.groupby("h_id", as_index=False).first()
temp_sampled_receipts : pd.DataFrame = sim_object.sampled_data.sampled_receipts.groupby("h_id", as_index=False).first()

#%%
sim_object.sampled_data.metadata

#%%
su.compare_single(sim_object.sampled_data, "education")
#%%


#%%
su.compare_health_by_group(sim_object.sampled_data, "education")
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
