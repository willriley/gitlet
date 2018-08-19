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

def get_last_commit():
    head = os.path.abspath('.gitlet/HEAD')
    with open(head) as f:
        current_branch = f.read()
    with open(current_branch) as f:
        commit_id = f.read()

    commit = os.path.abspath('.gitlet/objects/' + commit_id)
    with open(commit) as f:
        last_commit = pickle.load(f)
    return commit_id, last_commit


def get_sha(file):
    sha = hashlib.sha1()
    with open(file) as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()
