#%%
from typing import Any
import class_defs as sim

#%%
husholdninger: list[sim.Husholdning] = sim.simuler(n_befolkning=1000)

print("Completed")

#%%
print(husholdninger[1])
print(husholdninger[2])
#%%

alle_kvitteringer : list[sim.Kvittering] = []

for h in husholdninger:
    for k in h.kvitteringer:
        alle_kvitteringer.append(k)

print("Completed kvitteringer")
print(len(alle_kvitteringer))
# %%
