Quick project for filling the contributions graph 
- show the amount of work you put in repos you can't or don't want to push to GitHub 
(for various reasons, such as confidentiality or embarrassment of public display).

Made with [GitPython](https://github.com/gitpython-developers/GitPython)

# Installation
Clone the repo and get the required packages
(you probably want to enclose it in venv)
```
git clone https://github.com/ikarmus2001/git-confidential-history-copy.git 
cd .\git-confidential-history-copy
pip install -r requirements.txt
```

# Usage
```
py git-confidential-history-copy 
    --repo_org P:\aths\can\be\absolute
    --repo_new ..\or\relative
```
> [!IMPORTANT]
> Script doesn't push or publish the repo - you should review it manually before you publish it anywhere.

Arguments:
    `repo_org`: Mandatory - you have to select the repo you want to use as base
    `repo_new`: Optional - defaults to `../repo_new` - Target repository (created if not present, including dir)

The script will list all authors found in your repo, you have to select ones you want to select "as you", so you won't create commits for someone elses code.

> [!NOTE]
> You might be listed few times if you used git web interface or few git clients - for me it was just one record.

> [!IMPORTANT]
> Running script few times will create the same commits over and over, some validation could be implemented (probably using original SHA stored in new commit's message). 
> You might use it for your advantage to merge few histories into one.

Example:
```
PS M:\GitRepos\git-confidential-history-copy> py git-confidential-history-copy.py --repo_org 'M:\\GitRepos\\my\\repo' --repo_new '../my_new_repo'
Select author(s) from list (e.g. 0,2,5):
[0] Joe Doe                        joe.doe@whatever.pl                                commits:  2137
[1] Joe Doe                        joe.doe@whatever.pl                                commits:   123
[2] Joe Doe                        joe.doe@whatever.pl                                commits:    12
[3] Joe Doe                        joe.doe@whatever.pl                                commits:     1
[4] Joe Doe                        joe.doe@whatever.pl                                commits:  3119
[5] Kacper Hałaczkiewicz           kacper.halaczkiewicz@mydomain.pl                   commits:   683
...
[70] Joe Doe                       joe.doe@whatever.pl                                commits:  3119
Authors (comma-separated): 5
Selected authors: kacper.halaczkiewicz@mydomain.pl
Found 683 commits to copy.
History copied successfully.
```
Optionally you can implement your own lambdas to filter out commits (`CommitFilter`) and/or generate commit messages, alter dates and commit author (`NewCommitBuilder`) - but for that you have to code it yourself.

# How does it work?
Thanks to the [GitPython](https://github.com/gitpython-developers/GitPython), script is really simple:
1. it reads all commits from `repo_org`, applying filters from `CommitFilter`
2. transforms real commit to anonymised one (`NewCommitBuilder`)
3. commits them to your `repo_new`

There are a lot of things that can be made better, 
I'm not planning on developing it further, but feel free to PR or contact me.

> [!TIP]
> For your convenience, I left `.vscode` directory with `launch.json` and `.code-workspace` file :)