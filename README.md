# zipcode-coordinates-tz

[![CI Build](https://github.com/rcolfin/geolocation/actions/workflows/ci.yml/badge.svg)](https://github.com/rcolfin/geolocation/actions/workflows/ci.yml)

A Python package that enables converting a US Zip Code into a timezone.  This is done through the querying of the USPS API, then joining it with the GeoLocation data from the US Census, and finally taking the coordinates and using `timezonefinder` to determine the timezone.

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
df_postal_locales = timezone.fill_timezones(df_postal_locales)
print(df_postal_locales)
```

As a CLI

```sh
 python -m zipcode_coordinates_tz save NJ.json --state NJ --timezones
 ```

## Documentation
The documentation for pymkv can be found [here](https://rcolfin.github.io/geolocation/) or in the project's docstrings.
