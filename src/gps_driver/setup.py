from setuptools import find_packages, setup
from glob import glob
import os

package_name = 'gps_driver'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),
        
        #('lib/' + package_name, ['gps_driver/driver.py']),
        #('share/' + package_name + '/launch', ['launch/gps_launch.py']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='priyanshu',
    maintainer_email='ranka.pr@northeastern.edu',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
         	'driver = gps_driver.driver:main',
        ],
    },
)