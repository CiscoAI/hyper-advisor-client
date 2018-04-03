from distutils.core import setup

from setuptools import find_packages

setup(
    name='advisorclient',
    version='0.0.1',
    author='Adel Liu',
    author_email='i@6-79.cn',
    description='auto tuning adviser client',
    url='https://github.com/ciscoai/adviser-client',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'advisor-client=advisorclient.cmdline:execute',
        ]
    },
    install_requires=[
        'grpcio>=1.7.0',
        'requests>=2.18.4',
    ]
)
