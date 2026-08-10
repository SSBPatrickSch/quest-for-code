#%%

from random import randint
from typing import Any
from kvittering import class_defs as simS
from kvittering import simulate_util as su
import kvittering.class_defs as sim
import pandas as pd

#%%
import sys
print(sys.executable)
import subprocess
subprocess.run([sys.executable, "-m", "pip", "show", "pandas"])

#%%
params: sim.SimHandleFrekvensParams = sim.SimHandleFrekvensParams(
    sim_pop=100,utdanning_effekt= 1,
    husholdning_antall_effekt= 1,
    rural_effekt= 2,
    rural_prob=0.3,
    strukturert_effekt=1, 
    strukturert_prob=3,
    default_turer=200)

sim_object: su.HusholdningsHandleSim = su.lag_husholdnings_handle_sim(sim_config=params, printout=True)


#%%
print(sim_object)


#%%

sim_object.print_husholdninger(n_print_husholdninger=10)
#%%
sim_object.alle_kvitteringer
#%%

#%%

husholdninger: list[sim.Husholdning] = sim_object.husholdninger

#%%
print(husholdninger[1])
print(husholdninger[2])


#%%
husholdninger_handlet : list[sim.Husholdning] = sim.simuler_handling(husholdninger)
print("Completed")
print(husholdninger[1])
print(husholdninger[2])
print(len(husholdninger_handlet))

#%%
alle_kvitteringer : list[sim.Kvittering] = []

for h in husholdninger:
    for k in h.kvitteringer:
        alle_kvitteringer.append(k)

print("Completed kvitteringer")
print(len(alle_kvitteringer))

#%%
tot_sum : int = 0

for k in alle_kvitteringer:
    tot_sum += k.pris

print(tot_sum)


# %%

def print_litt(husholdninger : list[sim.Husholdning],n_print_husholdninger : int = 0):
    to_print: list[sim.Husholdning] = []
    for i in range(n_print_husholdninger):
        to_print.append(husholdninger[i + randint(0,100000)])

    print("Simulerte husholdninger: ",len(husholdninger_handlet))
    print("Konstruerte kvitteringer: ",len(alle_kvitteringer))
    print("Totalt handlet for: ", tot_sum)
    print("Totalt handlet for: ", round(tot_sum/1000000), "millioner")
    print("Gjennomsnittlig kvittering kostnad: ", round(sum(k.pris for k in alle_kvitteringer) / len(alle_kvitteringer)))
    print("Gjennomsnittlig årlig kost pr husholdning ",  tot_sum / 100000)
    print("Tilfeldig husholdninger:", to_print)
# %%
print_litt(husholdninger, 4)
# %%
