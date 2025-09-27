Here are the Directions for the Project:

gps_analysis Folder :
Folder stationary_data - It has data collected while sitting at one place (outside snell library)
Folder walking_data_1 - It has data collected while walking from one point to another in almost a straight line (Ruggles station to 2nd bridge)
Folder walking_data_1 - It has data collected while walking, but faster thus taking lesser time, from one point to another in almost a straight line
(2nd bridge to Ruggles station)
gps_analysis.py - Plots the Northing Vs Easting for stationary, walking data as well as Walking(fast) data, just file name is to be altered.
gps_analysis.py - Plots the Latitude Vs Longitude Vs Altitude for stationary, walking data as well as Walking(fast) data, just file name is to be altered.


In all the cases the data was collected but the data obtained was eratic. Thus to eliminate the rubish data, during analysis, I filtered the data. 
The filter applied was for latitude to be greater than 42 and longitude between -70 and -72, in order to get optimum results. 
The analysis is as in the folder and report.

gps_driver Folder :
Has another folder with same name that holds the driver.py file.

gps_msg Folder :
This is another package build in src. It contains the msg folder that has our custom massage.
