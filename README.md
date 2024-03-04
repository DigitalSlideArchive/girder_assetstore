# girder_assetstore

A Girder plugin that allows for other Girder instances to be accessed as Assetstores.

## Build Instructions

### Local
1. Create/activate a virtualenv: ``python -m venv .venv && source .venv/bin/activate``
2. Install the package in editable mode: ``pip install -e .``
3. Build the package: ``girder build``
   - For development, rebuild client JS with ``girder build --watch-plugin girder_assetstore``
5. Launch a Mongo server: ``mongod``
6. Launch a Girder server: ``girder serve``
7. Visit the the Girder instance http://localhost:8080

### DSA
Alternatively, using [digital slide archive](https://github.com/DigitalSlideArchive/digital_slide_archive/tree/master/devops/dsa):

1. Add mount for ``girder_assetstore`` in the ``docker-compose.yaml`` file:
```yaml
girder:
  volumes:
   # ensure this local path is correct (relative to docker-compose.yaml)
   - ../../../girder_assetstore:/opt/girder_assetstore
```
2. Add editable pip install and client rebuild in ``provision.yaml``:
```yaml
pip:
 - -e /opt/girder_assetstore
shell:
 - timeout 10 girder build --watch-plugin girder_assetstore
```

## Usage

- TODO
