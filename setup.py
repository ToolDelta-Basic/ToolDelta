import setuptools

with open('requirements.txt', 'r+', encoding='utf-8') as file:
    dependences = file.read().strip().split('\n')

with open('README.md', 'r+', encoding='utf-8') as file:
    long_description = file.read()

with open('version', 'r+', encoding='utf-8') as file:
    version = file.read().strip()

setuptools.setup(
    name='Tooldelta',
    version=version,
    author='SuperScript-PRC',
    description='Plugin Loader for NeteaseRentalServer on Panel',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/SuperScript-PRC/ToolDelta',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=dependences,
    python_requires='>=3.11',
)