import gzip
import hashlib
import os
import cPickle as pickle
import shutil

BUF_SIZE = 65536


def add_blob(path, sha):
    backup_path = get_abs_blob_path(sha)
    if not os.path.exists(backup_path):
        with open(path, 'rb') as f_in, gzip.open(backup_path, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def copy_blob(path, sha):
    blob_path = get_abs_blob_path(sha)
    with gzip.open(blob_path, 'rb') as blob, open(path, 'w') as file:
        while True:
            data = blob.read(BUF_SIZE)
            if not data:
                break
            file.write(data)


def get_abs_blob_path(blob_name):
    return os.path.abspath('.gitlet/objects/{}'.format(blob_name))


def get_sha(file):
    """
    Calculates a sha based on a file's contents.
    """
    if not os.path.isfile(file):
        return None

    sha = hashlib.sha1()
    with open(file) as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()


def get_work_tree():
    return {os.path.abspath(f): get_sha(f) for f in os.listdir(os.getcwd()) if f != '.gitlet'}


def zip_labels(lists, labels=['modified', 'deleted', 'new file']):
    return ['\t{}: {}'.format(label, os.path.relpath(elt)) for label, list in zip(labels, lists) for elt in list]

def print_status(labels_to_files):
    print '\n'.join(
        ['\n'.join([label] + files + ['']) for label, files in labels_to_files.items() if files]
    )
