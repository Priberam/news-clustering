#
# Script utils for clustering evaluation
# Adapted from Arturs Znotins script
#

from scipy.misc import comb
import numpy as np

# JavaScript like dictionary: d.key <=> d[key]
# http://stackoverflow.com/a/14620633
class Dict(dict):
    def __init__(self, *args, **kwargs):
        super(Dict, self).__init__(*args, **kwargs)
        self.__dict__ = self

    def __getattribute__(self, key):
        try:
            return super(Dict, self).__getattribute__(key)
        except:
            return

    def __delattr__(self, name):
        if name in self:
            del self[name]


def myComb(a,b):
    return comb(a,b,exact=True)


vComb = np.vectorize(myComb)


def get_tp_fp_tn_fn(cooccurrence_matrix):
    tp_plus_fp = vComb(cooccurrence_matrix.sum(0, dtype=int),2).sum()
    tp_plus_fn = vComb(cooccurrence_matrix.sum(1, dtype=int),2).sum()
    tp = vComb(cooccurrence_matrix.astype(int), 2).sum()
    fp = tp_plus_fp - tp
    fn = tp_plus_fn - tp
    tn = comb(cooccurrence_matrix.sum(), 2) - tp - fp - fn

    return [tp, fp, tn, fn]


def get_cooccurrence_matrix(true_labels, pred_labels):
    assert len(true_labels) == len(pred_labels)
    true_label_map = {}
    i = 0
    for l in true_labels:
        if not l in true_label_map:
            true_label_map[l] = i
            i += 1
    hyp_label_map = {}
    i = 0
    for l in pred_labels:
        if not l in hyp_label_map:
            hyp_label_map[l] = i
            i += 1
    m = [[0 for i in range(len(hyp_label_map))] for j in range(len(true_label_map))]
    for i in range(len(true_labels)):
        m[true_label_map[true_labels[i]]][hyp_label_map[pred_labels[i]]] += 1
    return (np.array(m), true_label_map, hyp_label_map)


def sum_sparse(a, b, amult=1, bmult=1):
    r = {}
    for x in a:
        r[x[0]] = amult * x[1]
    for x in b:
        r[x[0]] = bmult * x[1] + (r[x[0]] if x[0] in r else 0)
    res = []
    for k, v in r.items():
        res.append((k, v))
    return res


def trim_sparse(a, topn=100):
    return sorted(a, key=lambda x: x[1], reverse=True)[:topn]