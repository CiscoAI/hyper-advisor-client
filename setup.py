from distutils.core import setup

setup(
    name='adviser-client',
    version='0.1.5beta',
    author='Adel Liu',
    author_email='i@6-79.cn',
    description='auto tuning adviser client',
    url='https://github.com/ciscoai/adviser-client',
    license='MIT',
    packages=['adviserclient'],
    entry_points={
        'console_scripts': ['trail_server=adviserclient.trail_server:execute']
    },
    install_requires=[
        'grpcio>=1.7.0',
        'requests>=2.18.4',
    ]
)
