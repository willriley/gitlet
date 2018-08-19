import os
import pdb
from fileutils import add_object, get_last_commit, get_sha
from commit import Commit, Stage


def add(args):
    pdb.set_trace()
    filename = os.path.abspath(args[0])
    if not os.path.exists(filename):
        print "File doesn't exist."
        return

    # maybe use buffer for larger files to limit memory usage?
    sha = get_sha(filename)
    _, last_commit = get_last_commit()

    # current working version identical to last commit's; don't stage
    if (filename in last_commit.filemap and
        last_commit.filemap[filename] == sha):
        return

    # update staging area
    stage = Stage.from_index_file()
    if filename in stage.rm:
        stage.rm.remove(filename)
    stage.add[filename] = sha
    stage.to_index_file()

    add_object(filename, sha)


def rm(args):
    pdb.set_trace()
    path = os.path.abspath(args[0])
    stage = Stage.from_index_file()
    _, last_commit = get_last_commit()

    if not os.path.exists(path):
        print "File doesn't exist"
    elif path in stage.rm:
        return
    elif path not in stage.add and path not in last_commit.filemap:
        print "No reason to remove the file."
    else:
        stage.add.pop(path, None)
        stage.rm.add(path)
        stage.to_index_file()


def init(args):
    pdb.set_trace()
    if os.path.exists('.gitlet'):
        print "A gitlet version-control system already exists in the current directory."
        return

    # set up .gitlet directory structure
    subdirs = ['objects', 'refs/heads']
    for subdir in subdirs:
        path = os.path.abspath('.gitlet/' + subdir)
        try:
            os.makedirs(path)
        except OSError:
            if not os.path.isdir(path):
                raise OSError('Error initializing gitlet repo.')

    # create initial commit
    initial_commit = Commit(parent_id=None, message="initial commit")
    # change to initial_commit.commit()?
    commit_id = initial_commit.commit()

    # mark init commit's id as the master branch's last commit
    master_branch_path = os.path.abspath('.gitlet/refs/heads/master')
    with open(master_branch_path, 'w') as f:
        f.write(commit_id)

    # mark master branch as the current branch
    head_path = os.path.abspath('.gitlet/HEAD')
    with open(head_path, 'w') as f:
        f.write(master_branch_path)

    # create blank staging area for future changes
    Stage.blank().to_index_file()


def commit(args):
    # add optparser shit
    # support -m (then -am)

    last_commit_id, last_commit = get_last_commit()
    stage = Stage.from_index_file()

    if not stage.add and not stage.rm:
        print "No changes added to the commit."
        return

    # start with parent commit's files
    filemap = dict(last_commit.filemap)
    # add in the staged files
    filemap.update(stage.add)
    # ...and account for the removed ones, too
    for file in stage.rm:
        filemap.pop(file, None)

    next_commit = Commit(last_commit_id, message, filemap)

    # update head pointer

    # clear staging area
    Stage.blank().to_index_file()
