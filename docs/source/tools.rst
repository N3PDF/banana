Tools
=====

Extra tools shipped as |CLI| with banana.

genpdf
-----------

We provide also a console script called ``genpdf`` that is able to generate and install a custom |PDF|
set in the `lhapdf` format. In particular, the command ``genpdf install [NAME]`` simply install the |PDF| called [NAME]
in the lhapdf folder and the ``genpdf generate [NAME]`` command generates the custom |PDF| and saves it as [NAME] in
the current directory. Notice that the argument [NAME] is the only mandatory one.

The custom |PDF| can be generated in three different ways which are accessible trough the option ``-p [PARENT]``
(the complete spelling is ``genpdf generate [NAME] -p [PARENT]``):

  1. If [PARENT] is the name of an available |PDF|, it is used as parent |PDF| and thus copied to generate the new custom PDF.
  2. If [PARENT] is "toylh" or "toy", the **toy** |PDF| is used as parent
  3. If the option ``-p [PARENT]`` is not used, the |PDF| is generated using **x(1-x)** for all the flavors

Trough the use of the argument [LABEL] (``genpdf generate [NAME] [LABEL] [OPTIONS]``) it is also possible to specify a set of flavors
(expressed in |pid| basis) or a set of
**evolution** basis components on which filtering the custom |PDF|. In this way the specified set is kept in the final |PDF|,
while the rest is discarded. Leaving the argument [LABEL] empty discards all the flavors.

In the case of custom |PDF| generated starting from a parent |PDF|, it is possible to generate all the members trough the
flag ``-m``. If this flag is not used, only the *zero* member is generated (together with the *info* file of course). Using
the flag ``-m`` when the custom |PDF| is generated either using the **toy** |PDF| or the **x(1-x)** function, has no effects.

In order to automatically install the custom |PDF| in the lhapdf folder at generation time (so without using ``genpdf install [NAME]``
after the generation), it is possible to use the ``-i`` flag.

Examples
""""""""


We also provide an API with some additional features and possibilities such as generating a |PDF| with a custom function
for every |pid| (trough a ``dict`` structure) and filtering custom combination of flavors. Some details on how this |API|
works can be found :mod:`here <banana.data.genpdf>`
