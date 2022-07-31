import json
import random
import pickle
import numpy as np

import nltk
from nltk.stem import WordNetLemmatizer

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Activation, Dropout
from tensorflow.keras.optimizers import SGD
from nltk.corpus import wordnet

lemmatizer = WordNetLemmatizer

with open("intents.json", "r") as file:
    intents = json.load(file)

words = []
classes = []
docs = []

ignoreLetters = ["?", "!", ".", ",", "'"]

for intent in intents["intents"]:
    for pattern in intent["patterns"]:
        wordList = nltk.word_tokenize(pattern)
        words.extend(wordList)
        docs.append((wordList, intent["tag"]))
        if intent["tag"] not in classes:
            classes.append(intent["tag"])
words = [lemmatizer.lemmatize(wordnet.VERB, word) for word in words if word not in ignoreLetters]
words = sorted(set(words))
classes = sorted(set(classes))

pickle.dump(words, open("words.pkl", "wb"))
pickle.dump(classes, open("classes.pkl", "wb"))

training = []
outputEmpty = [0] * len(classes)

for doc in docs:
    bag = []
    wordPatterns = doc[0]
    wordPatterns = [lemmatizer.lemmatize(wordnet.VERB, word.lower()) for word in wordPatterns]
    for word in words:
        bag.append(1) if word in wordPatterns else bag.append(0)
    outputRow = list(outputEmpty)
    outputRow[classes.index(doc[1])] = 1
    training.append([bag, outputRow])
random.shuffle(training)
training = np.array(training)

trainX = list(training[:, 0])
trainY = list(training[:, 1])

model = Sequential()
model.add(Dense(128, input_shape=(len(trainX[0]),), activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(64, activation="relu"))
model.add(Dropout(0.5))
model.add(Dense(len(trainX[0]), activation = "softmax"))

sgd = SGD(lr = 0.01, decay = 1e-6, momentum = 0.9, nesterov = True)
model.compile(loss="categorical_crossentropy", optimizer=sgd, metrics = ["accuracy"])
model.fit(np.array(trainX), np.array(trainY), epochs=20, batch_size = 5, verbose = 1)
model.save(chatbot_model.model)

print("done!")
            
