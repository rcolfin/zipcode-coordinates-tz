# zipcode-coordinates-tz

[![CI Build](https://github.com/rcolfin/zipcode-coordinates-tz/actions/workflows/ci.yml/badge.svg)](https://github.com/rcolfin/zipcode-coordinates-tz/actions/workflows/ci.yml)
[![PyPI Version](https://img.shields.io/pypi/v/zipcode-coordinates-tz)](https://pypi.python.org/pypi/zipcode-coordinates-tz)
[![versions](https://img.shields.io/pypi/pyversions/zipcode-coordinates-tz.svg)](ttps://github.com/rcolfin/zipcode-coordinates-tz)

A Python package that enables converting a US Zip Code into a timezone.  This is done through the querying of the USPS API, then joining it with the zipcode-coordinates-tz data from the US Census, and finally taking the coordinates and using `timezonefinder` to determine the timezone.

## Dependencies:
- [Geocoding Services Web Application Programming Interface (API)](https://geocoding.geo.census.gov/geocoder/Geocoding_Services_API.pdf)
- [ZIP Codes by Area and District codes](https://postalpro.usps.com/ZIP_Locale_Detail)
- [timezonefinder](https://timezonefinder.readthedocs.io/en/stable/)

## Development

### Setup Python Environment:

Run [scripts/console.sh](../scripts/console.sh) poetry install

### If you need to relock:

Run [scripts/lock.sh](../scripts/lock.sh)

### Run code

Run [scripts/console.sh](../scripts/console.sh) poetry run jupyter notebook


## API Usage:

```python
from zipcode_coordinates_tz import census, postal, timezone

df_postal_locales = await postal.get_locales()
df_postal_locales = df_postal_locales.loc[df_postal_locales.State == "NJ"]
df_postal_locales = await census.get_coordinates(df_postal_locales)
df_postal_locales = timezone.fill_timezones(df_postal_locales, fill_missing=True)
print(df_postal_locales)
```

As a CLI

```sh
python -m zipcode_coordinates_tz save NJ.json --state NJ --timezones --fill
```

## Installation

To install zipcode-coordinates-tz from PyPI, use the following command:

    $ pip install zipcode-coordinates-tz

You can also clone the repo and run the following command in the project root to install the source code as editable:

    $ pip install -e .

## Documentation
The documentation for `zipcode-coordinates-tz` can be found [here](https://rcolfin.github.io/zipcode-coordinates-tz/) or in the project's docstrings.
