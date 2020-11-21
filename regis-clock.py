#!/usr/bin/python

#This program is a simple 7-segment clock that's being displayed on a DEC ReGIS compatible graphics terminals.
#todo:
#	properly handle exceptions
#	add some proper exit function
#	test various flow control modes
#	switch off cursor at the start and switch it back on at the end
#	add AM/PM mode?

#Config parameters:
#OutputType - interface that's connected to the terminal.
#	stdout - terminal is connected as a system console
#	serial - terminal is connected to a serial port that's not a system console
OutputType="stdout"

#SerPort - if Output Type is serial, this is the port the terminal is connected to.
#Otherwise, this parameter is unused.
SerPort="/dev/ttyUSB0"

#SerSpeed - if Output Type is serial, this is the serial communications speed.
#Otherwise, this parameter is unused. This should matche the spped on a terminal.
SerSpeed=4800

#Ser port - if Output Type is serial, this is type of the flow control.
#Otherwise, this parameter is unused. On certain adapters, various flow control
#modes might be unusable. Be sure that certain mode is supported and if it's working.
#Flow control mode should be the same as configured on the terminal.
#	none - no flow control is used
#	xonxoff - software flow control
#	rts - hardware flow control that uses RTS and CTS signals
SerFlowControl="none"

import sys
import time

#Imports serial module and shows fault message if it's not found.
if(OutputType=="serial"):
	try:
		import serial
	except:
		print "Python serial module ERROR"
		print "\"apt-get install python-serial\" might help in case it's not installed"
		sys.exit()

#SegmentArray is the array for coding the number to the seven segment code.
#Array index number is the digit to be coded and each bit in the string represents
#one segment. First seven is segments A-G. Last bit is unused.
SegmentArray=["11111100","01100000","11011010","11110010","01100110","10110110","10111110","11100000","11111110","11110110"]

#SegmentCode is the part of the ReGIS commant, that's used to draw a corresponding
#segment. First array entry is segment A, last one is G.
#After drawing each segment, the graphics cursor is returned to the starting point.
SegmentCode=[]
SegmentCode.append("P(B)[+22,+18],V[+27,+10],[+85,+0],[+13,-28],[-105,+0],C(S)[+0,+0],[-12,+6],[-8,+12],[](E),P(E),")
SegmentCode.append("P(B)[+155,+0],V[-14,+28],[-7,+74],[+19,+22],[+8,-8],[+9,-98],C(S)[+0,+0],[-5,-12],[-10,-6],[](E),P(E),")
SegmentCode.append("P(B)[+149,+236],V[+9,-99],[-6,-6],[-23,+21],[-8,+74],[+8,+28],C(S)[+0,+0],[+13,-7],[+7,-11],[](E),P(E),")
SegmentCode.append("P(B)[+16,+254],V[+106,+0],[-8,-28],[-84,+0],[-30,+11],C(S)[+0,+0],[+5,+11],[+11,+6],[](E),P(E),")
SegmentCode.append("P(B)[+1,+229],V[+29,-10],[+7,-67],[-19,-21],[-8,+7],[-9,+91],P(E),")
SegmentCode.append("P(B)[+21,+25],V[-9,+92],[+7,+7],[+23,-22],[+7,-66],[-28,-11],P(E),")
SegmentCode.append("P(B)[+25,+127],V[+16,-14],[+91,+0],[+13,+14],[-15,+14],[-92,-0],[-13,-14],P(E),")

#These are much simpler digit segments, simple straight lines, that was used
#for testing the overall concept.
#SegmentCode.append("V(B)[+150,+0],P(E),")
#SegmentCode.append("P(B)[+150,+0],V[+0,+150],P(E),")
#SegmentCode.append("P(B)[+150,+150],V[+0,+150],P(E),")
#SegmentCode.append("P(B)[+150,+300],V[-150,+0],P(E),")
#SegmentCode.append("P(B)[+0,+300],V[+0,-150],P(E),")
#SegmentCode.append("P(B)[+0,+150],V[+0,-150],P(E),")
#SegmentCode.append("P(B)[+0,+150],V[+150,-0],P(E),")


#DrawDigit is the function for drawing a single digit.
#Arguments:	Digit - digit to draw
#		Xcoord - X coordinate of upper left corner
#		Ycoord - Y coordinate of upper left corner
def	DrawDigit(Digit,Xcoord,Ycoord):
	#Regis command is formed as a long strinng.
	#Starts ReGIS mode
	RegisString="\x1BP0p,"
	#Outputs the given coordinate
	RegisString+="P["+str(Xcoord)+","+str(Ycoord)+"],"
	#Loop that tests which segment should be drawn and adds respective code
	#to the ReGIS command
	for i in range(0,7):
		if(SegmentArray[Digit][i]=="1"):
			RegisString+=SegmentCode[i]
	#Ends ReGIS mode
	RegisString+="\x1B\\"
	#Outputs the ReGIS command to preferred interface
	if(OutputType=="serial"):
		ser.write(RegisString)
	else:
		sys.stdout.write(RegisString)
		sys.stdout.flush()

#DrawDots is the function that draws the two dots between hours and minutes
def	DrawDots():
	if(OutputType=="serial"):
		ser.write("\x1BP0p,")
		ser.write("P[405,166],C[+17],")
		ser.write("P[395,268],C[+17],")
		ser.write("\x1B\\")
	else:
		sys.stdout.write("\x1BP0p,P[405,166],C[+17],P[395,268],C[+17],\x1B\\")
		sys.stdout.flush()

#Erase screen clears the screen from the ReGIS graphics
def	EraseScreen():
	if(OutputType=="serial"):
		ser.write("\x1BP0p,S(E),\x1B\\")
	else:
		sys.stdout.write("\x1BP0p,S(E),\x1B\\")
		sys.stdout.flush()


#Program starts here
try:
	#Opens serial port if it should be used
	if(OutputType=="serial"):
		if(SerFlowControl=="none"):
			ser=serial.Serial(SerPort,SerSpeed)
		elif(SerFlowControl=="xonxoff"):
			ser=serial.Serial(SerPort,SerSpeed,xonxoff=True)
		elif(SerFlowControl=="rtscts"):
			ser=serial.Serial(SerPort,SerSpeed,rtscts=True)
		elif(SerFlowControl=="dsrdtr"):
			ser=serial.Serial(SerPort,SerSpeed,dsrdtr=True)

		ser.write("\x1B[f\x1B[J")	#Erases text on the screen
	else:
		sys.stdout.write("\x1B[f\x1B[J")
		sys.stdout.flush()

	#Initialises a variable that is being used to check if the minute has passed
	oldmin=""
	#Constant loop that updates the digits every minute
	while(1):
		#Checks if minute digit has changed
		newmin=time.strftime("%M")
		if(oldmin!=newmin):
			oldmin=newmin
			#Erases the screen and shows updated numbers
			EraseScreen()
			hours=time.strftime("%H")
			DrawDigit(ord(hours[0])-48,15,90)
			DrawDigit(ord(hours[1])-48,195,90)
			DrawDots()
			DrawDigit(ord(newmin[0])-48,435,90)
			DrawDigit(ord(newmin[1])-48,615,90)

finally:
	EraseScreen()
	print "that's it" 
	if(OutputType=="serial"):
		ser.close()
