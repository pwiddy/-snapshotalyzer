from setuptools import setup

setup(
        name='snapshotalyzer',
        version='0.1',
        author="Paul Widmer",
        author_email="pwidmer@gmail.com",
        description="Snapshotalyzer is a tool to manage EC2 instances, volumes, and snapshots",
        license="GPLv3+",
        packages=['shotty'],
        url="https://github.com/pwiddy/snapshotalyzer",
        install_requires=[
            'click',
            'boto3'
        ],
        entry_points='''
            [console_scripts]
            shotty=shotty.shotty:cli
        ''',
)
