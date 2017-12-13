from distutils.core import setup

setup(
    name='adviser-client',
    version='0.0.1beta',
    author='Adel Liu',
    author_email='i@6-79.cn',
    description='auto tuning adviser client',
    url='https://github.com/ciscoai/adviser-client',
    license='MIT',
    packages={
        'adviser-client'
    },
    entry_points={
        'console_scripts': ['trail_server = adviser-client.trail_server.py']
    }
)
