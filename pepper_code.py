from __future__ import print_function
import json
import os
import base64
import requests
from os.path import join, dirname
from watson_developer_cloud import SpeechToTextV1
from watson_developer_cloud.websocket import RecognizeCallback
import re
from ftplib import FTP
from pydub import AudioSegment
import time
from naoqi import ALBroker
from naoqi import ALProxy
from threading import Thread
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import qi
import sys
import argparse
import watson_developer_cloud
import datetime
from PIL import Image, ImageDraw, ImageFont
import inflect
import calendar
import random
import urllib2
from uber_rides.session import Session
from uber_rides.client import UberRidesClient

ip = "155.245.22.39"
port = 9559

#--------> Global Variables <--------
p = inflect.engine()
file_number = 1
Recording = True
Conversation = False
text = ''
elapsed_silence_time = 0
sounds_level = 4000
chat_context = {}
Wait = False
Face_Detected = False
chatbot_memory = ""
Display_Image = False
Tablet_Wait = False
Output_global = ""
Correct_Input = False
New_question = ""
Face = ""
show_acom = False
run_program = True
entertainment_value = False
Tickle = False
start = []
end = []
end_location = ""
New_question_input = ""

#--------> Initialize qi framework <-------------
connection_url = "tcp://" + ip + ":" + str(port)
app = qi.Application(["ReactToTouch", "--qi-url=" + connection_url])

# ----------> Connect to Watson Assistant <-------------
assistant = watson_developer_cloud.AssistantV1(
    username='d7e60c74-5ca1-41b2-af0b-d32a0f9f2dea',
    password='ppnuzCC3WUMS',
    version='2018-07-10'
)

# ----------> Connect to Watson Speech to Text <-------------
speech_to_text = SpeechToTextV1(
    username='6fea7152-9300-4cb7-acff-101f15fc136e',
    password='j6nGHCboVvKi',
    url='https://stream.watsonplatform.net/speech-to-text/api')


# ----------> Connect to robot <----------
tts = ALProxy("ALTextToSpeech", ip, port)
mic = ALProxy("ALAudioDevice", ip, port)
record = ALProxy("ALAudioRecorder", ip, port)
aup = ALProxy("ALAudioPlayer", ip, port)
tts = ALProxy("ALTextToSpeech", ip, port)
animated_speech = ALProxy("ALAnimatedSpeech", ip, port)
speech = ALProxy("ALTextToSpeech", ip, port)
memory = ALProxy("ALMemory", ip, port)
speech_rec = ALProxy("ALSpeechRecognition", ip, port)
ALFrameManager = ALProxy("ALFrameManager", ip, port)
managerProxy = ALProxy("ALBehaviorManager", ip, port)
tablet = ALProxy("ALTabletService", ip, port)
motionProxy = ALProxy("ALMotion", ip, port)
postureProxy = ALProxy("ALRobotPosture", ip, port)
touch = ALProxy("ALTouch", ip ,port)
faceProxy = ALProxy("ALFaceDetection", ip, port)
managerProxy = ALProxy("ALBehaviorManager", ip, port)

speech_rec.setAudioExpression(False)
speech_rec.setVisualExpression(True)

#--------> A simple class to react to face detection events <---------
class HumanGreeter(object):
    global Face
    def __init__(self, app):
        """
        Initialisation of qi framework and event detection.
        """
        app.start()
        session = app.session
        self.memory = session.service("ALMemory")
        self.subscriber = self.memory.subscriber("FaceDetected")
        self.subscriber.signal.connect(self.on_human_tracked)
        self.face_detection = session.service("ALFaceDetection")
        self.face_detection.subscribe("HumanGreeter")
        self.got_face = False

    def on_human_tracked(self, value):
        global Face
        if not self.got_face:
            self.got_face = True
            faceInfoArray = value[1]
            for j in range( len(faceInfoArray)-1 ):
                faceInfo = faceInfoArray[j]
                faceShapeInfo = faceInfo[0]
                faceExtraInfo = faceInfo[1]
                Face = str(faceExtraInfo[2])
            app.stop()

    def run(self):
        while self.got_face == False:
            time.sleep(1)

#--------------> Learn faces <-----------------
def learn_face():
    #faceProxy.clearDatabase()
    faceProxy.learnFace('Master')
    print(faceProxy.getLearnedFacesList())
    #http://doc.aldebaran.com/2-4/naoqi/peopleperception/alfacedetection.html
            
#--------> Get Audio Levels <---------
def Audio_Level():
    global sounds_level
    mic.enableEnergyComputation()
    time_start = time.time()
    elapsed_time = 0
    print("Measuring noise levels...")
    while(elapsed_time < 10):
        elapsed_time = time.time() - time_start
        energy = mic.getFrontMicEnergy()
        if (energy > sounds_level):
            sounds_level = energy
    sounds_level = sounds_level + 200
    print(sounds_level)

#--------------> Create Image <---------------
def image(Text_1):
    img = Image.new('RGB', (1280, 800), color = (0, 210, 252))
    fnt = ImageFont.truetype("arial.ttf", 40)
    d = ImageDraw.Draw(img)
    d.text((80,80), Text_1, font=fnt, fill=(0, 0, 0))
    img.save('new_question.jpg')

#-----------> Get touch data for tablet <-----------
def touch_tablet(dif):
    global app
    global tablet_time
    global Correct_Input
    global text
    global New_question
    global chatbot_memory
    global entertainment_value
    global Tickle
    global Display_Image
    global Tablet_Wait
    global New_question_input
    app.start()
    session = app.session
    tabletService = session.service("ALTabletService")
    signalID = 0
    Out = ""
    
    def menu(x, y):
        global text
        global New_question
        global chatbot_memory
        global entertainment_value
        global New_question_input
        #Top row
        if 0 < x < 490 and 0 < y < 210:
            speech.stopAll()
            Out = Chat_Bot("Accommodation")
            chatbot_memory = "Accommodation "
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('Accommodation', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 490 < x < 920 and 0 < y < 210:
            speech.stopAll()
            Out = Chat_Bot("Student Loan")
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('Student_Loan', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 920 < x < 1280 and 0 < y < 210:
            speech.stopAll()
            Out = Chat_Bot("Courses")
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('Courses', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        #Second row   
        if 0 < x < 490 and 210 < y < 410:
            speech.stopAll()
            entertainment_value = True
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 490 < x < 920 and 210 < y < 410:
            speech.stopAll()
            Out = Chat_Bot("Department")
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('CSEE_department', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 920 < x < 1280 and 210 < y < 410:
            speech.stopAll()
            Out = Chat_Bot("Book Taxi")
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('Book_Taxi', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        #Third row
        if 0 < x < 490 and 410 < y < 610:
            speech.stopAll()
            Out = Chat_Bot("Pepper Tell me about yourself")
            Tablet_Display(Out)
            speech.say(Out)
            #create_example('Pepper_info', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 490 < x < 920 and 410 < y < 610:
            speech.stopAll()
            Out = Chat_Bot("Data and Time")
            now = datetime.datetime.now()
            Out = Out+" "+p.number_to_words(now.hour)+" "+p.number_to_words(now.minute)+" "+p.number_to_words(now.day)+" "+calendar.month_name[now.month]+" "+p.number_to_words(now.year)
            #create_example('DateAndTime', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 920 < x < 1280 and 410 < y < 610:
            speech.stopAll()
            Out = Chat_Bot("Goodbye")
            #create_example('Goodbye', text)
            Conversation = False
            record.stopMicrophonesRecording()
            tablet.resetTablet()
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        #Bottom Row 
        if 0 < x < 490 and 610 < y < 800:
            speech.stopAll()
            if(New_question_input != ""):
                Out = Chat_Bot(New_question_input)
                create_example('question1', text)
                Tablet_Display(Out)
                speech.say(Out)
                tabletService.onTouchDown.disconnect(signalID)
                app.stop()
            else:
                speech.say("No other question available")
            
        if 490 < x < 920 and 610 < y < 800:
            speech.stopAll()
            speech.say("OK I will remember that question and find out the answer later")
            tablet.resetTablet()
            New_question = text
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 920 < x < 1280 and 610 < y < 800:
            speech.stopAll()
            Out = Chat_Bot("Shut Down")
            #create_example('Shut_Down', text)
            run_program = False
            Conversation = False
            record.stopMicrophonesRecording()
            tablet.resetTablet()
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()

    def student_acom(x, y):
        global text
        if 0 < x < 426 and 0 < y < 400:
            speech.stopAll()
            Out = Chat_Bot("Copse")
            #create_synonym('accommodation', 'Copse', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 426 < x < 853 and 0 < y < 400:
            speech.stopAll()
            Out = Chat_Bot("Houses")
            #create_synonym('accommodation', 'Houses', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 853 < x < 1280 and 0 < y < 400:
            speech.stopAll()
            Out = Chat_Bot("Meadows")
            #create_synonym('accommodation', 'Meadows', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 0 < x < 426 and 400 < y < 800:
            speech.stopAll()
            Out = Chat_Bot("Quays")
            #create_synonym('accommodation', 'Quays', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 426 < x < 853 and 400 < y < 800:
            speech.stopAll()
            Out = Chat_Bot("South Courts")
            #create_synonym('accommodation', 'South Courts', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 853 < x < 1280 and 400 < y < 800:
            speech.stopAll()
            Out = Chat_Bot("Towers")
            #create_synonym('accommodation', 'Towers', text)
            Tablet_Display(Out)
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
            
    def anywhere(x, y):
        global Tablet_Wait
        global Display_Image
        global Correct_Input
        if (Correct_Input == True):
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        elif 0 < x < 1280 and 0 < y < 800:
            Tablet_Wait = True
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        

    def tickle(x, y):
        global Tickle
        def tickle_1():
            managerProxy.startBehavior(".lastUploadedChoregrapheBehavior/animations/tickle_1")
        def tickle_2():
            managerProxy.startBehavior(".lastUploadedChoregrapheBehavior/animations/tickle_2")
        if (Tickle == False):
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        elif 0 < x < 1280 and 0 < y < 800:
            random.choice([tickle_1,tickle_2])()

    def entertainment(x, y):
        global Tablet_Wait
        global Correct_Input
        global Tickle
        if 0 < x < 640 and 0 < y < 400:
            speech.stopAll()
            Out = Chat_Bot("Tickle Me")
            #create_example('Tickle_Me', text)
            Tickle = True
            speech.say(Out)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
        if 0 < x < 640 and 400 < y < 800:
            speech.stopAll()
            #create_example('Weather', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
            speech.say(weather())
        if 640 < x < 1280 and 0 < y < 400:
            speech.stopAll()
            #create_example('News', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
            speech.say(news())
        if 640 < x < 1280 and 400 < y < 800:
            speech.stopAll()
            #create_example('Movies', text)
            tabletService.onTouchDown.disconnect(signalID)
            app.stop()
            speech.say(Movie())

    # attach the callback function to onJSEvent signal
    if (dif == "Menu"):
        signalID = tabletService.onTouchDown.connect(menu)
        app.run()
    if (dif == "acom"):
        signalID = tabletService.onTouchDown.connect(student_acom)
        app.run()
    if (dif == "tickle"):
        signalID = tabletService.onTouchDown.connect(tickle)
        app.run()
    if (dif == "Entertainment"):
        signalID = tabletService.onTouchDown.connect(entertainment)
        app.run()
    if (Correct_Input == False and dif == "Anywhere"):
        signalID = tabletService.onTouchDown.connect(anywhere)
        app.run()

#---------> Display Something on Tablet <-----------
def Tablet_Display(chat_out):
    URL = ""
    department = "https://www.essex.ac.uk/departments/computer-science-and-electronic-engineering"
    student_loan = "https://online.essex.ac.uk/student-finance/student-loans/"
    pepper = "https://www.softbankrobotics.com/emea/en/robots/pepper"
    courses = "https://www.essex.ac.uk/course-search?collection=uoe-courses-meta&f.Department%7CDepartment=Computer+Science+and+Electronic+Engineering+(School+of)&f.Location%7CcourseLocationCampus=Colchester+Campus"
    accommodation_home = "https://www1.essex.ac.uk/accommodation/default.aspx"
    accommodation = "https://www1.essex.ac.uk/accommodation/residences/default.aspx"
    Copse = "https://www1.essex.ac.uk/accommodation/residences/copse/Default.aspx"
    Houses = "https://www1.essex.ac.uk/accommodation/residences/houses/default.aspx"
    Meadows = "https://www1.essex.ac.uk/accommodation/residences/meadows/default.aspx"
    Quays = "https://www1.essex.ac.uk/accommodation/residences/quays/default.aspx"
    South_Courts = "https://www1.essex.ac.uk/accommodation/residences/south_courts/default.aspx"
    Towers = "https://www1.essex.ac.uk/accommodation/residences/towers/default.aspx"
    
    text = chat_out[0:10]
    #Questions
    if (text == "I am Peppe"):
        URL = pepper
    if (text == "The univer"):
        URL = accommodation_home
    if (text == "If you loo"):
        URL = student_loan
    if (text == "Our resear"):
        URL = department
    if (text == "We have 24"):
        URL = courses
    if(text == "There are "):
        URL = accommodation

    #Accommodations
    if (text == "The Copse "):
        URL = Copse
    if (text == "If you enj"):
        URL = Houses
    if (text == "The Meadow"):
        URL = Meadows
    if (text == "Close to c"):
        URL = Quays
    if (text == "South Cour"):
        URL = South_Courts
    if (text == "A real soc"):
        URL = Towers

    if (text == "I have a r"):
        Entertainment()
    #No URL reset tablet
    elif (URL == ""):
        tablet.hideImage()
        #tablet.resetTablet()
        #tablet.hideWebview()
    elif tablet.loadUrl(URL):
        tablet.showWebview()

#----------> Watson Assistant Functions <----------
def create_intent(intent_name, intent_examples):
    response = assistant.create_intent(
        workspace_id = '7832297f-b856-40cb-a498-c2017396c0a0',
        intent = intent_name,
        examples = intent_examples
    )

def create_example(intent_name, example):
    response = assistant.create_example(
        workspace_id = '7832297f-b856-40cb-a498-c2017396c0a0',
        intent = intent_name,
        text = example
    )

def create_dialog_node(condition, response):
    response = assistant.create_dialog_node(
        workspace_id = '7832297f-b856-40cb-a498-c2017396c0a0',
        dialog_node = condition,
        conditions = '#'+condition,
        output = {
            'text': response
        },
        title = condition
    )

def create_synonym(ent, val, syn):
    response = assistant.create_synonym(
        workspace_id = '7832297f-b856-40cb-a498-c2017396c0a0',
        entity = ent,
        value = val,
        synonym = syn
    )

#----------> Recording <-------------
def Record():
    Record = True
    Lissen = True
    Quiet = False
    num = 0.5
    end_record_time = time.time()
    stream_time = time.time()
    while(Lissen == True):
        energy = mic.getFrontMicEnergy()
        elapsed_record_time = time.time() - end_record_time
        elapsed_stream_time = time.time() - stream_time
        if (energy < sounds_level): #mic energy levels
            Quiet = True
        if (energy > sounds_level):
            Quiet = False
            end_record_time = time.time()
            num = 0.5
        if (Quiet == True and elapsed_record_time >= num): #every half a second, add half a second to variable num
            num = num+0.5
        if (num == 2.0 and file_number != 1): #if quiet for two seconds then stop recording. 
            Lissen = False
            Record = False
        if (Quiet == True and elapsed_stream_time >= 2):
            Lissen = False
    return(Record)

#--------> Move Audio File <-----------
def Move_File(file_number):
    os.system('"C:\Program Files (x86)\PuTTY\pscp" -pw Be9utiful nao@155.245.22.39:/home/nao/record'+str(file_number)+'.wav E:\Pepper_Code_Final')

#--------> Copy Image File <-----------
def Copy_Image():
    os.system('"C:\Program Files (x86)\PuTTY\pscp" -pw Be9utiful E:\Pepper_Code_Final\new_question.jpg nao@155.245.22.39:/var/persistent/home/nao/.local/share/PackageManager/apps')

#---------> Speech to Text <-----------
def Speech_to_Text(file_number):
    transcript = "ERROR!"
    with open(join(dirname(__file__), "record"+str(file_number)+".wav"),"rb") as audio_file:
        data = json.dumps(speech_to_text.recognize(audio=audio_file,content_type='audio/wav'),indent=2)
        text = re.search('"transcript": "(.+?)"', data)
        if text:
            transcript = text.group(1)
    return (transcript)

#-----------> Cut Audio <----------
def Cut_Audio(seconds):
    segment = AudioSegment.from_file("record1.wav", format="wav")
    new_segment = segment[(seconds*1000):]
    new_segment.export("%s" % "record1.wav", format="wav")

#------> Audio Streaming + Conversion <-------
def Stream():
    global Output_global
    global file_number
    global Recording
    global elapsed_silence_time
    global Correct_Input
    global run_program
    global Tickle
    global Display_Image
    global Tablet_Wait
    while(run_program == True):
        Face_Detection()
        while(Conversation == True):
            if(Wait == False):
                Lissen = False
                file_number = 1
                silence_time = time.time()
                while(Recording == True):
                    record_path = "/home/nao/record"+str(file_number)+".wav"
                    record.startMicrophonesRecording(record_path, "wav", 16000, (0,0,1,0))
                    if(Lissen == False):
                        energy = mic.getFrontMicEnergy()
                        while(energy < sounds_level): #mic energy levels
                            energy = mic.getFrontMicEnergy() #wait for sound
                        elapsed_silence_time = time.time() - (silence_time+0.5)
                        print("Sound Detected")
                    Recording = Record()
                    Lissen = True
                    record.stopMicrophonesRecording()
                    file_number = file_number+1
                #print("Recording Ended!")
                Lissen = False
                time.sleep(0.5)
            else:
                text_out = Output_global[0:10]
                if (Display_Image == True and Correct_Input == False and text_out != "I didn't r"):
                    tablet_time = time.time()
                    elapsed_tablet_time = time.time() - tablet_time
                    while(elapsed_tablet_time < 4):
                        elapsed_tablet_time = time.time() - tablet_time
                    if (Tablet_Wait == False and Display_Image == True):
                        Tablet_Display(Output_global)
                        Correct_Input = True
                        Display_Image = False
                        Tablet_Wait = False
                if (Tickle == True):
                    tablet.showImage("http://198.18.0.1/apps/tickle_here.png")
                    tablet_time = time.time()
                    elapsed_tablet_time = time.time() - tablet_time
                    while(elapsed_tablet_time < 15):
                        elapsed_tablet_time = time.time() - tablet_time
                    Tickle = False
                    tablet.resetTablet()
        tablet.resetTablet()
        time.sleep(3)

#-----------> Move File + Conversion <----------
def Conversion():
    global text
    global Conversation
    global Recording
    global Wait
    global chatbot_memory
    global Display_Image
    global Output_global
    global Correct_Input
    global New_question
    global show_acom
    global run_program
    global Tickle
    global New_question_input
    while(run_program == True):
        answer_question = False
        finish_question = False
        question = ""
        answer = ""
        reset_chatbot_memory = False
        cut_output = ""
        previous_reply = ""
        while(Conversation == True):
            text = ''
            num = 2
            while(Recording == True):
                if(file_number == num): 
                    Move_File(num-1)
                    Wait = True
                    if(num == 2):
                        Cut_Audio(elapsed_silence_time)
                    text = text+' '+Speech_to_Text(num-1)
                    num = num+1
                time.sleep(0.2)
            print(text)
            if(answer_question == True):
                if(text == " ERROR!"):
                    Output = Chat_Bot(text)
                    speech.say(Output)
                elif(finish_question == True):
                    finish_question = False
                    answer_question = False
                    name = "question1"
                    examples = []
                    create_intent(name, examples)
                    create_example(name, New_question)
                    create_dialog_node(name,text)
                    New_question_input = New_question
                    New_question = ""
                    speech.say("Thank you. That question has now been added to my memory. What else can I help you with today?")
            else:
                Output = Chat_Bot(chatbot_memory+text)
                cut_output = Output[0:10]
                if(chatbot_memory == "Question "):
                    reset_chatbot_memory = True
                if(reset_chatbot_memory == True and text != " ERROR!"):
                    chatbot_memory = ""
                if(cut_output == "The univer"):
                    chatbot_memory = "Accommodation "
                    reset_chatbot_memory = True 
                if(Output == "Where would you like to book a taxi to?"):
                    chatbot_memory = "Uber "
                now = datetime.datetime.now()
                if(Output == "The date is"):
                    Output = Output+" "+p.number_to_words(now.day)+" "+calendar.month_name[now.month]+" "+p.number_to_words(now.year)
                if(Output == "The time is"):
                    Output = Output+" "+p.number_to_words(now.hour)+" "+p.number_to_words(now.minute)
                if(Output == "The time and date is"):
                    Output = Output+" "+p.number_to_words(now.hour)+" "+p.number_to_words(now.minute)+" "+p.number_to_words(now.day)+" "+calendar.month_name[now.month]+" "+p.number_to_words(now.year)
                Output_global = Output
                if(text == " ERROR!" or Output == "Ok. The question is."):
                    Display_Image = False
                else:
                    if(previous_reply == "There are "):
                        show_acom = True
                    previous_reply = ""
                    Display_Image = True
                    Correct_Input = False
                if(Output == "Ok. The question is."):
                    answer_question = True
                    finish_question = True
                    Output = Output+" "+New_question
                    time.sleep(1)
                if(cut_output == "Ok. Where "):
                    end_location = Output[67:len(Output)]
                    end = Location(Output[67:len(Output)])
                    Output = Output[0:67]
                if(cut_output == "Ok. The ta"):
                    start = Location(Output[24:len(Output)])
                    price = Book_taxi(start, end)
                    Output = Output[0:24]+" From "+Output[24:len(Output)]+" To "+end_location+". and the estimated price is, "+price
                    start = []
                    end = []
                    end_location = []
                    reset_chatbot_memory = True
                if(Output == "news"):
                    Output = news()
                if(Output == "weather"):
                    Output = weather()
                if(Output == "movies"):
                    Output = Movie()
                if(Output == "Ok. Feel free to tickle me. "):
                    Tickle = True
                speech.say(Output)
                if(Output == "Ok then. Have a nice day. Feel free to chat with me again. "):
                    Conversation = False
                    record.stopMicrophonesRecording()
                    tablet.resetTablet()
                if(Output == "Ok. Ending Program and Exiting Code."):
                    run_program = False
                    Conversation = False
                    record.stopMicrophonesRecording()
                    tablet.resetTablet()
                previous_reply = cut_output
                time.sleep(0.5)
                while(Display_Image == True):
                    pass
            Recording = True
            Wait = False
    
#------------> Chat Bot <-------------
def Chat_Bot(ChatIn):
    global chat_context
    url = "https://robot-flow.eu-gb.mybluemix.net/botchat"
    payload = {"msgdata": ChatIn}
    #payload['context']= chat_context
    r=requests.post(url, data=payload)
    response = r.json()
    #chat_context = response['botresponse']['messageout']['context']
    output = str(response['botresponse']['messageout']['output']['text'][0])
    return (output)

#--------> Tablet Thread <-----------
def tablet_thread():
    global Display_Image
    global Tablet_Wait
    global Output_global
    global Conversation
    global Correct_Input
    global show_acom
    global run_program
    global entertainment_value
    global Tickle
    while(run_program == True):
        while(Conversation == True):
            if (Display_Image == True):
                text_out = ""
                text_out = Output_global[0:10]
                if(show_acom == True and text_out == "I didn't r"):
                    tablet.showImage("http://198.18.0.1/apps/Acom.jpg")
                    Tablet_Wait = True
                    touch_tablet("acom")
                    show_acom = False
                elif(text_out == "I didn't r"):
                    tablet.showImage("http://198.18.0.1/apps/Menu1.jpg")
                    Tablet_Wait = True
                    touch_tablet("Menu")
                    if(entertainment_value == True):
                        tablet.showImage("http://198.18.0.1/apps/Entertainment.jpg")
                        touch_tablet("Entertainment")
                        if(Tickle == True):
                            tablet.showImage("http://198.18.0.1/apps/tickle_here.png")
                            touch_tablet("tickle")
                            speech.say("That was fun. Feel free to ask me about something else.")
                else:
                    tablet.showImage("http://198.18.0.1/apps/Touch_Here.jpg")
                    touch_tablet("Anywhere")
                    if(Correct_Input == True):
                        Display_Image = False
                        Tablet_Wait = False
                    if(Tickle == True):
                        tablet.showImage("http://198.18.0.1/apps/tickle_here.png")
                        touch_tablet("tickle")
                        speech.say("That was fun. Feel free to ask me about something else.")
                    if(Tablet_Wait == True):
                        speech.stopAll()
                        time.sleep(0.5)
                        if (show_acom == True):
                            tablet.showImage("http://198.18.0.1/apps/Acom.jpg")
                            speech.say("Sorry that I didn't understand you correctly pick what accommodation you were talking about")
                            touch_tablet("acom")
                            show_acom = False
                        else: 
                            tablet.showImage("http://198.18.0.1/apps/Menu1.jpg")
                            speech.say("Sorry that I didn't understand you correctly pick what you meant using the tablet and I will answer your query")
                            touch_tablet("Menu")
                            if(entertainment_value == True):
                                tablet.showImage("http://198.18.0.1/apps/Entertainment.jpg")
                                touch_tablet("Entertainment")
                                if(Tickle == True):
                                    tablet.showImage("http://198.18.0.1/apps/tickle_here.png")
                                    touch_tablet("tickle")
                                    speech.say("That was fun. Feel free to ask me about something else.")
                Display_Image = False
                Tablet_Wait = False
                entertainment_value = False

#-----------> Send Email <---------------
def email(address, subject, message):
    fromaddr = "tlharr@essex.ac.uk"
    toaddr = address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body, 'plain'))
    server = smtplib.SMTP('smtp.essex.ac.uk')
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login("tlharr", "BabyBess 29")
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)

#--------> Shake Hands With User <---------
def handshake():
    elapsed_handshake_time = 0

    motionProxy.setStiffnesses("RShoulder", 1.0)
    motionProxy.setStiffnesses("RElbow", 1.0)
    motionProxy.setStiffnesses("RWrist", 1.0)
    
    names  = ["RShoulderPitch", "RShoulderRoll", "RElbowRoll", "RElbowYaw", "RWristYaw"]
    angles  = [0.3, -0.25, 0.8, 0.8, 0.4]
    shake_down_angles  = [0.5, -0.13, 0.8, 1.1, -0.2]
    shake_up_angles  = [0.0, -0.13, 0.74, 0.84, 0.7]
    useSensors = False
    fractionMaxSpeed  = 0.2
    dif = 0.003
    shake = False
    handshake_time = time.time()
    #raise arm and wait
    while(elapsed_handshake_time < 16):
        num = 0
        motionProxy.setAngles(names, angles, fractionMaxSpeed)
        motionProxy.openHand("RHand")
        elapsed_handshake_time = time.time() - handshake_time
        if(elapsed_handshake_time > 4):
            if((motionProxy.getAngles(names, useSensors)[0]-0.3) > dif or (motionProxy.getAngles(names, useSensors)[0]-0.3) < -(dif)):
                motionProxy.closeHand("RHand")
                print("RShoulderPitch")
                shake = True
                break
            if((motionProxy.getAngles(names, useSensors)[1]-(-0.25)) > dif or (motionProxy.getAngles(names, useSensors)[1]-(-0.25)) < -(dif)):
                motionProxy.closeHand("RHand")
                print("RShoulderRoll")
                shake = True
                break
            if((motionProxy.getAngles(names, useSensors)[2]-0.8) > dif or (motionProxy.getAngles(names, useSensors)[2]-0.8) < -(dif)):
                motionProxy.closeHand("RHand")
                print("RElbowRoll")
                shake = True
                break
            if((motionProxy.getAngles(names, useSensors)[3]-0.8) > dif or (motionProxy.getAngles(names, useSensors)[3]-0.8) < -(dif)):
                motionProxy.closeHand("RHand")
                print("RElbowYaw")
                shake = True
                break
            if((motionProxy.getAngles(names, useSensors)[4]-0.4) > dif or (motionProxy.getAngles(names, useSensors)[4]-0.4) < -(dif)):
                motionProxy.closeHand("RHand")
                print("RWristYaw")
                shake = True
                break
            
    if(shake == True):
        handshake_time = time.time()
        motionProxy.closeHand("RHand")
        while(elapsed_handshake_time < 4):
            motionProxy.closeHand("RHand")
            elapsed_handshake_time = time.time() - handshake_time

    motionProxy.openHand("RHand")
    postureProxy.goToPosture("StandInit", 0.2)

#------------> Detect Face and Introduction <---------------
def Face_Detection():
    global Face
    global chatbot_memory
    global Conversation
    print("Looking for face...")
    Face = ""
    human_greeter = HumanGreeter(app)
    human_greeter.run()
    if (Face == "Tom" and New_question != ""):
        speech.say("Hello Tom, Can I ask you a question?")
        chatbot_memory = "Question "
    elif (Face != ""):
        speech.say("Hello "+Face+" Nice to see you again, how can I help?")
    else:
        speech.say("Hello, i am Pepper nice to meet you, how can I help you today?")
    Conversation = True

#-------------> News <-------------
def news():
    url = "http://newsapi.org/v1/articles?source=bbc-news&sortBy=top&apiKey=6481286796094f27b389285d267b6b5c"
    newsbot = urllib2.urlopen(url)
    newsbot = json.load(newsbot)
    news =  "BREAKING NEWS.\n"+str(newsbot["articles"][0]["title"])+".\n"+str(newsbot["articles"][0]["description"])+"\nIn other news.\n"+str(newsbot["articles"][1]["title"])+".\n"+str(newsbot["articles"][1]["description"])
    return(news)

#------------> Weather <------------
def weather():
    url = "http://api.openweathermap.org/data/2.5/weather?lat=51.8959&lon=0.8919&appid=01e7a487b0c262921260c09b84bdb456"
    weatherbot = urllib2.urlopen(url)
    weatherinfo = json.load(weatherbot)
    weather = "The Weather In Colchester Today Is: " + str(weatherinfo["weather"][0]["main"])
    return(weather)

#------------> Latest Movie <-------------
def Movie():
    url = "https://api.themoviedb.org/3/movie/now_playing?api_key=58c70c9e44a6565d189fcdff11a15cfa&language=en-US&page=1"
    moviebot = urllib2.urlopen(url)
    movieinfo = json.load(moviebot)
    movie = "The most popular movie in cinemas right now, is. "+str(movieinfo["results"][0]["title"])+".\n"+str(movieinfo["results"][0]["overview"])
    return(movie)

#----------> Ordering taxi service <-----------
def Book_taxi(start, end):
    pounds = ""
    pence = ""
    session = Session(server_token="G9Z6BMQoH7PMreyBXx1IKtiE9l796fcdCkvI7-Mw")
    client = UberRidesClient(session)
    response = client.get_price_estimates(
        start_latitude=start[0],
        start_longitude=start[1],
        end_latitude=end[0],
        end_longitude=end[1],
        seat_count=2
    )
    price = response.json.get('prices')
    average_price = str(((price[0]["high_estimate"]+price[0]["low_estimate"])/2))+"0"
    count = 0
    for c in average_price:
        if(c == "."):
            break
        count = count + 1
    pounds = p.number_to_words(average_price[0:count])
    pence = p.number_to_words(average_price[count+1:len(average_price)])
    out = pounds+" pounds and "+pence+" pence"
    return(out)

#----------> Get Place Location <---------------
def Location(Input):
    location = []
    if(Input == "North_Car_Park"):
        location = [51.878996, 0.943742]
    if(Input == "South_Car_Park"):
        location = [51.874400, 0.948763]
    if(Input == "Train_Station"):
        location = [51.902325, 0.895361]
    if(Input == "High_Street"):
        location = [51.889755, 0.901345]
    if(Input == "Tesco"):
        location = [51.884492, 0.930338]
    return(location)
    
#------------> Threads for Speech <--------------
def Speech_Threads():
    speech.stopAll()
    tablet.resetTablet()
    record.stopMicrophonesRecording()
    t1 = Thread(target=Stream)
    t2 = Thread(target=Conversion)
    t3 = Thread(target=tablet_thread)
    t1.start()
    t2.start()
    t3.start()

#-----------> Run Code Here <---------------------
#Audio_Level()
#Speech_Threads()
#learn_face()

