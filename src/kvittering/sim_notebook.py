#%%
from pydoc import describe

from random import randint
from typing import Any
from kvittering import class_defs as sim
from kvittering import simulate_util as su
import pandas as pd

#%%
## Set the simulation configuration. We can reuse this, then control in the simulation call what effects we want implemented.
sim_config = sim.SimConfig(
    sim_pop=100000,
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


#%%

sim_object: su.HouseholdSim = su.simulate(sim_config, sim_affect=sim.ParameterAffects.BOTH, printout=False)


data_report: pd.DataFrame = su.compare_report(sim_object)
full_dat:pd.DataFrame = sim_object.sampled_data.all_households

#%%

#%%
data_report

#%%

sim_object2: su.HouseholdSim = su.simulate(sim_config, sim_affect=sim.ParameterAffects.HEALTHINESS,printout=False)

data_report2: pd.DataFrame = su.compare_report(sim_object=sim_object2)
full_dat2:pd.DataFrame = sim_object2.sampled_data.all_households

#%%
data_report2
#su.receipt_count_by_group(sim_object2.sampled_data, "household_type")

#%%

sim_object3: su.HouseholdSim = su.simulate(sim_config,sim_affect=sim.ParameterAffects.NONE, printout=False)


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
