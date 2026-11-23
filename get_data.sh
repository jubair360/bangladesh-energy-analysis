#!/usr/bin/env bash
# Download the two Our World in Data files used by this analysis.
set -euo pipefail
mkdir -p data
curl -sSL -o data/owid-energy-data.csv https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv
curl -sSL -o data/owid-co2-data.csv     https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-data.csv
echo "Downloaded to data/"
