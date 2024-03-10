import json
from ast import literal_eval
from json import JSONDecodeError
from typing import List, Union, Optional, Dict

from gentopia import PromptTemplate
from gentopia.agent.base_agent import BaseAgent
from gentopia.llm.client.openai import OpenAIGPTClient
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.output.base_output import BaseOutput
from gentopia.prompt import VanillaPrompt
from gentopia.tools import BaseTool
from gentopia.utils.cost_helpers import calculate_cost


class OpenAIFunctionChatAgent(BaseAgent):
    """
    OpenAIFunctionChatAgent class inherited from BaseAgent. Implementing OpenAI function call api as agent.

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
    :param message_scratchpad: Scratchpad for storing message history.
    :type message_scratchpad: List[Dict], optional
    """
    name: str = "OpenAIFunctionCallAgent"
    type: AgentType = AgentType.openai
    version: str = "NA"
    description: str = "OpenAI Function Call Agent"
    target_tasks: list[str] = []
    llm: OpenAIGPTClient
    prompt_template: PromptTemplate = VanillaPrompt
    plugins: List[Union[BaseTool, BaseAgent]] = []
    examples: Union[str, List[str]] = None
    message_scratchpad: List[Dict] = [{"role": "system", "content": "You are a helpful AI assistant."}]

    def __init__(self, **data):
        super().__init__(**data)
        self.initialize_system_message(f"Your name is {self.name}. You are described as: {self.description}")


    def initialize_system_message(self, msg):
        """Initialize the system message to openai function call agent.

        :param msg: System message to be initialized.
        :type msg: str
        :raises ValueError: Raised if the system message is modified after run
        """
        if len(self.message_scratchpad) > 1:
            raise ValueError("System message must be initialized before first agent run")
        self.message_scratchpad[0]["content"] = msg

    def _format_plugin_schema(self, plugin: Union[BaseTool, BaseAgent]) -> Dict:
        """Format tool into the open AI function API.

        :param plugin: Plugin to be formatted.
        :type plugin: Union[BaseTool, BaseAgent]
        :return: Formatted plugin.
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

    def _format_function_schema(self) -> List[Dict]:
        """Format function schema into the open AI function API.

        :return: Formatted function schema.
        :rtype: List[Dict]
        """
        # List the function schema.
        function_schema = []
        for plugin in self.plugins:
            function_schema.append(self._format_plugin_schema(plugin))
        return function_schema

    def run(self, instruction: str, output: Optional[BaseOutput] = None) -> AgentOutput:
        """Run the agent with the given instruction.

        :param instruction: Instruction to be run.
        :type instruction: str
        :param output: Output manager object to be used, defaults to None.
        :type output: Optional[BaseOutput], optional
        """
        self.clear()
        if output is None:
            output = BaseOutput()
        self.message_scratchpad.append({"role": "user", "content": instruction})
        total_cost = 0
        total_token = 0

        function_map = self._format_function_map()
        function_schema = self._format_function_schema()

        output.thinking(self.name)
        response = self.llm.function_chat_completion(self.message_scratchpad, function_map, function_schema)
        output.done()
        if response.state == "success":
            output.done(self.name)
            output.panel_print(response.content)
            # Update message history
            self.message_scratchpad.append(response.message_scratchpad)
            total_cost += calculate_cost(self.llm.model_name, response.prompt_token,
                                         response.completion_token) + response.plugin_cost
            total_token += response.prompt_token + response.completion_token + response.plugin_token
            return AgentOutput(
                output=response.content,
                cost=total_cost,
                token_usage=total_token,
            )

    def stream(self, instruction: Optional[str] = None, output: Optional[BaseOutput] = None):
        """Stream output the agent with the given instruction.

        :param instruction: Instruction to be run, defaults to None.
        :type instruction: str
        :param output: Output manager object to be used, defaults to None.
        :type output: Optional[BaseOutput], optional
        """

        if output is None:
            output = BaseOutput()
        output.thinking(self.name)
        if instruction is not None:
            self.message_scratchpad.append({"role": "user", "content": instruction})
        output.debug(self.message_scratchpad)
        assert len(self.message_scratchpad) > 1
        function_map = self._format_function_map()
        function_schema = self._format_function_schema()
        response = self.llm.function_chat_stream_completion(self.message_scratchpad, function_map, function_schema)

        ans = []
        _type = ''
        for _t, item in response:
            if _type == '':
                output.done()
                output.print(f"[blue]{self.name}: ")
            _type = _t
            ans.append(item.content)
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
            self.message_scratchpad.append(
                dict(role='assistant', content=None, function_call={i: str(j) for i, j in result.items()}))
            self.message_scratchpad.append({"role": "function",
                                            "name": function_name,
                                            "content": function_response})
            self.stream(output=output)
        # else:
        #     self.message_scratchpad.append({"role": "user", "content": "Summarize what you have done and continue if you have not finished."})
        #     self.stream(output=output)

    def clear(self):
        self.message_scratchpad = self.message_scratchpad[:1]