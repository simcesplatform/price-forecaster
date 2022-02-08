# Price-Forecaster-Component

A simulation platform component used to simulate price forecaster whose published states are determined by a file containing a time series of attribute values for each epoch.

## Requirements

- python 3.7
- pip for installing requirements

Install requirements:

```bash
# optional create a virtual environment:
python3 -m venv .env
# activate it
. .env/bin/activate # *nix
.env\scripts\activate # windows.
# install required packages
pip install -r requirements.txt
```

## Usage

The component is based on the AbstractSimulationCompoment class from the [simulation-tools](https://github.com/simcesplatform/simulation-tools)
 repository. It is configured via environment variables which include common variables for all AbstractSimulationComponent subclasses such as rabbitmq connection and component name. Environment variables specific to this component are listed below:

- PRICE_FORECASTER_STATE_CSV_FILE (required): Location of the csv file which contains the price information used in the simulation for each epoch. Relative file paths are in relation to the current working directory. 
- PRICE_FORECASTER_STATE_CSV_DELIMITER (optional, default ,): Delimiter used in the csv file.

When using a CSV file as price state source the file should contain at least the following columns: MarketId, UnitOfMeasure, Time1, Price1.

The component can be started with:

    python -m PriceForecaster

It can be also used with docker via the included dockerfile.