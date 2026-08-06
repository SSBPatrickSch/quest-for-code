
from random import randint
from typing import Any
import class_defs as sim

def lag_og_simuler(n_befolkning : int = 100, printout : bool = True) -> list[sim.Husholdning]
    husholdninger: list[sim.Husholdning] = sim.lag_befolkning(n_befolkning=100000)
    if printout:
        print("Complete: Husholdninger handlet for ett år: ", len(husholdninger))
        print("Første kvittering :", husholdninger[1].kvitteringer[1])
    husholdninger_handlet :list[sim.Husholdning] = sim.simuler_handling(husholdninger)
    if printout:
        print("Complete: Husholdninger konstruert uten handling :", len(husholdninger_handlet))
        print("Første husholdning :", (len(husholdninger_handlet)))
    
    return husholdninger_handlet

def get_alle_kvitteringer(husholdninger_handlet : list[sim.Husholdning])-> list[sim.Kvittering]:
    alle_kvitteringer : list[sim.Kvittering] = []

    for h in husholdninger_handlet:
        for k in h.kvitteringer:
            alle_kvitteringer.append(k)

def get_kvitt_sum(alle_kvitteringer : list[sim.Kvittering]) -> int:
    tot_sum : int = 0
    for k in alle_kvitteringer:
        tot_sum += k.pris
    return tot_sum

def print_litt(husholdninger_handlet, alle_kvitteringer, kvitt_sum : int, n_print_husholdninger : int = 0):
    to_print: list[int] = []
    for i in range(n_print_husholdninger):
        to_print.append(husholdninger_handlet[i + randint(0,100000)])

    print("Simulerte husholdninger: ",len(husholdninger_handlet))
    print("Konstruerte kvitteringer: ",len(alle_kvitteringer))
    print("Totalt handlet for: ", kvitt_sum)
    print("Totalt handlet for: ", round(kvitt_sum/1000000), "millioner")
    print("Gjennomsnittlig kvittering kostnad: ", round(sum(k.pris for k in alle_kvitteringer) / len(alle_kvitteringer)))
    print("Gjennomsnittlig årlig kost pr husholdning ",  kvitt_sum / len(husholdninger_handlet))
    print("Tilfeldig husholdninger:", to_print)
