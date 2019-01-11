import os
import pdb
from collections import OrderedDict
from util import *
from itertools import izip_longest
from objects import *


def add(args):
    """
    Stages a file for the next commit. Fails if that file doesn't
    exist or is unchanged from the previous commit.
    """
    file = args[0] if os.path.isabs(args[0]) else os.path.abspath(args[0])
    if not os.path.isfile(file):
        print "Error: no file named {}.".format(file)
        return

    # update staging area; add blob to object store
    index, sha = Commit.index(), get_sha(file)
    index.filemap[file] = sha
    index.set_index()
    add_blob(file, sha)


def rm(args):
    """
    Removes a file from the index, or from the working directory
    and the index.

    Fails if the file has updates staged in the index, if
    the file differs from its version at the HEAD, or if
    the file is not in the index.
    """
    file = args[0] if os.path.isabs(args[0]) else os.path.abspath(args[0])
    index = Commit.index()

    if file not in index.filemap:
        print "Error: pathspec {} did not match any files".format(file)
        return

    if os.path.exists(file):
        last_commit = Commit.last()
        old_sha, sha = last_commit.filemap.get(file), get_sha(file)

        # don't remove file if it has updates in the index, or if it
        # differs from its version at the HEAD; otherwise remove it
        if (index.filemap.get(file) != sha or old_sha != sha):
            print "Error: file has staged/unstaged changes"
            return
        os.remove(file)

    # remove from index and update index to disk
    del index.filemap[file]
    index.set_index()


def init(args):
    """
    Initializes a gitlet repository.
    """
    if os.path.exists('.gitlet'):
        print "Error: a gitlet version-control system already exists in the current directory."
        return

    # set up .gitlet directory structure
    subdirs = ['objects', 'refs/heads']
    for subdir in subdirs:
        path = os.path.abspath('.gitlet/' + subdir)
        os.makedirs(path)

    # mark master branch as the current branch
    Branch.set_head('master')

    # create initial commit and set as last commit in master branch
    init_commit = Commit(parent_id=None)
    init_commit.commit("initial commit")

    # create blank staging area for future changes
    stage = Commit(init_commit.id, dict(init_commit.filemap))
    stage.set_index()


def commit(args):
    """
    Commits the staging area to the current branch, then clears
    the staging area for future commits. Fails if the staging
    area is empty or if no commit message is specified.
    """
    message, last_commit, curr_commit = args[0], Commit.last(), Commit.index()
    if last_commit.filemap == curr_commit.filemap:
        print "Nothing to commit."
        return

    curr_commit.commit(message)
    index = Commit(curr_commit.id, dict(curr_commit.filemap))
    index.set_index()


def log(args):
    """
    Prints info about all the commits in the current branch.
    """
    print "\n".join(str(commit) for commit in Branch())


def global_log(args):
    """
    Prints info about all the commits in the repo, done in no
    guaranteed order.
    """
    seen, branch_dir = set(), os.path.abspath('.gitlet/refs/heads')
    branches = (os.path.join(branch_dir, b) for b in os.listdir(branch_dir))
    for branch_path in branches:
        for commit in Branch(path=branch_path):
            if commit.id not in seen:
                print commit
                seen.add(commit.id)


def branch(args):
    """
    Creates a new branch and sets it to be the new HEAD.
    """
    branch_path = Branch.abspath(args[0])
    if os.path.exists(branch_path):
        print "A branch with that name already exists."
    else:
        # sets last commit of new branch
        head_commit_id = Commit.last_id()
        with open(branch_path, 'w') as f:
            f.write(head_commit_id)

        # sets new branch to be HEAD
        Branch.set_head(branch_path)


def rm_branch(args):
    """
    Removes the head of a branch.
    """
    branch_path = Branch.abspath(args[0])
    if not os.path.exists(branch_path):
        print "A branch with that name doesn't exist."
    elif branch_path == Branch.current_path():
        print "Cannot remove the current branch."
    else:
        os.remove(branch_path)


def status(args):
    # diff btwn last commit and index
    # gives you "changes to be committed"
    last, index = Commit.last().filemap, Commit.index().filemap
    s_last, s_index = set(last), set(index)

    new, deleted = s_index - s_last, s_last - s_index
    modified = [f for f, sha in index.items() if f in last and last[f] != sha]

    # diff btwn index and working directory
    # gives you "changes not staged for commit" and "untracked files"
    work_tree = get_work_tree()
    s_tree = set(work_tree)

    unstaged_deleted, untracked = s_index - s_tree, s_tree - s_index
    unstaged_modified = [
        f for f,
        sha in work_tree.items() if f in index and index[f] != sha]

    import pdb; pdb.set_trace()
    print_status(OrderedDict([
        ('Branches:', Branch.all()),
        ('Changes to be committed:', zip_labels([modified, deleted, new])),
        ('Changes not staged for commit:', zip_labels([unstaged_modified, unstaged_deleted])),
        ('Untracked files:', ['\t' + os.path.relpath(f) for f in untracked])
    ]))


def reset(args):
    id = args[0]
    try:
        commit = Commit.from_id(id)
        prev_stage = Stage.from_index_file()

        Stage.blank().to_index_file()
        if restore_commit(commit):
            # set commit as head of current branch
            set_branch_head_commit(id)
        else:
            # restore stage if reset fails
            prev_stage.to_index_file()
    except BaseException:
        print "No commit with that id exists."


def checkout_file(file, commit_id):
    """
    Overwrite's a file's contents to match those from a specific
    commit. If the file was marked for removal in the stage, this command unmarks it. Finally, this command adds the changes to
    the stage, unless the file is checked out to its state in the
    previous commit.

    Fails if the commit is invalid, or the file doesn't exist
    in the specified commit.
    """
    commit = Commit.from_id(commit_id)
    if not commit:
        print "Invalid commit specified"
    elif file not in commit.filemap:
        print "{} does not exist in commit {}".format(file, commit_id)
    else:
        # restores file to its state in commit_id
        copy_blob(file, commit.filemap[file])

        stage = Stage.from_index_file()
        # if file was marked for removal, unmark it
        stage.rm.discard(file)

    # overwrites working directory, not stage
    # clears it from the stage

    # 1) checkout file to its state in the commit
    # at the head of the branch
    # usage: git checkout -- <filename>

    # 2) checkout file to its state in the given commit
    # automatically adds it
    # usage: git checkout <cid> -- <filename>

    # 3) checks out all files in the working directory
    # to their versions in the commit at head of the
    # given branch, and makes that branch the new
    # current branch.
    # usage: git checkout <branch> or git checkout -b <branch>


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
    file = args[0] if os.path.isabs(args[0]) else os.path.abspath(args[0])
    _, last_commit = get_last_commit()

    if file not in last_commit.filemap:
        print "File doesn't exist in that commit."
    else:
        checkout_file(file, last_commit.filemap[file])


def checkoutt(args):

    pdb.set_trace()
    # add argparser
    commit_id = args[0]
    file = args[1] if os.path.isabs(args[1]) else os.path.abspath(args[1])
    try:
        commit = Commit.from_id(commit_id)
    except BaseException:
        print "No commit with that id exists."
        return

    if file not in commit.filemap:
        print "File doesn't exist in that commit."
    else:
        checkout_file(file, commit.filemap[file])


def restore_commit(restored_commit, checkout=lambda *args: True):
    _, last_commit = get_last_commit()
    stage, untracked = Stage.from_index_file(), []
    pdb.set_trace()
    # check if there are untracked files in current branch
    # that would be overwritten/deleted
    for file in restored_commit.filemap:
        if (
            file not in last_commit.filemap and
            file not in stage.add and
            os.path.exists(file)
        ):
            untracked.append(file)

    if untracked:
        print "The following file(s) are untracked:"
        for f in untracked:
            print f
        print "Please add or delete them before resetting."
        return False

    for file, sha in restored_commit.filemap.items():
        if checkout(file, sha, stage, last_commit.filemap):
            checkout_file(file, sha)

    for file in last_commit.filemap:
        if file not in restored_commit.filemap:
            try:
                os.remove(file)
            except OSError:
                pass

    return True


def checkout_file_condition(file, sha, stage, last_commit_files):
    return (
        file not in stage.add and
        file not in stage.rm and
        (file not in last_commit_files or sha != last_commit_files[file])
    )


def checkout_branch(args):
    branch, branch_path = args[0], get_abs_branch_path(args[0])
    if not os.path.exists(branch_path):
        print "No such branch exists."
    elif branch_path == get_current_branch_path():
        print "No need to checkout the current branch."
    else:
        with open(branch_path) as f:
            branch_head_commit = Commit.from_id(f.read())

        if restore_commit(
                branch_head_commit,
                checkout=checkout_file_condition):
            # set new branch to be the head
            set_head(branch)


def get_split_point(branch_a, branch_b):
    seen = set()
    for commit_a, commit_b in izip_longest(
            branch_iterator(branch_a), branch_iterator(branch_b)):
        for commit in [commit_a, commit_b]:
            if commit:
                if commit[0] in seen:
                    return commit[0]
                seen.add(commit[0])
    return None


def merge(args):
    other_branch, curr_branch = get_abs_branch_path(
        args[0]), get_current_branch_path()

    if not os.path.exists(other_branch):
        print "A branch with that name doesn't exist."
    elif other_branch == curr_branch:
        print "Cannot merge a branch with itself."
    else:
        stage = Stage.from_index_file()
        if stage.add or stage.rm:
            print "You have uncommitted changes."
            return

        last_cid, last_commit = get_last_commit()
        branch_head_cid = get_last_commit_id(other_branch)

        split_point_cid = get_split_point(curr_branch, other_branch)
        if split_point_cid == branch_head_cid:
            print "Given branch is an ancestor of the current branch."
        elif split_point == last_cid:
            reset([branch_head_cid])
            print "Current branch fast-forwarded."
        else:
            branch_head_commit = Commit.from_id(branch_head_cid)
            split_point_commit = Commit.from_id(split_point_cid)

            # checkout and stage files that were in the split point
            # and were MODIFIED in the other branch but UNMODIFIED in the
            # current branch

            # don't touch files that were in the split point but were
            # only modified in the current branch

            # don't touch files that weren't in the split point but
            # are now only in the current branch

            # check out and stage files that weren't in split point but
            # are now only in the other branch

            # for file, sha in branch_head_commit.filemap.items():
            #     if file in split_point_commit.filemap
