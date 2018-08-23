import os
import datetime
from fileutils import get_current_branch_path
import hashlib
import cPickle as pickle

class Commit:
    def __init__(self, parent_id, message, filemap={}):
        self.parent_id = parent_id
        self.message = message
        self.timestamp = datetime.datetime.now()
        # map filenames to blob ids
        self.filemap = filemap

    def commit(self):
        data = pickle.dumps(self)
        id = hashlib.sha1(data).hexdigest()
        path = os.path.abspath('.gitlet/objects/' + id)

        # serialize commit info
        with open(path, 'wb') as f:
            f.write(data)

        # point current branch to this commit
        current_branch = get_current_branch_path()
        with open(current_branch, 'w') as f:
            f.write(id)

    @staticmethod
    def from_id(id):
        path = os.path.abspath('.gitlet/objects/' + id)
        with open(path) as f:
            commit = pickle.load(f)
        return commit

    def pretty_print(self, id):
        print '\n'.join([
            '===',
            'Commit {}'.format(id),
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            self.message,
            '',
        ])


class Stage:
    INDEX_PATH = os.path.abspath('.gitlet/index')

    def __init__(self, add={}, rm=set()):
        self.add = add
        self.rm = rm

    @classmethod
    def blank(cls):
        return cls()

    @staticmethod
    def from_index_file():
        with open(Stage.INDEX_PATH) as f:
            stage = pickle.load(f)
        return stage

    def to_index_file(self):
        with open(Stage.INDEX_PATH, 'w') as f:
            pickle.dump(self, f)


def branch_iterator(branch_path=None):
    branch_path = branch_path if branch_path else get_current_branch_path()
    with open(branch_path) as f:
        commit_id = f.read()

    while commit_id:
        commit = Commit.from_id(commit_id)
        prev_commit_id, commit_id = commit_id, commit.parent_id
        yield prev_commit_id, commit
