from nltk.sentiment import SentimentAnalyzer
from nltk.sentiment.util import *
import re
import connect_to_mongo

db = connect_to_mongo.db
sid = SentimentAnalyzer()

# intialize training dataset
data_pos = []
data_neg = []


def load_training_data():
    global db, data_pos, data_neg
    data_pos = db.ideas_2013.find({"entities.sentiment.basic": "Bullish"})
    data_neg = db.ideas_2013.find({"entities.sentiment.basic": "Bearish"})
load_training_data()
print("Grabbed data, yo")


def pre_process(data, segment):
    training_data = data[segment].lower()
    training_data = re.sub('((www\.[^\s]+)|(https?://[^\s]+))', 'URL', training_data)
    training_data = re.sub('@[^\s]+', 'AT_USER', training_data)
    training_data = re.sub('[\s]+', ' ', training_data)
    training_data = re.sub(r'#([^\s]+)', r'\1', training_data)
    training_data = training_data.strip('\'"')
    return training_data


def process(cursor):
    data = []
    for document in cursor:
        data.append(pre_process(document, 'body'))
    return data


# tokenizes ideas into seperate words deleting punctuation.
def tokenize(idea):
    feature_vector = []
    words = idea.split()
    for w in words:
        w = w.strip('\'"?./')
        val = re.search(r"^[a-zA-z][a-zA-Z0-9]*$", w)
        if val is None:
            continue
        else:
            feature_vector.append(w.lower())
    return feature_vector


def get_features(vector):
    ideas = []
    processed_idea = process(vector)
    for row in processed_idea:
        features = tokenize(row)
        ideas.append(features)
    return ideas


def concat_features():
    neg_features = get_features(data_neg[:500])
    pos_features = get_features(data_pos[:500])
    full_features = []
    for row in neg_features:
        full_features.append((row, "neg"))
    for row in pos_features:
        full_features.append((row, "pos"))
    return full_features

ideas = concat_features()


# Gets relevant features from ideas
def get_words_in_ideas(ideas):
    all_words = []
    for (words, sentiment) in ideas:
        all_words.extend(words)
    return all_words


# Gets feature list
def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_featuress = wordlist.keys()
    return word_featuress


# noinspection PyTypeChecker
word_features = get_word_features(get_words_in_ideas(ideas))


# Extracts features from feature vector for processing use
def extract_features(idea):
    idea_words = set(idea)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in idea_words)
    return features

# HERE DOWN: Trains classifier and does classification
training_set = nltk.classify.apply_features(extract_features, ideas)
print("Features have been extracted, you may proceed")

classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Training completed")

tweet = 'this below expectation happy'

print(classifier.show_most_informative_features(32))
print(extract_features(tweet.split()))
print(classifier.classify(extract_features(tweet.split())))

