import sys
import hashlib
import os
import gzip
import shutil

def add_blob(file_name):
    # add blob to data store
    import pdb; pdb.set_trace()
    sha = hashlib.sha1(file_name).hexdigest()
    if os.path.exists(sha):
        print file_name, "already backed up."
    else:
        with open(file_name, 'rb') as f_in, gzip.open(sha, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def add(args):
    pass

if __name__ == '__main__':
    commands = {
        'add': add_blob,
    }

    a, b = sys.argv[1], sys.argv[2]
    if a in commands:
        commands[a](b)
