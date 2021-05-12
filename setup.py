#!/usr/bin/env python

#                         PyOnlineSVR
#               Copyright 2021 - Sebastian Schmidl
#
# This file is part of PyOnlineSVR.
#
# PyOnlineSVR is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyOnlineSVR is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with PyOnlineSVR. If not, see
# <https://www.gnu.org/licenses/gpl-3.0.html>.


# This future is needed to print Python2 EOL message
from __future__ import print_function
from distutils.errors import DistutilsExecError
import sys
if sys.version_info < (3,):
    print("Python 2 has reached end-of-life and is not supported by pyonlinesvr.")
    sys.exit(-1)

import platform
python_min_version = (3, 6, 2)
python_min_version_str = ".".join(map(str, python_min_version))
if sys.version_info < python_min_version:
    print(f"You are using Python {platform.python_version()}. Python >={python_min_version_str} is required.")
    sys.exit(-1)


import os
from pathlib import Path
import shutil
import glob
from setuptools import setup, Extension, Command, find_packages
from setuptools.command.build_py import build_py as _build_py


cwd = Path(os.path.dirname(__file__)).absolute()
lib_path = Path("pyonlinesvr") / "lib"
readme = (cwd / "README.md").read_text(encoding="UTF-8")


# get __version__ from _version.py
with open(Path("pyonlinesvr") / "_version.py") as f:
    exec(f.read())


onlinesvr_module = Extension("pyonlinesvr.lib._onlinesvr",
    sources=list(map(lambda x: str(lib_path / x), [
        "CrossValidation.cpp", "File.cpp", "Forget.cpp", "Kernel.cpp",
        "OnlineSVR.cpp", "Show.cpp", "Stabilize.cpp", "Train.cpp",
        "Variations.cpp",
        #"OnlineSVR_wrap.cxx",
        "OnlineSVR.i",
    ])),
    depends=list(map(lambda x: str(lib_path / x), ["OnlineSVR.h", "Matrix.h", "Vector.h"])),
    swig_opts=["-c++", "-py3"],
)


class build_py(_build_py):
    def run(self):
        # run build_ext before build_py to generate the swig python files beforehand
        self.run_command("build_ext")
        return super().run()


class clean(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        files = ["pyonlinesvr/lib/onlinesvr.py", "pyonlinesvr/lib/OnlineSVR_wrap.c*", "*/*.so", "*/**/*.so"]
        dirs = ["build", "dist", "*.egg-info", "*/**/__pycache__"]
        for d in dirs:
            for filename in glob.glob(d):
                shutil.rmtree(filename, ignore_errors=True)

        for f in files:
            for filename in glob.glob(f):
                try:
                    os.remove(filename)
                except OSError:
                    pass


setup(name = "PyOnlineSVR",
      version = __version__,  # noqa
      author = "Sebastian Schmidl",
      author_email = "info@sebastianschmidl.de",
      description = "Python-Wrapper for Francesco Parrella's OnlineSVR C++ implementation.",
      long_description = readme,
      long_description_content_type = "text/markdown",
      url = "tbd",
      license = "GPLv3",
      packages = find_packages(),
      package_data={"pyonlinesvr": ["py.typed"]},
      ext_modules = [onlinesvr_module],
      cmdclass = {
          "build_py": build_py,
        #   "build_ext": build_ext,
          "clean": clean,
      },
      zip_safe = False,
      python_requires = f">={python_min_version_str}",
)
