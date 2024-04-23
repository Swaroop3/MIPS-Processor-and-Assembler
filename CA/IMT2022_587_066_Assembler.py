# Defining mips opcodes, registers values and functions values in maps
opcode_map = {
    "ADD": "000000",
    "SUB": "000000",
    "LW": "100011",
    "SW": "101011",
    "ADDI": "001000",
    "BNE": "000101",
    "BEQ": "000100",
    "J": "000010",
    "SLT": "000000",
    "SLL": "000000",
    "SRL": "000000",
    "SRA": "000000"
}

register_map = {
    "$0": "00000",
    "$t0": "01000",
    "$t1": "01001",
    "$t2": "01010",
    "$t3": "01011",
    "$t4": "01100",
    "$t5": "01101",
    "$t6": "01110",
    "$t7": "01111",
    "$t8": "11000",
    "$t9": "11001"
}

funct_map = {
    "ADD": "100000",
    "SUB": "100010",
    "SLT": "101010",
    "SLL": "000000",
    "SRL": "000010",
    "SRA": "000011"
}

label_table = {} 

def d_t_b(n, w):  #function to convert decimal string to binary string
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

def b_t_d(n): #function to convert binary string to decimal string
    k = len(n)
    sum = 0
    j = 1
    for i in range(k-1, -1, -1):
        sum += int(n[i])*j
        j *= 2
    return str(sum)

def comp(inp, w): #function to give 2's compliment 
    n = len(inp)
    out = ""
    for i in range (0,n):
        if(inp[i] == '0'):
            out = out + '1'
        else:
            out = out + '0'
    out = d_t_b(int(b_t_d(out)) + 1, w)
    return str(out)

def assemble_instruction(instruction,address): #fuction to convert 1 line of MIPS assembly code to machine code
    parts = instruction.split()
    opcode = opcode_map[parts[0].upper()]

    def register_to_bin(register_str):#function to convert register name to its integer value
        return register_map[register_str.rstrip(',')]

    # writing machine codes for R-type instructions
    if parts[0].upper() in ["ADD", "SUB","SLT"]:
        rd = register_to_bin(parts[1])
        rs = register_to_bin(parts[2])
        rt = register_to_bin(parts[3])
        funct = funct_map[parts[0].upper()]
        machine_code = opcode + rs + rt + rd + "00000" + funct
    elif parts[0].upper() in ["SLL","SRL","SRA"]:
        rd = register_to_bin(parts[1])
        rt = register_to_bin(parts[2])
        rs = d_t_b(0,5)
        shamt = d_t_b(parts[3],5)
        funct = funct_map[parts[0].upper()]
        machine_code = opcode + rs + rt + rd + shamt + funct
    
    # writing machine codes for  I-type instructions
    elif parts[0].upper() in ["ADDI"]:
        rt = register_to_bin(parts[1])
        rs = register_to_bin(parts[2])
        add_or_imm = d_t_b(parts[3],16)
        machine_code = opcode + rs + rt + add_or_imm
    elif parts[0].upper() in ["LW", "SW"]:
        rt = register_to_bin(parts[1])
        add_or_imm = d_t_b(int(parts[2].split('(')[0]), 16)
        rs = register_to_bin(parts[2].split('(')[1][0:-1])
        machine_code = opcode + rs + rt + add_or_imm
    elif parts[0].upper() in ["BEQ", "BNE"]:
        rs = register_to_bin(parts[1])
        rt = register_to_bin(parts[2])
        add_or_imm = d_t_b((label_table[parts[3]]-address)/4, 16)
        machine_code = opcode + rs + rt + add_or_imm
    
    #writing machine codes for  J-type instructions
    elif parts[0].upper() in ["J", "JAL"]:
        target_address = d_t_b(label_table[parts[1]]/4 , 26) #Instructions assumed to be stored from address 1048576 onwards
        machine_code = opcode + target_address
    else:
        machine_code = "UNKNOWN INSTRUCTION"
    
    return '"' + machine_code + '",'

ip_file = "input.asm"
op_file = "output.bin"

with open(ip_file, "r") as input_file: #reading and storing the instructions lines from input.asm
    lines = input_file.readlines()

#building the label table by traversing input lines
address = 0
for line in lines:
    line = line.strip()
    if line.startswith("#"):  #the comments are to be ignored
        continue
    if line.endswith(":"):    #to identify labels (assumption: there is no instruction in the same line as the label)
        label = line[:-1]
        label_table[label] = address
    else:
        address += 4

#assembling instructions
address=0
machine_code = []
for line in lines:
    line = line.strip()
    if not line or line.startswith("#"):  #to ignore empty lines and comments
        continue
    if not line.endswith(":"):            #to ignore labels for assembling
        address+=4
        machine_code.append(assemble_instruction(line, address))
    
with open(op_file, "w") as output_file: #writing the machine code into output.bin
    for code in machine_code:
        output_file.write(code + "\n")