from dataclasses import dataclass
from random import randint
from typing import Any
import time
import pandas as pd
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
            f"{self.sim_config}\n"
            "==================================================\n"
            f"Simulerte husholdninger: {len(self.husholdninger)}\n"
            f"Konstruerte kvitteringer: {len(self.alle_kvitteringer)}\n"
            f"Totalt handlet for: {self.kvitteringssum}\n"
            f"Totalt handlet for: {round(number=self.kvitteringssum/1000000, ndigits=2)} millioner\n"
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
        print(f"Complete: Husholdninger handlet for ett år: {len(husholdninger_handlet)}")
        print(f'Kjøretid: {end_sim - start_sim:.4f} sekunder')
        print(f"Første husholdning :\n {husholdninger_handlet[0]}")
        print(f"Første kvittering : \n {husholdninger_handlet[0].kvitteringer[1]}")

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

class SampledData:
    husholdninger : pd.DataFrame
    sampled_husholdninger: pd.DataFrame
    sampled_kvitteringer : pd.DataFrame
    
    def __init__(self,sim_object: HusholdningsHandleSim,sample_frac: float = 0.01,) -> None:

        husholdning_df : pd.DataFrame = pd.DataFrame( h.as_dict() for h in sim_object.husholdninger)
        kvittering_df : pd.DataFrame = pd.DataFrame(sim_object.alle_kvitteringer)

        husholdning_uttrekk : pd.DataFrame = husholdning_df.sample(frac=sample_frac)
        kvittering_uttrekk : pd.DataFrame = kvittering_df.sample(frac=sample_frac)

        self.husholdninger = husholdning_df
        self.sampled_husholdninger = husholdning_uttrekk.merge(right=kvittering_df, on="h_id", how="inner")
        self.sampled_kvitteringer =kvittering_uttrekk.merge(right=husholdning_df, on="h_id", how="inner")


def compare_sampling(sampled_data: SampledData, column: str) -> pd.DataFrame:
    # True distribution: all receipts
    households: pd.DataFrame = (sampled_data.husholdninger[column].value_counts(normalize=True) * 100)

    # Household sampling: 1% households, then all their receipts
    husholdning_trekk : pd.DataFrame = (sampled_data.sampled_husholdninger[column].value_counts(normalize=True) * 100)
    # Receipt sampling: 1% of all receipts
    kvittering_trekk : pd.DataFrame = (sampled_data.sampled_kvitteringer[column].value_counts(normalize=True) * 100)

    order: list[str] | None = sim.get_compare_pattern(column)

    result : pd.DataFrame  = pd.DataFrame({
        "Fordeling full sim": households,
        "Husholdningsuttrekk": husholdning_trekk,
        "Kvitteringsuttrekk": kvittering_trekk,
    }).reindex(order).fillna(0)

    if order is not None:
        result = result.reindex(order)
    else:
        result = result.sort_index()

    # Bias relative to the true receipt distribution
    result["Diff husholdningsuttrekk"] = (result["Husholdningsuttrekk"] - result["Fordeling full sim"])
    result["Diff kvitteringsuttrekk"] = (result["Kvitteringsuttrekk"] - result["Fordeling full sim"] )

    return result.round(2)


def sim_og_rapporter(params : sim.SimHandleFrekvensParams) -> pd.DataFrame:
    sim_object: HusholdningsHandleSim = lag_husholdnings_handle_sim(sim_config=params, printout=False)
    sample_data : SampledData = SampledData(sim_object)
    return compare_sampling(sample_data, "utdanning")
