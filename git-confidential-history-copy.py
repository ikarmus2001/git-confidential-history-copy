import os
from git import Repo
from git.util import Actor
from pathlib import Path
from functions import CommitFilter, NewCommitBuilder, HistoryCopist, choose_authors, get_authors_with_counts

targetAuthor: Actor = Actor("Your name", "21372137+githubNickname@users.noreply.github.com")
targetCommitMessage = "Company secrets, can't leak that!"

def main(repo_org='./', repo_new='../repo_new'):
    repo_org = os.path.abspath(repo_org)
    repo_new = os.path.abspath(repo_new)

    if not Path(repo_org, '.git').exists():
        print(f"{repo_org} is not a valid git repo.")
        return

    sourceRepo = Repo(repo_org)

    authors_with_counts: dict[Actor, int] = get_authors_with_counts(sourceRepo)
    selected_authors: list[Actor] = choose_authors(authors_with_counts)

    print(f"Selected authors: {', '.join([str(author.email) for author in selected_authors])}")

    newRepo: Repo
    try: 
        newRepo = Repo(repo_new) 
    except: 
        newRepo = Repo.init(repo_new, mkdir=True)
     
    copist = HistoryCopist(sourceRepo, newRepo, 
                           commitFilter=CommitFilter(authors=selected_authors),
                           newCommitBuilder=NewCommitBuilder(
                               transformer_message=lambda commit: targetCommitMessage,
                               transformer_author_email=lambda commit: targetAuthor
                           ))
    copist.RunCopyHistory()
    sourceRepo.close()
    newRepo.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Mirror git commit activity.")
    parser.add_argument('--repo_org', type=str, default='./', help="Path to original repo")
    parser.add_argument('--repo_new', type=str, default='../repo_new', help="Path to new repo")

    args = parser.parse_args()
    main(args.repo_org, args.repo_new)
