import json
from ast import literal_eval
from json import JSONDecodeError
from typing import List, Union, Optional, Dict, Callable

from gentopia import PromptTemplate
from gentopia.agent.base_agent import BaseAgent
from gentopia.agent.openai import OpenAIFunctionChatAgent
from gentopia.llm.client.openai import OpenAIGPTClient
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.output.base_output import BaseOutput
from gentopia.prompt import VanillaPrompt
from gentopia.tools import BaseTool
from .load_memory import LoadMemory
from ...utils.cost_helpers import calculate_cost


class OpenAIMemoryChatAgent(OpenAIFunctionChatAgent):
    """
    OpenAIMemoryChatAgent class inherited from OpenAIFunctionChatAgent. Implementing OpenAI function call api as agent with long term memory.

    :param name: Name of the agent, defaults to "OpenAIAgent".
    :type name: str, optional
    :param type: Type of the agent, defaults to AgentType.openai.
    :type type: AgentType, optional
    :param version: Version of the agent.
    :type version: str
    :param description: Description of the agent.
    :type description: str
    :param target_tasks: List of target tasks for the agent.
    :type target_tasks: list[str]
    :param llm: Language model that the agent uses.
    :type llm: OpenAIGPTClient
    :param prompt_template: Template used to create prompts for the agent, defaults to None.
    :type prompt_template: PromptTemplate, optional
    :param plugins: List of plugins used by the agent, defaults to None.
    :type plugins: List[Union[BaseTool, BaseAgent]], optional
    :param examples: Fewshot examplars used for the agent, defaults to None.
    :type examples: Union[str, List[str]], optional
    :param loaded_memory_tool: Flag to check if memory tool is loaded, defaults to False.
    :type loaded_memory_tool: bool, optional

    """
    name: str = "OpenAIAgent"
    type: AgentType = AgentType.openai
    version: str = "NA"
    description: str = "OpenAI Function Call Agent with memory"
    target_tasks: list[str] = []
    llm: OpenAIGPTClient
    prompt_template: PromptTemplate = VanillaPrompt
    plugins: List[Union[BaseTool, BaseAgent]]
    examples: Union[str, List[str]] = None

    loaded_memory_tool = False
    
    def __add_system_prompt(self, messages):
        return [{"role": "system", "content": "You are a helpful AI assistant."}] + messages
    
    def __add_load_memory_tool(self):
        if self.loaded_memory_tool == False:
            self.plugins.append(LoadMemory(memory=self.memory))
            self.loaded_memory_tool = True

    def _format_plugin_schema(self, plugin: Union[BaseTool, BaseAgent]) -> Dict:
        """Format tool into the open AI function API.

        :param plugin: Tool to be formatted.
        :type plugin: Union[BaseTool, BaseAgent]
        :return: Formatted tool.
        :rtype: Dict
        """
        if isinstance(plugin, BaseTool):
            if plugin.args_schema:
                parameters = plugin.args_schema.schema()
            else:
                parameters = {
                    # This is a hack to get around the fact that some tools
                    # do not expose an args_schema, and expect an argument
                    # which is a string.
                    # And Open AI does not support an array type for the
                    # parameters.
                    "properties": {
                        "__arg1": {"title": "__arg1", "type": "string"},
                    },
                    "required": ["__arg1"],
                    "type": "object",
                }

            return {
                "name": plugin.name,
                "description": plugin.description,
                "parameters": parameters,
            }
        else:
            parameters = plugin.args_schema.schema()
            return {
                "name": plugin.name,
                "description": plugin.description,
                "parameters": parameters,
            }

    def _format_function_map(self) -> Dict[str, Callable]:
        # Map the function name to the real function object.
        function_map = {}
        for plugin in self.plugins:
            if isinstance(plugin, BaseTool):
                function_map[plugin.name] = plugin._run
            else:
                function_map[plugin.name] = plugin.run
        return function_map

    def _format_function_schema(self) -> List[Dict]:
        # List the function schema.
        function_schema = []
        for plugin in self.plugins:
            function_schema.append(self._format_plugin_schema(plugin))
        return function_schema

    def run(self, instruction: str, output: Optional[BaseOutput] = None) -> AgentOutput:
        """Run the agent with the given instruction.

        :param instruction: Instruction for the agent to run.
        :type instruction: str
        :param output: Output object for the agent to use, defaults to None.
        :type output: Optional[BaseOutput], optional
        :return: Output of the agent.
        :rtype: AgentOutput
        """
        self.clear()
        if output is None:
            output = BaseOutput()
        self.memory.clear_memory_II()
        message_scratchpad = self.__add_system_prompt(self.memory.lastest_context(instruction, output))
        total_cost = 0
        total_token = 0

        self.__add_load_memory_tool() # add a tool to load memory
        function_map = self._format_function_map()
        function_schema = self._format_function_schema()

        # TODO: stream output, cost and token usage
        output.thinking(self.name)
        # print(message_scratchpad)
        response = self.llm.function_chat_completion(message_scratchpad, function_map, function_schema)
        output.done()
        if response.state == "success":
            output.done(self.name)
            output.panel_print(response.content)
            self.memory.save_memory_I({"role": "user", "content": instruction}, response.message_scratchpad[-1], output)

            if len(response.message_scratchpad) != len(message_scratchpad) + 1: # normal case
                self.memory.save_memory_II(response.message_scratchpad[-3], response.message_scratchpad[-2], output, self.llm)       

            total_cost += calculate_cost(self.llm.model_name, response.prompt_token,
                                         response.completion_token) + response.plugin_cost
            total_token += response.prompt_token + response.completion_token + response.plugin_token
            return AgentOutput(
                output=response.content,
                cost=total_cost,
                token_usage=total_token,
            )

    def stream(self, instruction: Optional[str] = None, output: Optional[BaseOutput] = None, is_start: Optional[bool] = True):
        """Stream output the agent with the given instruction.

        :param instruction: Instruction to be run, defaults to None.
        :type instruction: str
        :param output: Output manager object to be used, defaults to None.
        :type output: Optional[BaseOutput], optional
        :param is_start: Whether this is the start of the conversation, defaults to True.
        :type is_start: Optional[bool], optional
        """
        if output is None:
            output = BaseOutput()
        output.thinking(self.name)
        if is_start:
            self.memory.clear_memory_II()
        message_scratchpad = self.__add_system_prompt(self.memory.lastest_context(instruction, output))
        output.debug(message_scratchpad)
        assert len(message_scratchpad) > 1

        self.__add_load_memory_tool() # add a tool to load memory
        function_map = self._format_function_map()
        function_schema = self._format_function_schema()
        # print(message_scratchpad)
        response = self.llm.function_chat_stream_completion(message_scratchpad, function_map, function_schema)

        ans = []
        _type = ''
        _role = ''
        for _t, item in response:
            if _type == '':
                output.done()
                output.print(f"[blue]{self.name}: ")
            _type = _t
            ans.append(item.content)
            _role = item.role 
            output.panel_print(item.content, f"[green] Response of [blue]{self.name}: ", True)
        if _type == "function_call":
            ans.append('}')
            output.panel_print('}\n', f"[green] Response of [blue]{self.name}: ", True)
            # output.stream_print('}\n')
        result = ''.join(ans)
        output.clear()
        if _type == "function_call":
            try:
                result = json.loads(result)
            except JSONDecodeError:
                result = literal_eval(result)
            function_name = result["name"]
            fuction_to_call = function_map[function_name]
            function_args = result["arguments"]
            output.update_status("Calling function: {} ...".format(function_name))
            function_response = fuction_to_call(**function_args)
            output.done()

            # Postprocess function response
            if isinstance(function_response, AgentOutput):
                function_response = function_response.output
            output.panel_print(function_response, f"[green] Function Response of [blue]{function_name}: ")

            self.memory.save_memory_II(dict(role='assistant', content=None, function_call={i: str(j) for i, j in result.items()}),
                                            {"role": "function",
                                            "name": function_name,
                                            "content": function_response}, output, self.llm)
            self.stream(instruction, output=output, is_start=False)
        else:
            self.memory.save_memory_I({"role": "user", "content": instruction}, {"role": _role, "content": result}, output)
        # else:
        #     self.message_scratchpad.append({"role": "user", "content": "Summarize what you have done and continue if you have not finished."})
        #     self.stream(output=output)

