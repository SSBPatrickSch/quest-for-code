from typing import Any


from random import random, randint
import pandas as pd


class Kvittering:
    def __init__(self, ant_varer: int, pris: int, id_: str):
        self.ant_varer = ant_varer
        self.pris = pris
        self.id_ = id_


class Husholdning:
    def __init__(
        self,
        ant_pers: int,
        utdanning: bool,
        er_strukturert: bool,
        id_: int,
    ):
        self.ant_pers: int = ant_pers
        self.utdanning: bool = utdanning
        self.er_strukturert: bool = er_strukturert
        self.id_: int = id_
        self.kvitteringer: list[Any] = []

    def __repr__(self) -> str:
        return (
            f"Ant pers: {self.ant_pers}\n"
            f"Utdanning: {self.utdanning}\n"
            f"Strukturert: {self.er_strukturert}\n"
            f"Ant kvitteringer: {len(self.kvitteringer)}\n"
            f"Tot pris: {self.get_tot_pris()} kroner"
        )

    def get_tot_pris(self) -> int:
        return sum(k.pris for k in self.kvitteringer)

    def handletur(self, dag: int) -> None:
        if self.er_strukturert:
            if random() < 0.1:
                ant_varer: int = randint(10, 100)
                pris: int = (
                    randint(50, 150)
                    * ant_varer
                    * max(int(self.ant_pers * 0.8), 1)
                )

                self.kvitteringer.append(
                    Kvittering(
                        ant_varer=ant_varer,
                        pris=pris,
                        id_=f"{self.id_}-{dag}",
                    )
                )

        else:
            if random() < 0.75:
                ant_varer = randint(5, 15)
                pris = (
                    randint(50, 150)
                    * ant_varer
                    * max(int(self.ant_pers * 0.8), 1)
                )

                self.kvitteringer.append(
                    Kvittering(
                        ant_varer=ant_varer,
                        pris=pris,
                        id_=f"{self.id_}-{dag}",
                    )
                )


def lag_husholdninger(n_bef: int = 5000):
    hush = []

    for n in range(n_bef // 2):
        r = random()
        if r < 0.5:
            ant_pers = 1
        elif r < 0.75:
            ant_pers = 2
        elif r < 0.9:
            ant_pers = 3
        else:
            ant_pers = 4

        utdanning = random() >= 0.5
        er_strukturert = random() >= 0.75

        hush.append(
            Husholdning(
                ant_pers=ant_pers,
                utdanning=utdanning,
                er_strukturert=er_strukturert,
                id_=n,
            )
        )

    return hush


def simuler(hush, dager=365):
    for dag in range(dager):
        for h in hush:
            h.handletur(dag)


def bygg_dataframe(hush):
    alle_kvitteringer = {}

    for h in hush:
        for k in h.kvitteringer:
            alle_kvitteringer[k.id_] = [
                k.ant_varer,
                k.pris,
            ]

    return pd.DataFrame(alle_kvitteringer)


def main():
    hush = lag_husholdninger()

    simuler(hush)

    print(hush[10])

    df = bygg_dataframe(hush)

    print(df.head())


if __name__ == "__main__":
    main()