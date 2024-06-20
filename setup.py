from setuptools import find_packages, setup

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [
    'girder>=3.2.3',
    'girder-jobs>=3.2.3',
    'girder-client>=3.2.3',
]

setup(
    name='girder_assetstore',
    version='0.1.0',
    description='A Girder plugin to connect remote Girder instances as Assetstores.',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Kitware, Inc.',
    author_email='kitware@kitware.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    install_requires=requirements,
    license='Apache Software License 2.0',
    include_package_data=True,
    keywords='girder-plugin, girder_assetstore',
    packages=find_packages(exclude=['test', 'test.*']),
    url='https://github.com/DigitalSlideArchive/girder_assetstore',
    zip_safe=False,
    entry_points={
        'girder.plugin': [
            'girder_assetstore = girder_assetstore:GirderPlugin'
        ]
    }
)
