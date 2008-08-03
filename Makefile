#
# Makefile for AppleScriptLexer
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Combines scripts for common tasks.
#
# :copyright: 2008 by Takanori Ishikawa.
# :license: MIT, see LICENSE for more details.
#

PYTHON ?= python

.PHONY: all clean test

all: test
clean:
	
test:
	@$(PYTHON) tests/runtests.py
