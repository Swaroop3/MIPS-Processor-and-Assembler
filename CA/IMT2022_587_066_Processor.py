# Defining mips opcodes, registers values and functions values in maps
opcode_map = {
    "100011":"LW",
    "101011":"SW",
    "001000":"ADDI",
    "000101":"BNE",
    "000100":"BEQ",
    "000010":"J",
    "011100":"MUL",
    "000000":"R-type"
}

funct_map = {
    "ADD": "100000",
    "SUB": "100010",
    "SLT": "101010",
    "SLL": "000000",
    "SRL": "000010",
    "SRA": "000011",
    "MUL": "000010",
    "100000": "ADD",
    "100010": "SUB",
    "101010": "SLT",
    "000000": "SLL",
    "000010": "SRL",
    "000011": "SRA",
    "000010": "MUL"
}


def d2b(n, w): # Function to convert decimal string to binary string
    n=int(n)
    i=n
    if n<0:
        n = -n
    if n == 0:
        return '0' * w
    bin_str = ''
    while n > 0:
        r = n % 2
        bin_str = str(r) + bin_str
        n = n // 2
    num_zeros = w - len(bin_str)
    if num_zeros > 0:
        bin_str = '0' * num_zeros + bin_str
    if i>0:
        return bin_str
    else:
        return comp(bin_str, w)

def b2d(n): # Function to convert binary string to decimal string
    k = len(n)
    sum = 0
    j = 1
    for i in range(k-1, -1, -1):
        sum += int(n[i])*j
        j *= 2
    if n[0]=='1':
        return str(sum-2**len(n))
    return str(sum)

def comp(inp, w): # Function to give 2's compliment 
    n = len(inp)
    out = ""
    for i in range (0,n):
        if(inp[i] == '0'):
            out = out + '1'
        else:
            out = out + '0'
    out = d2b(int(b2d(out)) + 1, w)
    return str(out)

class Processor: #Processor class to simulate MIPS processor.
    def __init__(self, instruction_memory, data_memory, register_file):
        self.instruction_memory = instruction_memory
        self.data_memory = data_memory
        self.register_file = register_file
        self.PC = 0
        self.clock_cycles = 0
        self.pipelining = None
        self.if_id = None
        self.id_ex = None
        self.ex_mem = None
        self.mem_wb = None
        self.hazard = None

    def fetch(self):
        # Instruction fetch
        if self.PC >= len(self.instruction_memory) and self.pipelining:
            if not self.hazard:
                self.PC +=1
            return
        
        machine_code = self.instruction_memory[self.PC]
        self.if_id = machine_code
        if (self.pipelining and not self.hazard) or not self.pipelining:
            self.PC += 1
    
    def decode(self):
        # Decode the machine code instruction to extract opcode, registers, and immediate values
        if self.PC-len(self.instruction_memory) >= 1 and self.pipelining:
            return
        if (self.pipelining and not self.hazard) or not self.pipelining:
            self.machine_code = self.if_id

        opcode = self.machine_code[0:6]
        if opcode in opcode_map:
            operands = []

            if opcode in ["000000"]:  # R-type
                rs = self.machine_code[6:11]
                rt = self.machine_code[11:16]
                rd = self.machine_code[16:21]
                shamt = self.machine_code[21:26]
                funct = self.machine_code[26:32]
                operands = [self.register_file[int(b2d(rs))], self.register_file[int(b2d(rt))], int(b2d(rd)), funct, int (b2d(shamt))]
                wr = rd
                r1 = rs
                r2 = rt
            
            elif opcode in ["001000"]:  # I-type ADDI
                rs = self.machine_code[6:11]
                rt = self.machine_code[11:16]
                imm = self.machine_code[16:32]
                operands = [self.register_file[int(b2d(rs))], int(b2d(rt)), int(b2d(imm))]
                wr = rt
                r1 = rs
                r2 = rt

            elif opcode in ["011100"]: #MUL
                rs = self.machine_code[6:11]
                rt = self.machine_code[11:16]
                rd = self.machine_code[16:21]
                shamt = self.machine_code[21:26]
                operands = [self.register_file[int(b2d(rs))], self.register_file[int(b2d(rt))], int(b2d(rd)), int (b2d(shamt))]
                wr = rd
                r1 = rs
                r2 = rt
                                         
            elif opcode in ["100011"]:  # LW
                rs = self.machine_code[6:11]
                rt = self.machine_code[11:16]
                offset = self.machine_code[16:32]
                operands = [self.register_file[int(b2d(rs))], int(b2d(rt)), int(b2d(offset))]
                wr = rt
                r1 = rs
                r2 = None

            elif opcode in ["101011"]:  #SW
                rs = self.machine_code[6:11]
                rt = self.machine_code[11:16]
                offset = self.machine_code[16:32]
                operands = [self.register_file[int(b2d(rs))], self.register_file[int(b2d(rt))], int(b2d(offset))]
                wr = None
                r1 = rs
                r2 = rt

            elif opcode in ["000100", "000101"]:  # BEQ or BNE
                rs = self.register_file[int(b2d(self.machine_code[6:11]))]
                rt = self.register_file[int(b2d(self.machine_code[11:16]))]
                offset = int(b2d(self.machine_code[16:32]))
                wr = None
                r1 = self.machine_code[6:11]
                r2 = self.machine_code[11:16]
            
            elif opcode in ["000010"]:  #Jump instruction
                j_address = self.machine_code[6:32]
                j_address = int(b2d(j_address))
                self.PC = j_address
                wr = None
                r1 = None
                r2 = None

            # Hazard detection unit
            if self.pipelining and self.id_ex is not None and r1 is not None and r1 == self.id_ex[-1]:
                self.hazard = True
            elif self.pipelining and self.ex_mem is not None and r1 is not None and r1 == self.ex_mem[-1]:
                self.hazard = True
            elif self.pipelining and self.id_ex is not None and r2 is not None and r2 == self.id_ex[-1]:
                self.hazard = True
            elif self.pipelining and self.ex_mem is not None and r2 is not None and r2 == self.ex_mem[-1]:
                self.hazard = True
            elif self.pipelining:
                self.hazard = False
            

            if (self.pipelining and not self.hazard or not self.pipelining) and ((opcode_map[opcode] == "BEQ" and  rs == rt) or (opcode_map[opcode] == "BNQ" and rs != rt)):
                self.PC += offset
            if (self.pipelining and not self.hazard) or not self.pipelining:
                self.id_ex = (opcode, operands, wr)

    def execute(self): #Execute the decoded instruction.
        if self.PC-len(self.instruction_memory) >= 2 and self.pipelining:
            return
        if self.pipelining and self.hazard:
            self.id_ex = None
            return
        
        opcode, operands, wr = self.id_ex
        if opcode == "000000":
            # R-type instruction
            src1_value, src2_value, dest_register, funct, shamt = operands
            if funct in funct_map:
                if funct == funct_map["ADD"]:
                    result = src1_value + src2_value
                elif funct == funct_map["SUB"]:
                    result = src1_value - src2_value
                elif funct == funct_map["SLL"]:
                    result = src2_value * 2**shamt
                elif funct == funct_map["SLT"]:
                    if(src1_value < src2_value):
                        result = 1
                    else:
                        result = 0
                else:
                    result = None  # Unsupported funct value
                self.ex_mem = (opcode, 0, 0, dest_register, result, wr)
        
        elif opcode == "001000":  # I-type ADDI instruction
            src_value, dest_register, imm = operands
            result = src_value + imm
            self.ex_mem = (opcode, 0, src_value, dest_register, result, wr)

        elif opcode == "011100": #MUL
            funct = self.machine_code[26:32]
            if funct in funct_map:
                src1_value, src2_value, dest_register, shamt = operands
                if funct == funct_map["MUL"]:
                    result = (src1_value)*(src2_value)
                    self.ex_mem = (opcode, 0, 0, dest_register, result, wr)
        
        elif opcode == "100011":  # LW instruction
            rs, rt, offset = operands
            src_address = rs + offset
            self.ex_mem = (opcode, src_address, rt, None, None, wr)
        
        elif opcode == "101011":  # SW instruction
            rs, rt, offset = operands
            address = rs + offset
            self.ex_mem = (opcode, address, rt, None, None, wr)
        
        elif opcode in ["000100", "000101"]:  # BEQ or BNE
            self.ex_mem = (opcode, 0, 0, None, None, wr)
        
    def memory_access(self): #Memeory access stage.
        if self.PC-len(self.instruction_memory) >= 3 and self.pipelining:
            return

        opcode, address, rt, dest_register, result, wr = self.ex_mem
   
        if opcode == "100011":  # LW instruction
            self.mem_wb = (opcode, rt, self.data_memory[int(address)], wr)
        elif opcode == "101011":  # SW instruction
            self.data_memory[int(address)] = rt
        if dest_register is not None:
            self.mem_wb = (opcode, dest_register, result, wr)

    def writeback(self): #writeback stage.
        opcode, dest_register, result, wr = self.mem_wb
        if opcode in ["100011", "000000", "001000"]:  # Write back the result of R-type, I-type ADDI and LW instruction to the destination register
            self.register_file[dest_register] = result
    
    def run_non_pipeline(self): #run the processor without pipelining
        self.pipelining = False
        while self.PC < len(self.instruction_memory):
            self.fetch()
            self.clock_cycles += 1
            self.decode()
            self.clock_cycles += 1
            self.execute()
            self.clock_cycles += 1
            self.memory_access()
            self.clock_cycles += 1
            self.writeback()
            self.clock_cycles += 1

    def run_pipeline(self): #run the processor with pipelining.
        self.pipelining = True
        while self.PC - len(self.instruction_memory) < 4:
            if self.hazard:
                if self.mem_wb is not None:
                    self.writeback()
                if self.ex_mem is not None:
                    self.memory_access()
                if self.id_ex is not None:
                    self.execute()
                if self.if_id is not None: 
                    self.decode()
                self.fetch()
                self.clock_cycles += 1
                
                if self.mem_wb is not None:
                    self.writeback()
                self.mem_wb = None
                self.ex_mem = None
                if self.if_id is not None: 
                    self.decode()
                self.fetch()
                self.clock_cycles += 1
                
            else:
                if self.mem_wb is not None:
                    self.writeback()
                if self.ex_mem is not None:
                    self.memory_access()
                if self.id_ex is not None:
                    self.execute()
                if self.if_id is not None: 
                    self.decode()
                self.fetch()
                self.clock_cycles += 1


# insertion sort  machine code instructions, data memory, and register file setup
instruction_memory_sort =[
"00000000000000000100000000100000",
"00000001000010010110000000101010",
"00010001100000000000000000001000",
"00000000000010000110100000000000",
"00000001101010100110100000100000",
"10001101101011100000000000000000",
"00000000000010000110100000000000",
"00000001101010110110100000100000",
"10101101101011100000000000000000",
"00100001000010000000000000000001",
"00001000000000000000000000000001",
"00100000000010000000000000000001",
"00000001000010010110000000101010",
"00010001100000000000000000010111",
"00000000000010000110100000000000",
"00000001101010110110100000100000",
"10001101101011100000000000000000",
"00100001000011111111111111111111",
"00000001111000000110000000101010",
"00010101100000000000000000001011",
"00000000000011110110100000000000",
"00000001101010110110100000100000",
"10001101101110010000000000000000",
"00000001110110010110000000101010",
"00010001100000000000000000000110",
"00100001111011010000000000000001",
"00000000000011010110100000000000",
"00000001101010110110100000100000",
"10101101101110010000000000000000",
"00100001111011111111111111111111",
"00001000000000000000000000010010",
"00100001111011010000000000000001",
"00000000000011010110100000000000",
"00000001101010110110100000100000",
"10101101101011100000000000000000",
"00100001000010000000000000000001",
"00001000000000000000000000001100"]

n=int(input("Number of integers to sort :")) #take the size of the array.
arr = [ int(input()) for i in range(n)]
                                  
data_memory = arr + [0] * (1024-n)
register_file = [0] * 32
register_file[9] = n    #$t1 = length of array
register_file[10] = 0   #$t2 = base address
register_file[11] = n+2 #$t3 = dest address

# Create a non-pipelined processor
processor = Processor( instruction_memory_sort, data_memory, register_file)
processor.run_non_pipeline()
print("Total clock cycles for non-pipelining:", processor.clock_cycles)
#for x in range(int(register_file[11]),int(register_file[11])+register_file[9]):
#    print(data_memory[x])
print(data_memory)


data_memory = arr + [0] * (1024-n)
register_file = [0] * 32
register_file[9] = n    #$t1 = length of array
register_file[10] = 0   #$t2 = base address
register_file[11] = n+2 #$t3 = dest address

#Create a pipelined processor.
processor = Processor( instruction_memory_sort, data_memory, register_file)
processor.run_pipeline()
print("Total clock cycles for pipelining:", processor.clock_cycles)
#for x in range(int(register_file[11]),int(register_file[11])+register_file[9]):
#    print(data_memory[x])
print(data_memory)

