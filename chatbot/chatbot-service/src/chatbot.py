import json
import pickle
import random
from urllib import response
import boto3
import nltk
import numpy as np
from flask import Flask, jsonify, request
from keras.models import load_model
from nltk.stem import WordNetLemmatizer
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')

lemmatizer: WordNetLemmatizer = WordNetLemmatizer()

nltk.download('punkt')
nltk.download('wordnet')
nltk.download('omw-1.4')


s3 = boto3.client('s3')


def loadDataFromS3():
    bucket = "chatbotbucket-demo1"
    training_bucket = "chatbot-training-data-demo1"

    chat_model = 'model/chatbot_model.h5'
    data_classes = 'data/classes.pkl'
    data_intents = 'data/intents.json'
    data_words = 'data/words.pkl'

    s3.download_file(
        bucket,
        chat_model,
        chat_model
    )
    s3.download_file(
        bucket,
        data_classes,
        data_classes
    )
    s3.download_file(
        training_bucket,
        data_intents,
        data_intents
    )
    s3.download_file(
        bucket,
        data_words,
        data_words
    )

    model = load_model('model/chatbot_model.h5')
    intents = json.loads(open('data/intents.json').read())
    words = pickle.load(open('data/words.pkl', 'rb'))
    classes = pickle.load(open('data/classes.pkl', 'rb'))
    return model, intents, words, classes


def clean_up_sentence(sentence):
    # tokenize the pattern - split words into array
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word - create short form for word
    sentence_words = [lemmatizer.lemmatize(word.lower()) for word in sentence_words]
    return sentence_words


# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence

def bow(sentence, _words, show_details=True):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words - matrix of N words, vocabulary matrix
    bag = [0] * len(_words)
    for s in sentence_words:
        for i, w in enumerate(_words):
            if w == s:
                # assign 1 if current word is in the vocabulary position
                bag[i] = 1
                if show_details:
                    print("found in bag: %s" % w)
    return np.array(bag)


def predict_class(sentence, _model, words, classes):
    # filter out predictions below a threshold
    p = bow(sentence, words, show_details=False)
    res = _model.predict(np.array([p]))[0]
    ERROR_THRESHOLD = 0.25
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({"intent": classes[r[0]], "probability": str(r[1])})
    return return_list


def getResponse(ints, intents_json):
    result = ""
    tag = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result


def chatbot_response(text, model, intents, words, classes):
    ints = predict_class(text, model, words, classes)
    res = getResponse(ints, intents)
    return res


# print(chatbot_response("can you show me the features of passman"))


app = Flask(__name__)


@app.route('/', methods=['POST'])
def update_record():
    model, intents, words, classes = loadDataFromS3()
    data = json.loads(request.data)
    print(data)
    question = data["question"]
    res = chatbot_response(question, model, intents, words, classes)
    return jsonify({"answer": res, "question": question, "link": "google.com"})


app.run(host='0.0.0.0', port=3000)
