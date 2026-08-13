from pandas.core.frame import DataFrame
from dataclasses import dataclass
from enum import Enum
from random import randint
from typing import Any, Never
import time
import pandas as pd
from kvittering import class_defs as sim

@dataclass
class HouseholdSim:
    """
    Data container for completed simulation of households and one year worth of their shopping trips.
    To stay leaner it stores the sim results in two lists of dedicated classes.

    sampled_data (Optional, set arg when running sim):
    
    sampled_data contains a SampleData dataclass consisting of pandas DataFrames that are merged and comparable, including 1% sampled data:

    alle_husholdninger : pd.DataFrame
    alle_kvitteringering : pd.DataFrame
    sampled_husholdninger: pd.DataFrame
    sampled_kvitteringer : pd.DataFrame
    """
    sim_config : sim.SimConfig
    households : list[sim.Household]
    receipts : list[sim.Receipt]
    receipt_tot_sum: int
    sampled_data: "SampledData | None" = None

    def __repr__(self) -> Any:
        return(
            f"{self.sim_config}\n"
            "==================================================\n"
            f"Simulated households: {len(self.households)}\n"
            f"N receipts made: {len(self.receipts)}\n"
            f"Total shopping cost: {self.receipt_tot_sum}\n"
            f"Total shopping: {round(number=self.receipt_tot_sum/1000000, ndigits=2)} millions\n"
            f"Average receipt sum cost: {round(sum(k.cost for k in self.receipts) / len(self.receipts))}\n"
            f"Average cost per household {self.receipt_tot_sum / len(self.households)}\n"
            f"SampleData set: {'yes' if self.sampled_data is not None else 'no'}\n"
            "==================================================\n"
            )
    def create_sampled_data(self, sample_frac: float = 0.01) -> None:
        self.sampled_data = SampledData(
        self,
        sample_frac,
    )



def print_households(sim_object : HouseholdSim,n_to_print : int = 1) -> Any:
    """Prints (arg2) amount of random households from simulation (arg1)"""
    print(f" {n_to_print} Random households:\n")
    for i in range(n_to_print):
        idx: int = randint(0, n_to_print)
        print(f"{sim_object.households[idx]}")


def simulate(sim_config: sim.SimConfig|None = None, printout : bool = True, create_sample_data : bool = True) -> HouseholdSim:
    """ Creates households and simulates one year of shopping.

    Returns a HouseholdSim data object.

    Optional parameters:

    printout (default True)
    
    create_sample_data (default True) makes a pandas DataFrame container with sampled data. 
    Set to false to lessen runtime and access lists in returned HouseholSim directly.
    """

    if sim_config == None:
        sim_config = sim.SimConfig()

    households: list[sim.Household] = simulate_no_class(sim_config, printout)
    receipts: list[sim.Receipt] = get_all_receipts(households, printout)
    receipt_tot_sum: int = create_receit_total_cost(receipts, printout)

    new_sim: HouseholdSim = HouseholdSim(sim_config,households,receipts,receipt_tot_sum)
    if create_sample_data:
        new_sim.create_sampled_data(sample_frac=0.01)
    return new_sim


def simulate_no_class(sim_config: sim.SimConfig, printout : bool) -> list[sim.Household]:
    if printout:
        start_lag_husholdning: float = time.time()

    households: list[sim.Household] = sim.create_households(sim_params=sim_config)
    
    if printout:
        end_lag_husholdning: float = time.time()
        print("Complete: Households constructed (prior to shopping sim) :", len(households))
        print(f'Run time: {end_lag_husholdning - start_lag_husholdning:.2f} sekunder')
        start_sim: float = time.time()

    households_shopped :list[sim.Household] = sim.simulate_shopping(households, sim_config)

    if printout:
        end_sim: float = time.time()
        print(f"Complete: Simulated shopping for: {len(households_shopped)} households")
        print(f'Run time: {end_sim - start_sim:.4f} seconds')
        print(f"First household :\n {households_shopped[0]}")
        print(f"Receipts first housheold : {len(households_shopped[0].receipts)}")
        print(f"First receipt : \n {households_shopped[0].receipts[0]}")

    return households_shopped

def get_all_receipts(households_shopped : list[sim.Household], printout : bool)-> list[sim.Receipt]:
    """Fetches all receipts in houshold and returns as list"""
    all_receipts : list[sim.Receipt] = []
    for h in households_shopped:
        for k in h.receipts:
            all_receipts.append(k)
    if printout:
        print("N receipts: ", len(all_receipts))
    return all_receipts

def create_receit_total_cost(alle_kvitteringer : list[sim.Receipt], printout : bool) -> int:
    """Creates the grand total for all receits"""
    tot_sum : int = 0
    for k in alle_kvitteringer:
        tot_sum += k.cost
    if printout:
        print("Samlede kvitteringssum ", tot_sum)
    return tot_sum


def write_files(base_path : str) -> None:
    """Writes a sim object to bøtte"""
    pass

class SampledData:
    """Pandas DataFrame container. all_X is the full simulated datasets. sampled_x is a 1% sample: unit : receipt, households merged on."""
    all_households : pd.DataFrame
    all_receipts : pd.DataFrame
    sampled_households: pd.DataFrame
    sampled_receipts : pd.DataFrame
    
    def __init__(self,sim_object : HouseholdSim, sample_frac: float = 0.01) -> None:

        self.all_households = pd.DataFrame( h.as_dict() for h in sim_object.households)
        self.all_receipts = pd.DataFrame(sim_object.receipts)

        self.sampled_households = self.all_households.sample(frac=sample_frac)
        self.sampled_receipts = self.all_receipts.sample(frac=sample_frac)

        self.sampled_households = self.sampled_households.merge(right=self.all_receipts, on="h_id", how="inner")
        self.sampled_receipts =self.sampled_receipts.merge(right=self.all_households, on="h_id", how="inner")


def compare_sampling(sampled_data: SampledData | None, column: str) -> pd.DataFrame:
    """General comparison function that returns a minimal display DataFrame for one variable of interest.
    
    It has three columns of distributions: The full data, the household sampled, and the receipt sampled."""

    if sampled_data is None:
        print("Cannot compare without SampledData Object. Pass HouseholdSim.sampled_data instead")
        return pd.DataFrame()
        
    # True distribution of column in full data
    households: pd.DataFrame = (sampled_data.all_households[column].value_counts(normalize=True) * 100)

    # Household sampling: 1% households, then all their receipts
    household_sampling : pd.DataFrame = (sampled_data.sampled_households[column].value_counts(normalize=True) * 100)
    # Receipt sampling: 1% of all receipts
    receipt_sampling : pd.DataFrame = (sampled_data.sampled_receipts[column].value_counts(normalize=True) * 100)

    result : pd.DataFrame  = pd.DataFrame({
        SampleType.FULL_SIM.name: households,
        SampleType.HOUSEHOLD_SAMPLING.name : household_sampling,
        SampleType.RECEIPT_SAMPLING.name : receipt_sampling,
    }).fillna(0)

    order: list[str] | None = sim.get_compare_pattern(column)

    if order is not None:
        result = result.reindex(order)
    else:
        result = result.sort_index()

    # Bias relative to the true receipt distribution
    result[SampleType.DIFF_HOUSEHOLD.name] = (result[SampleType.HOUSEHOLD_SAMPLING.name] - result[SampleType.FULL_SIM.name])
    result[SampleType.DIFF_RECEIPT.name] = (result[SampleType.RECEIPT_SAMPLING.name] - result[SampleType.FULL_SIM.name])

    return result.round(2)


class SampleType(Enum):
    FULL_SIM = 0
    HOUSEHOLD_SAMPLING = 1
    RECEIPT_SAMPLING = 2
    DIFF_HOUSEHOLD = 3
    DIFF_RECEIPT = 4


def sim_and_compare(sim_config : sim.SimConfig, colnames : str | list[str]) -> pd.DataFrame | dict[str,pd.DataFrame]:
    """Pure utility option that produces full sim and returns comparison dataframe directly.
    Good for small N sims for param tuning.
    
    Pass either a single colname or a list of colnames. If passing a list, returns a list of comparison dataframes
    """
    sim_object: HouseholdSim = simulate(sim_config, printout=False)
    if sim_object.sampled_data is None:
        return None
    sample_data: SampledData = sim_object.sampled_data
    # hacks
    if isinstance(colnames, str):
        return _sim_and_compare_single(sample_data, colnames)

    elif isinstance(colnames, list):
        return _sim_and_compare_multiple(sample_data, colnames)
    
def _sim_and_compare_single(sample_data : SampledData, colname : str) -> pd.DataFrame:
    """Simulates and returns comparison dataframe for given colname"""
    return compare_sampling(sample_data, colname)

def _sim_and_compare_multiple(sample_data : SampledData, colnames: list[str]) -> dict[str, pd.DataFrame]:
    """Simulates and returns list of comparison dataframes """
    comp_dfs : dict[str, pd.DataFrame] = {}
    for col in colnames:
        comp_dfs[str("comp_"+col)] = compare_sampling(sample_data, col)
    return comp_dfs

def compare_health_by_group(sampled_data: SampledData, group: str) -> pd.DataFrame:
    full: pd.DataFrame = sampled_data.all_households[["h_id", group, "shopped_healthy"]]

    household_sample: pd.DataFrame = sampled_data.sampled_households[["h_id", group, "shopped_healthy"]].drop_duplicates("h_id")

    receipt_sample: pd.DataFrame = sampled_data.sampled_receipts[["h_id", group, "shopped_healthy"]].drop_duplicates("h_id")

    full_result: pd.Series = full.groupby(group)["shopped_healthy"].mean() * 100
    household_result: pd.Series = household_sample.groupby(group)["shopped_healthy"].mean() * 100
    receipt_result: pd.Series = receipt_sample.groupby(group)["shopped_healthy"].mean() * 100

    result: pd.DataFrame = pd.DataFrame({
        "FULL": full_result,
        "HOUSEHOLD_SAMPLE": household_result,
        "RECEIPT_SAMPLE": receipt_result
    })

    result["DIFF_HOUSEHOLD"] = result["HOUSEHOLD_SAMPLE"] - result["FULL"]
    result["DIFF_RECEIPT"] = result["RECEIPT_SAMPLE"] - result["FULL"]

    return result.round(2)