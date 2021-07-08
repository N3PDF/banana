Preparation of the Setup
========================

Runcards
--------

Since both |eko| and |yadism| work with runcards, the outcome *shoud* be fully specified by
specifing the respective runcards. Both programs consume as a first dependency a **unique** theory
runcard (Note that also this is subject to be changed in future versions), that mainly
defines the physical setup, e.g. reference value of the strong coupling
:math:`\alpha_s(Q_{ref})`. In addition, they consume a second runcard that is one of the main
**differences** between the two codes: ``eko`` consumes an operator runcard, that e.g. defines the
target evolution scales, and ``yadism`` consumes a observable runcard, that e.g. defines the
kinematic points of the structure functions. Henceforth, we will refer to the respective cards
uniquely as **[o-card]** as we can actually abstract some logic here in ``banana``.


Specifing the Desired Setup
---------------------------

Each table comes with a default runcard from which one can extend. Hence, one needs to specify
*only* the key-value pairs that one wants to change. The typical benchmark run will look like
this: :py:`runner.run(theory_updates,ocard_updates,pdfs)`


I/O databases' structure
------------------------

Input database will consist of the tables:

- **theories**: each entry of this table will represent a *physical theory*,
  i.e. it will specify a set of parameters involved in QFT computations; the
  following entries are expected:

  - *PTO*: perturbative order
  - *XIF*, *XIR*:
  - *mc*. *Qmc*, *mb*, *Qmb*, *mt*, *Qmt*:
  - etc.

- **observables**: each entry of this table will represent a *set of DIS
  observables*, and also some parameters involved in the computation of the
  observables themselves; the following entries are expected:

  - *xgrid*: the grid on which the interpolation is evaluated
  - etc.

- **cache**: to keep a cache of the external output. Since it is stable
  there is no need of rerunning it multiple times to compute the same
  observables (while rerunning is needed for *yadism* during its development,
  of course...)

- **logs**: keep a log of the comparisons between *yadism* and the external program
