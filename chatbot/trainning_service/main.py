import json
import pickle
import random
import nltk
import numpy as np
from keras.layers import Dense, Dropout
from keras.models import Sequential
from keras.optimizers import SGD
from nltk.stem import WordNetLemmatizer
import boto3
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

s3 = boto3.client('s3')


def loadS3TrainingData():
    bucket = "chatbot-training-data-demo1"
    response = s3.list_objects_v2(Bucket=bucket)
    files = response.get("Contents")
    trainData = []
    for file in files:
        obj = s3.get_object(Bucket=bucket, Key=file['Key'])
        j = json.loads(obj['Body'].read())
        trainData.extend(j['intents'])
    print(trainData)
    return trainData


def uploadDataToS3():
    bucket = 'chatbotbucket-demo1'

    file_name = "model/chatbot_model.h5"
    response = s3.upload_file("./"+file_name, bucket, file_name)
    print(response)

    file_name = "data/classes.pkl"
    response = s3.upload_file("./"+file_name, bucket, file_name)
    print(response)

    file_name = "data/words.pkl"
    response = s3.upload_file("./"+file_name, bucket, file_name)
    print(response)


def loadLocalData(filePath):
    data_file = open(filePath).read()
    intents = json.loads(data_file)
    return intents


def trainingData(intents):
    lemmatizer = WordNetLemmatizer()
    words = []
    classes = []
    documents = []
    ignore_words = ['?', '!']

    for intent in intents:
        for pattern in intent['patterns']:

            # tokenize each word
            w = nltk.word_tokenize(pattern)
            words.extend(w)
            # add documents in the corpus
            documents.append((w, intent['tag']))

            # add to our classes list
            if intent['tag'] not in classes:
                classes.append(intent['tag'])

    # lemmatize, lower each word and remove duplicates
    words = [lemmatizer.lemmatize(w.lower()) for w in words if w not in ignore_words]
    words = sorted(list(set(words)))
    # sort classes
    classes = sorted(list(set(classes)))
    # documents = combination between patterns and intents
    print(len(documents), "documents")
    # classes = intents
    # words = all words, vocabulary
    print(len(words), "unique lemmatized words", words)

    pickle.dump(words, open('data/words.pkl', 'wb'))
    pickle.dump(classes, open('data/classes.pkl', 'wb'))

    training = []
    output_empty = [0] * len(classes)
    # training set, bag of words for each sentence
    for doc in documents:
        # initialize our bag of words
        bag = []
        # list of tokenized words for the pattern
        pattern_words = doc[0]
        # lemmatize each word - create base word, in attempt to represent related words
        pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
        # create our bag of words array with 1, if word match found in current pattern
        for w in words:
            bag.append(1) if w in pattern_words else bag.append(0)

        # output is a '0' for each tag and '1' for current tag (for each pattern)
        output_row = list(output_empty)
        output_row[classes.index(doc[1])] = 1

        training.append([bag, output_row])

    random.shuffle(training)
    training = np.array(training)

    train_x = list(training[:, 0])
    train_y = list(training[:, 1])
    print("Training data created")

    model = Sequential()
    model.add(Dense(128, input_shape=(len(train_x[0]),), activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(64, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(train_y[0]), activation='softmax'))

    sgd = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
    model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy'])
    hist = model.fit(np.array(train_x), np.array(train_y), epochs=200, batch_size=5, verbose=1)
    model.save('model/chatbot_model.h5', hist)
    model_json = model.to_json()
    with open("model/chatbot_model.json", "w") as json_file:
        json_file.write(model_json)
    print("model created")


data = loadS3TrainingData()
# data = loadLocalData("data/intents.json")["intents"]
trainingData(data)
uploadDataToS3()
