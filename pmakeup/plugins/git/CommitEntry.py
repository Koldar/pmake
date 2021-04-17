from datetime import datetime


class CommitEntry:
    """
    Entry in the git log
    """

    def __init__(self, hash: str, author: str, author_email: str, author_date: datetime, commit_date: datetime, title: str, description: str):
        self.hash = hash
        self.author = author
        self.author_email = author_email
        self.author_date = author_date
        self.commit_date = commit_date
        self.title = title
        self.description = description

    def __str__(self):
        return f"hash={self.hash}, author={self.author}, mail={self.author_email}, date={self.author_date}, title={self.title}, description={self.description}"