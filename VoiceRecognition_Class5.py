
#importing librarys
import os
import random
import time as sleep
import threading
import json
import pyttsx3
import pyaudio
import torch
import datetime
from model import NeuralNet
from nltk_utils import bag_of_words, tokenize
import virtualAssistantFuncs2 as funcs
import screen_brightness_control as pct
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from vosk import Model, KaldiRecognizer
from enum import Enum, auto




class Mode(Enum):
    MONITOR = auto()
    TALKING = auto()
    TEXT = auto()
    MUTE = auto()

class App(threading.Thread):
    def __init__(self, isNameNeeded = False, roomTopic = "MePro/0/room/"):
        super().__init__()
        try:
            fd = open("welcome.txt")
            welcomeSign = fd.read()
            fd.close()
            print(welcomeSign)
        except:
            pass

        #model = Model(r"D:\my files\pyTzur\voice reconizer\virtual asistant\offline\model")
        ##model = Model(r"./model 1.8g")
        model = Model(r"./model")
        self.recognizer = KaldiRecognizer(model, 16000)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        #self.model = model

        #Making the takling engine
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")     #< Get bank of voices
        engine.setProperty("voice", voices[1].id) #< Choose the second voice in the bank
        engine.setProperty("rate", 195)           #< Set the talking speed
        self.engine = engine                      #< Save the engine for later access

        #loading json
        cfgFile = open("./settings.json", "r", encoding="utf-8")
        self.cfg = json.load(cfgFile)
        cfgFile.close()
        
        with open('intents.json', 'r') as json_data:
            self.intents = json.load(json_data)
        self.FILE = "data.pth"
        self.data = torch.load(self.FILE)

        #setting up pyaudio
        audio = pyaudio.PyAudio()
        stream = audio.open(format = pyaudio.paInt16,  #< Samples of 16 bit
                            channels = 1,              #< Mono output
                            rate = 16000,              #< Sampling rate
                            input = True,              #< Use the microphone
                            frames_per_buffer = 819
                            )
        stream.start_stream()
        self.stream = stream                           #< Save the stream for later access
        self.running = False
        self.setMute(True)
        self.mode = Mode.MONITOR  #< "monitor", "wakeup", "mute", "failed", "talking"
        self.answer = ""
        self.isNameNeeded = isNameNeeded

        self.roomTopic = roomTopic
        
    def stop(self):
        self.running = False
        self.setMute(True)

    def setMute(self, val):
        self.mute = val

    def isMute(self):
        return self.mute

    def getMode(self):
        return self.mode

    def getDetectedText(self):
        return self.answer
        
    def run(self):
        self.voiceRecognition()

    def say(self, text):
        self.engine.say(text)
        self.engine.runAndWait()
        self.mode = Mode.TALKING
        #self.mode = Mode.MONITOR

    def chatingFunc(self):
        self.chating = True
        self.begin = sleep.time()
        return(self.chating, self.begin)

    def voiceRecognition(self):
        #program
        self.setMute(False)
        self.running = True
        self.chating = False
        self.personality = False
        self.begin = 0
        self.bot_name = "FUTURE"
        self.perMode = "normal"
        funcs.say("all systems ready", self.engine)    #< Say the welcome message
        while self.running:
            if self.isMute() == False:
                #self.mode = "monitor"
                self.text = self.stream.read(1600)
                if self.recognizer.AcceptWaveform(self.text):
                    self.engine = pyttsx3.init()
                    self.mode = Mode.TEXT
                    answer = self.recognizer.Result()
                    answer = json.loads(answer)
                    answer = answer["text"]
                    answer = str(answer)
                    self.answer = answer

                    self.wakeup = self.cfg["wakeup"]
                    self.commands = self.cfg["commands"]
                    self.spWords = self.cfg["words"]
                    self.apps = self.cfg["apps"]
                    self.files = self.cfg["files"]

                    self.input_size = self.data["input_size"]
                    self.hidden_size = self.data["hidden_size"]
                    self.output_size = self.data["output_size"]
                    self.all_words = self.data['all_words']
                    self.tags = self.data['tags']
                    self.model_state = self.data["model_state"]

                    self.NLModel = NeuralNet(self.input_size, self.hidden_size, self.output_size).to(self.device)
                    self.NLModel.load_state_dict(self.model_state)
                    self.NLModel.eval()

                    self.sentence = tokenize(self.answer)

                    self.X = bag_of_words(self.sentence, self.all_words)
                    self.X = self.X.reshape(1, self.X.shape[0])
                    self.X = torch.from_numpy(self.X).to(self.device)
                    self.output = self.NLModel(self.X)
                    _, self.predicted = torch.max(self.output, dim=1)
                    self.tag = self.tags[self.predicted.item()]
                    self.probs = torch.softmax(self.output, dim=1)
                    self.prob = self.probs[0][self.predicted.item()]

                    self.words = self.answer.split()
                    self.words = funcs.removeConjunctions(self.words)
                    
                    for file in self.files:
                        self.apps[file] = file+".txt"
                    if self.personality == True:
                        if self.answer != "":
                            if self.chating == True:
                                self.end = sleep.time()
                                if self.end-self.begin >= 10:
                                    self.chating = False
                            if self.prob.item() > 0.9:
                                for intent in self.intents['intents']:
                                    if self.tag == intent["tag"]:
                                        if self.tag == "name":
                                            self.words = ""
                                            name = random.choice(intent[self.perMode])
                                            name = name.split()
                                            for self.word in name:
                                                if self.word == "(name)":
                                                    self.word = self.bot_name
                                                elif self.word == "(start)":
                                                    self.word = list(self.bot_name)[0]
                                                elif self.word == "(end)":
                                                    self.word = list(self.bot_name)[len(self.bot_name)-1]
                                                print(self.word)
                                                self.words += self.word + " "
                                            self.say(self.words)
                                            print(f"{self.bot_name}: {self.words}")

                                        else:
                                            r = random.choice(intent[self.perMode])
                                            self.say(r)
                                            print(f"{self.bot_name}: {r}")

                    self.words = self.answer.split()
                    self.words = funcs.removeConjunctions(self.words)

                    if self.answer != "": # check if text is not empty(false detection)
                        print(self.answer)

                    while len(self.words) > 0:
                        ### Start the comand engine after a "WAKEUP" key word
                        if self.chating == False: 
                            self.command = funcs.lookForWord( self.words.pop(0), self.wakeup ) #< Look for the first "wakeup" key word

                        else:
                            self.chating, self.begin = self.chatingFunc()

                        if self.chating == True or self.command == "wakeup" or self.command == self.bot_name:
                            self.mode = "wakeup"
                            if len(self.words) > 0:
                                while len(self.words) > 0:
                                    try:
                                        self.word = funcs.lookForWord(self.words.pop(0), self.spWords)
                                        self.command = funcs.lookForWord(self.word, self.commands)
                                    except Exception as e:
                                        print("error: "+str(e))

                                    try:
                                        if self.command == "open":
                                            while len(self.words) > 0:
                                                self.app = funcs.lookForWord(self.words.pop(0), self.spWords) #< Look for an APPLICATION keyword
                                                if self.app == "apps":
                                                    apps = funcs.listApps()
                                                    with open("recipe.txt", "w") as file:
                                                        data = funcs.listApps()
                                                        file.write(data)
                                                    os.startfile("recipe.txt")
                                                else:
                                                    if self.app in self.apps.keys():
                                                        self.exe = self.apps[self.app]
                                                        os.startfile(self.exe)
                                                        #self.engine.say("opening")
                                                        self.engine.runAndWait()
                                                        #funcs.say("opening "+self.app, self.engine)
                                                        self.say("opening "+self.app)

                                        elif self.command == "close":
                                            while len(self.words) > 0:
                                                self.app = funcs.lookForWord(self.words.pop(0), self.spWords) #< Look for an APPLICATION keyword
                                                try:
                                                    funcs.closeFile(self.app)
                                                    print(self.app)
                                                except Exception as e:
                                                    print(e)
                                                    break
                                                
                                        elif self.command == "personality":
                                            self.command = funcs.lookForWord(self.words.pop(0), self.spWords)
                                            if self.command == "on":
                                                print("on")
                                                self.personality = True
                                                self.say("changing personality to on")
                                            elif self.command == "off" or self.command == "of":
                                                print("off")
                                                self.personality = False
                                                self.say("changing personality to off")
                                                
                                            elif self.command == "mode":
                                                self.mode = funcs.lookForWord(self.words.pop(0), self.spWords)
                                                if self.mode == "nice":
                                                    self.perMode = "nice"
                                                    
                                                elif self.mode == "normal":
                                                    self.perMode = "normal"

                                                elif self.mode == "mean":
                                                    self.perMode = "mean"
                                                self.say("changing personality mode to "+self.perMode)

                                        elif self.command == "name":
                                            self.name = funcs.lookForWord(self.words.pop(0), self.spWords)
##                                            if self.name == "off" or self.name == "of":
##                                                self.isNameNeeded = False
##                                            elif self.name == "on":
##                                                self.isNameNeeded = True
                                            if self.name == "change":
                                                self.name = funcs.lookForWord(self.words.pop(0), self.spWords)
                                                self.say("confirm change name to "+self.name+"?")
                                                waiting = True
                                                while waiting:
                                                    self.text = self.stream.read(1600)
                                                    if self.recognizer.AcceptWaveform(self.text):
                                                        answer = self.recognizer.Result()
                                                        answer = json.loads(answer)
                                                        answer = answer["text"]
                                                        answer = str(answer)
                                                        self.answer = answer
                                                        waiting = False
                                                if "yes" in self.answer:
                                                    self.bot_name = self.name
                                                    self.say("name changed to "+self.name)
                                                else:
                                                    self.say("process canceled")
                                                    
                                                

                                        elif self.command == "data":
                                            apps = funcs.listApps()
                                            with open("recipe.txt", "w") as file:
                                                data = funcs.pcData()
                                                for d in data:
                                                    line = d+": "+data[d]+"\n"
                                                    print(line)
                                                    file.write(line)
                                            os.startfile("recipe.txt")

                                        elif self.command == "search":
                                            self.text = funcs.combineWords(self.words)
                                            funcs.search(self.text)
                                            self.say("searching " + self.text)
    
                                        elif self.command == "youtube":
                                            self.text = funcs.combineWords(self.words)
                                            funcs.search_youtube(self.text)
                                            self.say("searching on youtube " + self.text)

                                        elif(self.command == "fact"
                                             or self.command == "definition"
                                             or self.command == "what's"
                                             or self.command == "what" and self.words[0] == "is"
                                             or self.command == "what" and self.words[0] == "are"
                                             or self.command == "where" and self.words[0] == "is"
                                             or self.command == "where" and self.words[0] == "are"
                                             or self.command == "how" and self.words[0] == "to"
                                             or self.command == "what" and self.words[0] == "can"):
                                            quastion = self.command + funcs.combineWords(self.words)
                                            self.engine.setProperty("rate", 160)
                                            self.say(funcs.askGoogle(str(quastion)))
                                            self.engine.setProperty("rate", 195)
                                            self.words = []

                                        elif self.command == "time":
                                            timeNow = funcs.timeNow()
                                            self.say(str(timeNow))
                                            self.mode = Mode.TALKING
                                            
                                        elif self.command == "weather":
                                            weather = funcs.weather()
                                            self.say("it is"+weather)
                                            
    ##                                    elif self.command == "download":
    ##                                        self.command = funcs.lookForWord( self.words.pop(0), self.wakeup )
    ##                                        if self.command == "video":
    ##                                            download(input("url: "))
                                                
                                        elif self.command == "system":
                                            self.command = funcs.lookForWord( self.words.pop(0), self.commands)
                                            if self.command == "volume":
                                                try:
                                                    self.vol = self.words.pop(0)
                                                    if self.vol == "to":
                                                        self.vol = self.words.pop(0)
                                                    self.vol = funcs.numToInt(self.vol)
                                                    self.engine.setProperty('volume',self.vol/10)
                                                    self.say("changing system volume to "+str(self.vol))
                                                except:
                                                    print("problem ocured converting vol to int")
                                                    
                                        elif self.command == "volume":
                                            try:
                                                self.vol = self.words.pop(0)
                                                if self.vol == "to":
                                                    self.vol = self.words.pop(0)
                                                self.vol = funcs.numToInt(self.vol)
                                                sessions = AudioUtilities.GetAllSessions()
                                                for session in sessions:
                                                    self.volume = session._ctl.QueryInterface(ISimpleAudioVolume)
                                                    self.volume.SetMasterVolume(self.vol/10, None)
                                                self.say("changing volume to "+str(self.vol))
                                            except:
                                                print("problem ocured converting vol to int")
                                                
                                        elif self.command == "brightness":
                                            try:
                                                self.brt = self.words.pop(0)
                                                if self.brt == "to":
                                                    self.brt = self.words.pop(0)
                                                self.brt = funcs.numToInt(self.brt)
                                                pct.set_brightness(self.brt*10)
                                                self.say("changing brightness to "+str(self.brt))


                                            except:
                                                print("problem ocured converting brightness to int")
                                        elif self.command == "recipes":
                                            self.text = funcs.combineWords(self.words)
                                            searchRecipes.Search(self.text)
        ##                                elif self.command == "update":
        ##                                    updateRecipes.Update()
                                        else:
                                            for self.file in self.files:
                                                if str(self.file) in self.answer:
                                                    while len(self.words) > 0:
                                                        if self.command == self.file:
                                                            self.text = funcs.combineWords(self.words)
                                                            funcs.writeFile(funcs.timeNow(),self.text,"future",self.file+".txt","a")
                                                            self.say("adding %s to your %s "%(self.text, self.file))
                                                        self.command = funcs.lookForWord(self.words.pop(0), self.wakeup)
                                    except Exception as e:
                                        print(str(e))
            else:
                self.mode = Mode.MUTE
                sleep.sleep(0.5)

if __name__ == "__main__":
    app = App()
    app.run()
    #app.start()
#    t = threading.Thread(target=app.run)
#    t.start()
