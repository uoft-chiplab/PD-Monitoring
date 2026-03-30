import serial 
import time 

arduino = serial.Serial(port='COM3', baudrate=115200, timeout=1) 
time.sleep(2)  # <-- Add this line, wait for Arduino to reset

def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    time.sleep(0.05) 
    data = arduino.readline() 
    return data 

while True: 
    num = input("Enter a number: ")
    value = write_read(num) 
    print(value)