zipcode-coordinates-tz
=====

Welcome to the zipcode-coordinates-tz documentation! Here you will find links to the core modules and examples of how to use each.


A Python package that enables converting a US Zip Code into a timezone.

This is done through the querying of the USPS API, then joining it with the GeoLocation data from the US Census,
and finally taking the coordinates and using `timezonefinder <https://pypi.org/project/timezonefinder/>`_ to determine the timezone.

Modules
-------

If there is functionality that is missing or an error in the docs, please open a new issue `here <https://github
.com/rcolfin/zipcode-coordinates-tz/issues>`_.

.. toctree::
    :maxdepth: 1

    zipcode_coordinates_tz/cenus
    zipcode_coordinates_tz/models
    zipcode_coordinates_tz/postal
    zipcode_coordinates_tz/timezone

Install
-------

To install zipcode-coordinates-tz from PyPI, use the following command:

    $ pip install zipcode-coordinates-tz

You can also clone the repo and run the following command in the project root to install the source code as editable:

    $ pip install -e .

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Examples
-----------------

The following example will query for all the US Locales,
filter by the NJ state.  Enrich the Pandas DataFrame with
the Longitude and Latitude Coordinates, then add a TZ
column for the timezones.

.. code-block:: Python

    from zipcode_coordinates_tz import census, postal, timezone

    df_postal_locales = await postal.get_locales()
    df_postal_locales = df_postal_locales.loc[df_postal_locales.State == "NJ"]
    df_postal_locales = await census.get_coordinates(df_postal_locales)
    df_postal_locales = timezone.fill_timezones(df_postal_locales)
    print(df_postal_locales)

This example makes the same query as above, but saves it to a JSON file.

.. code-block:: bash

    python -m zipcode_coordinates_tz save NJ.json --state NJ --timezones