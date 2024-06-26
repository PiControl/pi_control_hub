"""
   Copyright 2024 Thomas Bonk

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

from setuptools import setup

from pi_control_hub import __version__, __author__, __author_email__

setup(
    name='pi_control_hub',
    version=__version__,
    description='The PiControl Hub server',
    url='https://github.com/PiControl/pi_control_hub',
    author=__author__,
    author_email=__author_email__,
    license='Apache 2.0',
    packages=['pi_control_hub'],
    install_requires=[
        'fastapi==0.109.2',
        'zeroconf>=0.131.0',
        'cachetools>=5.3.2',
        'pi_control_hub_api @ git+https://github.com/PiControl/pi_control_hub_api.git@main#egg=pi_control_hub_api',
        'pi_control_hub_driver_api @ git+https://github.com/PiControl/pi_control_hub_driver_api.git@main#egg=pi_control_hub_driver_api',
    ],
    entry_points={
        'console_scripts': [
            'pi-control-hub = pi_control_hub.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
    ],
)
