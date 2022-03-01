Navigator
=========

Having a database of inputs and outputs logs is very useful, in order to
retrieve past runs, compare differences in inputs, and tracking the results of
any investigation in general.

While this is conceptually great, in practice, retrieving and inspecting results
from the database manually is a pain, since a large overhead of database
operations is needed over and over.

For this reason, a **navigator** is provided, that makes much simpler and more
useful to inspect the content of the database itself.

The navigator is designed to be maximally useful when used in interactive mode,
and so trade-offs are considered with this usage in mind.
For example, instead of preserving name scopes and avoid dangerous clashes, the
default CLI entry point exports a lot of global names, together with brief
(and otherwise meaningless) aliases.

Core concepts
-------------

The main part of the navigator consists in tables management. In general, the
following tables are supposed to be present:

1. `Theory` table, containing the dump of used theory runcards used in
   benchmarks
2. `Ocard` table, containing the program specific runcards
3. `Cache` table, in which the results collected from external (and usually
   non-python) programs are stored; since these are not the developed programs,
   their results are supposed to be stable (for an identical input), and so they
   are reused over and over
4. `Logs` table, where the resulting comparisons are all logged, for later
   inspection

Each record of each table is identified by a unique identifier (``uid``), and it
has an associated ``hash``, that corresponds to its content, and allows for
quick comparison (useful to find out what is changed and what not).

.. _row-id:

Row Identifiers
~~~~~~~~~~~~~~~

In general, any record can be accessed through the table it belongs plus one of
the following properties:

- its ``uid``
- a partial ``hash``, starting from the beginning and long enough to uniquely
  point to it (``git`` -like way)
- its position from the end of the table (so the last element inserted
  corresponds to ``-1``, and the previous one to ``-2``)

Configurations
~~~~~~~~~~~~~~

In order to locate the database, and to provide useful information (e.g. on the
tables) the same :ref:`configuration file<configs>` used for benchmarks is also
read by the navigator.

Frequently used tools
---------------------

In order to retrieve element from a given table use::

  g(table, id)

``table`` is a table identifier, that is any long enough string to describe the
name of the tale (more or less like ``hash``, but usually is only needed a
unique letter), and ``id`` is a :ref:`row identifier <row-id>`.

To retrieve the list of elements in a table run::

  ls(table)

Instead of printing, this function is returning a :class:`pandas.DataFrame`,
containing the one row per record in the table, containing the main
information on the record.
This always includes the ``uid``, the ``hash``, and the creation time of the
record, as a difference in words from current time (it is mainly used as a
reference for the person that is manually inspecting the database).
