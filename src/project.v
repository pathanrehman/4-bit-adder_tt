/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_example (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // 4-bit CPU with simple instruction set
    // Instruction format: [3:0] = opcode, data comes from ui_in[7:4]
    
    // CPU registers
    reg [3:0] accumulator;      // Main accumulator register
    reg [3:0] program_counter;  // Program counter (4-bit for 16 instructions)
    reg [3:0] memory [0:15];    // 16 x 4-bit memory
    reg [3:0] instruction_reg;  // Current instruction
    reg [3:0] data_reg;         // Data for current instruction
    
    // CPU state machine
    typedef enum reg [1:0] {
        FETCH = 2'b00,
        DECODE = 2'b01,
        EXECUTE = 2'b10,
        WRITEBACK = 2'b11
    } cpu_state_t;
    
    cpu_state_t state, next_state;
    
    // Instruction opcodes (4-bit)
    localparam [3:0] NOP  = 4'b0000;  // No operation
    localparam [3:0] LOAD = 4'b0001;  // Load immediate to accumulator
    localparam [3:0] ADD  = 4'b0010;  // Add immediate to accumulator
    localparam [3:0] SUB  = 4'b0011;  // Subtract immediate from accumulator
    localparam [3:0] AND  = 4'b0100;  // Bitwise AND with immediate
    localparam [3:0] OR   = 4'b0101;  // Bitwise OR with immediate
    localparam [3:0] XOR  = 4'b0110;  // Bitwise XOR with immediate
    localparam [3:0] SHL  = 4'b0111;  // Shift left accumulator
    localparam [3:0] SHR  = 4'b1000;  // Shift right accumulator
    localparam [3:0] CMP  = 4'b1001;  // Compare accumulator with immediate
    localparam [3:0] JMP  = 4'b1010;  // Jump to address
    localparam [3:0] JZ   = 4'b1011;  // Jump if zero flag set
    localparam [3:0] STORE= 4'b1100;  // Store accumulator to memory
    localparam [3:0] LOAM = 4'b1101;  // Load from memory to accumulator
    localparam [3:0] OUT  = 4'b1110;  // Output accumulator
    localparam [3:0] HALT = 4'b1111;  // Halt CPU
    
    // Status flags
    reg zero_flag;
    reg carry_flag;
    reg halt_flag;
    
    // Input parsing - ui_in[3:0] = opcode, ui_in[7:4] = data
    wire [3:0] input_opcode = ui_in[3:0];
    wire [3:0] input_data = ui_in[7:4];
    
    // Control signals
    wire load_instruction = uio_in[0];  // Load new instruction from input
    wire step_cpu = uio_in[1];          // Single step execution
    wire reset_cpu = uio_in[2];         // CPU reset
    wire run_mode = uio_in[3];          // Continuous run mode
    
    // State machine - next state logic
    always_comb begin
        case (state)
            FETCH: next_state = DECODE;
            DECODE: next_state = EXECUTE;
            EXECUTE: next_state = WRITEBACK;
            WRITEBACK: next_state = (halt_flag || (!run_mode && !step_cpu)) ? WRITEBACK : FETCH;
            default: next_state = FETCH;
        endcase
    end
    
    // State machine - state update
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= FETCH;
        end else if (ena) begin
            state <= next_state;
        end
    end
    
    // CPU execution logic
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n || reset_cpu) begin
            // Reset all registers and flags
            accumulator <= 4'b0000;
            program_counter <= 4'b0000;
            instruction_reg <= 4'b0000;
            data_reg <= 4'b0000;
            zero_flag <= 1'b0;
            carry_flag <= 1'b0;
            halt_flag <= 1'b0;
            
            // Initialize memory with some default program
            memory[0] <= 4'b0001;   // LOAD
            memory[1] <= 4'b0010;   // ADD
            memory[2] <= 4'b1110;   // OUT
            memory[3] <= 4'b1111;   // HALT
            memory[4] <= 4'b0000;
            memory[5] <= 4'b0000;
            memory[6] <= 4'b0000;
            memory[7] <= 4'b0000;
            memory[8] <= 4'b0000;
            memory[9] <= 4'b0000;
            memory[10] <= 4'b0000;
            memory[11] <= 4'b0000;
            memory[12] <= 4'b0000;
            memory[13] <= 4'b0000;
            memory[14] <= 4'b0000;
            memory[15] <= 4'b0000;
            
        end else if (ena) begin
            case (state)
                FETCH: begin
                    if (load_instruction) begin
                        // Load instruction from input
                        instruction_reg <= input_opcode;
                        data_reg <= input_data;
                    end else begin
                        // Fetch from memory
                        instruction_reg <= memory[program_counter];
                        data_reg <= input_data;  // Data always comes from input
                    end
                end
                
                DECODE: begin
                    // Instruction decode happens here
                    // Most decode logic is in the execute stage
                end
                
                EXECUTE: begin
                    case (instruction_reg)
                        NOP: begin
                            // No operation
                        end
                        
                        LOAD: begin
                            accumulator <= data_reg;
                            zero_flag <= (data_reg == 4'b0000);
                        end
                        
                        ADD: begin
                            {carry_flag, accumulator} <= accumulator + data_reg;
                            zero_flag <= ((accumulator + data_reg) & 4'hF) == 4'b0000;
                        end
                        
                        SUB: begin
                            {carry_flag, accumulator} <= accumulator - data_reg;
                            zero_flag <= ((accumulator - data_reg) & 4'hF) == 4'b0000;
                        end
                        
                        AND: begin
                            accumulator <= accumulator & data_reg;
                            zero_flag <= (accumulator & data_reg) == 4'b0000;
                            carry_flag <= 1'b0;
                        end
                        
                        OR: begin
                            accumulator <= accumulator | data_reg;
                            zero_flag <= (accumulator | data_reg) == 4'b0000;
                            carry_flag <= 1'b0;
                        end
                        
                        XOR: begin
                            accumulator <= accumulator ^ data_reg;
                            zero_flag <= (accumulator ^ data_reg) == 4'b0000;
                            carry_flag <= 1'b0;
                        end
                        
                        SHL: begin
                            {carry_flag, accumulator} <= {accumulator, 1'b0};
                            zero_flag <= {accumulator[2:0], 1'b0} == 4'b0000;
                        end
                        
                        SHR: begin
                            {accumulator, carry_flag} <= {1'b0, accumulator};
                            zero_flag <= {1'b0, accumulator[3:1]} == 4'b0000;
                        end
                        
                        CMP: begin
                            zero_flag <= (accumulator == data_reg);
                            carry_flag <= (accumulator < data_reg);
                        end
                        
                        JMP: begin
                            program_counter <= data_reg;
                        end
                        
                        JZ: begin
                            if (zero_flag) begin
                                program_counter <= data_reg;
                            end
                        end
                        
                        STORE: begin
                            memory[data_reg] <= accumulator;
                        end
                        
                        LOAM: begin
                            accumulator <= memory[data_reg];
                            zero_flag <= memory[data_reg] == 4'b0000;
                        end
                        
                        OUT: begin
                            // Output handled in output assignment
                        end
                        
                        HALT: begin
                            halt_flag <= 1'b1;
                        end
                        
                        default: begin
                            // Invalid instruction - treat as NOP
                        end
                    endcase
                end
                
                WRITEBACK: begin
                    // Update program counter for most instructions
                    if (!halt_flag && instruction_reg != JMP && !(instruction_reg == JZ && zero_flag)) begin
                        program_counter <= program_counter + 1;
                    end
                end
            endcase
        end
    end
    
    // Output assignments
    assign uo_out[3:0] = accumulator;           // Lower 4 bits: accumulator value
    assign uo_out[4] = zero_flag;               // Zero flag
    assign uo_out[5] = carry_flag;              // Carry flag  
    assign uo_out[6] = halt_flag;               // Halt flag
    assign uo_out[7] = (state == EXECUTE);     // Execution indicator
    
    // Bidirectional I/O outputs
    assign uio_out[3:0] = program_counter;      // Program counter
    assign uio_out[7:4] = instruction_reg;     // Current instruction
    
    // Set bidirectional pins as outputs for status
    assign uio_oe[3:0] = 4'b1111;  // PC output
    assign uio_oe[7:4] = 4'b1111;  // Instruction output
    
    // List all unused inputs to prevent warnings
    wire _unused = &{ena, 1'b0};

endmodule
