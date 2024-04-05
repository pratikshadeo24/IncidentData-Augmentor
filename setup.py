from setuptools import setup, find_packages

setup(
    name='assignment2',
    version='1.0',
    author='Pratiksha Deodhar',
    author_email='pdeodhar@ufl.edu',
    url="https://github.com/pratikshadeo24/cis6930sp24-assignment2",
    packages=find_packages(exclude=('tests', 'docs', 'resources')),
    install_requires=[
        'pypdf==4.0.0'
    ],
    tests_require=[
        'pytest==7.4.4',
        'pytest-mock==3.12.0',
    ]
)
