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
            "===            HOUSEHOLD SIMULATION            ===\n"
            "==================================================\n"
            f"{len(self.households):<15}: Simulated households\n"
            f"{len(self.receipts):<15}: N receipts made\n"
            f"{self.receipt_tot_sum:<15}: Total shopping cost\n"
            f"{round(number=self.receipt_tot_sum/1000000, ndigits=2):<15}: Total shopping (millions)\n"
            f"{round(sum(k.cost for k in self.receipts) / len(self.receipts)):<15}: Average receipt sum cost\n"
            f"{self.receipt_tot_sum / len(self.households):<15}: Average cost per household\n"
            f"{('yes' if self.sampled_data is not None else 'no'):<15}: SampleData set\n"
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
        idx: int = randint(0, len(sim_object.households) - 1)
        print(f"{sim_object.households[idx]}")


def simulate(sim_config: sim.SimConfig|None = None,
        sim_affect : sim.ParameterAffects = sim.ParameterAffects.BOTH,
        printout : bool = True, 
        create_sample_data : bool = True
    ) -> HouseholdSim:
    
    """ Creates households and simulates one year of shopping.

    Returns a HouseholdSim data object.

    Optional parameters:

    sim_affect of enum type sim.SimAffect. This dictates what will be employed in the simulation, allowing you to reuse a sim_config.

    printout (default True)
    
    create_sample_data (default True) makes a pandas DataFrame container with sampled data. 
    Set to false to lessen runtime and access lists in returned HouseholSim directly.
    """

    if sim_config == None:
        sim_config = sim.SimConfig()
    
    ## Sets the config to run with said effect
    sim_config.parameter_affects = sim_affect

    households: list[sim.Household] = simulate_no_class(sim_config, printout)
    receipts: list[sim.Receipt] = get_all_receipts(households)
    receipt_tot_sum: int = create_receit_total_cost(receipts)

    new_sim: HouseholdSim = HouseholdSim(sim_config,households,receipts,receipt_tot_sum)
    if create_sample_data:
        new_sim.create_sampled_data(sample_frac=0.01)
    if printout:
        print(new_sim)
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

    households_shopped :list[sim.Household] = sim.simulate_shopping(households)

    if printout:
        end_sim: float = time.time()
        print(f"Complete: Simulated shopping for: {len(households_shopped)} households")
        print(f'Run time: {end_sim - start_sim:.4f} seconds')

    return households_shopped

def get_all_receipts(households_shopped : list[sim.Household])-> list[sim.Receipt]:
    """Fetches all receipts in houshold and returns as list"""
    all_receipts : list[sim.Receipt] = []
    for h in households_shopped:
        for k in h.receipts:
            all_receipts.append(k)
    return all_receipts

def create_receit_total_cost(alle_kvitteringer : list[sim.Receipt]) -> int:
    """Creates the grand total for all receits"""
    tot_sum : int = 0
    for k in alle_kvitteringer:
        tot_sum += k.cost
    return tot_sum


def write_files(base_path : str) -> None:
    """Writes a sim object to bøtte"""
    pass

class SampleType(Enum):
    FULL_SIM = 0
    HOUSEHOLDS_SAMPLED = 1
    RECEIPT_SAMPLING = 2
    DIFF_HOUSEHOLD = 3
    DIFF_RECEIPT = 4

class SampledData:
    """Pandas DataFrame container. all_X is the full simulated datasets. sampled_x is a 1% sample: unit : receipt, households merged on."""
    all_households : pd.DataFrame
    all_receipts : pd.DataFrame
    sampled_receipts : pd.DataFrame
    sampled_households : pd.DataFrame
    metadata:  pd.DataFrame

    def __init__(self, sim_object: HouseholdSim, sample_frac: float = 0.01) -> None:
        self.all_households = pd.DataFrame(h.as_dict() for h in sim_object.households)
        self.all_receipts = pd.DataFrame(sim_object.receipts)

        self.sampled_receipts = self.all_receipts.sample(frac=sample_frac)
        self.sampled_receipts = self.sampled_receipts.merge(right=self.all_households, on="h_id", how="inner")
        self.sampled_households = self.sampled_receipts.drop_duplicates("h_id")

        self.metadata = self.make_sample_metadata()

    def make_sample_metadata(self)-> pd.DataFrame:
        meta_data: list[dict] = [
        {
            "sample": "FULL",
            "n_receipts": len(self.all_receipts),
            "n_households": len(self.all_households),
            "receipts_pr_hh": len(self.all_receipts) / len(self.all_households),
            "receipt_frac": 1.0,
            "household_frac": 1.0,
            "n_hh_healthy" : self.all_households["shopped_healthy_frac"].mean(),
            "n_hh_organized" : self.all_households["organized"].mean()
        },
        {
            "sample": "RECEIPT_SAMPLE",
            "n_receipts": len(self.sampled_receipts),
            "n_households": len(self.sampled_receipts["h_id"].drop_duplicates()),
            "receipts_pr_hh": len(self.sampled_receipts) / len(self.sampled_receipts["h_id"].drop_duplicates()),
            "receipt_frac": len(self.sampled_receipts) / len(self.all_receipts),
            "household_frac": len(self.sampled_receipts["h_id"].drop_duplicates()) / len(self.all_households),
            "hh_shopped_healthy" : self.sampled_receipts["shopped_healthy_frac"].mean(),
            "hh_organized" : self.sampled_receipts["organized"].mean(),
        }
        ]
        return pd.DataFrame(meta_data)


def compare_sampling(sampled_data: SampledData | None, column: str) -> pd.DataFrame:
    """General comparison function that returns a minimal display DataFrame for one variable of interest.
    
    It has three columns of distributions: The full data, the receipt sampled, and the households from the sampled receipts."""

    if sampled_data is None:
        print("Cannot compare without SampledData Object. Pass HouseholdSim.sampled_data instead")
        return pd.DataFrame()
        
    # True distribution of column in full data
    households: pd.DataFrame = (sampled_data.all_households[column].value_counts(normalize=True) * 100)
    # Receipt sampling: 1% of all receipts
    receipt_sampling : pd.DataFrame = (sampled_data.sampled_receipts[column].value_counts(normalize=True) * 100)
    # Only the households that were sampled with 1% of all receipts
    households_sampled : pd.DataFrame = (sampled_data.sampled_households[column].value_counts(normalize=True) * 100)

    result : pd.DataFrame  = pd.DataFrame({
        SampleType.FULL_SIM.name: households,
        SampleType.HOUSEHOLDS_SAMPLED.name : households_sampled,
        SampleType.RECEIPT_SAMPLING.name : receipt_sampling,
    }).fillna(0)

    order: list[str] | None = sim.get_compare_pattern(column)

    if order is not None:
        result = result.reindex(order)
    else:
        result = result.sort_index()

    # Bias relative to the true receipt distribution
    result[SampleType.DIFF_HOUSEHOLD.name] = result[SampleType.HOUSEHOLDS_SAMPLED.name] - result[SampleType.FULL_SIM.name]
    result[SampleType.DIFF_RECEIPT.name] = result[SampleType.RECEIPT_SAMPLING.name] - result[SampleType.FULL_SIM.name]

    return result.round(2)


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
        return compare_single(sample_data, colnames)

    elif isinstance(colnames, list):
        return compare_multiple(sample_data, colnames)
    
def compare_single(sample_data : SampledData, colname : str) -> pd.DataFrame:
    """Simulates and returns comparison dataframe for given colname"""
    return compare_sampling(sample_data, colname)

def compare_multiple(sample_data: SampledData, colnames: list[str]) -> pd.DataFrame:
    comp_dfs: list[pd.DataFrame] = []

    for col in colnames:
        comp_df: pd.DataFrame = compare_sampling(sample_data, col)
        comp_df.index.name = "value"
        comp_df["variable"] = col
        comp_dfs.append(comp_df)

    result: pd.DataFrame = pd.concat(comp_dfs).reset_index()

    return result[["variable","value",SampleType.FULL_SIM.name,SampleType.HOUSEHOLDS_SAMPLED.name,SampleType.RECEIPT_SAMPLING.name,SampleType.DIFF_HOUSEHOLD.name,SampleType.DIFF_RECEIPT.name]]
     
def compare_report(sim_object: HouseholdSim, printout=False) -> pd.DataFrame:
    assert sim_object.sampled_data is not None

    colnames: list[str] = [
        "organized",
        "rural",
        "household_type",
        "education",
    ]

    if printout:
        print(sim_object)

    result = compare_multiple(sim_object.sampled_data, colnames)
    health = compare_health(sim_object.sampled_data)

    health.insert(0, "variable", "shopped_healthy_frac")
    health.insert(1, "value", "MEAN")

    return pd.concat([result, health], ignore_index=True)

def compare_health(sampled_data: SampledData) -> pd.DataFrame:
    full = sampled_data.all_households["shopped_healthy_frac"].mean() * 100
    households_sampled = sampled_data.sampled_households["shopped_healthy_frac"].mean() * 100
    receipts_sampled = sampled_data.sampled_receipts["healthy"].mean() * 100

    return pd.DataFrame({
        "FULL_SIM": [full],
        "HOUSEHOLDS_SAMPLED": [households_sampled],
        "RECEIPT_SAMPLING": [receipts_sampled],
        "DIFF_HOUSEHOLD": [households_sampled - full],
        "DIFF_RECEIPT": [receipts_sampled - full],
    }).round(2)

def receipt_count_by_group(sampled_data: SampledData, group_col: str) -> pd.DataFrame:
    receipts = sampled_data.all_receipts.merge(sampled_data.all_households[["h_id", group_col]], on="h_id", how="left")
    result = receipts.groupby(group_col).size().to_frame("n_receipts")
    result["receipt_share"] = result["n_receipts"] / result["n_receipts"].sum() * 100
    result["household_count"] = sampled_data.all_households.groupby(group_col).size()
    result["receipts_per_household"] = result["n_receipts"] / result["household_count"]
    return result.round(2)