#
# Makefile
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# Combines scripts for common tasks.
#
# :copyright: 2008 by Takanori Ishikawa.
# :license: MIT, see LICENSE for more details.
#

PYTHON ?= python

.PHONY: all clean profiler

CFLAGS += -O2 -Wall
LDFLAGS += -framework CoreFoundation

all: core_foundation_parser profiler
clean:
	rm -f *.pyc
	rm -f core_foundation_parser
	rm -rf core_foundation_parser.dSYM
profiler:
	@$(PYTHON) profiler.py
