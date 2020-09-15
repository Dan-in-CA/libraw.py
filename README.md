libraw.py
==========
Python bindings using ctypes for [libraw](http://www.libraw.org/).\
Python3 compatible.  

Originally based on the paper [Processing RAW images in Python](https://www.researchgate.net/publication/314239357_Processing_RAW_images_in_Python).\
This version is updated and modified for use on Raspberry Pi and includes a pre-compiled libraw.so.20.0.0 file.\
It is able to open .jpg files containing raw bayer data created with **raspistill -r**.  

Installation
---------
`git clone https://github.com/Dan-in-CA/libraw_py.git`\
`cd libraw_py`\
`pip3 install .`\
(Be sure to include the trailing dot (.)).

Uses
---------
The libraw.py module may be run stand-alone from the libraw_py folder:\
`python3 libraw.py "[/path/to/filename].jpg"`\
This will process the raw bayer data and output a **"[fileneme]. ppm'** file.

When imported into a Python3 program the libraw module can be used to open a Raspi raw .jpg file and the raw data loaded into a numpy array which can then be processed using [numpy](https://numpy.org/), [openCV](https://docs.opencv.org/master/d6/d00/tutorial_py_root.html), [scikit-image](https://scikit-image.org), etc.\
 See files in the examples folder and the code at the and of libraw.py in the `if __name__ == "__main__":` block for help getting started.

Licensing
---------
LGPLv2 (same as libraw)
