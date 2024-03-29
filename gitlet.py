import sys
from commands import *

if __name__ == '__main__':
    commands = {
        'init': init,
        'add': add,
        'rm': rm,
        'commit': commit,
        'log': log,
        'branch': branch,
        'rm-branch': rm_branch,
        'checkout': checkout,
        'checkoutt': checkoutt,
        'cb': checkout_branch,
        'status': status,
        'global-log': global_log,
        'reset': reset,
    }

    if len(sys.argv) < 2:
        print "Please enter a command."
        sys.exit(1)

    command, command_args = sys.argv[1], sys.argv[2:]
    if command in commands:
        commands[command](command_args)
    else:
        print "No command with that name exists."
