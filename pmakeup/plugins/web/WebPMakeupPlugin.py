import os
import urllib.request
from typing import Iterable

import pmakeup as pm


class WebPMakeupPlugin(pm.AbstractPmakeupPlugin):
    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("wen")
    def download_url(self, url: str, destination: pm.path = None, ignore_if_file_exists: bool = True) -> pm.path:
        """
        Download an artifact from internet

        :param url: the url where the file is lcoated
        :param destination: the folder where the file will be created
        :param ignore_if_file_exists: if true, we will not perform the download at all
        :return: path containing the downloaded item
        """
        dst = self.paths.abs_path(destination)
        self._log_command(f"""Downloading {url} from internet into {dst}""")
        if ignore_if_file_exists and os.path.exists(dst):
            return dst

        result, http_message = urllib.request.urlretrieve(url, dst)
        return result

WebPMakeupPlugin.autoregister()
