# ⚠️Supercedence Notice

This work has been superseded by https://github.com/Priberam/projected-news-clustering.

# news-clustering

run download_data.sh to download dataset
run run.sh to execute and print scores

Implementation of the paper: Multilingual Clustering of Streaming News, Sebastião Miranda, Artūrs Znotiņš, Shay B. Cohen, Guntis Barzdins, In EMNLP 2018 (http://aclweb.org/anthology/D18-1483)

The original paper, as mentioned above, used proprietary software by Priberam. Unfortunately, we are unable to release this software (because of licensing issues and because it is embedded in a larger C++ system), so we provide a re-implementation in Python that we hope will also be clearer to work with and change. Some parts, such as the feature extraction and svm training code are proprietary or part of proprietary code, so we provide the dataset with the features already extracted and also the pre-trained models.
