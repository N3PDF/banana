# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

BANANADIR = ../src/banana
BANANAOUT = $(SOURCEDIR)/modules/banana

TODOOUTFILE = ./source/development/code_todos.rst

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile cleanall todos clean-todos

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile todos
	sphinx-apidoc --module-first -o "$(BANANAOUT)" "$(BANANADIR)"
	@rm -f $(BANANAOUT)/modules.rst
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# # sphinx
# html: todos
# 	sphinx-apidoc --module-first -o "$(EKOOUT)" "$(EKODIR)"
# 	@rm -f $(EKOOUT)/modules.rst
# 	sphinx-apidoc --module-first -o "$(EKOMARKOUT)" "$(EKOMARKDIR)"
# 	@rm -f $(EKOMARKOUT)/modules.rst
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

# view: html
# 	$(BROWSER) $(BUILDDIR)/html/index.html

# clean:
# 	rm -rf build
# 	rm -rf _build

cleanall: clean clean-todos
	rm -rf $(SOURCEDIR)/modules

# TODOs
todos:
	mkdir -p source/development && touch ${TODOOUTFILE}
	python generate_code_todos.py "$(BANANADIR)" "$(TODOOUTFILE)"

clean-todos:
	rm "$(TODOOUTFILE)"
