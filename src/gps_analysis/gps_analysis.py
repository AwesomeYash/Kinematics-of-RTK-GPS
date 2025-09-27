import os
import rclpy
import rosbag2_py
from gps_msg.msg import GPSmsg
import matplotlib.pyplot as plt
from rclpy.serialization import deserialize_message

class BagFileParser:
    def __init__(self, bag_file):
        # Set up ROS2 and bag reader
        rclpy.init()
        self.reader = rosbag2_py.SequentialReader()

        storage_options = rosbag2_py.StorageOptions(uri=bag_file, storage_id='sqlite3')
        converter_options = rosbag2_py.ConverterOptions(input_serialization_format='cdr', output_serialization_format='cdr')

        self.reader.open(storage_options, converter_options)

        # Get available topics
        self.topics = {t.name: t.type for t in self.reader.get_all_topics_and_types()}

    def get_messages(self, topic_name):
        if topic_name not in self.topics:
            raise ValueError(f"Topic '{topic_name}' not found in the bag file.")
        
        messages = []
        while self.reader.has_next():
            (topic, data, t) = self.reader.read_next()
            if topic == topic_name:
                # Deserialize the message using rclpy.serialization.deserialize_message
                msg = deserialize_message(data, GPSmsg)
                messages.append(msg)
        
        return messages

if __name__ == "__main__":
    # Use the expanded path
    bag_file = os.path.expanduser('~/gps_ws/src/gps_analysis/walking_data_1_0.db3')
    parser = BagFileParser(bag_file)

    # Extract GPS data
    gps_messages = parser.get_messages("/gps")
    if gps_messages:
        easting = []
        northing = []

        # Filter points based on latitude and longitude
        for msg in gps_messages:
            if msg.latitude > 42 and -72 <= msg.longitude <= -70:
                easting.append(msg.utm_easting)
                northing.append(msg.utm_northing)

        # Ensure there are points after filtering
        if easting and northing:
            # Plotting
            plt.figure(figsize=(10, 6))
            plt.plot(easting, northing, label='GPS Path (Filtered)', color='blue')
            plt.scatter(easting, northing, s=50, label='GPS Points (Filtered)', color='red')
            plt.xlabel('UTM Easting')
            plt.ylabel('UTM Northing')
            plt.title('Filtered GPS Path Visualization')
            plt.legend()
            plt.grid()
            plt.show()
        else:
            print("No GPS points found within the specified latitude/longitude range.")
    else:
        print("No GPS messages found.")
