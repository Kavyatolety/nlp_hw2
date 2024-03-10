from pathlib import Path

from gentopia.assembler.agent_assembler import AgentAssembler


class PluginManager:
    """Manager for agent plugins (tools or agents), providing functions to run them.

    :param config: Configuration for the plugin manager which can be a str, Path or list.
    :type config: Union[str, Path, List]
    """

    def __init__(self, config):
        if isinstance(config, str) or isinstance(config, Path):
            config = AgentAssembler(file=config)
        elif isinstance(config, list):
            config = AgentAssembler(config=config)
        config.get_agent()
        self.config = config
        self.plugins = self.config.plugins

    def run(self, name, *args, **kwargs):
        """Runs a plugin given its name.

        :param name: Name of the plugin to be run.
        :type name: str
        :raises ValueError: Raised if the plugin name is not found.
        :return: The result of the run function of the plugin.
        :rtype: Any
        """
        if name not in self.plugins:
            return "No evidence found"
        plugin = self.plugins[name]
        return plugin.run(*args, **kwargs)

    def __call__(self, plugin, *args, **kwargs):

        self.run(plugin, *args, **kwargs)

    # @property
    # def cost(self):
    #     return {name: self.plugins[name].cost for name in self.tools}
