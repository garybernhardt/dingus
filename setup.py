from setuptools import setup

setup(name='dingus',
      version='0.3.1',
      description='A record-then-assert mocking library',
      long_description=file('README.rst').read(),
      author='Gary Bernhardt',
      author_email='gary.bernhardt@gmail.com',
      py_modules=['dingus'],
      license='MIT',
      url='https://github.com/garybernhardt/dingus',
      keywords='testing test mocking mock double stub fake record assert',
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Testing",
                   ],
     )

