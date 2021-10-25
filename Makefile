###############################################################################
MK_INFO := https://pypi.org/project/vmklib
ifeq (,$(shell which mk))
$(warning "No 'mk' in $(PATH), install 'vmklib' with 'pip' ($(MK_INFO))")
endif
ifndef MK_AUTO
$(error target this Makefile with 'mk', not '$(MAKE)' ($(MK_INFO)))
endif
###############################################################################

.PHONY: all lint

.DEFAULT_GOAL  := all

LINT_TARGETS := $(YAML_PREFIX)lint-color \
                $(YAML_PREFIX)lint-includes \
                $(YAML_PREFIX)lint-schema_types \
                $(YAML_PREFIX)lint-schemas \
                $(YAML_PREFIX)lint-variables

lint: $(LINT_TARGETS)
	-yamllint $($(PROJ)_DIR)/configs
	-yamllint $($(PROJ)_DIR)/release

all: lint
