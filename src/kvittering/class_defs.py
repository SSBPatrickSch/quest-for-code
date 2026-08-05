## husholdning class

from inspect import _void
from random import random, randint, gauss
from dataclasses import dataclass
from enum import Enum

## enum classes for indikatorer med varians

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
def set_ant_pers(husholdningstype : HusholdningsType) -> int:
    match husholdningstype:
        case HusholdningsType.ALENEBOENDE: return 1
        case HusholdningsType.PAR_UTEN_BARN: return 2
        case HusholdningsType.PAR_MED_BARN: return randint(3, 6)
        case HusholdningsType.ENSLIG_MED_BARN: return 2
        case HusholdningsType.ANNET: return randint(2, 7)
    
def set_handlefrekvens(utdanning: Utdanning, strukturert : bool, ant_pers : int) -> int:
    turer : int = 150
    if strukturert:
        turer -= 50
    # Mer utdanning, færre turer
    turer -= utdanning.value * 5
    # Fler folk, flere turer
    turer += (ant_pers - 1) * 8

    return max(30, turer)  


    # høy utdanning (5) * strukturert (2) = 10 / 7
    # lav utdanning (1) * ustrukturet (1) = 1
    # 
    # 365/handle_prob = 36,5
    # 365/handle_prob = 365

# Burde erstattes av noe logikk
def set_er_strukturert() -> bool:
    rfloat: float = random()
    if rfloat > 0.75: return True 
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
    er_strukturert : bool
    ant_pers : int
    handleturer_pr_aar : int

def lag_husholdnings_definisjon() -> HusholdningsDefinisjon:
    _husholdningstype: HusholdningsType = set_husholdningstype()
    _utdanning : Utdanning = set_utdanning()
    _er_strukturert : bool = set_er_strukturert()
    _ant_pers: int = set_ant_pers(husholdningstype=_husholdningstype)
    _handleturer_pr_aar: int = set_handlefrekvens(utdanning=_utdanning,strukturert=_er_strukturert, ant_pers=_ant_pers)

    return HusholdningsDefinisjon(
        husholdningstype= _husholdningstype,
        utdanning= _utdanning,
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
            f"Ant pers: {self.husholdningstype}\n"
            f"Ant pers: {self.ant_pers}\n"
            f"Utdanning: {self.utdanning}\n"
            f"Strukturert: {self.er_strukturert}\n"
            f"Ant kvitteringer: {len(self.kvitteringer)}\n"
            f"Tot pris: {self.get_kvitt_pris()} kroner\n"
        )

    def get_kvitt_pris(self) -> int:
            return sum(k.pris for k in self.kvitteringer)

    def handletur(self):
        # Vi regner omtrentlig 57 120 i året pr voksen på mat: (4760 pr måned for voksen mann 30-50 år)
        # https://www.oslomet.no/om/sifo/referansebudsjettet

        aarlig_target: int = 57120 * self.ant_pers
        snitt_kvittering: float = aarlig_target / self.handleturer_pr_aar



        for tur in range(self.handleturer_pr_aar):
            _pris: int = round(number=gauss(mu=snitt_kvittering, sigma=snitt_kvittering * 0.25))
            pris: int = max(_pris, 100)
            snitt_varepris = 45
            ant_varer: int = max(1, round(number=pris / snitt_varepris))
            self.kvitteringer.append(
                Kvittering(
                    ant_varer=ant_varer,
                    pris=pris,
                    k_id=f"{self.h_id}-{tur}",
                ))

def simuler(n_befolkning : int = 100) -> list:
    husholdninger : list[Husholdning] = []
    for n in range(n_befolkning):
        husholdninger.append(Husholdning(h_id= n, definisjon=lag_husholdnings_definisjon()))
        for h in husholdninger:
            h.handletur()
    return husholdninger