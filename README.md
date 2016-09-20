# RoomPresenceDF16
Meeting room presence algorithm that messages Salesforce when room is occupied.

#Usage
##Salesforce Config
- Create master / detail custom objects named Room__c and Room_Occupancy__c respectively. The master will be the room object and the detail will represent when the room is occupied.
- Create custom field Occupied__c in Room__c object
- Create Start_Time__c and End_Time__c in Room_Occupancy__c object

##Python Script
###Set the parameters at the top of the python script

Authentication parameters and Room Record Identification
- USER_NAME = 'Username'
- PASSWORD = 'User Password'
- TOKEN = 'User security token (if not admin)'
- SANDBOX = 'TRUE or FALSE'
- ROOM_ID = 'Room ID'
- PIR_PIN = 7

Parameters for occupancy and vacancy tests
- Detection_Window = 60  (seconds to run the motion detection loop between tests for occupancy)
- Occupied_Trigger = 30  (seconds between first and last movement within detection window to declare a space occupied)
- Vacancy_Threshold = 3  (number of zero movement detection windows to declare a space vacant)
