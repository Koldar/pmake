# import re
# from datetime import datetime
# from typing import Iterable, Any
#
# import pmakeup as pm
#
#
# class GitPMakeupPlugin(pm.AbstractPmakeupPlugin):
#
#     def _setup_plugin(self):
#         pass
#
#     def _teardown_plugin(self):
#         pass
#
#     def _get_dependencies(self) -> Iterable[type]:
#         return []
#
#
#
#     @pm.register_command.add("git")
#     def get_git_commit(self, *folder) -> str:
#         """
#         Call from the given directory "git status" in order to retrieve the current commit. If the path is relative,
#         it is relative to the cwd
#
#         :param folder: the folder we need to call "git status" in
#         :return: the commit hash
#         """
#         p = self._abs_wrt_cwd(*folder)
#         result, stdout, stderr = self.platform.execute_return_stdout(
#             commands=[["git", "rev-parse", "HEAD"]],
#             cwd=p,
#         )
#         return stdout.strip()
#
#     @pm.register_command.add("git")
#     def get_git_branch(self, *folder) -> str:
#         """
#         Call from the given directory "git" in order to retrieve the current branch.
#         If the path is relative, it is relative to the cwd
#
#         :param folder: the folder we need to call "git status" in
#         :return: the current branch name
#         """
#         p = self._abs_wrt_cwd(*folder)
#         result, stdout, stderr = self.platform.fire_command_and_capture_stdout(
#             commands=[["git", "branch", "--show-current"]],
#             cwd=p,
#         )
#         return stdout.strip()
#
#     @pm.register_command.add("git")
#     def is_git_repo_clean(self, *folder) -> bool:
#         """
#         Call from the given directory "git" in order to retrieve if the associated git repo has no changes.
#         If the path is relative, it is relative to the cwd
#
#         :param folder: the folder we need to call "git status" in
#         :return: True if the repo has no changes to be made, false otherwise
#         """
#         p = self._abs_wrt_cwd(*folder)
#         result, stdout, stderr = self.platform.fire_command_and_capture_stdout(
#             commands=[["git", "status"]],
#             cwd=p,
#         )
#         return "nothing to commit, working tree clean" in stdout
#
#     @pm.register_command.add("git")
#     def git_config(self, name: str, value: Any, cwd: pm.path):
#         """
#         Call "git config" program
#
#         :param name: name fo the property to set (e.g., user.name)
#         :param value: value of the property to set
#         :param cwd: directory where to execute the commit (needs to be a git repository)
#         """
#         self.execute_return_stdout(
#             commands=[["git", "config", name, f"\"{value}\""]],
#             cwd=cwd,
#         )
#
#     @pm.register_command.add("git")
#     def git_get_local_latest_tag(self, cwd: pm.path) -> str:
#         """
#         Get the latest tag present in the local repository. If tag is present, raise an exception
#
#         :param cwd: path inside a git repository
#         :return: latest tag name
#         """
#         exit_code, stdout, stderr = self.execute_return_stdout(
#             commands=[["git", "describe"]],
#             cwd=cwd,
#         )
#         return stdout.strip()
#
#     @pm.register_command.add("git")
#     def git_log(self, cwd: pm.path, start_commit: str, end_commit: str) -> Iterable[pm.CommitEntry]:
#         """
#         generate the log entry
#
#         :param cwd: git repository to manage
#         :param start_commit: initial commit to filter the log. Either a commit hash, HEAD pattern or a tag name.
#         :param end_commit: end commit to filter the log. Either a commit hash, HEAD pattern or a tag name.
#         """
#
#         # use %% to print % in the command line
#         syntax = """newcommit%%ncommit:%%H%%nsubject:%%s%%nauthorname:%%aN%%nauthormail:%%aE%%nauthordate:%%aI%%nbody:%%b%%nendcommit"""
#
#         exit_code, stdout, stderr = self.execute_return_stdout(
#             commands=[["git", "log", "--date=iso", f"""--pretty=format:{syntax}""", f"{start_commit}..{end_commit}"]],
#             cwd=cwd,
#             check_exit_code=True
#         )
#         commit_hash: str = ""
#         subject: str = ""
#         body: str = ""
#         author_name: str = ""
#         author_mail: str = ""
#         author_date: datetime = datetime.utcnow()
#         body_started: bool = False
#         for line in map(lambda x: x.strip(), stdout.splitlines()):
#             if line == "newcommit":
#                 commit_hash = ""
#                 subject = ""
#                 body = ""
#                 author_name = ""
#                 author_mail = ""
#                 author_date = datetime.utcnow()
#                 body_started = False
#                 continue
#             if line == "endcommit":
#                 yield pm.CommitEntry(
#                     hash=commit_hash,
#                     author=author_name,
#                     author_email=author_mail,
#                     author_date=author_date,
#                     commit_date=author_date,
#                     title=subject,
#                     description=body
#                 )
#                 continue
#             m = re.match(r"^commit:(?P<hash>.+)$", line)
#             if m is not None:
#                 commit_hash = m.group("hash")
#             else:
#                 m = re.match(r"^subject:(?P<subject>.+)$", line)
#                 if m is not None:
#                     subject = m.group("subject")
#                 else:
#                     m = re.match(r"^authorname:(?P<authorname>.+)$", line)
#                     if m is not None:
#                         author_name = m.group("authorname")
#                     else:
#                         m = re.match(r"^authormail:(?P<authormail>.+)$", line)
#                         if m is not None:
#                             author_mail = m.group("authormail")
#                         else:
#                             m = re.match(r"^authordate:(?P<authordate>.+)$", line)
#                             if m is not None:
#                                 author_date = datetime.fromisoformat(m.group("authordate"))
#                             else:
#                                 m = re.match(r"^body:(?P<body>.*)$", line)
#                                 if m is not None:
#                                     body = m.group("body")
#                                     body_started = True
#                                 else:
#                                     if body_started:
#                                         # it is still part of the body
#                                         body = body + "\n" + line
#                                     elif line.strip() == "":
#                                         continue
#                                     else:
#                                         raise ValueError(f"Cannot detect where this line belongs to! Line is \"{line}\"")
#
#     @pm.register_command.add("git")
#     def git_commit(self, message: str, cwd: pm.path):
#         """
#         Perform a commit in the given git repository
#
#         :param message: message used to commit
#         :param cwd: directory where to execute the commit (needs to be a git repository)
#         """
#         self.platform.fire_command_and_wait(
#             commands=[["git", "commit", "-m", f"\"{message}\""]],
#             cwd=cwd,
#         )
#
#     @pm.register_command.add("git")
#     def git_push(self, remote: str, cwd: pm.path, push_tags_as_well: bool = True):
#         """
#         Perform a git push command
#
#         :param remote: the remote where you want to push
#         :param cwd: directory where to execute the commit (needs to be a git repository)
#         :param push_tags_as_well: if true, we will push tags as well
#         """
#         push_cmd = ["git", "push", remote]
#         if push_tags_as_well:
#             push_cmd.append("--tags")
#         self.platform.fire_command_and_wait(
#             commands=[push_cmd],
#             cwd=cwd,
#         )
#
#     @pm.register_command.add("git")
#     def git_add_remote(self, remote_name: str, remote_url: str, cwd: pm.path):
#         """
#         Perform a "git remote add", used to add a remote on the current cworking directory
#
#         :param remote_name: name of the remote to add
#         :param remote_url: url of the remote to add
#         :param cwd: directory where to execute the commit (needs to be a git repository)
#         """
#
#         self.platform.fire_command_and_wait(
#             commands=[["git", "remote", "add", remote_name, f"\"{remote_url}\""]],
#             cwd=cwd,
#         )
#
#     @pm.register_command.add("git")
#     def git_create_tag(self, tag_name: str, description: str, cwd: pm.path):
#         """
#         Perform a "git remote add", used to add a remote on the current cworking directory
#
#         :param tag_name: name of the tag.
#         :param description: description of the tag
#         :param cwd: directory where to execute the commit (needs to be a git repository)
#         """
#
#         self.platform.fire_command_and_wait(
#             commands=[["git", "tag", "-a", f"\"{tag_name}\"", "-m", f"\"{description}\""]],
#             cwd=cwd
#         )