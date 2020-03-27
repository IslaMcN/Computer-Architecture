"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ADD = 0b10100000
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
PRA = 0b01001000

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = bytearray(256)
        self.register = [0] * 8
        self.pc = 0
        self.sp = 7
        self.fl = 0b00000000
        self.op_a = None
        self.op_b = None
        self.branchtable = {}
        self.branchtable[LDI] = self.interpret_LDI
        self.branchtable[PRN] = self.interpret_PRN
        self.branchtable[MUL] = self.interpret_MUL
        self.branchtable[ADD] = self.interpret_ADD
        self.branchtable[PUSH] = self.interpret_PUSH
        self.branchtable[POP] = self.interpret_POP
        self.branchtable[CALL] = self.interpret_CALL
        self.branchtable[RET] = self.interpret_RET
        self.branchtable[CMP] = self.interpret_CMP
        self.branchtable[JMP] = self.interpret_JMP
        self.branchtable[JEQ] = self.interpret_JEQ
        self.branchtable[JNE] = self.interpret_JNE
        self.branchtable[PRA] = self.interpret_PRA
        self.MAR = None
        self.MDR = None

    def ram_read(self, x):
        print(self.register[x])
        return self.register[x]

    def ram_write(self, x, y):
        self.register[x] = y

    def load(self):
        """Load a program into memory."""

        try:
            address = 0
            with open(sys.argv[1]) as f:
                for line in f:
                    comment_split = line.strip().split('#')
                    value = comment_split[0].strip()
                    self.ram[address] = int(value, 2)
                    address += 1
            print(self.ram)
        except FileNotFoundError:
            print('File not Found')
            sys.exit(2)

    def interpret_PRN(self):
        self.ram_read(self.ram[self.pc + 1])
        self.pc += 2
    
    def interpret_ADD(self):
        self.alu("ADD", self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
    
    def interpret_MUL(self):
        self.alu('MUL', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def interpret_PUSH(self):
        val = self.register[self.ram[self.pc + 1]]
        # Cpy the value in the given register to the address pointed to by SP
        self.register[self.sp] -= 1
        self.ram[self.register[self.sp]] = val
        self.pc += 2
        
    def interpret_POP(self):
        val = self.ram[self.register[self.sp]]
        # Cpy the value from the address pointed to by the SP to the register
        self.register[self.ram[self.pc + 1 ]] = val
        self.register[self.sp] += 1
        self.pc += 2
        return val

    def interpret_CALL(self):
        # Calls a subroutine at the address stored in the register
        # Address of the instruction
        val = self.pc + 2
        self.register[self.sp] -= 1

        # Pushing the address of the instruction onto the stack
        self.ram[self.register[self.sp]] = val

        # PC is set to the address stored in the register
        reg = self.op_a
        self.pc = self.register[reg]

    def interpret_RET(self):
        self.pc = self.ram[self.register[self.sp]]
        self.register[self.sp] += 1

    def interpret_CMP(self):
        value1 = self.register[self.ram[self.pc + 1]]
        value2 = self.register[self.ram[self.pc + 2]]
        if value1 == value2:
            self.fl = 0b00000001
        elif value1 < value2:
            self.fl = 0b00000100
        else:
            self.fl = 0b00000010
        self.pc += 3

    def interpret_JMP(self):
        # Jump to the address stored in the register
        address = self.register[self.op_a]
        self.pc = address
    
    def interpret_JEQ(self):
        # If equal flag is set true, jump to the address stored in the given register
        address = self.register[self.op_a]

        if self.fl & 0b00000001 == 0:
            self.pc = address
        else:
            self.pc += 2

    def interpret_JNE(self):
        # If E flag is clear jump to the address stored in register
        address = self.register[self.op_a]

        if self.fl & 0b00000001 == 0:
            self.pc = address
        else:
            self.pc += 2

    def interpret_PRA(self):
        print(self.register[self.ram[self.pc + 1 ]])
        print('ASCII', chr(self.register[self.ram[self.pc + 1]]))
        self.pc += 2

    def interpret_LDI(self):
        self.ram_write(self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def interpret_HALT(self):
        # Exit current program
        sys.exit()

    def interpret_LOAD(self):
        # Load value to register
        self.register[self.op_a] = self.op_b
    
    def interpret_PRINT(self):
        # Print the value in a register
        print(self.register[self.op_a])

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        elif op == 'MUL':
            result = self.register[reg_a] * self.register[reg_b]
            self.register[reg_a] = result
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.register[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        while True:
            IR = self.ram[self.pc]
            if IR == HLT:
                print(self.ram)
                exit(2)
            self.branchtable[IR]()
                
            
