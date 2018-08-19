import os
import datetime
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
        sha = hashlib.sha1(data).hexdigest()
        path = os.path.abspath('.gitlet/objects/' + sha)

        with open(path, 'wb') as f:
            f.write(data)
        return sha

    def update_refs(self, branch_name='master'):
        pass


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
