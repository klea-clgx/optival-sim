from setuptools import setup, find_packages

setup(
    name='avm_app',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'openpyxl'
    ],
    entry_points={
        'console_scripts': [
            'avm_app = avm_app.main:main'
        ]
    },
)
