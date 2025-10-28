from setuptools import setup, find_packages

setup(
    name='glimpse-rv',
    version='0.2.0',
    description='CLI application for Remote Viewing testing with random target images',
    author='',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'click>=8.1.7',
        'requests>=2.31.0',
        'python-dotenv>=1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'glimpse=glimpse.cli:cli',
        ],
    },
    python_requires='>=3.8',
)
