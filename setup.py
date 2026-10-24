import os
from glob import glob
from setuptools import find_packages, setup

package_name = 'delivery_robot'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Abdul Wahab',
    maintainer_email='abdulwahab@ros2.local',
    description='Indoor Delivery Robot with Safety Zones',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'delivery_server = delivery_robot.delivery_server:main',
            'obstacle_spawner = delivery_robot.obstacle_spawner:main',
        ],
    },
)
