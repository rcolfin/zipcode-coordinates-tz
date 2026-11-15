commands
-------------

The CLI is built on `asyncclick <https://pypi.org/project/asyncclick/>`_. Run any command with
``--help`` for the most up-to-date usage.

.. code-block:: text

    $ python -m zipcode_coordinates_tz --help
    Usage: python -m zipcode_coordinates_tz [OPTIONS] COMMAND [ARGS]...

      Entry point for the zipcode-coordinates-tz CLI.

    Options:
      --log-level [critical|error|warning|info|debug|notset]
      --help                          Show this message and exit.

    Commands:
      save

save
~~~~

Queries the USPS and US Census APIs for zip code locale, coordinate, and timezone data, and saves
the result to a CSV, JSON, or Excel file.

.. code-block:: text

    $ python -m zipcode_coordinates_tz save --help
    Usage: python -m zipcode_coordinates_tz save [OPTIONS] FILE

    Options:
      --date [%Y-%m-%d]
      --city CASEFOLD    Filter on City or Town
      --state UPPER      Filter on State
      --zipcode TEXT     Filter on Zipcode
      --coordinates      Flag indicating whether to include coordinates
      --timezones        Flag indicating whether to include timezones
      --fill             Flag indicating whether to fill in missing timezones with
                         a value from their closest location.
      --help             Show this message and exit.
