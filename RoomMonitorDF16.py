#---------------------------------------------------------------------------------------------------
# Room Monitor
#
# February 2016
# Larry Allan, Mark Williamson
# The Regional Municipality of York
#
# Determine space occupancy from PIR sensor data.
# Update Salesforce with room state information and create occupancy records for the monitored room.
#
# Dreamforce 16 IoT Demo
#---------------------------------------------------------------------------------------------------

# Authentication parameters Room Record Id and GPIO Pin
USER_NAME = ‘me@myDomain'
PASSWORD = ‘myPassword'
TOKEN = ‘myToken’
SANDBOX = False

ROOM_ID = ‘myRoomID'
PIR_PIN = 7

# Parameters for occupancy and vacancy tests
Detection_Window = 60  # seconds to run the motion detection loop between tests for occupancy
Occupied_Trigger = 30  # seconds between first and last movement within detection window to declare a space occupied
Vacancy_Threshold = 3  # number of zero movement detection windows to declare a space vacant

# Constants
VACANT = 0
OCCUPIED = 1
ONE_SECOND = 1

# Load libraries for GPIO interface, timer functions and Salesforce
import RPi.GPIO as GPIO
import time
from simple_salesforce import Salesforce

# Configure GPIO interface to listen for sensor input on Pin 7
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

# Initialize state and time keeping variables
Room = VACANT
Vacancy_Count = 0
First_Movement = time.time()
Last_Movement = First_Movement

print ("Begin Motion Sensing (CNTL+C to exit)")

try:
    # Continuous loop keeps program active (Terminate loop with CNTL+C)
    while 1:

        # Reset control variables for Detection Loop
        First_Detection = True
        Detection_Loop_Seconds = 0
        print ("   Start Detection Loop Window: ", time.asctime(time.gmtime()))
        
        # Detection loop records time stamps for first and last detected motion within  
        # the detection loop window
        while Detection_Loop_Seconds < Detection_Window:
            if GPIO.input(PIR_PIN):
                if First_Detection:
                    First_Detection = False
                    Vacancy_Count = 0
                    First_Movement = time.time()
                    First_Motion = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    print("      First Motion Detected", time.asctime(time.gmtime()))
                else:
                    Last_Movement = time.time()
                    Last_Motion =  time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
                    print("      Last  Motion Detected", time.asctime(time.gmtime()))

            time.sleep(ONE_SECOND)
            Detection_Loop_Seconds += ONE_SECOND

        # Analyze data from the last detection loop
        # Should the Room State change from Vacant to Occupied?  Room must currently be vacant and
        # time between first and last hits must be at least [Occupied_Trigger] seconds
        if Room == VACANT and Last_Movement - First_Movement > Occupied_Trigger: 
            # Set room occupied and save the First_Motion time stamp - needed later for Occupancy Record 
            Room = OCCUPIED
            Start_Time = First_Motion
            # Update Salesforce - set Room Occupied
            sf = Salesforce(username = USER_NAME, password=PASSWORD, security_token=TOKEN, sandbox=SANDBOX)
            sf.Room__c.update(ROOM_ID, {'Occupied__c':True})
            print ("   [*]  Set Room Occupied at ", First_Motion)

        # If no motion detected during the last detection loop increment our counter to test for vacancy
        if First_Detection == True:
            Vacancy_Count += 1

        if Room == VACANT:
            print ("   [ ]  Vacant", time.asctime(time.gmtime()))

        # Should the room state change from Occupied to Vacant?  Room must currently be occupied and
        # the vacancy count must meet the threshold to change the state
        if Room == OCCUPIED and Vacancy_Count == Vacancy_Threshold:
            # Set room vacant and zero out difference between the last pair of movement records
            # This eliminates falsly setting a room occupied based on "old" movement records
            Room = VACANT
            First_Movement = Last_Movement
            # Update Salesforce - Set Room Vacant and create Occupancy record
            sf = Salesforce(username = USER_NAME, password=PASSWORD, security_token=TOKEN, sandbox=SANDBOX)
            sf.Room__c.update(ROOM_ID, {'Occupied__c':False})
            sf.Room_Occupancy__c.create({'Room__c':ROOM_ID, 'Start_Time__c':Start_Time, 'End_Time__c': Last_Motion})
            print ("   [ ]  Set Room Vacant   at ", Last_Motion)
            print ("   ***  Create occupancy Record from ", Start_Time, " To ", Last_Motion)

    # End of continuous loop
    
except KeyboardInterrupt:
    print ("Stop Motion Sensing")

    # If space is currently occupied, Change state to Vacant and create Occupancy record
    if Room == OCCUPIED:
       Room = VACANT 
       sf = Salesforce(username = USER_NAME, password=PASSWORD, security_token=TOKEN, sandbox=SANDBOX)
       sf.Room__c.update(ROOM_ID, {'Occupied__c':False})
       sf.Room_Occupancy__c.create({'Room__c':ROOM_ID, 'Start_Time__c':Start_Time, 'End_Time__c': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())})
       print ("   [ ]  Set Room Vacant   at ", Last_Motion)
       print ("   ***  Create occupancy Record from ", Start_Time, " To ", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    
    GPIO.cleanup()

    
