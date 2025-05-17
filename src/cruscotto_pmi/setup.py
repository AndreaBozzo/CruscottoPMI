from setuptools import setup, find_packages

setup(
    name='cruscotto_pmi',
    version='0.5.0',
    description='Cruscotto Finanziario per PMI - Analisi KPI, bilanci e reportistica',
    author='Andrea Bozzo',
    author_email='andreabozzo92@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pandas',
        'streamlit',
        'matplotlib',
        'reportlab'
    ],
    python_requires='>=3.8',
)