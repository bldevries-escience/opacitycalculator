from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='opticalconstants',
      version='0.1',
      description=    'Database of optical constants (refractive indices) \
                  of minerals',
      long_description=readme(  ),
      # classifiers=[
      #   'Development Status :: under developement',
      #   'License :: nothing yet',
      #   'Programming Language :: Python :: 2.7',
      #   'Topic :: astronomical :: calculations :: minerals',
      # ],
      keywords='',
      url='',
      author='B.L. de Vries',
      author_email='',
      license='',
      packages=['opticalconstants'],
      package_data={
          'opticalconstants': ['SQLITE_NK_DATABASE.db'],
      },
      # install_requires=[
      #     'markdown',
      # ],
      # test_suite='nose.collector',
      # tests_require=['nose', 'nose-cover3'],
      # entry_points={
      #     'console_scripts': ['funniest-joke=funniest.command_line:main'],
      # },
      include_package_data=True,
      zip_safe=True)
