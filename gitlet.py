import sys
from commands import add, init, rm, commit, log

if __name__ == '__main__':
    commands = {
        'init': init,
        'add': add,
        'rm': rm,
        'commit': commit,
        'log': log,
    }

    if len(sys.argv) < 2:
        print "Please enter a command."
        sys.exit(1)

    command, command_args = sys.argv[1], sys.argv[2:]
    if command in commands:
        commands[command](command_args)
    else:
        print "No command with that name exists."
