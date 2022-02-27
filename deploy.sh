#!/bin/sh
poetry export -f requirements.txt --output requirements.txt --without-hashes
sed -i "/numpy/d" requirements.txt
sed -i "/scipy/d" requirements.txt
poetry run chalice deploy --profile $profile
rm requirements.txt
