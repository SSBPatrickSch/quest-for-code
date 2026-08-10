#%%


from pandas.core.frame import DataFrame
from pydoc import describe

from random import randint
from typing import Any
from kvittering import class_defs as sim
from kvittering import simulate_util as su
import pandas as pd


#%%

## Kjør to simuleringer hvor vi kun endrer effekten av utdanning

params: sim.SimHandleFrekvensParams = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    utdanning_effekt= -5)

sim_object: su.HusholdningsHandleSim = su.lag_husholdnings_handle_sim(sim_config=params, printout=False)
su.compare_sampling(sampled_data=su.SampledData(sim_object), column="utdanning")

#%%
params: sim.SimHandleFrekvensParams = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    utdanning_effekt= 0)

sim_object: su.HusholdningsHandleSim = su.lag_husholdnings_handle_sim(sim_config=params, printout=False)
su.compare_sampling(sampled_data=su.SampledData(sim_object), column="utdanning")



#%%



#%%
params: sim.SimHandleFrekvensParams = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    utdanning_effekt= -5,
    husholdning_antall_effekt= 2,
    rural_effekt= -3,
    rural_prob=0.3,
    strukturert_effekt= -5, 
    strukturert_prob=0.3,
    default_turer=200)

sim_object: su.HusholdningsHandleSim = su.lag_husholdnings_handle_sim(sim_config=params, printout=True)

#%%
## lag sample data

#%%
#%%

sample_data1 : su.SampledData = su.SampledData(sim_object)
su.compare_sampling(sample_data1, "utdanning")

####

#%%

interesting_cols: list[str] = ['husholdningstype', 'utdanning', 'ant_pers', 'er_strukturert']

for col in interesting_cols:
    print(su.compare_sampling(sample_data,column=col))

#%%

# %%
