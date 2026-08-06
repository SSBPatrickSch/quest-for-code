## husholdning class

from inspect import _void
from random import random, randint, gauss
from dataclasses import dataclass
from enum import Enum
from typing import Annotated

## enum classes for indikatorer med en ønsket varians

class Utdanning(Enum):
    UOPPGITT = 0
    GRUNNSKOLE = 1
    VIDEREGÅENDE = 2
    FAGSKOLE = 3
    HØYERE = 4

class HusholdningsType(Enum):
    ALENEBOENDE = 1
    PAR_UTEN_BARN = 2
    PAR_MED_BARN = 3
    ENSLIG_MED_BARN = 4 
    ANNET = 5


@dataclass 
class Kvittering:
    ant_varer : int = 0
    pris : int = 1
    k_id : str = ""


# Fordeling hentet fra :
# https://www.ssb.no/utdanning/utdanningsniva/statistikk/befolkningens-utdanningsniva
# Kumulativ regnet først som andel av samlet, deretter andel + andel
utdanningsfordeling : dict[float, Utdanning] = {
    0.050 : Utdanning.UOPPGITT, 
    0.232 : Utdanning.GRUNNSKOLE, 
    0.583 : Utdanning.VIDEREGÅENDE, 
    0.617 : Utdanning.FAGSKOLE, 
    1.000 : Utdanning.HØYERE
}

# 06944: Inntekt for husholdninger, etter år og husholdningstype
# https://www.ssb.no/statbank/table/06944
# Kumulativ regnet først som andel av samlet, deretter andel + andel
husholdningstype_fordeling : dict[float, HusholdningsType] = {
    0.421: HusholdningsType.ALENEBOENDE,
    0.662 : HusholdningsType.PAR_UTEN_BARN,
    0.847 : HusholdningsType.PAR_MED_BARN,
    0.888 : HusholdningsType.ENSLIG_MED_BARN,
    1.00 : HusholdningsType.ANNET
}

class SimHandleFrekvensParams():
    """Config objekt for å endre hvordan husholdningsindikatorer endrer handlefrekvens.

    Positive verdier vil øke handlefrekvens, negative vil senke handlefrekvens.

    Utdanning og husholdningsantall blir behandlet lineært, for enkelthets skyld.

    Noe tilfeldig varians blir inkludert, for moro skyld mest.
    
    Arguments:

    ant_pop_sim : int                   -- Antall husholdninger som skal simuleres
    utdanning_effekt : int              -- Utdanningsskala Uoppgitt(0)-høyere(4)
    husholdning_antall_effekt : int     -- Antall 1-7
    rural_effekt : int                  -- Effekten av å bo urbant
    rural_prob : float                  -- Sannsynligheten for å bli bosatt ruralt
    strukturert_effekt : int            -- Effekten av å være strukturert (bool)
    strukturert_prob : float (0.00-1.00)-- Sannsynligheten for at en husholdning er strukturert (bool)
    default_turer : int = 150           -- Basis antatt antall handleturer. varians fra andre variabler vil endre utfra denne
    """
    def __init__(self,
                sim_pop : int = 1,
                utdanning_effekt : int = 0,
                husholdning_antall_effekt : int= 1,
                rural_effekt : int = 0,
                rural_prob : float = 0.2,
                strukturert_effekt : int = 1,
                strukturert_prob : float = 0.5,
                default_turer : int = 150) -> None:

        self.sim_pop : int = sim_pop
        self.utdanning_effekt : int = utdanning_effekt
        self.husholdning_antall_effekt : int = husholdning_antall_effekt
        self.rural_effekt : int = rural_effekt
        self.rural_prob : float = rural_prob
        self.strukturert_effekt : int = strukturert_effekt
        self.strukturert_prob : float = strukturert_prob
        self.default_turer : int = default_turer

    def __repr__(self) -> str:
        return (
            "\n"
            "============== SIMULERINGSPARAMETRE =============="
            "==================================================\n"
            f"Simulerte husholdninger: {self.sim_pop}\n"
            f"Default handleturer: {self.default_turer}\n"
            f"Utdanningseffekt pr steg: {self.utdanning_effekt}\n"
            f"Husholdningsantallseffekt pr ekstra: {self.husholdning_antall_effekt}\n"
            f"Rural effekt på bool: {self.rural_effekt}\n"
            f"Sansynlighet for husholdning rural: {self.rural_prob}\n"
            f"Strukturert effekt på bool: {self.strukturert_effekt}\n"
            f"Sansynlighet for husholdning strukturert: {self.strukturert_prob}\n"
            "==================================================\n"
        )

def set_ant_pers(husholdningstype : HusholdningsType) -> int:
    match husholdningstype:
        case HusholdningsType.ALENEBOENDE: return 1
        case HusholdningsType.PAR_UTEN_BARN: return 2
        case HusholdningsType.PAR_MED_BARN: return randint(3, 7)
        case HusholdningsType.ENSLIG_MED_BARN: return 2
        case HusholdningsType.ANNET: return randint(2, 7)


def set_handlefrekvens(params : SimHandleFrekvensParams, utdanning: Utdanning, strukturert : bool, ant_pers : int, rural : bool) -> int:
    turer : int = params.default_turer

    if strukturert:
        turer += params.strukturert_effekt
    turer += (utdanning.value * params.utdanning_effekt)
    turer += (rural * params.rural_effekt)
    turer += (ant_pers * params.husholdning_antall_effekt)
    
    return turer
 
def set_er_strukturert(strukturert_prob : float) -> bool:
    rfloat: float = random()
    if rfloat > min(1.00,strukturert_prob): return True 
    else: return False

def set_rural(rural_prob : float) -> bool:
    rfloat: float = random()
    if rfloat > min(1.00, rural_prob): return True 
    else: return False

def set_utdanning()-> Utdanning:
    rfloat: float = random()
    for key in utdanningsfordeling.keys():
        if key > rfloat:
            return utdanningsfordeling[key]
    #should never trigger, but for the intellisense
    return Utdanning.HØYERE

def set_husholdningstype() -> HusholdningsType:
    rfloat: float = random()
    for key in husholdningstype_fordeling.keys():
        if key > rfloat:
            return husholdningstype_fordeling[key]
    #should never trigger, but for the intellisense
    return HusholdningsType.ANNET

@dataclass
class HusholdningsDefinisjon:
    husholdningstype: HusholdningsType
    utdanning : Utdanning
    bor_ruralt : bool
    er_strukturert : bool
    ant_pers : int
    handleturer_pr_aar : int


def lag_husholdnings_definisjon(sim_params : SimHandleFrekvensParams) -> HusholdningsDefinisjon:
    _husholdningstype: HusholdningsType = set_husholdningstype()
    _utdanning : Utdanning = set_utdanning()
    _er_strukturert : bool = set_er_strukturert(strukturert_prob=sim_params.strukturert_effekt)
    _bor_ruralt : bool = set_rural(sim_params.rural_prob)
    _ant_pers: int = set_ant_pers(husholdningstype=_husholdningstype)
    _handleturer_pr_aar: int = set_handlefrekvens(params = sim_params,
                                                utdanning=_utdanning,
                                                strukturert=_er_strukturert, 
                                                ant_pers=_ant_pers,
                                                rural=_bor_ruralt
                                                )

    return HusholdningsDefinisjon(
        husholdningstype= _husholdningstype,
        utdanning= _utdanning,
        bor_ruralt= _bor_ruralt,
        er_strukturert= _er_strukturert,
        ant_pers= _ant_pers,
        handleturer_pr_aar= _handleturer_pr_aar)


class Husholdning:
    def __init__(self, h_id : int, definisjon : HusholdningsDefinisjon) -> None:

        self.h_id : int = h_id
        # Fra definisjon
        self.husholdningstype : HusholdningsType= definisjon.husholdningstype
        self.utdanning: Utdanning = definisjon.utdanning
        self.ant_pers : int = definisjon.ant_pers
        self.er_strukturert: bool = definisjon.er_strukturert
        self.handleturer_pr_aar : int = definisjon.handleturer_pr_aar
        # Fra konstruksjon
        self.kvitteringer : list[Kvittering] = []

    def __repr__(self) -> str:
        return (
            "\n"
            "==================================================\n"
            f"ID: {self.h_id}\n"
            f"Husholdningstype: {self.husholdningstype.name}\n"
            f"Ant pers: {self.ant_pers}\n"
            f"Utdanning: {self.utdanning.name}\n"
            f"Strukturert: {self.er_strukturert}\n"
            f"Ant kvitteringer: {len(self.kvitteringer)}\n"
            f"Tot pris: {self.get_kvitt_pris()} kroner\n"
        )

    def get_kvitt_pris(self) -> int:
            return sum(k.pris for k in self.kvitteringer)

    def handle_ett_aar(self):
        # Vi regner omtrentlig 57 120 i året pr voksen på mat: (4760 pr måned for voksen mann 30-50 år)
        # https://www.oslomet.no/om/sifo/referansebudsjettet

        aarlig_target: int = 57120 * self.ant_pers
        snitt_kvittering: float = aarlig_target / self.handleturer_pr_aar

        for tur in range(self.handleturer_pr_aar):
            _pris: int = round(number=gauss(mu=snitt_kvittering, sigma=snitt_kvittering * 0.25))
            pris: int = max(_pris, 100)
            snitt_varepris = 45
            ant_varer: int = max(1, round(number= pris/ snitt_varepris))
            self.kvitteringer.append(
                Kvittering(
                    ant_varer=ant_varer,
                    pris=pris,
                    k_id=f"{self.h_id}-{tur}",
                ))

def lag_befolkning(sim_config : SimHandleFrekvensParams) -> list[Husholdning]:

    husholdninger : list[Husholdning] = []
    for n in range(sim_config.sim_pop):
        husholdninger.append(Husholdning(h_id= n, definisjon=lag_husholdnings_definisjon(sim_params=sim_config)))
    return husholdninger

def simuler_handling(husholdninger : list[Husholdning]) -> list[Husholdning]:
    for h in husholdninger:
        h.handle_ett_aar()
    return husholdninger