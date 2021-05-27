from setuptools import setup, find_packages
import program_slicing
import os
from setuptools.command.build_py import build_py
from shutil import copytree

HERE = os.path.abspath(os.path.dirname(__file__))
NAME = "vendor"


class BuildCommand(build_py):
    def run(self):
        build_py.run(self)
        if not self.dry_run:
            target_dir = os.path.join(self.build_lib, NAME)
            copytree(os.path.join(HERE, NAME), target_dir)


setup(
    name='program_slicing',
    version=program_slicing.__version__,
    description=program_slicing.__doc__.strip(),
    long_description='Set of methods for source code decomposition.',
    url='https://github.com/acheshkov/program_slicing',
    download_url='https://github.com/acheshkov/program_slicing',
    author=program_slicing.__author__,
    author_email=['yakimetsku@gmail.com'],
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
    ],
    cmdclass={"build_py": BuildCommand},
)
