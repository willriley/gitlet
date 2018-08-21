import gzip
import hashlib
import os
import cPickle as pickle
import shutil

BUF_SIZE = 65536

def add_object(path, sha):
    backup_path = os.path.abspath('.gitlet/objects/' + sha)
    if not os.path.exists(backup_path):
        with open(path, 'rb') as f_in, gzip.open(backup_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

def get_abs_branch_path(branch_name):
    return os.path.abspath('.gitlet/refs/heads/{}'.format(branch_name))

def get_current_branch_path():
    head = os.path.abspath('.gitlet/HEAD')
    with open(head) as f:
        return f.read()

def get_last_commit_id():
    current_branch = get_current_branch_path()
    with open(current_branch) as f:
        return f.read()

def get_last_commit():
    cid = get_last_commit_id()
    commit = os.path.abspath('.gitlet/objects/' + cid)
    with open(commit) as f:
        last_commit = pickle.load(f)
    return cid, last_commit

def get_sha(file):
    # calculate sha1 hash for a file
    # uses a buffer to control memory usage
    sha = hashlib.sha1()
    with open(file) as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

def list_files():
    # list all files in this directory and all its subdirectories
    total = set()
    for path, dirs, files in os.walk(os.getcwd()):
        dirs[:] = [dir for dir in dirs if not dir.startswith('.')]
        total.update([os.path.join(path, file) for file in files])
    return total

def determine_modification(filename):
    pass
