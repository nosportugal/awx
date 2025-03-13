#!/bin/bash

act \
    --workflows .github/workflows/devel_images.yml \
    --artifact-server-path $PWD/.artifacts \
    --env-file  env/env \
    --var-file  env/vars \
    --secret-file env/secrets \
    --input-file env/input

