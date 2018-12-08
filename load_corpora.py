# The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import json
import datetime


class Corpus:
    def __init__(self):
        self.index = {}
        self.documents = []

    def build_index(self):
        self.documents = sorted(self.documents, key=lambda k: datetime.datetime.strptime(
            k["date"], "%Y-%m-%d %H:%M:%S"))
        self.index = {}
        i = -1
        for sorted_document in self.documents:
            rem = []
            for fn, fv in sorted_document["features"].items():
                if not fv:
                    rem.append(fn)
            for fr in rem:
                del(sorted_document["features"][fr])

            i += 1
            self.index[sorted_document["id"]] = i

    def get_document(self, id):
        return self.documents[self.index[id]]


def load(dataset_path, dataset_tok_ner_path, languages):
    corpus_index = {}
    with open(dataset_path, errors="ignore", mode="r") as data_file:
        corpus_data = json.load(data_file)
        for d in corpus_data:
            corpus_index[d["id"]] = d

    with open(dataset_tok_ner_path, errors="ignore", mode="r") as data_file:
        for l in data_file:
            tok_ner_document = json.loads(l)
            corpus_index[tok_ner_document["id"]
                         ]["features"] = tok_ner_document["features"]

    corpus = Corpus()
    corpus.documents = []
    for archive_document in corpus_index.values():
        if archive_document["lang"] not in languages:
            continue
        corpus.documents.append(archive_document)

    corpus.build_index()
    return corpus
