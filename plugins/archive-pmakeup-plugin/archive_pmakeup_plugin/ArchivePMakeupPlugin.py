import os
import shutil
from typing import Iterable

import pmakeup as pm


class ArchivePMakeupPlugin(pm.AbstractPmakeupPlugin):

    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("archive")
    def zip_files(self, files: Iterable[pm.path], zip_name: pm.path, zip_format: str, base_dir: str = None,
                  create_folder_in_zip_file: bool = False, folder_name_in_zip_file: str = None) -> pm.path:
        """
        Zip the files into a single zip file

        :param files: the files to zip. Accepts folders as well. In this case the whole tree will be archived
        :param base_dir: when the files you want to copy are all inside a commons directory (either directed or undirected), you may want to save such files inside
        a directory hierarchy (e.g., you want to archive a/b/foo/c.txt and a/b/foo/d.txt by creating subfolder foo, but not folders a/b.
        To do so, set this parameter (in the example as a/b/foo)
        :param zip_name: name of the zip file
        :param zip_format: values accepted by shutil make_achive (i.e., zip,tar, gztar, bztar, xztar)
        :param create_folder_in_zip_file: if true, we will create a temp directory where all the files are copied. Then, we will zip that directory
        :param folder_name_in_zip_file: if create_folder_in_zip_file is specified, the name of temp folder to create
        """

        zip_basename = self.paths.get_basename_with_no_extension(zip_name)
        base_dir = base_dir or self.paths.cwd()

        with self.get_plugin("TempFilesPMakeupPlugin").create_temp_directory_with("zip_files") as folder_abspath:
            if create_folder_in_zip_file:
                copy_into = self.files.create_empty_directory(self.paths.abs_path(folder_abspath, folder_name_in_zip_file))
            else:
                copy_into = folder_abspath
            zip_root = folder_abspath
            for f in files:
                abs_f = self.paths.abs_path(f)
                dst = os.path.join(copy_into, self.paths.get_relative_path_wrt(abs_f, reference=self.paths.abs_path(base_dir)))
                self.files.copy_tree(abs_f, dst)

            result = shutil.make_archive(
                base_name=zip_basename,
                format=zip_format,
                root_dir=zip_root
            )

            return result
