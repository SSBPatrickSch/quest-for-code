#%%
from random import randint
from typing import Any
import class_defs as sim

#%%
husholdninger: list[sim.Husholdning] = sim.lag_befolkning(n_befolkning=100000)

print("Completed")
print(len(husholdninger))

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

def print_litt(n_print_husholdninger : int = 0):
    to_print: list[int] = []
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
print_litt(1)
# %%
