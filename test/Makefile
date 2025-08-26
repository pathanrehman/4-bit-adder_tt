# Makefile for cocotb-based testbench

# defaults
SIM ?= icarus
TOPLEVEL_LANG ?= verilog

# Project sources - update this to match your source files
PROJECT_SOURCES = tt_um_4bit_cpu.v

# Normal simulation
ifeq ($(SIM),icarus)
	COMPILE_ARGS += -I.
	VERILOG_SOURCES += $(PWD)/tb.v
	VERILOG_SOURCES += $(addprefix $(PWD)/../src/,$(PROJECT_SOURCES))
else ifeq ($(SIM),verilator)
	COMPILE_ARGS += -I.
	VERILOG_SOURCES += $(PWD)/tb.v
	VERILOG_SOURCES += $(addprefix $(PWD)/../src/,$(PROJECT_SOURCES))
endif

# Gate level simulation
ifneq ($(GATES),)
	COMPILE_ARGS += -DGL_TEST
	COMPILE_ARGS += -DFUNCTIONAL
	COMPILE_ARGS += -DUSE_POWER_PINS
	VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v
	VERILOG_SOURCES += $(PDK_ROOT)/sky130A/libs.ref/sky130_fd_sc_hd/verilog/sky130_fd_sc_hd.v
	
	# Gate level netlist
	VERILOG_SOURCES += gate_level_netlist.v
	VERILOG_SOURCES += $(PWD)/tb.v
endif

# TOPLEVEL is the name of the toplevel module in your Verilog or VHDL file
TOPLEVEL = tb

# MODULE is the basename of the Python test file
MODULE = test

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
