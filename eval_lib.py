#
# Script for clustering evaluation
# Adapted from Arturs Znotins script
#
import sys
import os
from math import *
import json
from sklearn import metrics
import numpy as np
import time
from datetime import datetime
import logging
from pprint import pprint
from collections import Counter
from sklearn.metrics import precision_recall_fscore_support
import utils

def ScoreSet(true_labels, pred_labels, logging="", get_data=False):
    cooccurrence_matrix, true_label_map, pred_label_map = utils.get_cooccurrence_matrix(true_labels, pred_labels)
    tp, fp, tn, fn = utils.get_tp_fp_tn_fn(cooccurrence_matrix)

    acc = 1. * (tp + tn) / (tp + tn + fp + fn) if tp + tn + fp + fn > 0 else 0
    p = 1. * tp / (tp + fp) if tp + fp > 0 else 0
    r = 1. * tp / (tp + fn) if tp + fn > 0 else 0
    f1 = 2. * p * r / (p + r) if p + r > 0 else 0

    ri = 1. * (tp + tn) / (tp + tn + fp + fn) if tp + tn + fp + fn > 0 else 0

    entropies, purities = [], []
    for cluster in cooccurrence_matrix:
        cluster = cluster / float(cluster.sum())
        # ee = (cluster * [log(max(x, 1e-6), 2) for x in cluster]).sum()
        pp = cluster.max()
        # entropies += [ee]
        purities += [pp]
    counts = np.array([c.sum() for c in cooccurrence_matrix])
    coeffs = counts / float(counts.sum())
    purity = (coeffs * purities).sum()
    # entropy = (coeffs * entropies).sum()

    ari = metrics.adjusted_rand_score(true_labels, pred_labels)
    nmi = metrics.normalized_mutual_info_score(true_labels, pred_labels)
    ami = metrics.adjusted_mutual_info_score(true_labels, pred_labels)
    v_measure = metrics.homogeneity_completeness_v_measure(true_labels, pred_labels)

    pred_cluset = {}
    for v in pred_labels:
        pred_cluset[v] = True

    true_cluset = {}
    for v in true_labels:
        true_cluset[v] = True

    s = "{\n\"logging\" : \"" + logging + "\",\n"
    s += "\"f1\" : %.5f,\n" % f1
    s += "\"p\" : %.5f,\n" % p
    s += "\"r\" : %.5f,\n" % r
    s += "\"a\" : %.5f,\n" % acc
    s += "\"ari\" : %.5f,\n" % ari
    s += "\"size_true\" : %.5f,\n" % len(true_labels)
    s += "\"size_pred\" : %.5f,\n" % len(pred_labels)
    s += "\"num_labels_true\" : %.5f,\n" % len(true_cluset)
    s += "\"num_labels_pred\" : %.5f,\n" % len(pred_cluset)
    s += "\"ri\" : %.5f,\n" % ri
    s += "\"nmi\" : %.5f,\n" % nmi
    s += "\"ami\" : %.5f,\n" % ami
    s += "\"pur\" : %.5f,\n" % purity
    s += "\"hom\" : %.5f,\n" % v_measure[0]
    s += "\"comp\" : %.5f,\n" % v_measure[1]
    s += "\"v\" : %.5f,\n" % v_measure[2]
    s += "\"tp\" : %.5f,\n" % tp
    s += "\"fp\" : %.5f,\n" % fp
    s += "\"tn\" : %.5f,\n" % tn
    s += "\"fn\" : %.5f\n" % fn
    s += "}"

    if get_data:
      return s
    else:
      print (s)