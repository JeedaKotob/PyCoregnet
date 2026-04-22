import pandas as pd
import numpy as np

try:
    import fim
except ImportError as e:
    raise ImportError(
        "Required dependency 'fim' is not installed. Please install it using 'pip install fim' or report this issue on GitHub if the problem persists."
    ) from e


ALGO = fim.fpgrowth


class FrequentItemsets:
    @staticmethod
    def get_coregs(
        data: pd.DataFrame,
        min_gene_support: float,
        min_coreg_support: float,
        max_coreg: int,
    ):

        # Convert as percentage for fim.algo, as they take percentage as a paramter
        min_gene_support = (min_gene_support / 2) * 100
        min_coreg_support = (min_coreg_support / 2) * 100

        # Save columns of trans_reg_bit_data
        tfs = np.array(data.columns)
        # Reset trans_reg_bit_data's columns
        data.columns = list(range(data.shape[1]))

        transactions = [data.columns[row].to_list() for _, row in data.iterrows()]

        tups = ALGO(tracts=transactions, supp=min_gene_support, zmax=1)

        if max_coreg > 1:
            snd = ALGO(
                tracts=transactions,
                supp=min_coreg_support,
                zmin=2,
                zmax=max_coreg,
                target="c",
            )

            if len(tups) == 0 and len(snd) == 0:
                raise RuntimeError(
                    "No frequent itemsets or coregulations found, with the given paramters"
                )

            tups = tups + snd

        try:
            tups, _ = zip(*tups)
        except ValueError:
            raise RuntimeError(
                "No frequent itemsets or coregulations found, with the given paramters2"
            )

        tups = tuple([list(tup) for tup in tups])
        names = tuple([tfs[indices].tolist() for indices in tups])

        return tuple(zip(tups, names))

    @staticmethod
    def findMax(data: pd.DataFrame, min_common_genes, min_coreg, max_coreg):
        min_common_genes = (min_common_genes / len(data)) * 100
        data = list(data)
        fr = ALGO(
            data,
            supp=min_common_genes,
            zmin=min_coreg,
            zmax=max_coreg,
            target="m",
            report="s",
        )
        return pd.DataFrame(fr, columns=["itemsets", "support"])[
            ["support", "itemsets"]
        ]
