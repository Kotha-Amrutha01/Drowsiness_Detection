from scipy.spatial import distance
from imutils import face_utils
import imutils
import dlib
import cv2
import smbus

import os
import glob
import time
 
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'




import RPi.GPIO as GPIO
import time

 

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)



bus = smbus.SMBus(1)
bus.write_byte_data(0x53, 0x2C, 0x0B)
value = bus.read_byte_data(0x53, 0x31)
value &= ~0x0F;
value |= 0x0B;  
value |= 0x08;
bus.write_byte_data(0x53, 0x31, value)
bus.write_byte_data(0x53, 0x2D, 0x08)
def getAxes():
    bytes = bus.read_i2c_block_data(0x53, 0x32, 6)
        
    x = bytes[0] | (bytes[1] << 8)
    if(x & (1 << 16 - 1)):
        x = x - (1<<16)

    y = bytes[2] | (bytes[3] << 8)
    if(y & (1 << 16 - 1)):
        y = y - (1<<16)

    z = bytes[4] | (bytes[5] << 8)
    if(z & (1 << 16 - 1)):
        z = z - (1<<16)

    x = x * 0.004 
    y = y * 0.004
    z = z * 0.004

    x = x * 9.80665
    y = y * 9.80665
    z = z * 9.80665

    x = round(x, 2)
    y = round(y, 2)
    z = round(z, 2)

 
    return x,y,z

LCD_RS = 26
LCD_E  = 19
LCD_D4 = 13
LCD_D5 = 6
LCD_D6 = 5
LCD_D7 = 11

ss = 17
mot1=27
mot2=22

GPIO.setup(mot1,GPIO.OUT)
GPIO.setup(mot2,GPIO.OUT)
GPIO.setup(ss,GPIO.IN)



#initializing LCD

LCD_WIDTH = 16  
LCD_CHR = True
LCD_CMD = False

LCD_LINE_1 = 0x80 
LCD_LINE_2 = 0xC0 

# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setup(LCD_E, GPIO.OUT)  # E
GPIO.setup(LCD_RS, GPIO.OUT) # RS
GPIO.setup(LCD_D4, GPIO.OUT) # DB4
GPIO.setup(LCD_D5, GPIO.OUT) # DB5
GPIO.setup(LCD_D6, GPIO.OUT) # DB6
GPIO.setup(LCD_D7, GPIO.OUT) # DB7

# LCD functions

def lcd_init():
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)

def lcd_byte(bits, mode):
  GPIO.output(LCD_RS, mode) # RS

  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)

  # Toggle 'Enable' pin
  lcd_toggle_enable()

def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)

def lcd_string(message,line):

  message = message.ljust(LCD_WIDTH," ")

  lcd_byte(line, LCD_CMD)

  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)

lcd_init()
lcd_byte(0x01,LCD_CMD)
lcd_string("    WELCOME",LCD_LINE_1)
lcd_string("BABY MONITORING",LCD_LINE_2)

def send_sms(msg):
    print("sending SMS..")

    cmd='AT\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(20)
    print(rcv)
    cmd='AT+CMGF=1\r\n'
    ser.write(cmd.encode())
    time.sleep(2)
    rcv = ser.read(20)
    print(rcv)                                             
    phno="9989492830"                          
    cmd='AT+CMGS="'+str(phno)+'"\r\n'
    ser.write(cmd.encode())
    rcv = ser.read(20)
    print(rcv)                        
    time.sleep(1)
    cmd=msg
    ser.write(cmd.encode())  # Message
  
    time.sleep(1)
    cmd = "\x1A"
    ser.write(cmd.encode()) # Enable to send SMS
    time.sleep(10)
    print('SMS Sent')
    time.sleep(1)


 
def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f
        





def eye_aspect_ratio(eye):
        A = distance.euclidean(eye[1], eye[5])
        B = distance.euclidean(eye[2], eye[4])
        C = distance.euclidean(eye[0], eye[3])
        ear = (A + B) / (2.0 * C)
        return ear
        
thresh = 0.25
frame_check = 20
detect = dlib.get_frontal_face_detector()
predict = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")# Dat file is the crux of the code

(lStart, lEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["left_eye"]
(rStart, rEnd) = face_utils.FACIAL_LANDMARKS_68_IDXS["right_eye"]
cap=cv2.VideoCapture(0)
flag=0
fs=0
kk=0
ssv=0
os.system("omxplayer 1.mp3")

while True:
        x,y,z=getAxes()
            
            
        print("X:" + str(x))
        print("Y:" + str(y))
        if(x>5 or y>5 or y<-5 or x<-5):
                fs=1
        
        tmp=read_temp()[1]
        sval=GPIO.input(ss)
        print('SOUND:'+str(sval)  +' TEMP:'+str(int(tmp)) +' FS:'+str(fs))
        lcd_byte(0x01,LCD_CMD)
        lcd_string('S:'+str(sval)  +' T:'+str(int(tmp)) +' F:'+str(fs),LCD_LINE_1)
              
        if(fs==1):
                lcd_string("Fall detected",LCD_LINE_2) 
                print('Fall detected')
                if(kk==0):
                        kk=1
                        send_sms('Fll detected')

        if(sval==1):
                   ssv=ssv+1
                   if(ssv>10):
                        lcd_string("Cry detected",LCD_LINE_2) 
                        print('Cry detected')
                   
       
        ret, frame=cap.read()
        frame = imutils.resize(frame, width=450)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        subjects = detect(gray, 0)
        for subject in subjects:
                shape = predict(gray, subject)
                shape = face_utils.shape_to_np(shape)#converting to NumPy Array
                leftEye = shape[lStart:lEnd]
                rightEye = shape[rStart:rEnd]
                leftEAR = eye_aspect_ratio(leftEye)
                rightEAR = eye_aspect_ratio(rightEye)
                ear = (leftEAR + rightEAR) / 2.0
                leftEyeHull = cv2.convexHull(leftEye)
                rightEyeHull = cv2.convexHull(rightEye)
                cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
                cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)
                if ear < thresh:
                        flag += 1
                        print (flag)
                        if flag >= frame_check:
                                cv2.putText(frame, "****************Baby Sleeping!****************", (10, 30),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                cv2.putText(frame, "****************Baby Sleeping!****************", (10,325),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                GPIO.output(mot1,0)
                                GPIO.output(mot2,0)
                                #print ("Drowsy")
                else:
                        flag = 0
                        cv2.putText(frame, "****************Baby WakeUp!****************", (10, 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        cv2.putText(frame, "****************Baby WakeUp!****************", (10,325),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                        GPIO.output(mot1,1)
                        GPIO.output(mot2,0)
        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
                break
cv2.destroyAllWindows()
cap.release() 
