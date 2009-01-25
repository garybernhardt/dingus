from setuptools import setup, find_packages

setup(name='dingus',
      version='0.1',
      description='A record-then-assert mocking library',
      author='Gary Bernhardt',
      author_email='gary.bernhardt@gmail.com',
      packages=find_packages(),
      license='MIT',
      keywords='testing test mocking mock double stub fake',
      classifiers=["Development Status :: 2 - Pre-Alpha",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Testing",
                   ],
     )
