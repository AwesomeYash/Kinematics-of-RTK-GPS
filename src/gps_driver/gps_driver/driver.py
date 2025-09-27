#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from gps_msg.msg import GPSmsg
from std_msgs.msg import Header
import serial
import utm

class GPSDriver(Node):
    def __init__(self):
        super().__init__('gps_driver')
        
        self.declare_parameter('port', '/dev/pts/5')
        port = self.get_parameter('port').get_parameter_value().string_value
        
        self.publisher_ = self.create_publisher(GPSmsg, '/gps', 10)
        self.serial_connection = serial.Serial(port, baudrate=4800, timeout=1.0)
        self.get_logger().info(f"Connected to {port}, baudrate: 4800")
        
        # Timer to run the parsing function repeatedly
        self.create_timer(0.1, self.publish_gps_data)  # 10hz freq

    def publish_gps_data(self):
        if self.serial_connection.in_waiting > 0:
            line = self.serial_connection.readline().decode('ascii', errors='replace')

            if line.startswith('$GPGGA'):  # When we want to take only GPGGA data
                parsed_data = self.parse_gpgga(line)
                if parsed_data:
                    self.publisher_.publish(parsed_data)
                    # Only print GPGGA data in the requested format
                    self.get_logger().info(
                        f"Latitude = {parsed_data.latitude}, Longitude = {parsed_data.longitude}, "
                        f"Altitude = {parsed_data.altitude}, UTM Easting = {parsed_data.utm_easting}, "
                        f"UTM Northing = {parsed_data.utm_northing}, Zone = {parsed_data.zone}, "
                        f"Letter = {chr(parsed_data.letter)}"
                    )

    def parse_gpgga(self, gpgga_sentence):
        try:
            parts = gpgga_sentence.split(',')
            if len(parts) < 15:
                return None

            # Parsing the Latitude, Longitude, Altitude
            lat = float(parts[2])
            lat_dir = parts[3]
            lon = float(parts[4])
            lon_dir = parts[5]
            altitude = float(parts[9])

            # Convert to decimal degrees
            latitude = self.convert_to_decimal_degrees(lat, lat_dir)
            longitude = self.convert_to_decimal_degrees(lon, lon_dir)

            # Convert to UTM
            utm_easting, utm_northing, zone_number, zone_letter = utm.from_latlon(latitude, longitude)

            # Create the GPS message
            msg = GPSmsg()
            msg.header = Header()
            now = self.get_clock().now()
            msg.header.stamp.sec = int(now.nanoseconds / 1e9)
            msg.header.stamp.nanosec = int(now.nanoseconds % 1e9)
            msg.header.frame_id = "GPS1_Frame"
            msg.latitude = latitude
            msg.longitude = longitude
            msg.altitude = altitude
            msg.utm_easting = utm_easting
            msg.utm_northing = utm_northing
            msg.zone = zone_number
            msg.letter = ord(zone_letter)

            return msg
        except Exception as e:
            #self.get_logger().error(f"Failed to parse GPGGA: {e}")
            return None

    def convert_to_decimal_degrees(self, value, direction):
        degrees = int(value / 100)
        minutes = value - degrees * 100
        decimal_degrees = degrees + minutes / 60
        if direction in ['S', 'W']:
            decimal_degrees *= -1
        return decimal_degrees

def main(args=None):
    rclpy.init(args=args)

    gps_driver = GPSDriver()

    try:
        rclpy.spin(gps_driver)
    except KeyboardInterrupt:
        pass

    gps_driver.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
