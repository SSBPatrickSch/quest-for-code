#%%
from pandas.core.frame import DataFrame
from pydoc import describe

from random import randint
from typing import Any
from kvittering import class_defs as sim
from kvittering import simulate_util as su
import pandas as pd

#%%

def sim_and_compare(utdanning_effekt: int, sim_pop: int = 10000, colname : str = "") -> DataFrame:
    params = sim.SimHandleFrekvensParams(
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
default_comp: DataFrame = su.compare_sampling(sampled_data=su.SampledData(sim_object=default_sim), column="er_strukturert")

#%%
params_sjelden = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    strukturert_effekt= -5,
    strukturert_prob=0.2)

sjelden_sim = su.lag_husholdnings_handle_sim(sim_config=params_sjelden,printout=False)
sjelden_sampled_data = su.SampledData(sjelden_sim)
sjelden_comp = su.compare_sampling(sampled_data=sjelden_sampled_data,column="er_strukturert")

#%%
# Høyere utdanning = handler oftere

params_ofte = sim.SimHandleFrekvensParams(
    sim_pop=10000,
    strukturert_effekt= 5,
    strukturert_prob=0.2)

ofte_sim = su.lag_husholdnings_handle_sim(sim_config=params_ofte,printout=False)
ofte_sampled_data = su.SampledData(ofte_sim)
ofte_comp_str = su.compare_sampling(sampled_data=ofte_sampled_data,column="er_strukturert")

#%%


#%%
default_comp

#%%
sjelden_comp
#%%
ofte_comp


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
