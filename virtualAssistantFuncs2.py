import webbrowser
import datetime
import platform
import os
import subprocess
import requests as rt
import re
#import googlesearch
from bs4 import BeautifulSoup as bs

def pcData():
    data = {"Operating system":platform.architecture()[1]+" "+platform.architecture()[0],
            "Operating system version":platform.platform(),
            "Computer name":platform.node(),
            "User":str(os.getlogin()),
            "Machine":platform.machine(),
            "Computer cores":str(os.cpu_count()),
            "Processor":platform.processor(),
            "Release":platform.release(),
            "Python version":platform.python_version()
            }
    return(data)

def listApps():
    cmd = 'powershell "gps | where {$_.MainWindowTitle } | select Description'
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    lines = ""
    for line in proc.stdout:
        if line.rstrip():
            # only print lines that are not empty
            # decode() is necessary to get rid of the binary string (b')
            # rstrip() to remove `\r\n`
            lines += line.decode().rstrip() + "\n"
    return(lines)

def closeFile(file):
    try:
        os.system("TASKKILL /F /IM %s.exe"%(file))
        print("get absolutly destroyed")
    except Exception as e:
        print(e)

def say(text, engine):
    engine.say(text)
    engine.runAndWait()

def timeNow():
    now = datetime.datetime.now()
    dt = 12
    td = datetime.timedelta(hours = dt)
    hour = now.hour
    if int(hour) >= dt:
        now = now-td
    hour = now.hour
    minute = now.minute
    now = hour, minute
    return(now)

def search(text):
    sy = ("https://www.bing.com/search?q="+text)
    webbrowser.open_new(sy)
    
def search_youtube(text):
    sy = ("https://www.youtube.com/results?search_query="+text)
    webbrowser.open_new(sy)
    
def weather():
    url = ("https://weather.com/weather/today/l/Los+Angeles+CA?canonicalCityId=84c64154109916077c8d3c2352410aaae5f6eeff682000e3a7470e38976128c2")
    html = rt.get(url).text
    soup = bs(html, "lxml")
    weatherType = soup.find("div", "CurrentConditions--primary--2SVPh")
    weather = weatherType.find("div", "CurrentConditions--phraseValue--2Z18W").text
    return(weather)
    #webbrowser.open_new(sy)
    
def combineWords(wordList, delimiter=" "):
    text=""
    for word in wordList:
        text += delimiter +word
    return text

def lookForWord(word, dic):
    for key in dic.keys():
        if word in dic[key]:
            return key
    return word
def numToInt(num):
    numList = ["zero","one","two","three","four","five","six","seven","eight","nine","ten"]
    for i,n in enumerate(numList):
        if num == n:
            return(i)
def removeConjunctions(words):
    conj = ["and", "it", "the", "can", "set", "my", "please"] #"to", "are"
    words = [word for word in words if word not in conj]
    return(words)

def writeFile(pre,root,suf,loc,form):
    with open(loc,form) as file:
        file.write("%s-> %s <-%s \n"%(pre,root,suf))

##def findUrls(keyword, count = 1):
##    domainList = []
##    for domain in googlesearch.search(keyword,
##                                 tld = "com",
##                                 lang = "en",
##                                 num = count,
##                                 stop = count,
##                                 pause = 2.0
##                                 ):
##        domainList.append(domain)
##    return(domainList)

##def getInfoFromUrl(url):
##    res = rt.get(url)
##    html_page = res.content
##    soup = bs(html_page, 'html.parser')
##    text = soup.find_all(text=True)
##    output = ''
##    blacklist = [
##        '[document]',
##        'noscript',
##        'header',
##        'html',
##        'meta',
##        'head', 
##        'input',
##        'script',
##        "style",
##    ]
##
##    for t in text:
##        if t.parent.name not in blacklist:
##            output += '{} '.format(t)
##
##    return(output)

def askGoogle(quastion, clas = "BNeawe s3v9rd AP7Wnd"):
    url = "https://www.google.com/search?q=" + str(quastion.replace(" ", "+"))
    print(url)
    html = rt.get(url).text
    soup = bs(html, "lxml")
    
    answer = soup.find("div", clas)
    subAnswer = answer.find("div", "v9i61e")
    if subAnswer != None:
        answer = subAnswer
    if answer != None:
        answer = answer.text.replace("...", "").replace("  ", " ")
        return(answer)
    return(None)

if __name__ == "__main__":
    #urls = findUrls("defenition of microchip")
    #for url in urls:
    print(askGoogle("defenition of battery"))
    #weather()
    
