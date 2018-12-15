# The 3-Clause BSD License
# For Priberam Clustering Software
# Copyright 2018 by PRIBERAM INFORMÁTICA, S.A. ("PRIBERAM") (www.priberam.com)
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder (PRIBERAM) nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import datetime
import requests
import argparse
import subprocess
import json
import os
import time

bs_s = 0.0
bc_s = 2.35400649578408
be_s = 13.4723120090007

language_converter = {"deu": "de", "eng":  "en", "spa": "es"}
default_module_coverter = {"de": "CDataDE", "en":  "CDataEN", "es": "CDataES"}
default_module_coverter_ii = {}
for k, v in default_module_coverter.items():
    default_module_coverter_ii[v] = k

parser = argparse.ArgumentParser()
parser.add_argument(
    "url", help="the clustering service url where to PUT documents")
parser.add_argument(
    "reset_url", help="the clustering service url to PUT a system reset")
parser.add_argument("eval_script_path",
                    help="path to the clustering evaluation script")
parser.add_argument("corpora_archive", help="path to test corpora")
parser.add_argument(
    "center_thr", help="thr where to center the search", type=float)
parser.add_argument("pin_scale", help="scale of thr search pin", type=float)
parser.add_argument(
    "num_pins", help="num thr search pins (-p*s, c, +p*s)", type=int)
parser.add_argument("binary_iters", help="num binary iters", type=int)
parser.add_argument('languages', metavar='L', nargs='+',
                    help='A language to test')
parser.add_argument(
    "-s", "--silent", help="Disable all prints (except errors)",  action="store_true")
parser.add_argument("-m", "--monolingual",
                    help="Evaluate crosslingual score",  action="store_true")
parser.add_argument("-r", "--reverse_search",
                    help="Reverse search",  action="store_true")
parser.add_argument("-rf", "--forward_search",
                    help="Reverse reverse search",  action="store_true")
parser.add_argument("-c", "--crosslingual",
                    help="Evaluate crosslingual score (pass linking dataset as well)", nargs="+")
parser.add_argument("-g", "--gold_pass",
                    help="Dump gold into the api",  action="store_true")
parser.add_argument("-d", "--debug", help="Debug mode",  action="store_true")
parser.add_argument("-j", "--just_afew",
                    help="Run tests on just a few",  action="store_true")
parser.add_argument("-b", "--binary_search",
                    help="Opt with binary search (ignores pin-search)",  action="store_true")
parser.add_argument("-fo5", "--fo5", help="Use f0.5",  action="store_true")
parser.add_argument("-bg", "--binary_then_grid",
                    help="Run grid search after binary search",  action="store_true")
parser.add_argument("-ns", "--no_sort",
                    help="Dont sort by date.",  action="store_true")
parser.add_argument("-ls", "--long_sleep",
                    help="Do a long_sleep between resets",  action="store_true")
parser.add_argument("-es", "--early_stop",
                    help="Allow early stop",  action="store_true")
parser.add_argument("-uss", "--use_script_stats",
                    help="Use Script stats",  action="store_true")
parser.add_argument("-udt", "--use_default_thr",
                    help="Use default threshold",  action="store_true")
parser.add_argument("-to", "--test_once",
                    help="Test only once (no resets)",  action="store_true")
parser.add_argument("-rn", "--remote_names",
                    help="Use alternate module naming",  action="store_true")
args = parser.parse_args()

if args.remote_names:
    default_module_coverter = {"de": "German",
                               "en":  "English", "es": "Spanish"}
    default_module_coverter_ii = {}
    for k, v in default_module_coverter.items():
        default_module_coverter_ii[v] = k

# They are collected here since some may be changed acording to other options
url = args.url
reset_url = args.reset_url
eval_script_path = args.eval_script_path
corpora_archive = args.corpora_archive
center_thr = args.center_thr
pin_scale = args.pin_scale
num_pins = args.num_pins
reverse_search = args.reverse_search
binary_search = args.binary_search

if(args.binary_then_grid):
    binary_search = True
    print("Will run binary search followed by grid search")

debug_early_break = False
if args.just_afew:
    debug_early_break = True

allowed_languages = set()
for lang in args.languages:
    allowed_languages.add(lang)

with open(corpora_archive, errors="ignore") as data_file:
    corpora_data = json.load(data_file)


def reset_service():
    r = requests.put(reset_url + "/reset")
    if(r.status_code != 200):
        print(r.json())
        exit(-1)
    if args.long_sleep:
        time.sleep(30)
    else:
        time.sleep(10)


def evaluate_routine(mono_cluster_index, mono_to_cross_index, early_stop_iters):
    early_kill = False
    ts = str(time.time())
    cross_dump_name = "cross."+ts+".clu.dump"
    with open(cross_dump_name, "w") as cross_clusters_file:
        eval_batery = []
        for k, v in mono_cluster_index.items():
            cluster_group = k
            clusters = v
            dump_name = cluster_group + "."+ts+".clu.dump"
            with open(dump_name, "w") as clusters_file:
                for h, g in clusters.items():
                    cluster = h
                    documents = g
                    for document in documents:
                        if args.monolingual:
                            print(document, cluster, sep="\t",
                                  file=clusters_file)
                        if args.crosslingual:
                            print(
                                document, mono_to_cross_index[cluster], sep="\t", file=cross_clusters_file)
            if args.monolingual:
                eval_batery.append(
                    (dump_name, default_module_coverter_ii[cluster_group], False))
    if args.crosslingual:
        eval_batery.append((cross_dump_name, "cross", True))

    eval_results = []
    print()
    for eval_item in eval_batery:
        eval_arguments = ["python", eval_script_path,
                          eval_item[0], corpora_archive, "-f"]
        if eval_item[2]:
            eval_arguments.append("-c")
            for k, v in language_converter.items():
                eval_arguments.append(v)
            eval_arguments.append("-l")
            eval_arguments.append(args.crosslingual)
        # if args.debug:
        #  eval_arguments.append("-d")

        proc = subprocess.run(eval_arguments, stdout=subprocess.PIPE)
        out = proc.stdout
        err = None
        if err:
            print("error in eval script: ", err)
            exit(-1)
        try:
            eval_object = json.loads(out.decode('utf-8').rstrip())
        except:
            print("error in eval script. Dumping to debug.log")
            with open("debug.log", "w") as fdebug:
                print(out, file=fdebug)
            exit(0)
        st = eval_object["size_true"]
        sp = eval_object["size_pred"]
        nlt = eval_object["num_labels_true"]
        nlp = eval_object["num_labels_pred"]

        b_ = 0.5
        p_ = eval_object["p"]
        r_ = eval_object["r"]

        try:
            fo5 = (1 + b_**2) * ((p_*r_) / (b_**2 * p_ + r_))
        except:
            fo5 = 0

        if eval_object["f1"] < 0.70 and st > early_stop_iters:
            print("early_kill: ", eval_object["f1"])
            early_kill = True

        print(eval_item[0], "fo5:", fo5, "f1:", eval_object["f1"], "p:",
              eval_object["p"], "r:", eval_object["r"], "nlt:", nlt, "nlp:", nlp, "ni:", st)
        if "linking_score" in eval_object:
            print(eval_item[0], eval_object["linking_score"])

        assert (st == sp)
        eval_results.append((eval_item, eval_object))
    return (eval_results, early_kill)


archive_list = []
for archive_document in corpora_data:
    if archive_document["lang"] not in language_converter or language_converter[archive_document["lang"]] not in allowed_languages:
        continue
    archive_list.append(archive_document)

if not args.no_sort:
    print("sorting input by date")
    archive_list = sorted(archive_list, key=lambda k: datetime.datetime.strptime(
        k["date"], "%Y-%m-%d %H:%M:%S"))
else:
    print("not sorting input")


def run_iteration(threshold=0.0, get_stats=False, force_gold_pass=False, early_stop_iters=2000):
    mono_cluster_index = {}
    #cross_cluster_index = {}
    mono_to_cross_index = {}

    run_results = []

    if args.debug:
        print("num archives: ", len(archive_list))

    doc_i = -1
    for archive_document in archive_list:
        doc_i += 1
        if debug_early_break and doc_i >= 1000:
            break

        if archive_document["lang"] not in language_converter or language_converter[archive_document["lang"]] not in allowed_languages:
            assert(False)

        progress = int((doc_i / (1.0*len(archive_list))) * 100)
        if not args.silent:
            print("thr {0} | progress: {1:.0f}%\r".format(
                threshold, progress), sep=' ', end='', flush=True)

        step = 500
        if debug_early_break:
            step = 100

        early_kill = False
        if (doc_i != 0 and doc_i % step == 0) or (doc_i == len(archive_list) - 1):
            res, early_kill = evaluate_routine(
                mono_cluster_index, mono_to_cross_index, early_stop_iters)
            run_results.append((doc_i, res))

        if args.early_stop and early_kill:
            print("EARLY STOPPING...")
            break

        api_document = {}
        api_document["id"] = archive_document["id"]
        api_document["text"] = {}
        api_document["text"]["title"] = archive_document["title"]
        api_document["text"]["body"] = archive_document["text"]
        api_document["timestamp"] = archive_document["date"]
        api_document["timestamp_format"] = "%Y-%m-%d %H:%M:%S"
        api_document["language"] = language_converter[archive_document["lang"]]
        api_document["group_id"] = default_module_coverter[api_document["language"]]
        api_document["callback_url"] = "0.0.0.0:0000"
        if args.crosslingual or args.gold_pass or force_gold_pass:
            # for crosslingual, test with gold monolingual input
            api_document["forced_label"] = archive_document["cluster"]

        json_data = json.dumps(api_document)

        if args.use_default_thr:
            r = requests.put(url + "/document", data=json_data,
                             params={"async": "false"})
        else:
            r = requests.put(url + "/document", data=json_data,
                             params={"async": "false", "threshold": threshold})
        if(r.status_code != 200):
            print(r.json())
            exit(-1)

        response = r.json()
        try:
            for update in response["updates"]:
                if update["type"] == "mono":
                    group_id = update["group_id"]
                    mono_id = update["cluster_id"]
                    if group_id not in mono_cluster_index:
                        mono_cluster_index[group_id] = {}
                    if mono_id not in mono_cluster_index[group_id]:
                        mono_cluster_index[group_id][mono_id] = set()
                    mono_cluster_index[group_id][mono_id].add(
                        update["document_id"])

                elif update["type"] == "cross":
                    cross_updates = update["updates"]
                    for cupdate in cross_updates:
                        cross_id = cupdate["cross_id"]
                        #cross_cluster_index[cross_id] = set()
                        if "mono_ids" in cupdate:
                            for mono_id in cupdate["mono_ids"]:
                                mono_to_cross_index[mono_id] = cross_id
                                # cross_cluster_index[cross_id].add(mono_id)
                else:
                    raise ValueError("Unknown type: " + update["type"])
        except Exception as e:
            print("exception: "+str(e))
            print("server response:")
            print(response)
            exit(-1)

    if get_stats:
        r = requests.get(url + "/development")
        if(r.status_code != 200):
            print(r.json())
            exit(-1)
        return r.json()

    return run_results


results = []
ts = str(time.time())

best_thr = None
best_score = None
best_f1 = None
run_grid = False

if binary_search:
    # Get stats
    reset_service()

    if not args.use_script_stats:
        stats = run_iteration(0.5, get_stats=True,
                              force_gold_pass=True, early_stop_iters=2000)
        b_start = stats["decision_new_min"]
        b_center = stats["decision_new_avg"]
        b_end = stats["decision_new_max"]
    else:
        b_start = bs_s
        b_center = bc_s
        b_end = be_s

    if args.debug:
        print("binary search iters", args.binary_iters, b_start, b_center, b_end)

    for i in range(args.binary_iters):
        if args.debug:
            print("binary iter", i, b_start, b_center, b_end)

        b_thr_l = ((b_center - b_start) / 2) + b_start
        b_thr_r = ((b_end - b_center) / 2) + b_center
        print("will do l:", b_thr_l, "r:", b_thr_r)

        reset_service()
        result_l = run_iteration(b_thr_l, early_stop_iters=2000)
        f1_l = result_l[-1][1][0][1]["f1"]
        p_l = result_l[-1][1][0][1]["p"]
        r_l = result_l[-1][1][0][1]["r"]

        reset_service()
        result_r = run_iteration(b_thr_r, early_stop_iters=2000)
        f1_r = result_r[-1][1][0][1]["f1"]
        p_r = result_l[-1][1][0][1]["p"]
        r_r = result_l[-1][1][0][1]["r"]

        opt_val_l = f1_l
        opt_val_r = f1_r
        if(args.fo5):
            b_ = 0.5
            opt_val_l = (1 + b_**2) * ((p_l*r_l) / (b_**2 * p_l + r_l))
            opt_val_r = (1 + b_**2) * ((p_r*r_r) / (b_**2 * p_r + r_r))

        if args.debug:
            print("result of l:", b_thr_l, "r:", b_thr_r, "f1_l:", f1_l, "f1_r:", f1_r,
                  "opt_val_l:", opt_val_l, "opt_val_r:", opt_val_r, b_start, b_center, b_end)

        results.append((b_thr_l, result_l))
        results.append((b_thr_r, result_r))

        if opt_val_l > f1_r:
            b_end = b_center
            b_center = b_thr_l

            if not best_score or opt_val_l > best_score:
                best_f1 = f1_l
                best_score = opt_val_l
                best_thr = b_thr_l
        else:
            b_start = b_center
            b_center = b_thr_r

            if not best_score or opt_val_r > best_score:
                best_f1 = f1_r
                best_score = opt_val_r
                best_thr = b_thr_r

        report_fname = "results_binary_"+ts+".out"
        print("best thr:", best_thr, "best score:", best_score)
        with open(report_fname, "w") as fo:
            print("best thr:", best_thr, "best score:", best_score, file=fo)
            print(results, file=fo)
        print("updated report:", report_fname)

    report_fname = "results_binary_"+ts+".out"
    # print(results)
    with open(report_fname, "w") as fo:
        print("thr:", best_thr, "score:", best_score, file=fo)
        print(results, file=fo)
    print("thr:", best_thr, "score:", best_score)
    print("report:", report_fname)

    if(args.binary_then_grid):
        print("Configuring grid search phase...")
        center_thr = best_thr
        run_grid = True
        pin_scale = abs(best_thr) / 4.0

else:
    run_grid = True

if (run_grid):
    thresholds = list(
        reversed([center_thr - (p + 1)*pin_scale for p in range(num_pins)]))
    thresholds += [center_thr + p * pin_scale for p in range(num_pins + 1)]

    if reverse_search:
        thresholds = list(
            reversed([center_thr + p * pin_scale for p in range(num_pins + 1)]))

    if args.forward_search:
        thresholds = list(reversed(thresholds))

    if args.debug:
        print(thresholds)
    elif args.crosslingual:
        print(thresholds)

    for threshold in thresholds:

        if not args.test_once:
            reset_service()
        result = run_iteration(threshold, early_stop_iters=1000)
        f1 = result[-1][1][0][1]["f1"]
        results.append(result)
        if not best_score or f1 > best_score:
            best_score = f1
            best_thr = threshold
        print("best thr:", best_thr, "best score:", best_score)

        report_fname = "results_grid_inter_"+ts+".out"
        print(thresholds)
        print("tmp report to : ", report_fname)
        with open(report_fname, "w") as fo:
            print("best thr:", best_thr, "best score:", best_score, file=fo)
            print(thresholds, file=fo)
            print(results, file=fo)

    report_fname = "results_grid_"+ts+".out"
    print(thresholds)
    # print(results)
    with open(report_fname, "w") as fo:
        print("best thr:", best_thr, "best score:", best_score, file=fo)
        print(thresholds, file=fo)
        print(results, file=fo)

    print("best thr:", best_thr, "best score:", best_score)
    print("report:", report_fname)
