say "future" before a command to activate the virtual assistant

commands:

brightness(number 1-10) changes the screen brightness
volume(number 1-10) changes the master volume
system volume(number 1-10)changes the system(future) volume
open(fileName)(add it to the wakeup.json file in this format "app":"app path" and add a , at them end if necesary)
search(input) searchs the input
youtube(input)searchs the input on youtube
(textfile(the ones in the json file)) (input) add input to your textfile
time tells you the time in hours/min format
weather tells you the weather(needs internet)
close (app name)(closes a file(needs exact executable name))
personality (on/off)(toggles future's personality on/off)
personality mode (mean/normal/nice)(changes the personality mode)
name change (newName) changes futures name
data(opens a file with some data about your pc)
definition/what's/what is/what are/where is/where are/how to/what can(asks google a quastion and says the answer)

libraries needed:

simpleFiles(lets me easly use text files)
vosk(audio to text)
pygame(GUI)
json(get json data)
datetime(date and time)
requests(webscraping)
bs4(webscraping)
pyttsx3(sound)
webbrowser(open websites)
pyaudio(get audio)
screen_brightness_control(change screen brightness)
pycaw(change audio)
paho-mqtt(comunication using mqtt)
pyinstaller(to conver the .py file to exe)
pytorch(AI for personality)
numpy(some calculating)
nltk(parsing some text)

