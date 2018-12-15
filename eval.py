#The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from eval_lib import ScoreSet
import argparse
import json 
from dataset_loader import LoadLinkingDataset
from collections import OrderedDict

language_converter = { "de" : "deu" , "en" :  "eng", "es" : "spa"}

parser = argparse.ArgumentParser()
parser.add_argument("predfile", help="the file with the predictions")
parser.add_argument("goldfile", help="the file with the gold labels")
parser.add_argument("-f", "--fix_sizes", help="fix gold size to match pred size (used for midway validation)", action="store_true")
parser.add_argument("-c", "--crosslingual", help="Evaluate crosslingual score, args = languages considered", nargs='+')
parser.add_argument("-l", "--eval_linking_dataset", help="Evaluate on linking dataset (arg = path)", nargs='?')
parser.add_argument("-d", "--debug", help="Enable debug prints",  action="store_true")
parser.add_argument("-s", "--symetric_formats", help="Use same format for gold and pred",  action="store_true")
args = parser.parse_args()

fix_sizes = False
if args.fix_sizes:
  fix_sizes = True

crosslingual = False
if args.crosslingual:
  crosslingual = True

debug_prints = False
if args.debug:
  debug_prints = True

file_pred = args.predfile


clusters_pred = {}
clusters_to_docs_pred = {}
with open(file_pred, errors="ignore") as fp:
    for line in fp:
        sl = line.split('\t')
        clusters_pred[sl[0]] = sl[1] 
        if(not sl[1] in clusters_to_docs_pred):
            clusters_to_docs_pred[sl[1]] = []
        clusters_to_docs_pred[sl[1]].append(sl[0])

if(args.eval_linking_dataset):
  allowed_documents = set()
  for k,v in clusters_pred.items():
    allowed_documents.add(k)
  dataset_path = args.eval_linking_dataset
  linking_dataset = LoadLinkingDataset(dataset_path, set(['eng', 'deu', 'spa']), allowed_documents, limited=False)

clusters_gold = {}
clusters_to_docs_gold = {}
if(args.symetric_formats):
    with open(args.goldfile, errors="ignore") as fp:
        for line in fp:
            sl = line.split('\t')
            clusters_gold[sl[0]] = sl[1] 
            if(not sl[1] in clusters_to_docs_gold):
                clusters_to_docs_gold[sl[1]] = []
            clusters_to_docs_gold[sl[1]].append(sl[0])
else:
    with open(args.goldfile, "r", errors="ignore") as fg:
      documents = json.load(fg)
      for document in documents:
        if(fix_sizes):
          if not document["id"] in clusters_pred:
            continue

        clusters_gold[document["id"]] = document["cluster"]
        if(not document["cluster"] in clusters_to_docs_gold):
          clusters_to_docs_gold[document["cluster"]] = []

        clusters_to_docs_gold[document["cluster"]].append(document["id"])

if debug_prints:
    print("loaded files")

if not crosslingual:

  id_to_index = {}
  index = -1
  for k, v in clusters_pred.items():
      index += 1
      id_to_index[k] = index

  if debug_prints:
      print("ii built")
  
  if(len(clusters_gold) != len(clusters_pred)):
      print ("error:", len(clusters_gold), len(clusters_pred))
      for k0,v in clusters_gold.items():
          if k0 not in clusters_pred:
              print(k0)

      for k0,v in clusters_pred.items():
          if k0 not in clusters_gold:
              print(k0)

      assert(False)

  true_labels = [0 for i in range(len(clusters_gold))]
  for k, v in clusters_gold.items():
      true_labels[id_to_index[k]] = v

  pred_labels = [0 for i in range(len(clusters_pred))]
  for k, v in clusters_pred.items():
      pred_labels[id_to_index[k]] = v

  if debug_prints:
      print("running score set...")
      print (true_labels)
      print (pred_labels)
      
  ScoreSet(true_labels, pred_labels, "mono-score")

  if debug_prints:
      print("score set done.")   

else:
  cross_languages = set()
  for language in args.crosslingual:
    cross_languages.add(language_converter[language])

  if debug_prints:
    print(cross_languages)
	
  num_mono = 0
  gold_cross_clusters = []
  gold_cross_clusters_ids = []
  pred_cross_clusters = []
  pred_cross_clusters_ids = []

  # This is a bit legacy, needs to be re-written
  language_to_index = OrderedDict()
  mono_doc_to_cluster_gold = [{} for i in range(len(cross_languages))]
  with open(args.goldfile, "r", errors="ignore") as fg:
    documents = json.load(fg)
    for document in documents:
      if document["lang"] not in cross_languages:
        continue
      if(fix_sizes):
        if not document["id"] in clusters_pred:
          continue

      if document["lang"] not in language_to_index:
        nindex = len(language_to_index)
        language_to_index[document["lang"]] = nindex
      nindex = language_to_index[document["lang"]]
      mono_doc_to_cluster_gold[nindex][document["id"]] = document["cluster"]
    
  for cluster_id, doc_list in clusters_to_docs_gold.items():
      gold_cross_cluster = set()
      for doc_id in doc_list:
        
          i = -1
          for mono_d_t_c in mono_doc_to_cluster_gold:
              i += 1
              if(doc_id in mono_d_t_c):
                  gold_cross_cluster.add(mono_d_t_c[doc_id] + "_" + str(i))
      gold_cross_clusters.append(gold_cross_cluster)
      gold_cross_clusters_ids.append(cluster_id)
     
  if(debug_prints):
    foo = open("gold_cross.out", "w")
  y = -1
  for gc in gold_cross_clusters:
      y += 1
      for mono_id in gc:
        if(debug_prints):
          foo.write(str(gold_cross_clusters_ids[y]) + "\t" + str(mono_id) + "\n")
  if(debug_prints):
    foo.close()


  unique_docs = set()
  for cluster_id, doc_list in clusters_to_docs_pred.items():
      pred_cross_cluster = set()
      for doc_id in doc_list:
        
          i = -1
          for mono_d_t_c in mono_doc_to_cluster_gold:
              i += 1
              if(doc_id in mono_d_t_c):
                  pred_cross_cluster.add(mono_d_t_c[doc_id] + "_" + str(i))
                  assert (doc_id not in unique_docs)
                  unique_docs.add(doc_id)

      pred_cross_clusters.append(pred_cross_cluster)
      pred_cross_clusters_ids.append(cluster_id)

  if(debug_prints):
    foo = open("pred_cross.out", "w")
  y = -1
  for pc in pred_cross_clusters:
      y += 1
      for mono_id in pc:
        if(debug_prints):
          foo.write(str(pred_cross_clusters_ids[y]) + "\t" + str(mono_id) + "\n")
          #print (str(pred_cross_clusters_ids[y]) + "\t" + str(mono_id))
  if(debug_prints):
    foo.close()
    
  id_to_index = {}
  index = -1
  for pred_cluster in pred_cross_clusters:
      for mono_id in pred_cluster:
          index += 1
          id_to_index[mono_id] = index
  if(debug_prints):
    print("i", index)

  if debug_prints:
    u = set()
    for c in pred_cross_clusters:
      for p in c:
        print (p)
        assert (p not in u)
        u.add(p)
            
  # just to check len
  gold_id_to_index = {}
  index = -1
  for gold_cluster in gold_cross_clusters:
      for mono_id in gold_cluster:
          index += 1
          gold_id_to_index[mono_id] = index
    
  if(debug_prints):
    print (len(id_to_index))
  #print (len(id_to_index))
  assert(len(id_to_index) == len(gold_id_to_index))
        
  if(debug_prints):
    print (len(id_to_index))

  label = -1
  pred_labels = [-1 for i in range(len(id_to_index))]
  for pred_cluster in pred_cross_clusters:
      label += 1
      for mono_id in pred_cluster:
          #print(id_to_index[mono_id])

          if (debug_prints):
            with open("out.tmp","w") as outtmp:
              print (mono_id, file=outtmp)
              print (id_to_index, file=outtmp)
              print (pred_labels, file=outtmp)
              print (id_to_index[mono_id], file=outtmp)
              print (len(pred_labels), file=outtmp)

          pred_labels[id_to_index[mono_id]] = label
    
  #pred_labels = []
  #for l in pred_labels_tmp:
  #    if l == -1:
  #        break
  #    pred_labels.append(l)
    
  label = -1
  true_labels = [-1 for i in range(len(id_to_index))]
  for gold_cluster in gold_cross_clusters:
      label += 1
      for mono_id in gold_cluster:
          true_labels[id_to_index[mono_id]] = label
            
  #true_labels = []
  #for l in true_labels_tmp:
  #    if l == -1:
  #        break
  #    true_labels.append(l)
    
  #print (true_labels_tmp)
  #print (pred_labels_tmp)
  if(debug_prints):
    print (true_labels)
    print (pred_labels)
	
  additional_scoring = None
  if(args.eval_linking_dataset):
    #DEBUG
    num_annots=set()
    for bag_i, bag_l in linking_dataset["linking"].items():
      for bag_j in bag_l:
        num_annots.add(bag_i+bag_j)
        num_annots.add(bag_j+bag_i)
        #assert (linking_dataset["bags"][bag_i]["lang"] != linking_dataset["bags"][bag_j]["lang"])
    #print ("num_annots:",len(num_annots) / 2)

    lcount={}
    for document, lang in linking_dataset["ii_langs"].items():
      if lang not in lcount:
        lcount[lang] = 1
      else:
        lcount[lang] += 1
    #print(lcount)

    visited_documents = set()
    predicted_links_map = {}
    visited_pairs = set()
    for cross_cluster_id, document_list in clusters_to_docs_pred.items():
      bag_ids = set()
      for document in document_list:
        if document not in linking_dataset["ii"]:
          assert(False)
          #continue # document got rejected because it belongs to cloud which has not been linked across langs
        bag_id = linking_dataset["ii"][document]
        bag_ids.add(bag_id)
        visited_documents.add(document)
      if(len(bag_ids) <= 0):
        assert(False)

      for bag_id_0 in bag_ids:
        lang_0 = linking_dataset["bags"][bag_id_0]["lang"]
        for bag_id_1 in bag_ids:
          if bag_id_0 == bag_id_1 or bag_id_0+bag_id_1 in visited_pairs:
            continue
          lang_1 = linking_dataset["bags"][bag_id_1]["lang"]
          #if lang_0 == lang_1:  
          #  continue

          # predicted: pairs of bags of different languages
          
          if bag_id_0 not in predicted_links_map:
            predicted_links_map[bag_id_0] = set()
          predicted_links_map[bag_id_0].add(bag_id_1)
          
          if bag_id_1 not in predicted_links_map:
            predicted_links_map[bag_id_1] = set()
          predicted_links_map[bag_id_1].add(bag_id_0)

          visited_pairs.add(bag_id_0+bag_id_1)
          visited_pairs.add(bag_id_1+bag_id_0)

    #print ("Visited documents: ",len(visited_documents))
    #print ("dataset documents: ",len(linking_dataset["ii"]))
    #print("DEBUG", len(visited_pairs) / 2)
    #print("DEBUG", len(predicted_links_map))
    visited_data = set()
    for bag_t, bag_list in predicted_links_map.items():
        for bag_o in bag_list:
          visited_data.add(bag_t+bag_o)
          visited_data.add(bag_o+bag_t)
    #print ("LEN: ", len(visited_data) / 2)

    #import pdb; pdb.set_trace()

    tp = 0
    tn = 0
    fp = 0
    fn = 0
    visited_data = set()
    for bag_id_0, bag_links in linking_dataset["linking"].items():
      lang_0 = linking_dataset["bags"][bag_id_0]["lang"]
      for bag_id_1, gold_linking in bag_links.items():
        if bag_id_0+bag_id_1 in visited_data:
          continue

        lang_1 = linking_dataset["bags"][bag_id_1]["lang"]
        if lang_0 == lang_1:  
          continue # Cannot compare of same language, its a bias because for me those come as gold.

        #if not (bag_id_0 in predicted_links_map):
        #  continue
          #import pdb; pdb.set_trace()

        predicted_link = bag_id_0 in predicted_links_map and bag_id_1 in predicted_links_map[bag_id_0]

        if gold_linking == "positive":
          if predicted_link:
            tp += 1
          else:
            fn += 1
        elif gold_linking == "negative":
          if predicted_link:
            fp += 1
          else:
            tn +=1
        else:
          assert(False)

        visited_data.add(bag_id_0+bag_id_1)
        visited_data.add(bag_id_1+bag_id_0)

   	#print("gold-sweep:", len(visited_data) / 2)

    def Scoring (tp,fp,tn,fn):
      acc = 1. * (tp + tn) / (tp + tn + fp + fn) if tp + tn + fp + fn > 0 else 0
      p = 1. * tp / (tp + fp) if tp + fp > 0 else 0
      r = 1. * tp / (tp + fn) if tp + fn > 0 else 0
      f1 = 2. * p * r / (p + r) if p + r > 0 else 0
      return {
        "p" : p, 
        "r" : r, 
        "f1" : f1,
        "a" : acc,
        "tp" : tp,
		"fp" : fp,
		"tn" : tn,
		"fn" : fn,
		"tot" : tp+fp+tn+fn}

    additional_scoring = Scoring(tp,fp,tn,fn)
    

  eval_object = json.loads(ScoreSet(true_labels, pred_labels, "cross-score", get_data=True))
  if additional_scoring != None:
  	eval_object["linking_score"] = additional_scoring
  print(json.dumps(eval_object))
	