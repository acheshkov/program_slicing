from setuptools import setup, find_packages
import program_slicing

setup(
    name='veniq',
    version=program_slicing.__version__,
    description=program_slicing.__doc__.strip(),
    long_description='Set of methods for source code decomposition.',
    url='https://github.com/acheshkov/program_slicing',
    download_url='https://github.com/acheshkov/program_slicing',
    author=program_slicing.__author__,
    author_email=['katya.garmash@gmail.com'],
    license=program_slicing.__licence__,
    packages=find_packages(),
    extras_require={},
    install_requires=open('requirements.txt', 'r').readlines(),
    tests_require=open('requirements.txt', 'r').readlines(),
    classifiers=[
        'Programming Language :: Python',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Topic :: Utilities'
    ]
)
