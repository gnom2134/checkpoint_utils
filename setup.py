from setuptools import setup, find_packages


setup(
    name="checkpoint_utils",
    description="Checkpoint tool for working with unstable cloud services such as Google Colab or Kaggle Notebooks.",
    version="0.1.2",
    license="MIT",
    author="Masalskiy Daniil",
    author_email="gnom21345@gmail.com",
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/gnom2134/checkpoint_utils",
    keywords="checkpoint colab kaggle parameters save",
    install_requires=[],
)
