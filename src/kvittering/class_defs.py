## husholdning class

from random import random, randint, gauss
from dataclasses import dataclass
from enum import Enum

class Education(Enum):
    UOPPGITT = 0
    GRUNNSKOLE = 1
    VIDEREGÅENDE = 2
    FAGSKOLE = 3
    HØYERE = 4

class HouseholdType(Enum):
    ALENEBOENDE = 1
    PAR_UTEN_BARN = 2
    PAR_MED_BARN = 3
    ENSLIG_MED_BARN = 4 
    ANNET = 5

@dataclass 
class Receipt:
    """k_id is household_id (h_id)+ _ + household shopping trip number """
    k_id : str
    h_id : int 
    items : int
    cost : int
    healthy : bool

# Fordeling hentet fra :
# https://www.ssb.no/utdanning/utdanningsniva/statistikk/befolkningens-utdanningsniva
# Kumulativ regnet først som andel av samlet, deretter andel + andel
education_distribution : dict[float, Education] = {
    0.050 : Education.UOPPGITT, 
    0.232 : Education.GRUNNSKOLE, 
    0.583 : Education.VIDEREGÅENDE, 
    0.617 : Education.FAGSKOLE, 
    1.000 : Education.HØYERE
}

# 06944: Inntekt for husholdninger, etter år og husholdningstype
# https://www.ssb.no/statbank/table/06944
# Kumulativ regnet først som andel av samlet, deretter andel + andel
householdtype_distribution : dict[float, HouseholdType] = {
    0.421: HouseholdType.ALENEBOENDE,
    0.662 : HouseholdType.PAR_UTEN_BARN,
    0.847 : HouseholdType.PAR_MED_BARN,
    0.888 : HouseholdType.ENSLIG_MED_BARN,
    1.00 : HouseholdType.ANNET
}

class ParameterAffects(Enum):
    NONE = 0
    SHOPPING_FREQ = 1
    HEALTHINESS = 2
    BOTH = 3


class SimConfig():
    """
    Config object to tune parameters for the simulation, primarily how often households shop. Note that they converge, price wise.

    parameter_affects: Corresponds to three "states". Choose whether config effects affect shopping frequency, healthiness propensity or both.

    Positive values will increase shopping frequency
    Negative values will decrease shopping frequency

    All "_effect" are percentages, i.e., between 0.00-1.00
    
    All effects are implemented per 1 value increase, i.e., high and low values will be affected equally.

    All "_prob" determines the percentage of households that should have this trait.

    Randomness is only included in creating the household, not the shopping frequency.
    
    """
    def __init__(self,
                sim_pop : int = 1,
                parameter_affects: ParameterAffects = ParameterAffects.SHOPPING_FREQ,
                default_shop_n_year : int = 150,

                eats_healthy_prob : float = 0.5,
                organized_prob : float = 0.2,
                rural_prob : float = 0.2,

                education_effect : float = 0.00,
                rural_effect :  float = 0.00,
                organized_effect : float = 0.00,
                ) -> None:

        self.sim_pop : int = sim_pop
        self.parameter_affects: ParameterAffects = parameter_affects
        self.eats_healthy_prob: float = eats_healthy_prob
        self.default_shop_n_year : int = default_shop_n_year
        self.organized_prob : float = organized_prob
        self.rural_prob : float = rural_prob
        self.education_effect : float = education_effect
        self.rural_effect : float = rural_effect
        self.organized_effect : float = organized_effect

    def __repr__(self) -> str:
        return (
            "==================================================\n"
            "===             SIMULATION PARAMETERS          ===\n"
            "==================================================\n"
            f"{self.sim_pop:<10} Number of simulated households\n"
            f"{self.default_shop_n_year:<10} Default shopping trips per year\n"
            f"{self.eats_healthy_prob:<10} Probability of eating healthy\n"
            f"{self.organized_prob:<10} Probability of being 'organized'\n"
            f"{self.rural_prob:<10} Probability of living in a rural area\n"
            f"{self.education_effect:<10} Education effect\n"
            f"{self.rural_effect:<10} Rural effect\n"
            f"{self.organized_effect:<10} Organized effect\n"
        )

def create_healthy_frac(params: SimConfig, education: Education, organized: bool, rural: bool) -> float:
    healthiness: float = params.eats_healthy_prob

    if params.parameter_affects in (
        ParameterAffects.HEALTHINESS,
        ParameterAffects.BOTH,
    ):
        if organized:
            healthiness *= 1 + params.organized_effect
        if rural:
            healthiness *= 1 + params.rural_effect
        healthiness *= 1 + education.value * params.education_effect

    return max(0.0, min(1.0, healthiness))

def create_shopping_frequency(params: SimConfig, education: Education, organized: bool, hh_size: list[int], rural: bool) -> int:
    """Builds a frequency multiplier score from sim config params, then returns the default_trips * multiplier"""

    frequency: float = params.default_shop_n_year

    if params.parameter_affects in (
        ParameterAffects.SHOPPING_FREQ,
        ParameterAffects.BOTH,
    ):
        if organized:
            frequency *= 1 + params.organized_effect
        if rural:
            frequency *= 1 + params.rural_effect
        frequency *= 1 + education.value * params.education_effect
        frequency *= create_hh_size_weight(hh_size)

    return max(1, round(frequency))

## Affect State independent construction.
def create_household_size(household_type : HouseholdType) -> list[int]:  
    """Returns a a list where index[0] are adults, index[1] are children """

    match household_type:
        case HouseholdType.ALENEBOENDE: return [1,0]
        case HouseholdType.PAR_UTEN_BARN: return [2,0]
        case HouseholdType.PAR_MED_BARN: return [2, create_children_count()]
        case HouseholdType.ENSLIG_MED_BARN: return [1, create_children_count()]
        case HouseholdType.ANNET: return [randint(3,5), create_children_count() + create_children_count()]

def create_children_count() -> int:
    """Generates number of children + adults. For other cat, randomizes."""
    children : int = 0
    seed: int = randint(1,10)
    if seed > 8:
        children = 1
    elif seed > 5:
        children = 2
    else:
        children = seed
    return children


def create_hh_size_weight(hh_size : list[int]) -> float:
    """This creates a weigthed shopping cost-ish score for a household to model "stordriftsfordeler" to some extent.
    First adult is 1.0, each extra adult is fraction of 1.0 (arg2), and all children are fraction (arg2*0.7) of 1.0.
    """
    single_adult_household_equivalent : float = 1.0

    adults : int = hh_size[0]
    children : int = hh_size[1]

    if adults > 1:
        single_adult_household_equivalent += (0.7 * (adults -1))
    if children > 0:
        single_adult_household_equivalent += (0.4 * children)

    return single_adult_household_equivalent


def create_organized(organized_prob: float) -> bool:
    return random() < organized_prob

def create_rural(rural_prob : float) -> bool:
    return random() < rural_prob

def create_education()-> Education:
    rfloat: float = random()
    for key in education_distribution.keys():
        if key > rfloat:
            return education_distribution[key]
    #should never trigger, but for the intellisense
    return Education.HØYERE

def create_household_type() -> HouseholdType:
    rfloat: float = random()
    for key in householdtype_distribution.keys():
        if key > rfloat:
            return householdtype_distribution[key]
    #should never trigger, but for the intellisense
    return HouseholdType.ANNET



@dataclass
class HouseholdDefinition:
    household_type: HouseholdType
    education : Education
    rural : bool
    organized : bool
    household_size : list[int]
    eats_healthy_frac : float
    shopping_trips_year : int
    
def get_compare_pattern(colname : str) -> list[str] | None:
    match colname:
        case "husholdningstype" : return [e.name for e in HouseholdType]
        case "utdanning" : return [e.name for e in Education]
        case _: return None 


def create_household_definition(sim_params : SimConfig) -> HouseholdDefinition:
    organized : bool = create_organized(organized_prob=sim_params.organized_prob)
    rural : bool = create_rural(sim_params.rural_prob)
    
    household_type: HouseholdType = create_household_type()
    education : Education = create_education()

    household_size: list[int] = create_household_size(household_type=household_type)
    eats_healthy_frac: float = create_healthy_frac(sim_params,education,organized,rural)
    shopping_trips_year: int = create_shopping_frequency(params=sim_params,education=education,organized=organized,hh_size=household_size,rural=rural)

    return HouseholdDefinition(
        household_type= household_type,
        education= education,
        rural=rural,
        organized= organized,
        household_size=household_size,
        eats_healthy_frac=eats_healthy_frac,
        shopping_trips_year=shopping_trips_year
        )

class Household:
    """Note, shopped healthily is simple whether or not more than half of the receipts were healthy """
    def __init__(self, h_id : int, definition : HouseholdDefinition) -> None:

        self.h_id : int = h_id + 1
        # Fra definisjon
        self.household_type : HouseholdType= definition.household_type
        self.education: Education = definition.education
        self.eats_healthy_frac : float = definition.eats_healthy_frac
        self.shopped_healthy : bool
        self.rural : bool =definition.rural
        self.organized : bool = definition.organized
        self.adults : int =  definition.household_size[0]
        self.children : int =  definition.household_size[1]
        self.household_size: int = self.adults + self.children
        self.shopping_trips_year: int = max(1, definition.shopping_trips_year)
        # Fra konstruksjon
        self.receipts : list[Receipt] = []

    def __repr__(self) -> str:
        return (
            "==================================================\n"
            f"ID: {self.h_id}\n"
            f"Household type: {self.household_type.name}\n"
            f"Household size: {self.household_size}\n"
            f"Education: {self.education.name}\n"
            f"Lives in rural area: {self.rural}\n"
            f"Organized: {self.organized}\n"
            f"N receipts: {len(self.receipts)}\n"
            f"Total spending: {self.get_receit_tot_cost()} NOK\n"
        )
        # For quick and easy transform to dataframe.
    def as_dict(self) -> dict:
        return {
            "h_id": self.h_id,
            "household_type": self.household_type.name,
            "education": self.education.name,
            "household_size": self.household_size,
            "adults" : self.adults,
            "children" : self.children,
            "organized": self.organized,
            "rural" : self.rural,
            "eats_healthy_cfg": self.eats_healthy_frac,
            "shopped_healthy" : self.shopped_healthy,
            "shop_pr_yr": self.shopping_trips_year,
            "n_receipts": len(self.receipts),
            "tot_spending": self.get_receit_tot_cost()
        }

    def get_receit_tot_cost(self) -> int:
            return sum(k.cost for k in self.receipts)
    
    def create_receipt_healthiness(self) -> bool:
        return random() < self.eats_healthy_frac

    def shop_one_year(self):
        # We estimate 57 120 NOK per year per adult on groceries: (4760 pr måned for voksen mann 30-50 år)
        # https://www.oslomet.no/om/sifo/referansebudsjettet

        target_spending_year: int = 57120 * self.household_size
        target_average_receipt: float = target_spending_year / self.shopping_trips_year

        healthy_counter : int = 0

        for tur in range(self.shopping_trips_year):
            cost: int = round(number=gauss(mu=target_average_receipt, sigma=target_average_receipt * 0.25))
            cost = max(cost, 100)
            cost_avg_item = 45
            n_items: int = max(1, round(number= cost/ cost_avg_item))
            healthy : bool = self.create_receipt_healthiness()
            self.receipts.append(
                Receipt(
                    k_id=f"{self.h_id}-{tur}",
                    h_id= self.h_id,
                    items=n_items,
                    cost=cost,
                    healthy= healthy
                    ))
            if healthy:
                healthy_counter += 1
        self.shopped_healthy = healthy_counter > len(self.receipts)/ 2


def create_households(sim_params : SimConfig) -> list[Household]:
    households : list[Household] = []
    for n in range(sim_params.sim_pop):
        households.append(Household(h_id= n, definition=create_household_definition(sim_params=sim_params)))
    return households

def simulate_shopping(households : list[Household]) -> list[Household]:
    for h in households:
        h.shop_one_year()
    return households