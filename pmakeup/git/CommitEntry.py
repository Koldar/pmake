from datetime import datetime


class CommitEntry:

    def __init__(self, hash: str, author: str, author_email: str, author_date: datetime, commit_date: datetime, title: str, description: str):
        