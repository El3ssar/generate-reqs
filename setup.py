from setuptools import setup, find_packages

setup(
    name='generate-reqs',  # Replace with your package name
    version='0.1.0',
    author='Daniel',  # Replace with your name
    author_email='kemossabee@gmail.com',  # Replace with your email
    description='A utility to generate requirements.txt from a conda environment.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/El3ssar/generate-reqs',  # Replace with the actual repo link
    packages=find_packages(),
    include_package_data=True,
    py_modules=['generate_reqs'],  # This should match the Python script filename
    install_requires=[
        'Click',  # Dependencies for your package
        'pyyaml',
    ],
    entry_points={
        'console_scripts': [
            'generate-reqs = generate_reqs:main',  # Entry point for the CLI tool
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)

