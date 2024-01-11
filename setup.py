from setuptools import setup, find_packages

setup(
    name='gnps_postprocessing',
    version='0.1.1',
    packages=find_packages(),
    description='GNPS Postprocessing Scripts',
    url='https://github.com/lfnothias/gnps_postprocessing',
    author='Louis Felix Nothias',
    author_email='louisfelix.nothias@gmail.com',
    license='MIT',
    install_requires=[
        'numpy',
        'pandas',
        'rdkit',
        'molvs'
    ],
    # Add additional metadata if necessary
)
