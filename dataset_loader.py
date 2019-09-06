import pickle
import json
import os
import datetime


def LoadLinkingDataset(path, allowed_languages=None, allowed_documents=None, limited=True):
    dataset = {}

    dataset["linking"] = {}
    dataset["bags"] = {}
    dataset["ii"] = {}
    dataset["ii_langs"] = {}
    dataset["i_document_data"] = {}
    dataset["documents"] = set()

    ext_list = [".json"]
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if any(fname.endswith(ext) for ext in ext_list):
                complete_fname = dirName + "\\" + fname
                filedata = None
                with open(complete_fname) as file:
                    filedata = file.read()

                linkage_type = "negative"
                if "positive" in complete_fname:
                    linkage_type = "positive"

                if filedata:
                    try:
                        doc_object = json.loads(filedata)

                        langs = []
                        bag_ids = []
                        selected_annotation = {}
                        for k, v in doc_object.items():
                            if k == "meta":
                                continue
                            if "info" not in v:
                                continue
                            lang = v["info"]["lang"]

                            if allowed_languages and lang not in allowed_languages:
                                continue

                            # document bag
                            bag_id = k
                            articles = v["articles"]["results"]
                            allowed_articles = []
                            for article in articles:
                                article_id = article["id"]
                                if allowed_documents and article_id not in allowed_documents:
                                    continue
                                allowed_articles.append(article)

                            if len(allowed_articles) <= 0:
                                continue

                            bag_ids.append(k)
                            langs.append(lang)
                            selected_annotation[k] = (v, allowed_articles)

                        if limited and len(bag_ids) < 2:
                            continue

                        if limited:
                            assert(len(bag_ids) == 2)
                            if langs[0] == langs[1]:
                                continue

                        bag_ids = []
                        for k, v in selected_annotation.items():
                            lang = v[0]["info"]["lang"]
                            bag_event_id = v[0]["info"]["eventUri"]
                            allowed_articles = v[1]

                            assert(len(allowed_articles) > 0)

                            if allowed_languages:
                                assert(lang in allowed_languages)

                            bag_id = k

                            bag_ids.append(bag_id)
                            dataset["bags"][bag_id] = {}
                            dataset["bags"][bag_id]["linked_as"] = linkage_type
                            dataset["bags"][bag_id]["articles"] = set()
                            dataset["bags"][bag_id]["lang"] = lang
                            dataset["bags"][bag_id]["event_id"] = bag_event_id

                            for article in allowed_articles:
                                article_id = article["id"]
                                dataset["ii"][article_id] = bag_id
                                dataset["ii_langs"][article_id] = lang

                                dataset["i_document_data"][article_id] = {"id": article_id,
                                                                          "text": article["body"],
                                                                          "title": article["title"],
                                                                          "event_id": article["eventUri"],
                                                                          "duplicate": article["isDuplicate"],
                                                                          "lang": article["lang"],
                                                                          "bag_id": bag_id,
                                                                          "date": datetime.datetime.strptime(article['date'] + ' ' + article['time'], "%Y-%m-%d %H:%M:%S"),
                                                                          "source": article["source"]["title"]}

                                dataset["bags"][bag_id]["articles"].add(
                                    article_id)
                                dataset["documents"].add(article_id)

                        # Create linking annotation
                        for bag_id_0 in bag_ids:
                            for bag_id_1 in bag_ids:
                                if bag_id_0 == bag_id_1:
                                    continue
                                if bag_id_0 not in dataset["linking"]:
                                    dataset["linking"][bag_id_0] = {}
                                dataset["linking"][bag_id_0][bag_id_1] = linkage_type

                                if bag_id_1 not in dataset["linking"]:
                                    dataset["linking"][bag_id_1] = {}
                                dataset["linking"][bag_id_1][bag_id_0] = linkage_type

                    except Exception as e:
                        #raise e
                        print("Failed reading file", complete_fname, "e:", e)
    return dataset
