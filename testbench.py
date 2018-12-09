# The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


#python testbench.py
#python eval.py clustering.out  E:\Corpora\clustering\processed_clusters\dataset.test.json -f

import model
import clustering
import load_corpora

corpus = load_corpora.load(r"E:\Corpora\clustering\processed_clusters\dataset.test.json",
                           r"E:\Corpora\clustering\tok_ner_clusters\clustering.test.json", set(["eng"]))
clustering_model = model.Model()

#clustering_model.load(r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_es\2_1492035151.291134_100.0.model',
#                      r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_es\example_2017-04-12T215308.030747.ii')

#clustering_model.load(r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_de\2_1499938269.299021_100.0.model',
#                      r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_de\example_2017-07-13T085725.498310.ii')

clustering_model.load(r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_en\4_1491902620.876421_10000.0.model',
                      r'E:\Projects\IndexerLib\ClusteringLib\models\aaai18_best_en\example_2017-04-10T193850.536289.ii')

aggregator = clustering.Aggregator(clustering_model, 8.18067)

for i, d in enumerate(corpus.documents):
    print(i, "/", len(corpus.documents), " | #c= ", len(aggregator.clusters))
    #if i > 500:
    #    break
    aggregator.PutDocument(clustering.Document(d, "???"))


with open("clustering.out", "w") as fo:
  ci = 0
  for c in aggregator.clusters:
    for d in c.ids:
      fo.write(d)
      fo.write("\t")
      fo.write(str(ci))
      fo.write("\n")
    ci += 1
