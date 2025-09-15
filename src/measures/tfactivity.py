import pandas as pd
import numpy as np
from src.datahandler import GRNHandler
from scipy.sparse import csr_matrix

def prepare_data(num_exp_file: str = "CIT_BLCA_EXP.csv",grn_file:str="grn.json"):
    numerical_expression = pd.read_csv(num_exp_file, index_col=0)
    grn = GRNHandler(grn_file)

    bygene = grn.adjlist.get('bygene',{})
    bytf   = grn.adjlist.get('bytf',{})

    targets_grn = bygene.keys()
    tfs_grn = bytf.keys()

    targets = sorted(numerical_expression.index.intersection(targets_grn))
    tfs = sorted(numerical_expression.index.intersection(tfs_grn))

    targets_exp = numerical_expression.loc[targets]
    tfs_exp = numerical_expression.loc[tfs]

    tg_index = {tg:i for i,tg in enumerate(targets)}
    tf_index = {tf:i for i,tf in enumerate(tfs)}

    return targets, tfs, targets_exp, tfs_exp, tg_index, tf_index, bytf
    
def get_adj_matrix(bytf:dict,tg_index:dict,tf_index:dict):
    rows,cols=[],[]

    for tf, tf_targets in bytf.items():
        tf_targets=tf_targets.get("act")+tf_targets.get("rep")
        tf_i=tf_index.get(tf)
        for tg in tf_targets:
            tg_i=tg_index.get(tg)
            if tg_i is not None:
                rows.append(tg_i)
                cols.append(tf_i)

    data = np.ones(len(rows), dtype=np.float32)  
    adj_matrix = csr_matrix((data, (rows, cols)), shape=(len(tg_index), len(tf_index)), dtype=np.float32)
    
    # in case a target gene appears in act and rep fot tf and vice versa
    adj_matrix.sum_duplicates()
    adj_matrix.data[:] = 1.0 

    return adj_matrix



# # test 
# targets, tfs, targets_exp, tfs_exp, tg_index, tf_index, bytf=prepare_data()
# adj_matrix=get_adj_matrix(bytf,tg_index,tf_index)
# full_matrix = adj_matrix.toarray().astype(int) 
# adj_df = pd.DataFrame(full_matrix, index=targets, columns=tfs).to_csv('adj.csv')
