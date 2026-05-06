#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
from rclpy.duration import Duration
from sensor_msgs.msg import LaserScan
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point

class ScanRelay(Node):
    def __init__(self):
        super().__init__('scan_relay')

        qos_sub = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )
        qos_pub = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.RELIABLE,
            durability=DurabilityPolicy.VOLATILE
        )

        self.pub = self.create_publisher(LaserScan, '/scan_reliable', qos_pub)
        self.marker_pub = self.create_publisher(Marker, '/lidar_beam', qos_pub)
        self.sub = self.create_subscription(LaserScan, '/scan', self.callback, qos_sub)

    def callback(self, msg):
        msg.header.frame_id = 'laser_frame'
        self.pub.publish(msg)

        marker = Marker()
        marker.header = msg.header
        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.id = 0
        marker.scale.x = 0.02
        marker.lifetime = Duration(seconds=0.5).to_msg()  # some se não atualizar

        if msg.ranges:
            dist = msg.ranges[len(msg.ranges) // 2]

            if 0.3 < dist < 12.0:
                # Leitura válida — linha vermelha
                marker.color.r = 1.0
                marker.color.g = 0.0
                marker.color.b = 0.0
                marker.color.a = 1.0
                p1 = Point()
                p1.x, p1.y, p1.z = 0.0, 0.0, 0.0
                p2 = Point()
                p2.x, p2.y, p2.z = dist, 0.0, 0.0
            else:
                # Fora do range — linha cinza curta
                marker.color.r = 0.5
                marker.color.g = 0.5
                marker.color.b = 0.5
                marker.color.a = 1.0
                p1 = Point()
                p1.x, p1.y, p1.z = 0.0, 0.0, 0.0
                p2 = Point()
                p2.x, p2.y, p2.z = 0.1, 0.0, 0.0

            marker.points = [p1, p2]

        self.marker_pub.publish(marker)


def main():
    rclpy.init()
    node = ScanRelay()
    rclpy.spin(node)


if __name__ == '__main__':
    main()