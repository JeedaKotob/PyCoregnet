import warnings
from scipy.stats import fisher_exact
from statsmodels.stats.multitest import multipletests
from joblib import Parallel, delayed
import pandas as pd
import numpy as np

from analysis.patterns import FrequentItemsets
import json


def __doFisher(GRN, fr_coreg, lentrans, alternative, adjustMethod, joblib):
    fr_coreg["itemsets"] = fr_coreg["itemsets"].map(tuple)

    coregs = pd.DataFrame()

    coregs["Reg1"] = fr_coreg["itemsets"].map(lambda t: t[0])
    coregs["Reg2"] = fr_coreg["itemsets"].map(lambda t: t[1])
    coregs["Support"] = fr_coreg["support"]
    coregs["nGRN"] = fr_coreg["support"] * lentrans

    adjlist = GRN.get("adjlist", {})

    bygene = adjlist.get("bygene", [])
    bytf = adjlist.get("bytf", [])

    universe = set(bygene.keys())
    fisher_test = []
    p_adjust = []

    def process_row(row):

        reg1 = bytf[row.Reg1]
        reg1 = {
            "acts": set(reg1["act"]) - set(reg1["rep"]),
            "reps": set(reg1["rep"]) - set(reg1["act"]),
        }

        reg2 = bytf[row.Reg2]
        reg2 = {
            "acts": set(reg2["act"]) - set(reg2["rep"]),
            "reps": set(reg2["rep"]) - set(reg2["act"]),
        }

        coregulated_genes = (reg1["acts"] & reg2["acts"]) | (
            reg1["reps"] & reg2["reps"]
        )

        r10only = (reg1["acts"] - reg2["acts"]) | (reg1["reps"] - reg2["reps"])
        r20only = (reg2["acts"] - reg1["acts"]) | (reg2["reps"] - reg1["reps"])

        reste = universe - (reg1["acts"] | reg1["reps"] | reg2["acts"] | reg2["reps"])

        whale = [len(coregulated_genes), len(r10only), len(r20only), len(reste)]

        whale = np.array(whale).reshape(2, 2)

        fisht = fisher_exact(whale, alternative=alternative).pvalue
        pdj = multipletests([fisht], method=adjustMethod)[1][0]

        return fisht, pdj

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=DeprecationWarning)
        results = Parallel(*joblib)(
            delayed(process_row)(row)
            for row in list(coregs.itertuples(index=False, name="Row"))
        )

    fisher_test, p_adjust = zip(*results)

    coregs["fisherTest"] = fisher_test
    coregs["adjustedPvalue"] = p_adjust

    return coregs


def get_coregs(
    GRN: dict,
    max_coreg: int = 2,
    min_coreg: int = 2,
    min_common_genes: int = 10,
    alternative="greater",
    adjustMethod: str = "holm",
    joblib: tuple = (-1, "loky"),
):

    grn = pd.DataFrame.from_dict(GRN["GRN"]).set_index("Target")

    # Check state for bool
    act_state = len(grn["coact"][grn["coact"].fillna("").map(len) > 0])
    rep_state = len(grn["corep"][grn["corep"].fillna("").map(len) > 0])
    grn_state = act_state + rep_state

    if grn_state < 2:
        warnings.warn("No natural co-regulators found in the network")
    else:
        coregsinfo = {
            "max_coreg": max_coreg,
            "min_coreg": min_coreg,
            "min_common_genes": min_common_genes,
            "alternative": alternative,
            "adjustMethod": adjustMethod,
        }

        grn = grn.fillna("")
        grn = grn[["coact", "corep"]].map(
            lambda x: [] if x is pd.NA or x == "" or x is None else x
        )
        trans = grn["coact"] + grn["corep"]

        fr_coreg = FrequentItemsets.findMax(
            trans, min_common_genes, min_coreg, max_coreg
        )

        if not fr_coreg.empty:
            if max_coreg == 2 and min_coreg == 2:
                coregs = __doFisher(
                    GRN, fr_coreg, len(trans), alternative, adjustMethod, joblib
                )
                coregs.sort_values("nGRN", inplace=True, ascending=False)
                coregs.reset_index(drop=True, inplace=True)
                return coregs, coregsinfo
            else:
                coregs = pd.DataFrame(
                    {
                        "CoRegulators": fr_coreg["itemsets"].map(list),
                        "Support": fr_coreg["support"],
                        "nGRN": fr_coreg["support"] * len(trans),
                    }
                )
                coregs.sort_values("nGRN", inplace=True, ascending=False)
                coregs.reset_index(drop=True, inplace=True)
                return coregs, coregsinfo
        else:
            warnings.warn("No natural co-regulators found in the network")


if __name__ == "__main__":
    try:
        with open("./data/grn.json", "r") as f:
            grn = json.load(f)
    except FileNotFoundError:
        print("Error: grn.json not found")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in grn.json")

    coregz = get_coregs(grn)
