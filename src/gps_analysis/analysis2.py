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
    bag_file = os.path.expanduser('~/gps_ws/src/gps_analysis/walking_data_fast/walking_data_fast_0.db3')
    parser = BagFileParser(bag_file)

    # Extract GPS data
    gps_messages = parser.get_messages("/gps")
    if gps_messages:
        latitudes = []
        longitudes = []
        altitudes = []

        # Filter points based on latitude and longitude
        for msg in gps_messages:
            if msg.latitude > 42 and -72 <= msg.longitude <= -70:
                latitudes.append(msg.latitude)
                longitudes.append(msg.longitude)
                altitudes.append(msg.altitude)

        # Ensure there are points after filtering
        if latitudes and longitudes and altitudes:
            # Plot Latitude vs Longitude
            plt.figure(figsize=(10, 6))
            plt.scatter(longitudes, latitudes, c=altitudes, cmap='viridis', label='GPS Points', s=50)
            plt.colorbar(label='Altitude (meters)')
            plt.xlabel('Longitude')
            plt.ylabel('Latitude')
            plt.title('GPS Latitude vs Longitude (Color-coded by Altitude)')
            plt.grid(True)
            plt.legend()
            plt.show()
        else:
            print("No GPS points found within the specified latitude/longitude range.")
    else:
        print("No GPS messages found.")
