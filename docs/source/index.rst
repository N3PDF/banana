Bello banana!
=============

.. image:: ../_assets/logo.png
  :width: 450
  :align: center
  :alt: banana logo

Banana provides the benchmarking infrastructure for |eko| and |yadism|. In order to ensure the
correct implementation we constantly benchmark our codes against other external available
codes. We aim at a seamless and easy interface that can be run quickly and fully adaptive to
the feature under investigation. As it turns out, the framework has become an integral part
of our development process and is hence under constant development. Since we want to
serve equally |eko| and |yadism| but they have different application we only implement the
shared logic here and leave it to the respective benchmarking packages, ``ekomark`` and ``yadmark``,
to implement the remaining logic.

The benchmarking procedure can be separated into several steps:

1. :doc:`Preparation of the setup <benchmarks/setup>`
2. :doc:`Running our own implementation and the external benchmark program <benchmarks/running>`
3. :doc:`benchmarks/navigator`


In addition we provide a list of tools: see :doc:`tools/overview`.

.. toctree::
   :maxdepth: 2
   :caption: Benchmarks:
   :hidden:

   benchmarks/overview
   benchmarks/db
   benchmarks/setup
   benchmarks/running
   benchmarks/navigator


.. toctree::
   :maxdepth: 2
   :caption: Tools:
   :hidden:

   tools/overview
   tools/toy
   tools/genpdf

.. toctree::
   :maxdepth: 2
   :caption: Internals:
   :hidden:

   API <modules/banana/banana>
   TODOs <development/code_todos>



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
