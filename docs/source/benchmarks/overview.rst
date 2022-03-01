Overview
========


.. _configs:

Configuration
-------------

In order to provide relevant configurations (e.g. the location of the database),
a dedicated file might be provided, and it is read by `banana` during each run.

There are multiple ways to specify the location of this file, whose default name
is ``banana.yaml``. Any of the following will work:

1. pointing out the full path the file (in this case the
   default name is ignored)
2. or its parent folder
3. placing it into the current folder
4. or the home folder
5. or the user configuration folder (e.g. ``$XDG_CONFIG_HOME`` on Linux)
6. or the system configuration folder

Even though all the alternatives are checked in the order given, only the first
3 are recommended.

An example of a valid ``banana.yaml`` file is the following:

.. code-block:: yaml

     # the base path for all the others in the `path` section
     # if relative, is considered to be relative to the parent folder of this file
     root: benchmarks/
     # all relevant paths are in this section
     paths:
        database: data/benchmarks.db

     # input related configurations
     input:
         tables:
           - theories
           # the name of the following table is specific to `yadism`
           - observables

     # output related configurations
     ouptut:
         tables:
           - cache
