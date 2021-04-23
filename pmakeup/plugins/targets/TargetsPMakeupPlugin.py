import logging
from typing import Iterable, Callable

import pmakeup as pm


class TargetsPMakeupPlugin(pm.AbstractPmakeupPlugin):
    def _setup_plugin(self):
        pass

    def _teardown_plugin(self):
        pass

    def _get_dependencies(self) -> Iterable[type]:
        return []

    @pm.register_command.add("target")
    def is_target_requested(self, target_name: str) -> bool:
        """
        Check if the the user has specified the given target

        :param target_name: the name of the target that we need to check
        :return: true if the target has been declard by the user, false otherwise
        """
        return target_name in self._model.requested_target_names

    @pm.register_command.add("target")
    def declare_file_descriptor(self, description: str):
        """
        Defines what to write at the beginning of the info string that is displayed whenver the user wants to know
        what the given Pmakeupfile does

        :param description: string to show
        """
        self._model.info_description = description

    @pm.register_command.add("target")
    def declare_target(self, target_name: str, f: Callable[[], None], requires: Iterable[str] = None,
                       description: str = ""):
        """
        Declare that the user can declare a pseudo-makefile target.

        :param target_name: name of the target to declare
        :param description: a description that is shown when listing all available targets
        :param requires: list fo target names this target requires in order to be executed. They must already
            exist in pmakeup environment
        :param f: the function to perform when the user requests this target
        """
        if requires is None:
            requires = []
        if target_name in self._model.available_targets:
            raise ValueError(f"There already is a target with the name \"{target_name}\"!")
        self._model.target_network.add_node(target_name)
        self._model.available_targets[target_name] = pm.TargetDescriptor(
            name=target_name,
            description=description,
            requires=list(requires),
            function=f
        )

        for require in requires:
            self._model.target_network.add_edge(target_name, require)

    @pm.register_command.add("target")
    def get_target_descriptor(self, target_name: str) -> pm.TargetDescriptor:
        """
        Get a descriptor for a given pmakeup target. Raises exception if target is not declared

        :param target_name: name of the target
        :return: descriptor for the target
        """
        try:
            return self._model.available_targets[target_name]
        except KeyError:
            raise ValueError(
                f"No target named \"{target_name}\". Available are {', '.join(self._model.available_targets.keys())}")

    @pm.register_command.add("target")
    def process_targets(self):
        """
        Function used to process in the correct order. If the user requested to show the help for this file,
        the function will show it and return it

        It will call the function declared in declare_target
        """

        def show_target_help():
            if self._model.info_description is not None:
                print(self._model.info_description)
            for a_i, a_target_name in enumerate(self._model.available_targets):
                a_target_descriptor = self._model.available_targets[a_target_name]
                print(f" - {a_i}. {a_target_name}: {a_target_descriptor.description}")

        def perform_target(name: str, descriptor: pm.TargetDescriptor):
            if name in already_done:
                # do nothing if the node has already been processed
                return
            if name in doing:
                raise ValueError(f"Cyclic dependencies detected!")
            doing.add(name)
            out_edges = list(self._model.target_network.edges(name))
            if len(out_edges) == 0:
                # the node has no dependencies: perform the task
                descriptor.function()
            else:
                # G.edges([0, 2])
                # OutEdgeDataView([(0, 1), (2, 3)])
                for sink in map(lambda x: x[1], out_edges):
                    perform_target(sink, self._model.available_targets[sink])
                # we have satisfied all requirements. Perform this target
                descriptor.function()
            # mark the node as "already done"
            doing.remove(name)
            already_done.add(name)

        if self._model.should_show_target_help:
            show_target_help()
        else:
            doing = set()
            already_done = set()

            logging.info(f"Available targets are {', '.join(self._model.available_targets.keys())}")
            for i, target_name in enumerate(self._model.requested_target_names):
                if target_name not in self._model.available_targets:
                    raise pm.PMakeupException(
                        f"Invalid target {target_name}. Available targets are {', '.join(self._model.available_targets.keys())}")

                target_descriptor = self._model.available_targets[target_name]
                self._log_command(f"Executing target \"{target_descriptor.name}\"")
                perform_target(target_descriptor.name, target_descriptor)


TargetsPMakeupPlugin.autoregister()
