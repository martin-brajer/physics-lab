import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="physicslab",
    version="0.1.1",
    author="Martin Brajer",
    author_email="martin.brajer@seznam.cz",
    description="Physics experiments evaluation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/martin-brajer/physics-lab",
    packages=setuptools.find_packages(),
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
    ],
    keywords='physics',
    python_requires='>=3.6',
    install_requires=[
        'numpy',
        'scipy',
    ],
)
