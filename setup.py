from distutils.core import setup

setup(
    name='advisor-client',
    version='0.0.1',
    author='Adel Liu',
    author_email='i@6-79.cn',
    description='auto tuning adviser client',
    url='https://github.com/ciscoai/adviser-client',
    license='MIT',
    packages=['advisorclient'],
    entry_points={
        'console_scripts': [
            'trail_server=advisorclient.trail_server:execute',
            'trail_exec=advisorclient.run_trail:run',
        ]
    },
    install_requires=[
        'grpcio>=1.7.0',
        'requests>=2.18.4',
    ]
)
