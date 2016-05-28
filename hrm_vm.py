
import sys
"""
parse the commands into something we can run as instruction
"""

class Instruction(object):
    """Each instruction object defines the instruction that is available.
    """
    @classmethod
    def parse_command(cls, command):
        return None


class SingletonInstruction(Instruction):

    @classmethod
    def parse_command(cls, command):
        if len(command) == 1 and command[0] == cls.NAME:
            return cls.instance()

    @classmethod
    def instance(cls):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance


class Inbox(SingletonInstruction):
    """The inbox command that takes things from inbox
    """
    NAME = "INBOX"

    def run(self, machine):
        if len(machine.inbox) == 0:
            return -1

        value = machine.inbox.pop()
        machine.current_cache = value
        return None


class Outbox(SingletonInstruction):
    """The outbox instruction
    """
    NAME = "OUTBOX"

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to outbox empty value")
        machine.outbox.append(machine.current_cache)
        machine.current_cache = None
        return None


class MemoryValueInstruction(Instruction):

    @classmethod
    def parse_command(cls, command):
        if len(command) != 2 or command[0] != cls.NAME:
            return None

        is_memory = False
        value = None
        if command[1][0] == "[" and command[1][-1] == "]":
            is_memory = True
            value = command[1][1:-1]
        else:
            value = command[1]

        try:
            value = int(value)
        except Exception as e:
            return None

        return cls(value, is_memory)


class CopyFrom(MemoryValueInstruction):
    """The copyfrom command
    """
    NAME = "COPYFROM"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.current_cache = machine.memory[mem_pos]
        return None

class CopyTo(MemoryValueInstruction):
    """The copyto command
    """
    NAME = "COPYTO"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to copy empty value to memory")
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.memory[mem_pos] = machine.current_cache
        return None


class Add(MemoryValueInstruction):
    """The add instruction
    """
    NAME = "ADD"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to copy empty value to memory")
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.current_cache += machine.memory[mem_pos]


class Sub(MemoryValueInstruction):
    """The sub instruction
    """
    NAME = "SUB"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to copy empty value to memory")
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.current_cache == machine.memory[mem_pos]


class BumpUp(MemoryValueInstruction):
    """The bump up instruction
    """
    NAME = "BUMPUP"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.memory[mem_pos] += 1
        machine.current_cache = machine.memory[mem_pos]


class BumpDown(MemoryValueInstruction):
    """The bump down instruction
    """
    NAME = "BUMPDN"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory

    def run(self, machine):
        if self.value is None or self.value >= len(machine.memory):
            raise MachineException(message="Memory index out of bound")
        if self.is_memory:
            mem_pos = machine.memory[self.value]
        else:
            mem_pos = self.value
        if mem_pos is None:
            raise MachineException(message="Unable to access empty value memory")
        if mem_pos >= len(machine.memory) or mem_pos < 0:
            raise MachineException(message="Memory index out of bound")

        machine.memory[mem_pos] -= 1
        machine.current_cache = machine.memory[mem_pos]


class LabelInstruction(Instruction):

    @classmethod
    def parse_command(cls, command):
        if len(command) != 2 or command[0] != cls.NAME:
            return None

        return cls(command[1])

class Jump(LabelInstruction):
    """The jump instruction
    """
    NAME = "JUMP"

    def __init__(self, label):
        self.label = label
        self.line = -1

    def run(self, machine):
        return self.line


class JumpZ(LabelInstruction):
    """The Jump if zero instruction
    """
    NAME = "JUMPZ"

    def __init__(self, label):
        self.label = label
        self.line = -1

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to compare empty value")
        if machine.current_cache == 0:
            return self.line
        return None

class JumpN(LabelInstruction):
    """The Jump if negative instruction
    """
    NAME = "JUMPN"

    def __init__(self, label):
        self.label = label
        self.line = -1

    def run(self, machine):
        if machine.current_cache is None:
            raise MachineException(message="Unable to compare empty value")
        if machine.current_cache < 0:
            return self.line
        return None


AVAILABLE_COMMANDS = [ Inbox, Outbox, CopyFrom, CopyTo, Add, Sub, BumpUp, BumpDown, Jump, JumpZ, JumpN ]
AVAILABLE_COMMANDS_BY_KEY = { c.NAME: c for c in AVAILABLE_COMMANDS }

class ParserException(Exception):

    def __init__(self, message):
        super().__init__(message)

def parse_commands(commands):
    commands = [ c.strip().split(" ") for c in commands ]
    parsed_commands = []
    labels = {}
    require_labels = []
    for command in commands:
        command = [ c for c in command if c != "" ]
        if len(command) == 0:
            continue # ignore this
        if command[0][0] == "-":
            continue # ignore comment
        if command[0] in AVAILABLE_COMMANDS_BY_KEY:
            parsed_command = AVAILABLE_COMMANDS_BY_KEY[command[0]].parse_command(command)
            if parsed_command is None:
                raise ParserException(message="Unable to parse command '{0}'".format(" " .join(command)))
            parsed_commands.append(parsed_command)
            if hasattr(parsed_command, "label"):
                require_labels.append(parsed_command)
        elif len(command) == 1 and command[0][-1] == ":": # check for label
            labels[command[0][:-1]] = len(parsed_commands)
        else:
            raise ParserException(message="Unknown command '{0}'".format(" ".join(command)))

    for command in require_labels:
        if command.label not in labels:
            raise ParserException(message="Unable to find label : {0}".format(command.label))
        command.line = labels[command.label]

    return parsed_commands


class MachineException(Exception):

    def __init__(self, message):
        super().__init__(message)


def is_valid_value(value):
    if isinstance(value, int):
        return True
    if isinstance(value, str) and len(value) == 1:
        return True
    return False


class Machine(object):

    def __init__(self, memory_size, input, starting_memory=None):
        self.memory = [ None ] * memory_size
        self.inbox = list(reversed(input))
        self.outbox = []
        self.current_cache = None
        if starting_memory is not None:
            for mem_pos, value in starting_memory.items():
                if mem_pos < 0 or mem_pos >= len(self.memory):
                    raise MachineException(message="Starting memory out of index")
                self.memory[mem_pos] = value

    def run_commands(self, commands):
        current_instruction = 0
        while current_instruction >= 0  and current_instruction < len(commands):
            next_instruction = commands[current_instruction].run(machine)
            if next_instruction is None:
                current_instruction += 1
            else:
                current_instruction = next_instruction



if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        commands = f.readlines()
    parsed_commands = parse_commands(commands)
    machine = Machine(8, input=[1, 2, 3, 4])
    machine.run_commands(parsed_commands)
    print(machine.outbox)
