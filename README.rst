======
BYCEPS
======


BYCEPS is the Bring-Your-Computer Event Processing System.

It is **a tool to prepare and operate a LAN party**, both online on the
Internet and locally as an intranet system, for both organizers and
attendees.

The system incorporates both experience from more than 15 years of
organizing LAN parties as well as concepts and source code developed
for more than a decade.

Parties using BYCEPS:

- Since 2014, BYCEPS is the foundation of the public website and local
  party intranet of the LANresort_ (300+ attendees) event series.
- In 2016, `LANresort Bostalsee`_ was launched on BYCEPS.
- In 2017, NorthCon_ (1,300+ attendees) was relaunched on BYCEPS.


.. _LANresort: https://www.lanresort.de/
.. _LANresort Bostalsee: https://bostalsee.lanresort.de/
.. _NorthCon: https://www.northcon.de/


:Copyright: 2006-2019 Jochen Kupperschmidt
:License: Modified BSD, see LICENSE for details.
:Website: https://byceps.nwsnet.de/


Code Status
===========

|badge_travisci|
|badge_scrutinizer|
|badge-codeclimate|


.. |badge_travisci| image:: https://travis-ci.org/byceps/byceps.svg?branch=master
   :alt: Build Status
   :target: https://travis-ci.org/byceps/byceps

.. |badge_scrutinizer| image:: https://scrutinizer-ci.com/g/byceps/byceps/badges/quality-score.png?b=master
   :alt: Scrutinizer Code Quality
   :target: https://scrutinizer-ci.com/g/byceps/byceps/?branch=master

.. |badge-codeclimate| image:: https://codeclimate.com/github/codeclimate/codeclimate/badges/gpa.svg
   :alt: Code Climate
   :target: https://codeclimate.com/github/byceps/byceps


Installation
============

See ``docs/installation.rst``.


Testing
=======

In the activated virtual environment, install tox_ and pytest_:

.. code:: sh

    (venv)$ pip install -r requirements-test.txt

Have tox run the tests:

.. code:: sh

    (venv)$ tox

If run for the first time, tox will first create virtual environments
for the Python versions specified in `tox.ini`.


.. _tox: http://tox.testrun.org/
.. _pytest: http://pytest.org/


Serving
=======

To spin up a local server (only for development purposes!) on port 5000
with debugging middleware and in-browser code evaluation:

.. code:: sh

    $ BYCEPS_CONFIG=../config/development_admin.py FLASK_ENV=development flask run

In a production environment, it is recommended to have the application
served by uWSGI_ or Gunicorn_.

It is furthermore recommended to run it locally behind nginx_ and have
the latter both serve static files and provide SSL encryption.


.. _uWSGI: http://uwsgi-docs.readthedocs.io/
.. _Gunicorn: http://gunicorn.org/
.. _nginx: http://nginx.org/


Shell
=====

The application shell is an interactive command line that gives access to
BYCEPS' functionality as well as the persisted data.

.. code:: sh

    (venv)$ BYCEPS_CONFIG=../config/development_admin.py FLASK_APP=app.py flask shell

Installation of an extra package makes the shell easier to use due to features
like command history and auto-completion:

.. code:: sh

    (venv)$ pip install flask-shell-ipython
