This is code to use with an arduino to monitor FDS100 photodiodes. 

need to instal pyserial for serial to work 

Install Arduino IDE 2.3.8. There is a test.ino script to test your connection to the Arduino. You can also use photodiode_sketch.ino to upload to the arduino and then use the serial monitor (button on the far right top that looks like a spy glass with 4 dots) to test. You should see 6 numbers seperated by commas pertaining to each photodiode. If you see squares and not numbers is probably because your BAUD isn't the right value (in this code it is 9600). 

In python you need to run the code in terminal (not interactive window in VS Code). 
