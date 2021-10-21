Databases
=========

Infrastructure
--------------

To manage the runcards we use SQLAlchemy_ on top of sqlite_ that provides a fully fledge
database system. Upon creating the :class:`~banana.benchmark.runner.BenchmarkRunner` instance
a database connection is established and in the following used to retrieve or save data.

.. _SQLAlchemy: https://www.sqlalchemy.org/

.. _sqlite: https://www.sqlite.org/index.html


Configuration
-------------

Each subproject has to provide a file ``banana.yaml`` that provides the actual configuration:

- ``database_path`` file path to the database (e.g. ``data/benchmark.db``)


Git LFS
-------

In order to keep the databases in the projects we decided to use git-lfs_
(``git`` Large File Storage), a tool integrating with ``git`` and designed
specifically to manage large files inside a ``git`` repo.

.. _git-lfs: https://git-lfs.github.com
