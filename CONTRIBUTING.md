# Contributing Guidelines

🎉 **First of all, thanks for taking the time to contribute!** 🎉

## 🤔 How can I contribute?

**1.** Fix issue

**2.** Report bug

**3.** Improve Documentation


## Setup 🚀
You need to set up Textualize to make your contribution. Textual requires Python 3.7 or later (if you have a choice, pick the most recent Python). Textual runs on Linux, macOS, Windows, and probably any OS where Python also runs.

### Installation

**Install Texualize via pip:**
```bash
pip install textual
```
**Install [Poetry](https://python-poetry.org/)**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```
**To install all dependencies, run:**
```bash
poetry install --all 
```
**Make sure everything works fine:**
```bash
textual --version
```
### Demo

Once you have Textual installed, run the following to get an impression of what it can do:

```bash
python -m textual
```
If Texualize is installed, you should see this:
<img width="848" alt="demo" src="https://github.com/clairecharles/textual/assets/67120042/62fd53c0-7ad6-4429-8751-5a713180b836">

## Make contribution
**1.** Fork [this](repo) repository.

**2.** Clone the forked repository.

```bash
git clone https://github.com/<your-username>/textual.git
```

**3.** Navigate to the project directory.

```bash
cd textual
```

**4.** Create a new [pull request](https://help.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)


### 📣 Pull Requests(PRs)

The process described here should check off these goals:

- [x] Maintain the project's quality.
- [x] Fix problems that are important to users.
- [x] A changelog snippet was added (see below);
- [x] Your code was formatted with black (`make format`);
- [x] All of your code has docstrings in the style of the rest of the codebase;
- [x] Your code passes all tests (`make test`); and
- [x] You added documentation when needed.

### After the PR 🥳
When you open a PR, your code will be reviewed by one of the Textual maintainers.
In that review process,

- We will take a look at all of the changes you are making;
- We might ask for clarifications (why did you do X or Y?);
- We might ask for more tests/more documentation; and
- We might ask for some code changes.

The sole purpose of those interactions is to make sure that, in the long run, everyone has the best experience possible with Textual and with the feature you are implementing/fixing.

Don't be discouraged if a reviewer asks for code changes.
If you go through our history of pull requests, you will see that every single one of the maintainers has had to make changes following a review.



## 🛑 Important

- Make sure to read the issue instructions carefully. If you are a newbie you should look out for some good first issues because they should be clear enough and sometimes even provide some hints. If something isn't clear, ask for clarification!

- Add docstrings to all of your code (functions, methods, classes, ...). The codebase should have enough examples for you to copy from.

- Write tests for your code.

- If you are fixing a bug, make sure to add regression tests that link to the original issue.

- If you are implementing a visual element, make sure to add snapshot tests. See below for more details.


### Snapshot Testing
Snapshot tests ensure that things like widgets look like they are supposed to.
PR [#1969](https://github.com/Textualize/textual/pull/1969) is a good example of what adding snapshot tests means: it amounts to a change in the file ```tests/snapshot_tests/test_snapshots.py```, that should run an app that you write and compare it against a historic snapshot of what that app should look like.

When you create a new snapshot test, run it with ```pytest -vv tests/snapshot_tests/test_snapshots.py.```
Because you just created this snapshot test, there is no history to compare against and the test will fail automatically.
After running the snapshot tests, you should see a link that opens an interface in your browser.
This interface should show all failing snapshot tests and a side-by-side diff between what the app looked like when it ran VS the historic snapshot.

Make sure your snapshot app looks like it is supposed to and that you didn't break any other snapshot tests.
If that's the case, you can run ```make test-snapshot-update``` to update the snapshot history with your new snapshot.
This will write to the file ```tests/snapshot_tests/__snapshots__/test_snapshots.ambr```, that you should NOT modify by hand


### Updating the changelog
To update the changelog, **do not modify `CHANGELOG.md` directly**. Instead, *add* a file to `changelog.d` with a *one-line* description of your changes. If there are multiple changes you can add multiple files, but at that point it should probably be split into multiple PRs.

The filename should be in the format `{github_issue}.{change_type}.md` where `change_type` is one of `added`, `changed`, `fixed`, `security`, `removed`, or `deprecated`, e.g. `42.added.md`. If no issue exists (like for a simple bug-fix), then use the format *with the plus-sign prefix* `+{your_github_username}-{branch_name}.{change_type}.md`, e.g. `+willmcgugan-rendering-hotfix.fixed.md`.

Using this method (supported by [towncrier](https://github.com/twisted/towncrier)) to generate the changelog prevents merge conflicts, which allows your PR to be merged faster!


### 📈Join the community

- 😕 Seems a little overwhelming? Join our community on [Discord](https://discord.gg/uNRPEGCV) to get help.
