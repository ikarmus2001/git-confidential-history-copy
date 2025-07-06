from typing import Tuple, Callable
from git import Repo
from git.util import Actor
from git.objects.commit import Commit
from datetime import datetime
from time import gmtime

def choose_authors(authors_with_counts: dict[Actor, int]) -> list[Actor]:
    print("Select author(s) from list (np. 0,2,5):")
    indexed = list(authors_with_counts.items())
    for i, (author, commitCount) in enumerate(indexed):
        print(f"[{i}] {author.name:<30} {author.email:<50} commits: {commitCount:>5}")
    indices = input("Authors (comma-separated): ")
    selected = [indexed[int(i)][0] for i in indices.split(',')]
    return selected

def get_authors_with_counts(repo: Repo) -> dict[Actor, int]:
    """
    Get all authors with their commit counts in the repository.
    Returns a dictionary where keys are Actor objects and values are commit counts.
    """
    authors_with_counts = {}
    for commit in repo.iter_commits():
        author = commit.author
        if author not in authors_with_counts:
            authors_with_counts[author] = 0
        authors_with_counts[author] += 1
    return authors_with_counts

class NewCommitBuilder:
    """
    Controls how new commits are created in the repository.
    Used to apply rules, more details in the ctor.
    """
    def __init__(self, 
                 transformer_message:       None | Callable[[Commit], str] = None,
                 transformer_author_email:  None | Callable[[Commit], Actor] = None,
                 transformer_commit_date:   None | Callable[[Commit], datetime] = None) -> None:
        """_summary_

        Args:
            transformer_message (None | Callable[[Commit], str], optional): Defaults to None.
                Function to construct commit message based on the supplied commit.
                If None, uses the original message.
            transformer_author_email (None | Callable[[Commit], str], optional): Defaults to None.
                Author email transformer function.
                If None, uses the original author email.
            transformer_commit_date (None | Callable[[Commit], datetime], optional): Defaults to None.
                Date transformer function.
                If None, uses the original commit date.
        """
        self.transformer_message = transformer_message
        self.transformer_author_email = transformer_author_email
        self.transformer_commit_date = transformer_commit_date
        

    def Build(self, oldCommit: Commit) -> Commit:
        """Transforms the old commit into a new commit using provided options.
        Args:
            oldCommit (Commit): original commit, passed to transformers, e.g. message_constructor.

        Returns:
            Commit: newly built commit
        """
        message         =str(self.transformer_message(oldCommit) if self.transformer_message else oldCommit.message)
        author          =self.transformer_author_email(oldCommit) if self.transformer_author_email else oldCommit.author
        committed_date  =int(self.transformer_commit_date(oldCommit).timestamp()) if self.transformer_commit_date else int(oldCommit.committed_datetime.timestamp())

        return Commit(
            repo            =oldCommit.repo,    # not necessary here
            binsha          =oldCommit.binsha,  # not necessary here
            message         =message,
            author          =author,
            committed_date  =committed_date,
        )

class CommitFilter:
    def __init__(self, 
                 dateRange: None | Tuple[datetime, datetime] = None, 
                 authors: None | Actor | list[Actor] = None) -> None:
        
        # Set filters
        self.Funcs: list[Callable[[Commit], bool]] = []
        if isinstance(dateRange, tuple) and len(dateRange) == 2 and isinstance(dateRange[0], datetime) and isinstance(dateRange[1], datetime):
            self.DateRange: Tuple[datetime, datetime] = dateRange
            self.Funcs.append(lambda commit: self.CommitDateFilter(commit))

        self.Authors: list[Actor] = [authors] if isinstance(authors, Actor) else authors if (isinstance(authors, list) and len(authors) > 0) else []
        if len(self.Authors) > 0:
            self.Funcs.append(lambda commit: self.CommitAuthorFilter(commit))


    def CommitDateFilter(self, commit: Commit) -> bool:
        return self.DateRange[0] <= commit.committed_datetime <= self.DateRange[1]

    def CommitAuthorFilter(self, commit: Commit) -> bool:
        return commit.author in self.Authors or commit.committer in self.Authors
    
    def RunFilters(self, commit: Commit) -> bool:
        for func in self.Funcs:
            if not func(commit):
                return False
        return True


class HistoryCopist:
    """
    Process description:
    1. Get all old commits (according to filters)
    2. Create new repo if needed
    3. Commit every old change to new repo
    """
    def __init__(self, 
                 sourceRepo: Repo, 
                 targetRepo: Repo, 
                 commitFilter: None | CommitFilter = None, 
                 newCommitBuilder: None | NewCommitBuilder = None) -> None:
        self.SourceRepo = sourceRepo
        self.TargetRepo = targetRepo
        self.CommitFilter = commitFilter if commitFilter else CommitFilter()
        self.NewCommitBuilder = newCommitBuilder if newCommitBuilder else NewCommitBuilder()

    def GetOldCommits(self) -> list[Commit]:
        """
        Get all commits from source repo that match the filters.
        """
        return [commit for commit in self.SourceRepo.iter_commits() if self.CommitFilter.RunFilters(commit)]
    
    def CreateNewRepo(self) -> None:
        """
        Create a new repo if it doesn't exist.
        """
        if not self.TargetRepo.bare:
            raise ValueError("Target repo is not bare.")
        self.TargetRepo.init(mkdir=True, initial_branch='main')

    def RunCopyHistory(self) -> None:
        """
        Copy history from source repo to target repo.
        """
        old_filtered_commits = self.GetOldCommits()
        if not old_filtered_commits:
            print("No commits found matching the filters.")
            return
        print(f"Found {len(old_filtered_commits)} commits to copy.")
        
        if self.TargetRepo.bare:
            self.CreateNewRepo()
        
        for commit in sorted(old_filtered_commits, key=lambda c: c.committed_datetime):
            newCommit: Commit = self.NewCommitBuilder.Build(commit)
            self.TargetRepo.index.commit(
                message=str(newCommit.message),
                author=newCommit.author,
                author_date= newCommit.committed_datetime,
                commit_date=newCommit.committed_datetime,
            )
        print("History copied successfully.") # fingers crossed, nothing thrown
        
