Introduction
############

This is an open source python library to read and write CZML_ files for Cesium_, the WebGL Earth modeling engine.

.. _CZML: https://github.com/AnalyticalGraphicsInc/cesium/wiki/CZML-Guide
.. _Cesium: http://cesiumjs.org/

Requirements
------------

* pygeoif: https://github.com/cleder/pygeoif
* pytz: https://pypi.python.org/pypi/pytz

Tests
-----

To run the tests (in the czml directory)::

    > python setup.py test

czml is continually tested with *Travis CI*

.. image:: https://api.travis-ci.org/cleder/czml.png
    :target: https://travis-ci.org/cleder/czml

.. image:: https://coveralls.io/repos/cleder/czml/badge.png?branch=master
    :target: https://coveralls.io/r/cleder/czml?branch=master

Usage and Examples
------------------

The general approach to writing CZML with this python library is to define a document object, define packets and append them to the document, and then write the document to a file using the `data()` method passed to `json.dump()`.

:: code: python

    # Import the library
    from czml import czml

    # Initialize a document
    doc = czml.czml()

    # Create and append the document packet
    packet1 = czml.CZMLPacket(id='document',version='1.0')
    doc.packets.append(packet1)
    
    # Create and append a billboard packet
    packet2 = czml.CZMLPacket(id='billboard')
    bb = czml.Billboard(scale=0.7, show=True)
    bb.image = 'http://localhost/img.png'
    bb.color = {'rgba': [0, 255, 127, 55]}
    packet2.billboard = bb
    doc.packets.append(packet2)
    
    # Write the CZML document to a file
    filename = "example.czml"
    with open(filename, 'w') as file:
        json.dump(doc.data(), file)

Supported CZML Components
-------------------------

The components in this library are developed to follow the `CZML Content documentation`_. Supported components and subcomponents are listed in `docs/COMPONENTS.md`_.

.. _CZML Content documentation: https://github.com/AnalyticalGraphicsInc/cesium/wiki/CZML-Content
.. _docs/COMPONENTS.md: https://github.com/cleder/czml/docs/COMPONENTS.md
