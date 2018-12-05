# The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import math
import model
import pdb

def sparse_dotprod(fv0, fv1):
  dotprod = 0

  for f_id_0, f_value_0 in fv0.items():
    if f_id_0 in fv1:
      f_value_1 = fv1[f_id_0]
      dotprod += f_value_0 * f_value_1

  return dotprod

def cosine_bof(d0, d1):
  cosine_bof_v = {}
  for fn, fv0 in d0.items():
    if fn in d1:
      fv1 = d1[fn]
      cosine_bof_v[fn] = sparse_dotprod(fv0, fv1) / math.sqrt(sparse_dotprod(fv0, fv0) * sparse_dotprod(fv1, fv1))
  return cosine_bof_v

def cosine_sim(d0, d1, model: model.Model):
  bof = cosine_bof(d0, d1)
  return sparse_dotprod(bof, model.weights) - model.bias

class Document:
  def __init__(self, reprs, group_id):
    self.reprs = reprs
    self.group_id = group_id

class Cluster:
  def __init__(self, reprs):
    self.reprs = reprs
    self.num_docs = 1

  def add_bof(self, reprs0):
    for fn, fv0 in reprs0.items():
      if fn in self.reprs:
        for f_id_0, f_value_0 in fv0.items():
          if f_id_0 in self.reprs[fn]:
            self.reprs[fn][f_id_0] += f_value_0
          else:
            self.reprs[fn][f_id_0] = f_value_0
    self.num_docs += 1

class Aggregator:
  def __init__(self,  model: model.Model, thr):
    self.clusters = []
    self.model = model
    self.thr = thr
    
  def PutDocument(self, document):
    best_i = -1
    best_s = 0.0
    i = -1
    for cluster in self.clusters:
      i += 1
      score = cosine_sim(document.reprs, cluster.reprs, self.model)
      if score > best_s and score > self.thr:
        best_s = score
        best_i = i
    
    if best_i == -1:
      self.clusters.append(Cluster(document.reprs))
      best_i = len(self.clusters) - 1
    else:
      self.clusters[best_i].add_bof(document.reprs)
    
    return best_i