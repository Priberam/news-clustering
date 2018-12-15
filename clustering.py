#The 3-Clause BSD License
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
import datetime


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
            cosine_bof_v[fn] = sparse_dotprod(
                fv0, fv1) / math.sqrt(sparse_dotprod(fv0, fv0) * sparse_dotprod(fv1, fv1))
    return cosine_bof_v

def normalized_gaussian(mean, stddev, x):
  return (math.exp(-((x - mean) * (x - mean)) / (2 * stddev * stddev)))


def timestamp_feature(tsi, tst, gstddev):
  return normalized_gaussian(0, gstddev, (tsi-tst)/(60*60*24.0))

def sim_bof_dc(d0, c1):
    numdays_stddev = 3.0
    bof = cosine_bof(d0.reprs, c1.reprs)
    bof["NEWEST_TS"] = timestamp_feature(
        d0.timestamp.timestamp(), c1.newest_timestamp.timestamp(), numdays_stddev)
    bof["OLDEST_TS"] = timestamp_feature(
        d0.timestamp.timestamp(), c1.oldest_timestamp.timestamp(), numdays_stddev)
    bof["RELEVANCE_TS"] = timestamp_feature(
        d0.timestamp.timestamp(), c1.get_relevance_stamp(), numdays_stddev)
    bof["ZZINVCLUSTER_SIZE"] = 1.0 / float(100 if c1.num_docs > 100 else c1.num_docs)

    return bof

def model_score(bof, model: model.Model):
    return sparse_dotprod(bof, model.weights) - model.bias


class Document:
    def __init__(self, archive_document, group_id):
        self.id = archive_document["id"]
        self.reprs = archive_document["features"]
        self.timestamp = datetime.datetime.strptime(
            archive_document["date"], "%Y-%m-%d %H:%M:%S")
        self.group_id = group_id


class Cluster:
    def __init__(self, document):
        self.ids = set()
        self.num_docs = 0
        self.reprs = {}
        self.sum_timestamp = 0
        self.sumsq_timestamp = 0
        self.newest_timestamp = datetime.datetime.strptime(
            "1000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.oldest_timestamp = datetime.datetime.strptime(
            "3000-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
        self.add_document(document)

    def get_relevance_stamp(self):
        z_score = 0
        mean = self.sum_timestamp / self.num_docs
        try:
          std_dev = math.sqrt((self.sumsq_timestamp / self.num_docs) - (mean*mean))
        except:
          std_dev = 0.0
        return mean + ((z_score * std_dev) * 3600.0) # its in secods since epoch

    def add_document(self, document):
        self.ids.add(document.id)
        self.newest_timestamp = max(self.newest_timestamp, document.timestamp)
        self.oldest_timestamp = min(self.oldest_timestamp, document.timestamp)
        ts_hours =  (document.timestamp.timestamp() / 3600.0)
        self.sum_timestamp += ts_hours
        self.sumsq_timestamp += ts_hours * ts_hours
        self.__add_bof(document.reprs)

    def __add_bof(self, reprs0):
        for fn, fv0 in reprs0.items():
            if fn in self.reprs:
                for f_id_0, f_value_0 in fv0.items():
                    if f_id_0 in self.reprs[fn]:
                        self.reprs[fn][f_id_0] += f_value_0
                    else:
                        self.reprs[fn][f_id_0] = f_value_0
            else:
                self.reprs[fn] = fv0
        self.num_docs += 1


class Aggregator:
    def __init__(self,  model: model.Model, thr, merge_model: model.Model = None):
        self.clusters = []
        self.model = model
        self.thr = thr
        self.merge_model = merge_model

    def PutDocument(self, document):
        best_i = -1
        best_s = 0.0
        i = -1
        bofs = []
        for cluster in self.clusters:
            i += 1

            bof = sim_bof_dc(document, cluster)
            bofs.append(bof)
            score = model_score(bof, self.model)
            if score > best_s and (score > self.thr or self.merge_model):
                best_s = score
                best_i = i

        if best_i != -1 and self.merge_model:
            merge_score = model_score(bofs[best_i], self.merge_model) 
            i#print(merge_score)
            if merge_score <= 0:
                best_i = -1

        if best_i == -1:
            self.clusters.append(Cluster(document))
            best_i = len(self.clusters) - 1
        else:
            self.clusters[best_i].add_document(document)

        return best_i
