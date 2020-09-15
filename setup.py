from setuptools import setup, find_packages

setup(
    name="libraw_py",
    version="2.0",
    description="python bindings using ctypes for LibRaw",
    url="https://github.com/Dan-in-CA/libraw_py",
    author="Pavel Rojtberg, Dan Kimberling",
    license="LGPLv2",
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    platform="Raspberry Pi",
    py_modules=["libraw"],
    data_files=[('lib/', ['libraw.so.20.0.0'])]
)
