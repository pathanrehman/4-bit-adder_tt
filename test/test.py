import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles
from cocotb.types import LogicArray

# CPU Instruction opcodes
NOP   = 0b0000
LOAD  = 0b0001
ADD   = 0b0010
SUB   = 0b0011
AND   = 0b0100
OR    = 0b0101
XOR   = 0b0110
SHL   = 0b0111
SHR   = 0b1000
CMP   = 0b1001
JMP   = 0b1010
JZ    = 0b1011
STORE = 0b1100
LOAM  = 0b1101
OUT   = 0b1110
HALT  = 0b1111

async def reset_cpu(dut):
    """Reset the CPU and clear all registers"""
    dut.rst_n.value = 0
    dut.uio_in.value = 0
    dut.ui_in.value = 0
    await ClockCycles(dut.clk, 5)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 2)

async def execute_instruction(dut, opcode, data=0):
    """Execute a single instruction"""
    # Set instruction and data
    instruction = (data << 4) | opcode
    dut.ui_in.value = instruction
    
    # Load instruction signal
    dut.uio_in.value = 0b0001  # Set LOAD_INST bit
    await ClockCycles(dut.clk, 1)
    
    # Single step execution
    dut.uio_in.value = 0b0010  # Set STEP_CPU bit
    await ClockCycles(dut.clk, 1)
    
    # Clear control signals
    dut.uio_in.value = 0b0000
    await ClockCycles(dut.clk, 4)  # Wait for pipeline to complete

def get_accumulator(dut):
    """Get current accumulator value"""
    return int(dut.uo_out.value) & 0xF

def get_flags(dut):
    """Get CPU flags as dictionary"""
    output = int(dut.uo_out.value)
    return {
        'zero': bool(output & 0x10),
        'carry': bool(output & 0x20),
        'halt': bool(output & 0x40),
        'exec': bool(output & 0x80)
    }

@cocotb.test()
async def test_reset(dut):
    """Test CPU reset functionality"""
    clock = Clock(dut.clk, 10, units="us")  # 100kHz clock
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Check that accumulator is reset to 0
    assert get_accumulator(dut) == 0, f"Accumulator should be 0 after reset, got {get_accumulator(dut)}"
    
    # Check that flags are cleared
    flags = get_flags(dut)
    assert not flags['zero'], "Zero flag should be cleared after reset"
    assert not flags['carry'], "Carry flag should be cleared after reset" 
    assert not flags['halt'], "Halt flag should be cleared after reset"

@cocotb.test()
async def test_load_instruction(dut):
    """Test LOAD instruction"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load value 5 into accumulator
    await execute_instruction(dut, LOAD, 5)
    
    assert get_accumulator(dut) == 5, f"Expected accumulator = 5, got {get_accumulator(dut)}"
    
    # Load value 0 to test zero flag
    await execute_instruction(dut, LOAD, 0)
    
    assert get_accumulator(dut) == 0, f"Expected accumulator = 0, got {get_accumulator(dut)}"
    flags = get_flags(dut)
    assert flags['zero'], "Zero flag should be set when loading 0"

@cocotb.test()
async def test_arithmetic_operations(dut):
    """Test ADD and SUB instructions"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load 5 into accumulator
    await execute_instruction(dut, LOAD, 5)
    assert get_accumulator(dut) == 5
    
    # Add 3 (5 + 3 = 8)
    await execute_instruction(dut, ADD, 3)
    assert get_accumulator(dut) == 8, f"Expected 5 + 3 = 8, got {get_accumulator(dut)}"
    
    # Subtract 2 (8 - 2 = 6)
    await execute_instruction(dut, SUB, 2)
    assert get_accumulator(dut) == 6, f"Expected 8 - 2 = 6, got {get_accumulator(dut)}"
    
    # Test overflow: Load 15, add 1
    await execute_instruction(dut, LOAD, 15)
    await execute_instruction(dut, ADD, 1)
    
    # Should overflow to 0 and set carry flag
    assert get_accumulator(dut) == 0, f"Expected overflow to 0, got {get_accumulator(dut)}"
    flags = get_flags(dut)
    assert flags['carry'], "Carry flag should be set on overflow"
    assert flags['zero'], "Zero flag should be set when result is 0"

@cocotb.test()
async def test_logic_operations(dut):
    """Test AND, OR, XOR instructions"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load 0b1010 (10)
    await execute_instruction(dut, LOAD, 0b1010)
    
    # AND with 0b1100 (12) -> should get 0b1000 (8)
    await execute_instruction(dut, AND, 0b1100)
    assert get_accumulator(dut) == 0b1000, f"Expected 10 AND 12 = 8, got {get_accumulator(dut)}"
    
    # Load 0b1010 again
    await execute_instruction(dut, LOAD, 0b1010)
    
    # OR with 0b0101 (5) -> should get 0b1111 (15)
    await execute_instruction(dut, OR, 0b0101)
    assert get_accumulator(dut) == 0b1111, f"Expected 10 OR 5 = 15, got {get_accumulator(dut)}"
    
    # XOR with 0b0011 (3) -> should get 0b1100 (12)
    await execute_instruction(dut, XOR, 0b0011)
    assert get_accumulator(dut) == 0b1100, f"Expected 15 XOR 3 = 12, got {get_accumulator(dut)}"

@cocotb.test()
async def test_shift_operations(dut):
    """Test SHL and SHR instructions"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load 0b0101 (5)
    await execute_instruction(dut, LOAD, 0b0101)
    
    # Shift left -> should get 0b1010 (10)
    await execute_instruction(dut, SHL, 0)
    assert get_accumulator(dut) == 0b1010, f"Expected 5 << 1 = 10, got {get_accumulator(dut)}"
    
    # Shift right -> should get 0b0101 (5)
    await execute_instruction(dut, SHR, 0)
    assert get_accumulator(dut) == 0b0101, f"Expected 10 >> 1 = 5, got {get_accumulator(dut)}"
    
    # Test shift left with carry
    await execute_instruction(dut, LOAD, 0b1000)  # Load 8
    await execute_instruction(dut, SHL, 0)  # Should overflow and set carry
    
    assert get_accumulator(dut) == 0b0000, f"Expected shift overflow to 0, got {get_accumulator(dut)}"
    flags = get_flags(dut)
    assert flags['carry'], "Carry flag should be set on shift overflow"

@cocotb.test()
async def test_compare_instruction(dut):
    """Test CMP instruction and flags"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load 5 and compare with 5 (should set zero flag)
    await execute_instruction(dut, LOAD, 5)
    await execute_instruction(dut, CMP, 5)
    
    flags = get_flags(dut)
    assert flags['zero'], "Zero flag should be set when comparing equal values"
    assert not flags['carry'], "Carry flag should not be set when acc >= data"
    
    # Compare 5 with 7 (should set carry flag)
    await execute_instruction(dut, CMP, 7)
    
    flags = get_flags(dut)
    assert not flags['zero'], "Zero flag should not be set when comparing unequal values"
    assert flags['carry'], "Carry flag should be set when acc < data"

@cocotb.test()
async def test_halt_instruction(dut):
    """Test HALT instruction"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Execute HALT
    await execute_instruction(dut, HALT, 0)
    
    flags = get_flags(dut)
    assert flags['halt'], "Halt flag should be set after HALT instruction"

@cocotb.test()
async def test_simple_program(dut):
    """Test a simple program sequence"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Simple program: Load 3, Add 2, Add 1, should result in 6
    await execute_instruction(dut, LOAD, 3)
    assert get_accumulator(dut) == 3
    
    await execute_instruction(dut, ADD, 2)
    assert get_accumulator(dut) == 5
    
    await execute_instruction(dut, ADD, 1)
    assert get_accumulator(dut) == 6
    
    # Test final result
    assert get_accumulator(dut) == 6, f"Final result should be 6, got {get_accumulator(dut)}"

@cocotb.test()
async def test_nop_instruction(dut):
    """Test NOP instruction does nothing"""
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())
    
    await reset_cpu(dut)
    
    # Load a value
    await execute_instruction(dut, LOAD, 7)
    initial_acc = get_accumulator(dut)
    initial_flags = get_flags(dut)
    
    # Execute NOP
    await execute_instruction(dut, NOP, 0)
    
    # Check nothing changed
    assert get_accumulator(dut) == initial_acc, "NOP should not change accumulator"
    current_flags = get_flags(dut)
    assert current_flags['zero'] == initial_flags['zero'], "NOP should not change zero flag"
    assert current_flags['carry'] == initial_flags['carry'], "NOP should not change carry flag"
