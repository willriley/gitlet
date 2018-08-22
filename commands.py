import os
import pdb
from fileutils import add_blob, copy_blob, get_last_commit, get_sha, list_files, get_abs_branch_path, get_current_branch_path, get_last_commit_id
from objects import Commit, Stage, branch_iterator


def add(args):
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

    add_blob(filename, sha)


def rm(args):
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

    master_branch_path = get_abs_branch_path('master')
    # mark master branch as the current branch
    head_path = os.path.abspath('.gitlet/HEAD')
    with open(head_path, 'w') as f:
        f.write(master_branch_path)

    # create initial commit and set as last commit in master branch
    initial_commit = Commit(parent_id=None, message="initial commit")
    initial_commit.commit()

    # create blank staging area for future changes
    Stage.blank().to_index_file()


def commit(args):
    # add argparse shit to support -m (then -am)
    if not args:
        print "Please enter a commit message."

    message = args[0]
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

    # save commit info and point current branch to it
    next_commit = Commit(last_commit_id, message, filemap)
    next_commit.commit()

    # clear staging area
    Stage.blank().to_index_file()

def log(args):
    for id, commit in branch_iterator():
        commit.pretty_print(id)

def global_log(args):
    # set of seen commit ids (or even timestamps)
    # loop thru all branches
    # iterate thru each branch
    pass



def branch(args):
    pdb.set_trace()
    branch_path = get_abs_branch_path(args[0])
    if os.path.exists(branch_path):
        print "A branch with that name already exists."
    else:
        head_commit = get_last_commit_id()
        with open(branch_path, 'w') as f:
            f.write(head_commit)

def rm_branch(args):
    pdb.set_trace()
    branch_path = get_abs_branch_path(args[0])
    if not os.path.exists(branch_path):
        print "A branch with that name doesn't exist."
    elif branch_path == get_current_branch_path():
        print "Cannot remove the current branch."
    else:
        os.remove(branch_path)


def checkout_file(file, sha):
    # overwrites contents of file to have those pointed to by sha
    copy_blob(file, sha)

    # unstage file
    stage = Stage.from_index_file()
    if file in stage.rm:
        stage.rm.remove(file)
    stage.add.pop(file, None)
    stage.to_index_file()


def checkout(args):
    pdb.set_trace()
    # add argparser
    file = os.path.abspath(args[0])
    _, last_commit = get_last_commit()

    if file not in last_commit.filemap:
        print "File doesn't exist in that commit."
    else:
        checkout_file(file, last_commit.filemap[file])

def checkoutt(args):
    pdb.set_trace()
    # add argparser
    commit_id, file = args[0], os.path.abspath(args[1])
    try:
        commit = Commit.from_id(commit_id)
    except:
        print "No commit with that id exists."
        return

    if file not in commit.filemap:
        print "File doesn't exist in that commit."
    else:
        checkout_file(file, commit.filemap[file])


def status(args):
    def print_status(labels_to_files):
        for label, files in labels_to_files.items():
            print "=== {} ===".format(label)
            for file in files:
                print file
            print ""



    index = Stage.from_index_file()

    files = list_files()
    staged, removed = index.add, index.rm

    files.difference_update(staged, removed)

    # figure out if files were modified/deleted later
    # figure out untracked files later

    print_status({
        'Branches': get_branches(),
        'Staged Files': [os.path.relpath(f) for f in staged.keys()],
        'Removed Files': [os.path.relpath(f) for f in removed],
        'Unstaged Changes': unstaged,
        'Untracked Files': untracked,
    })
