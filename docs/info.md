# 4-bit Accumulator CPU

A compact 4-bit accumulator-based CPU implementation designed for TinyTapeout, featuring 16 instructions and a 4-stage pipeline.

## How it works

This design implements a **single accumulator architecture CPU** where all arithmetic and logic operations use the accumulator as the primary operand and result storage[2][3]. The CPU features:

### Architecture Overview
- **4-bit data width** with Harvard-style separation of instruction and data
- **Single accumulator register** for all computational operations
- **4-bit program counter** supporting up to 16 instructions in memory
- **16 x 4-bit internal memory** for program storage
- **4-stage pipeline**: Fetch → Decode → Execute → Writeback

### Instruction Set (16 total instructions)
The CPU supports a comprehensive instruction set with 4-bit opcodes:

**Arithmetic & Logic Operations:**
- `LOAD` (0001): Load immediate value to accumulator
- `ADD` (0010): Add immediate to accumulator with carry flag
- `SUB` (0011): Subtract immediate from accumulator
- `AND` (0100): Bitwise AND operation
- `OR` (0101): Bitwise OR operation  
- `XOR` (0110): Bitwise XOR operation
- `SHL` (0111): Shift accumulator left
- `SHR` (1000): Shift accumulator right

**Control Flow:**
- `CMP` (1001): Compare accumulator with immediate (sets flags)
- `JMP` (1010): Unconditional jump to address
- `JZ` (1011): Jump if zero flag is set

**Memory Operations:**
- `STORE` (1100): Store accumulator to memory location
- `LOAM` (1101): Load from memory to accumulator

**System Operations:**
- `NOP` (0000): No operation
- `OUT` (1110): Output accumulator value
- `HALT` (1111): Stop CPU execution

### Operation Modes
The CPU supports two execution modes:
1. **Interactive Mode**: Load single instructions via input pins
2. **Program Mode**: Execute stored programs from internal memory

Status flags (zero, carry, halt) provide feedback on operation results and CPU state.

## How to test

### Basic Testing Setup

**Input Configuration:**
- `ui[3:0]`: 4-bit instruction opcode
- `ui[7:4]`: 4-bit immediate data/operand
- `uio[0]`: Load instruction from input (pulse high)
- `uio[1]`: Single step execution (pulse high)  
- `uio[2]`: Reset CPU (hold high to reset)
- `uio[3]`: Continuous run mode (high for auto-execution)

**Output Monitoring:**
- `uo[3:0]`: Current accumulator value
- `uo[4]`: Zero flag (high when accumulator = 0)
- `uo[5]`: Carry flag (high on arithmetic overflow)
- `uo[6]`: Halt flag (high when CPU halted)
- `uo[7]`: Execution indicator (high during execute phase)
- `uio[7:4]`: Program counter value (when pins configured as output)

### Test Sequences

**1. Basic Arithmetic Test:**
