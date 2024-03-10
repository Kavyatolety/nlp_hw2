import io
from abc import ABC, abstractmethod
from typing import List, Dict, Union, Any, Optional, Type, Callable

from gentopia import PromptTemplate
from pydantic import BaseModel, create_model

from gentopia.llm.base_llm import BaseLLM
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.memory.api import MemoryWrapper
from rich import print as rprint

from gentopia.tools import BaseTool


class BaseAgent(ABC, BaseModel):
    """Base Agent class defining the essential attributes and methods for an ALM Agent.

    :param name: The name of the agent.
    :type name: str
    :param type: The type of the agent.
    :type type: AgentType
    :param version: The version of the agent.
    :type version: str
    :param description: A brief description of the agent.
    :type description: str
    :param target_tasks: List of target tasks for the agent.
    :type target_tasks: List[str]
    :param llm: BaseLLM instance or dictionary of BaseLLM instances (eg. for ReWOO, two separate LLMs are needed).
    :type llm: Union[BaseLLM, Dict[str, BaseLLM]]
    :param prompt_template: PromptTemplate instance or dictionary of PromptTemplate instances. (eg. for ReWOO, two separate PromptTemplates are needed).
    :type prompt_template: Union[PromptTemplate, Dict[str, PromptTemplate]]
    :param plugins: List of plugins available for the agent. PLugins can be tools or other agents.
    :type plugins: List[Any]
    :param args_schema: Schema for arguments, defaults to a model with "instruction" of type str.
    :type args_schema: Optional[Type[BaseModel]]
    :param memory: An instance of MemoryWrapper.
    :type memory: Optional[MemoryWrapper]
    """

    name: str
    type: AgentType
    version: str
    description: str
    target_tasks: List[str]
    llm: Union[BaseLLM, Dict[str, BaseLLM]]
    prompt_template: Union[PromptTemplate, Dict[str, PromptTemplate]]
    plugins: List[Any]
    args_schema: Optional[Type[BaseModel]] = create_model("ArgsSchema", instruction=(str, ...))
    memory: Optional[MemoryWrapper]

    @abstractmethod
    def run(self, *args, **kwargs) -> AgentOutput:
        """Abstract method to be overridden by child classes for running the agent.

        :return: The output of the agent.
        :rtype: AgentOutput
        """
        pass

    @abstractmethod
    def stream(self, *args, **kwargs) -> AgentOutput:
        """Abstract method to be overridden by child classes for running the agent in a stream mode.

        :return: The output of the agent.
        :rtype: AgentOutput
        """
        pass

    def __str__(self):
        """Overrides the string representation of the BaseAgent object.

        :return: The string representation of the agent.
        :rtype: str
        """
        result = io.StringIO()
        rprint(self, file=result)
        return result.getvalue()

    def _format_function_map(self) -> Dict[str, Callable]:
        """Format the function map for the open AI function API.

        :return: The function map.
        :rtype: Dict[str, Callable]
        """
        # Map the function name to the real function object.
        function_map = {}
        for plugin in self.plugins:
            if isinstance(plugin, BaseTool):
                function_map[plugin.name] = plugin._run
            else:
                function_map[plugin.name] = plugin.run
        return function_map

    def clear(self):
        """
        Clear and reset the agent.
        """
        pass
