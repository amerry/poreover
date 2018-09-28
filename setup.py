from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
import numpy as np

ext_modules = [
Extension("decoding.decoding_cpp", sources=["decoding/decoding_cpp.pyx"], include_dirs=[np.get_include()], language='c++',extra_link_args=['-std=c++11','-stdlib=libc++'], extra_compile_args=['-std=c++11','-stdlib=libc++']),
Extension("decoding.decoding_cy", sources=["decoding/decoding_cy.pyx"], include_dirs=[np.get_include()], language='c++',extra_link_args=['-std=c++11','-stdlib=libc++'], extra_compile_args=['-std=c++11','-stdlib=libc++']),
Extension("align.align", sources=["align/align.pyx"], include_dirs=[np.get_include()])
]

setup(
    ext_modules = cythonize(ext_modules, annotate=True)
)
