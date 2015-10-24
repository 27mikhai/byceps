Installation
============


Requirements
------------

* Python_ 3.4.2 or higher
* PostgreSQL_ 9.4 or higher
* Redis_ 2.8 or higher

.. _Python: http://www.python.org/
.. _PostgreSQL: http://www.postgresql.org/
.. _Redis: http://redis.io/


Debian
------

`Debian Linux`_ is the recommended operating system to run BYCEPS on.

The following packages are available in the Debian repository as part of
the "Jessie" release:

* ``postgresql-9.4``
* ``postgresql-contrib-9.4``
* ``python3.4``
* ``python3.4-dev``
* ``python3.4-venv``
* ``redis-server``

Additional required packages should be suggested for installation by
the package manager.

Update the package list and install the necessary packages (as the root
user):

.. code-block:: sh

    # aptitude update
    # aptitude install postgresql-9.4 postgresql-contrib-9.4 python3.4 python3.4-dev python3.4-venv redis-server

Refer to the Debian documentation for further details.

.. _Debian Linux: https://www.debian.org/


BYCEPS
------

Grab a copy of BYCEPS itself. For now, the best way probably is to
clone the Git repository from GitHub:

.. code-block:: sh

    $ git clone https://github.com/homeworkprod/byceps.git

A new directory, `byceps`, should have been created.

This way, it should be easy to pull in future updates to BYCEPS using
Git. (And there currently are no release tarballs anyway.)


Virtual Environment
-------------------

The installation should happen in an isolated Python_ environment just
for BYCEPS so that its requirements don't clash with different versions
of the same libraries somewhere else in the system.

Python_ already comes with the necessary tools, namely virtualenv_ and
pip_.

.. _virtualenv: http://www.virtualenv.org/
.. _pip: http://www.pip-installer.org/

It is recommended to do create the virtual environment inside of
BYCEPS's `webapp` path, so go there first:

.. code-block:: sh

    $ cd byceps/webapp

Then create a virtual environment (named "venv"):

.. code-block:: sh

    $ pyvenv venv

Activate it (but don't change into its path):

.. code-block:: sh

    $ . ./venv/bin/activate

Whenever you want to activate the virtual environment, make sure to do
that either in the path in which you have created it using the above
command, or adjust the path to reference it relatively (e.g.
`../../venv/bin/activate`) or absolutely (e.g.
`/var/www/byceps/webapp/venv/bin/activate`).

Make sure the correct version of Python is used:

.. code-block:: sh

    (venv)$ python -V
    Python 3.4.2

It's probably a good idea to update pip_ to the current version:

.. code-block:: sh

    (venv)$ pip install --upgrade pip

Install the Python depdendencies via pip_:

.. code-block:: sh

    (venv)$ pip install -r requirements.txt


Database
--------

There should already be a system user, likely 'postgres'.

Become root:

.. code-block:: sh

    $ su
    <enter root password>

Switch to the 'postgres' user:

.. code-block:: sh

    # su postgres

Create a database user named 'byceps':

.. code-block:: sh

    postgres@host$ createuser --echo --pwprompt byceps

You should be prompted to enter a password. Do that.

Create a schema, also named 'byceps':

.. code-block:: sh

    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps byceps

To run the tests, a dedicated user and database have to be created:

.. code-block:: sh

    postgres@host$ createuser --echo --pwprompt byceps_test
    postgres@host$ createdb --encoding=UTF8 --template=template0 --owner byceps_test byceps_test

Connect to the database:

.. code-block:: sh

    $ psql

Load the 'pgcrypto' extension:

.. code-block:: psql

    postgres=# CREATE EXTENSION pgcrypto;

Ensure that the function 'gen_random_uuid()' is available now:

.. code-block:: psql

    postgres=# select gen_random_uuid();

Expected result (the actual UUID hopefully is different!):

.. code-block:: psql

               gen_random_uuid
    --------------------------------------
     b30bd643-d592-44e2-a256-0e0e167ac762
    (1 row)
