import pigpio
import threading
import time
import paho.mqtt.client as pmc
from UltraSonique import DetectorHandler
import pygame
import time

 
seq_full = [
    [1,0,0,1],
    [1,1,0,0],
    [0,1,1,0],
    [0,0,1,1]
]
seq_simple = [
    [1,0,0,0],
    [0,1,0,0],
    [0,0,1,0],
    [0,0,0,1]
]

#M1,M2,M3,M4 = 5,19,13,6
M1,M2,M3,M4 = 13,5,6,19

step_motor_args = {
    "M1": M1,
    "M2" : M2,
    "M3" : M3,
    "M4" : M4,
    "seq" : seq_full
}
COLORS = ["red","green","blue"]
currentColorIndex = 0
STOPCMD = "close"
isOpened = False

 
pi = pigpio.pi()
 

pygame.init()
 
class MusicLoop(threading.Thread):
    def _init_(self, group=None,target=None,name=None,args= ...,kwargs=None, * ,daemon= None,pi=None,step_args= {}):
        super().__init__(group,target,name,args,kwargs,daemon=daemon)
        self.pi=pi
        self.step_args=step_args.copy()
 
    def run(self):
        self.kill=False
        lastRegisteredTime = time.time()
        pygame.mixer.init()
        my_sound = pygame.mixer.Sound('music.mp3')            
        my_sound.set_volume(1.0)
        my_sound.play()
        while not self.kill:
            if time.time() - lastRegisteredTime > 302:
                my_sound.set_volume(1.0)
                my_sound.play()
                lastRegisteredTime = time.time()
        my_sound.stop()
        pygame.mixer.quit()
       
       


   
   



class StepMotor(threading.Thread):
    def __init__(self, group = None, target = None, name = None, args = ..., kwargs = None, *, daemon = None, pi = None, step_args = {} ):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)
        self.pi = pi
        self.step_args = step_args.copy()
        
    def run(self):
        self.kill = False
        self.pi.set_mode(self.step_args["M1"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M2"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M3"],pigpio.OUTPUT)
        self.pi.set_mode(self.step_args["M4"],pigpio.OUTPUT)
        self.pi.write(self.step_args["M1"], 0)
        self.pi.write(self.step_args["M2"], 0)
        self.pi.write(self.step_args["M3"], 0)
        self.pi.write(self.step_args["M4"], 0)
        step_to_use = self.step_args["seq"].copy()
        print(step_to_use)
        for step in step_to_use:
            self.pi.write(self.step_args["M1"], step[0])
            self.pi.write(self.step_args["M2"], step[1])
            self.pi.write(self.step_args["M3"], step[2])
            self.pi.write(self.step_args["M4"], step[3])
            time.sleep(0.010)
            # if count == 2048:
            #     self.step_args["seq"].reverse()
        self.pi.write(self.step_args["M1"], 0)
        self.pi.write(self.step_args["M2"], 0)
        self.pi.write(self.step_args["M3"], 0)
        self.pi.write(self.step_args["M4"], 0)
        self.kill = True
 
 


 
step_motor_thread = StepMotor(pi=pi, step_args=step_motor_args)
ultra_thread = DetectorHandler()
music_thread = MusicLoop()

threads = [ultra_thread,music_thread]
 
 
for i in threads: #starts the threads
    i.start()
print("threads started")
 



BROKER = "mqttbroker.lan"
BROKERLOCAL = "192.168.137.1"
#192.168.1.5
PORT = 1883
TOPICLOCAL = "esp32-001/receive"
TOPIC = "/ex4/cedric"

def connexion(client, userdata, flags, code, properties):
    if code == 0:
        print("connectioon")
    else:
        print("Erreur connexcion: code", code)

def reception_msg(cl,userdata,msg):
    message_content = msg.payload.decode()
    print("Recu", message_content)
    if "2" in message_content:
        isOpened = not isOpened
        if not isOpened:
            client.publish(TOPICLOCAL,"close")


client = pmc.Client(pmc.CallbackAPIVersion.VERSION2,userdata="RapperPi")
client.on_connect = connexion
client.on_message = reception_msg
#client.connect(BROKER, PORT)
client.connect(BROKERLOCAL,PORT)
client.subscribe(TOPIC)
#client.subscribe(TOPICLOCAL)
client.loop_start()
def change_color():
    global currentColorIndex
    currentColorIndex += 1
    currentColorIndex %= len(COLORS)
    #client.publish(TOPICLOCAL,"close")
    print(COLORS[currentColorIndex])
    RED,GREEN,BLUE = 18,23,24
    client.publish(TOPICLOCAL,"close")
    client.publish(TOPICLOCAL,COLORS[currentColorIndex])


try:
    detected = False
    while True:
        
        # if step_motor_thread.kill:
        #     step_motor_thread.run()
        if ultra_thread.value < 10 and not detected:
            step_motor_thread.step_args["seq"].reverse()
            detected = True

            change_color()
            isOpened = True
        if not (ultra_thread.value < 20.0):
            detected = False
except KeyboardInterrupt:
    client.publish(TOPICLOCAL,"close")
    client.disconnect()
    

    
 
 
#check if all threads have been ended
threads_amount = len(threads)
all_threads_ended_number = threading.active_count() - threads_amount
for i in threads:
    i.kill = True
while threading.active_count() > all_threads_ended_number:
    print("waiting for {0} threads".format(str(threading.active_count() - all_threads_ended_number)))
    time.sleep(1)
 
 
print("Program end")