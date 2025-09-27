import os
import rclpy
import rosbag2_py
from gps_msg.msg import GPSmsg
import matplotlib.pyplot as plt
from rclpy.serialization import deserialize_message
import numpy as np

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

def calculate_cross_track_error(easting, northing, start_point, end_point):
    line_vec = end_point - start_point
    line_len = np.linalg.norm(line_vec)
    line_unitvec = line_vec / line_len
    errors = []

    for e, n in zip(easting, northing):
        point = np.array([e, n])
        point_vec = point - start_point
        proj_length = np.dot(point_vec, line_unitvec)
        proj_point = start_point + proj_length * line_unitvec
        error_vec = point - proj_point
        error = np.linalg.norm(error_vec)
        errors.append(error)

    return errors

def plot_gps_data(easting, northing, errors):
    plt.figure(figsize=(10, 6))
    plt.plot(easting, northing, label='GPS Path', color='blue')
    plt.scatter(easting, northing, s=10, color='red')
    plt.xlabel('UTM Easting')
    plt.ylabel('UTM Northing')
    plt.title('GPS Path Visualization')
    plt.legend()
    plt.grid()

    # Straight line from start to end point
    start_point = np.array([easting[0], northing[0]])
    end_point = np.array([easting[-1], northing[-1]])
    plt.plot([start_point[0], end_point[0]], [start_point[1], end_point[1]], color='green', label='Straight Line')
    plt.legend()
    plt.show()

   # # Plot errors over time
   # plt.figure(figsize=(10, 6))
   # plt.plot(errors, label='Cross-Track Error', color='purple')
   # plt.xlabel('Sample Index')
   # plt.ylabel('Error (m)')
   # plt.title('Cross-Track Error')
   # plt.legend()
   # plt.grid()
   # plt.show()

    # Print statistics about errors
    print(f'Mean Error: {np.mean(errors):.2f} meters')
    print(f'Standard Deviation of Error: {np.std(errors):.2f} meters')
    print(f'Maximum Error: {np.max(errors):.2f} meters')

if __name__ == "__main__":
    # Use the expanded path
    bag_file = os.path.expanduser('~/gps_ws/src/gps_analysis/walking_data_1_0.db3')
    parser = BagFileParser(bag_file)

    # Extract GPS data
    gps_messages = parser.get_messages("/gps")
    if gps_messages:
        easting = []
        northing = []

        # Collect UTM data
        for msg in gps_messages:
            easting.append(msg.utm_easting)
            northing.append(msg.utm_northing)

        # Ensure there are points after filtering
        if easting and northing:
            # Calculate cross-track errors
            start_point = np.array([easting[0], northing[0]])
            end_point = np.array([easting[-1], northing[-1]])
            errors = calculate_cross_track_error(easting, northing, start_point, end_point)

            # Plot and analyze GPS data
            plot_gps_data(easting, northing, errors)
        else:
            print("No GPS points found.")
    else:
        print("No GPS messages found.")
