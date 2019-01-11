import os
import datetime
from util import get_abs_blob_path
import hashlib
import cPickle as pickle


class Commit:
    INDEX_PATH = os.path.abspath('.gitlet/index')

    def __init__(self, parent_id, filemap={}):
        self.parent_id = parent_id
        self.filemap = filemap

    def commit(self, message):
        self.message, self.ts = message, datetime.datetime.now()
        data = pickle.dumps(self)

        # save serialized commit info
        self.id = hashlib.sha1(data).hexdigest()
        path = get_abs_blob_path(self.id)
        with open(path, 'wb') as f:
            f.write(data)

        # point current branch to this commit
        Branch.current().set_head_commit(self.id)

    def set_index(self):
        with open(Commit.INDEX_PATH, 'w') as f:
            pickle.dump(self, f)

    @staticmethod
    def index():
        return Commit.__at(Commit.INDEX_PATH)

    @staticmethod
    def from_id(id):
        path = os.path.abspath('.gitlet/objects/' + id)
        if os.path.exists(path):
            commit = Commit.__at(path)
            commit.id = id
            return commit
        return None

    @staticmethod
    def last(branch=None):
        """
        Returns the last commit on a given branch.
        """
        return Commit.from_id(Commit.last_id())

    @staticmethod
    def last_id(branch=None):
        """
        Returns the last commit id on a given branch.
        """
        branch = branch if branch else Branch.current_path()
        with open(branch) as f:
            return f.read()

    @staticmethod
    def __at(path):
        with open(path) as f:
            commit = pickle.load(f)
        return commit

    def __str__(self):
        return '\n'.join([
            '===',
            'Commit {}'.format(self.id),
            self.ts.strftime('%Y-%m-%d %H:%M:%S'),
            self.message,
            '',
        ])


class Branch:
    HEAD = os.path.abspath('.gitlet/HEAD')

    def __init__(self, path=None):
        self.path = path if path else Branch.current_path()

    def __iter__(self):
        with open(self.path) as f:
            self.commit_id = f.read()
        return self

    def next(self):
        if not self.commit_id:
            raise StopIteration

        curr_cid, curr_commit = self.commit_id, Commit.from_id(self.commit_id)
        self.commit_id = curr_commit.parent_id
        return curr_commit

    def set_head_commit(self, commit_id):
        with open(self.path, 'w') as f:
            f.write(commit_id)

    @staticmethod
    def set_head(branch_name):
        with open(Branch.HEAD, 'w') as f:
            f.write(Branch.abspath(branch_name))

    @staticmethod
    def current_path():
        with open(Branch.HEAD) as f:
            return f.read()

    @staticmethod
    def current():
        return Branch()

    @staticmethod
    def all():
        branches = os.listdir(os.path.abspath('.gitlet/refs/heads'))
        curr_branch = os.path.basename(Branch.current_path())
        return ['\t' + b if b != curr_branch else '\t*' + b for b in branches]        

    @staticmethod
    def abspath(branch_name):
        return os.path.abspath('.gitlet/refs/heads/{}'.format(branch_name))
