# Ajenti plugin for Threema

This plugin connects to your threema work account in order to facilitate the management of your users.

## Develop this plugin

You need to have docker installed.

Build the docker image with

```
pushd docker
./build_docker_image.sh
popd
```

Then generate some dummy data with

```
python3 generate_dummy_data.py
```

Move the file `threema.yml.template` to `threema.yml` and insert your API keys.

Run the docker image with

```
./run_dockerized.sh
```

and visit the Ajenti app on http://localhost:8000
