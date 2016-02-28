.. image:: https://img.shields.io/travis/ExCiteS/geokey-webresources/master.svg
    :alt: Travis CI Build Status
    :target: https://travis-ci.org/ExCiteS/geokey-webresources

.. image:: https://img.shields.io/coveralls/ExCiteS/geokey-webresources/master.svg
    :alt: Coveralls Test Coverage
    :target: https://coveralls.io/r/ExCiteS/geokey-webresources

geokey-webresources
===================

Extend GeoKey projects by adding web resources: GeoJSON, KML or GPX.

Install
-------

geokey-webresources requires:

- Python version 2.7
- GeoKey version 0.9 or greater

Install the geokey-webresources from PyPI:

.. code-block:: console

    pip install geokey-webresources

Or from cloned repository:

.. code-block:: console

    cd geokey-webresources
    pip install -e .

Add the package to installed apps:

.. code-block:: console

    INSTALLED_APPS += (
        ...
        'geokey_webresources',
    )

Migrate the models into the database:

.. code-block:: console

    python manage.py migrate geokey_webresources

You're now ready to go!

Update
------

Update the geokey-webresources from PyPI:

.. code-block:: console

    pip install -U geokey-webresources

Migrate the new models into the database:

.. code-block:: console

    python manage.py migrate geokey_webresources

Test
----

Run tests:

.. code-block:: console

    python manage.py test geokey_webresources

Check code coverage:

.. code-block:: console

    pip install coverage
    coverage run --source=geokey_webresources manage.py test geokey_webresources
    coverage report -m --omit=*/tests/*,*/migrations/*

Public API
----------

**Get all web resources of a project**

.. code-block:: console

    GET /api/projects/:project_id/webresources/

Response:

.. code-block:: console

    [
        {
            "id": 46,
            "status": "active",
            "name": "Public Houses",
            "description": "All public houses in London.",
            "data_format": "KML",
            "url": "http://london.co.uk/public-houses.kml",
            "colour": "#000000",
            "symbol": null
        }
    ]
