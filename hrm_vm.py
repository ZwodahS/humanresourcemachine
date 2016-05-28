
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


class Outbox(SingletonInstruction):
    """The outbox instruction
    """
    NAME = "OUTBOX"


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


class CopyTo(MemoryValueInstruction):
    """The copyto command
    """
    NAME = "COPYTO"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory


class Add(MemoryValueInstruction):
    """The add instruction
    """
    NAME = "ADD"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory


class Sub(MemoryValueInstruction):
    """The sub instruction
    """
    NAME = "SUB"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory


class BumpUp(MemoryValueInstruction):
    """The bump up instruction
    """
    NAME = "BUMPUP"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory


class BumpDown(MemoryValueInstruction):
    """The bump down instruction
    """
    NAME = "BUMPDN"

    def __init__(self, value, is_memory):
        self.value = value
        self.is_memory = is_memory


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


class JumpZ(LabelInstruction):
    """The Jump if zero instruction
    """
    NAME = "JUMPZ"

    def __init__(self, label):
        self.label = label
        self.line = -1


class JumpN(LabelInstruction):
    """The Jump if negative instruction
    """
    NAME = "JUMPN"

    def __init__(self, label):
        self.label = label
        self.line = -1


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

if __name__ == "__main__":
    with open(sys.argv[1]) as f:
        commands = f.readlines()
    parsed_commands = parse_commands(commands)
