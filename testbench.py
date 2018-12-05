# The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import model
import clustering
import dataset_loader

corpus = dataset_loader.load(r"E:\Corpora\clustering\processed_clusters\dataset.dev.json", 
                             r"E:\Corpora\clustering\tok_ner_clusters\clustering.dev.json", set(["eng"]))
clustering_model = model.Model()
clustering_model.load(r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_es\2_1492035151.291134_100.0.model', 
                      r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_es\example_2017-04-12T215308.030747.ii')
aggregator = clustering.Aggregator(clustering_model, 8.18067)


for i, d in enumerate(corpus.documents):
  print(i,"/",len(corpus.documents), " | #c= ", len(aggregator.clusters))
  aggregator.PutDocument(clustering.Document(d["features"], "???"))