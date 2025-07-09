from setuptools import setup

setup(
    name='todo-client',
    version='0.1',
    packages=['cli'],
    entry_points={
        'console_scripts': [
            'todo=cli.client:main',
        ],
    },
    install_requires=[
        'requests',
        'rich',
        'typer'
    ],
)