from dataclasses import dataclass
from random import randint
from typing import Any
import time

from kvittering import class_defs as sim


class HusholdningsHandleSim:
    """Container for gjennomført simulering av husholdninger og ett år av deres handleturer"""
    def __init__(
        self,
        sim_config : sim.SimHandleFrekvensParams,
        husholdninger : list[sim.Husholdning],
        alle_kvitteringer : list[sim.Kvittering],
        kvitteringssum : int
        ) -> None:

        self.sim_config : sim.SimHandleFrekvensParams = sim_config
        self.husholdninger : list[sim.Husholdning]  = husholdninger 
        self.alle_kvitteringer : list[sim.Kvittering] = alle_kvitteringer
        self.kvitteringssum : int = kvitteringssum 

    def __repr__(self) -> Any:
        return(
            "\n"
            "==================================================\n"
            f"Simulerte husholdninger: {len(self.husholdninger)}\n"
            f"Konstruerte kvitteringer: {len(self.alle_kvitteringer)}\n"
            f"Totalt handlet for: {self.kvitteringssum}\n"
            f"Totalt handlet for: {round(number=self.kvitteringssum/1000000)} millioner\n"
            f"Gjennomsnittlig kvittering kostnad: {round(sum(k.pris for k in self.alle_kvitteringer) / len(self.alle_kvitteringer))}\n"
            f"Gjennomsnittlig årlig kost pr husholdning {self.kvitteringssum / len(self.husholdninger)}\n"
            "==================================================\n"
            )

    def print_husholdninger(self,n_print_husholdninger : int = 1) -> Any:
        print(
            f" {n_print_husholdninger} tilfeldige husholdninger:\n"
            )
        for i in range(n_print_husholdninger):
            trekk: int = randint(0, n_print_husholdninger)
            print(f"{self.husholdninger[trekk]}")


def lag_husholdnings_handle_sim(sim_config: sim.SimHandleFrekvensParams|None = None, printout : bool = True) -> HusholdningsHandleSim:
    
    """Alternativ funksjon som ikke returnerer dedikert class. Gjennomfører en komplett simulering basert på ønsket befolkning (n_befolkning).
    Returnerer dataclass HusholdningsHandleSim
    
    Optional printout for å printe statusoppdateringer"""
    _sim_config: sim.SimHandleFrekvensParams
    if sim_config != None:
        _sim_config = sim_config
    else:
        _sim_config = sim.SimHandleFrekvensParams()
    husholdninger: list[sim.Husholdning] = lag_og_simuler(sim_config=_sim_config, printout=printout)
    alle_kvitteringer: list[sim.Kvittering] = get_alle_kvitteringer(husholdninger_handlet=husholdninger, printout=printout)
    kvitteringssum: int = get_kvitt_sum(alle_kvitteringer, printout=printout)

    return HusholdningsHandleSim(
        sim_config=_sim_config,
        husholdninger=husholdninger,
        alle_kvitteringer=alle_kvitteringer,
        kvitteringssum=kvitteringssum,
    )


def lag_og_simuler(sim_config: sim.SimHandleFrekvensParams, printout : bool) -> list[sim.Husholdning]:
    """Lager n_befolkning antall husholdninger og kjører simulering for ett år med handling.
    
    Optional printout for å printe statusoppdateringer"""

    if printout:
        start_lag_husholdning: float = time.time()

    husholdninger: list[sim.Husholdning] = sim.lag_befolkning(sim_config=sim_config)
    
    if printout:
        end_lag_husholdning: float = time.time()
        print("Complete: Husholdninger konstruert uten handling :", len(husholdninger))
        print(f'Kjøretid: {end_lag_husholdning - start_lag_husholdning:.2f} sekunder')
        start_sim: float = time.time()

    husholdninger_handlet :list[sim.Husholdning] = sim.simuler_handling(husholdninger)

    if printout:
        end_sim: float = time.time()
        print("Complete: Husholdninger handlet for ett år: ", len(husholdninger_handlet))
        print(f'Kjøretid: {end_sim - start_sim:.2f} sekunder')
        print("Første husholdning :", husholdninger_handlet[0])
        print("Første kvittering :", husholdninger_handlet[0].kvitteringer[1])

    return husholdninger_handlet

def get_alle_kvitteringer(husholdninger_handlet : list[sim.Husholdning], printout : bool)-> list[sim.Kvittering]:
    """Lager og returnerer liste over Kvittering objekter basert på simulering"""
    alle_kvitteringer : list[sim.Kvittering] = []
    for h in husholdninger_handlet:
        for k in h.kvitteringer:
            alle_kvitteringer.append(k)
    if printout:
        print("Antall kvitteringer: ", len(alle_kvitteringer))
    return alle_kvitteringer

def get_kvitt_sum(alle_kvitteringer : list[sim.Kvittering], printout : bool) -> int:
    """Lager og returnerer sum av pris på kvitteringer basert på simulering"""
    tot_sum : int = 0
    for k in alle_kvitteringer:
        tot_sum += k.pris
    if printout:
        print("Samlede kvitteringssum ", tot_sum)
    return tot_sum


def skriv_filer(base_path : str) -> None:
    """Skriver filer til bøtte"""
    pass