import logging
import re
from typing import List, Union, Optional, Type, Tuple

from gentopia import PromptTemplate

from gentopia.output.base_output import BaseOutput
from gentopia.tools.basetool import BaseTool
from pydantic import create_model, BaseModel

from gentopia.agent.base_agent import BaseAgent
from gentopia.assembler.task import AgentAction, AgentFinish
from gentopia.llm.client.openai import OpenAIGPTClient
from gentopia.model.agent_model import AgentType, AgentOutput
from gentopia.utils.cost_helpers import calculate_cost

FINAL_ANSWER_ACTION = "Final Answer:"


class ReactAgent(BaseAgent):
    """
    Sequential ReactAgent class inherited from BaseAgent. Implementing ReAct agent paradigm https://arxiv.org/pdf/2210.03629.pdf

    :param name: Name of the agent, defaults to "ReactAgent".
    :type name: str, optional
    :param type: Type of the agent, defaults to AgentType.react.
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
    :param args_schema: Schema for the arguments of the agent
    :type args_schema: Optional[Type[BaseModel]], optional
    """
    name: str = "ReactAgent"
    type: AgentType = AgentType.react
    version: str
    description: str
    target_tasks: list[str]
    llm: OpenAIGPTClient
    prompt_template: PromptTemplate
    plugins: List[Union[BaseTool, BaseAgent]]
    examples: Union[str, List[str]] = None
    args_schema: Optional[Type[BaseModel]] = create_model("ReactArgsSchema", instruction=(str, ...))

    intermediate_steps: List[Tuple[AgentAction, str]] = []

    def _compose_plugin_description(self) -> str:
        """
        Compose the worker prompt from the workers.

        Example:
        toolname1[input]: tool1 description
        toolname2[input]: tool2 description
        """
        prompt = ""
        try:
            for plugin in self.plugins:
                prompt += f"{plugin.name}[input]: {plugin.description}\n"
        except Exception:
            raise ValueError("Worker must have a name and description.")
        return prompt

    def _construct_scratchpad(
            self, intermediate_steps: List[Tuple[AgentAction, str]]
    ) -> str:
        """Construct the scratchpad that lets the agent continue its thought process."""
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought:"
        return thoughts

    def _parse_output(self, text: str) -> Union[AgentAction, AgentFinish]:
        includes_answer = FINAL_ANSWER_ACTION in text
        regex = (
            r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        )
        action_match = re.search(regex, text, re.DOTALL)
        if action_match:
            if includes_answer:
                raise Exception(
                    "Parsing LLM output produced both a final answer "
                    f"and a parse-able action: {text}"
                )
            action = action_match.group(1).strip()
            action_input = action_match.group(2)
            tool_input = action_input.strip(" ")
            # ensure if its a well formed SQL query we don't remove any trailing " chars
            if tool_input.startswith("SELECT ") is False:
                tool_input = tool_input.strip('"')

            return AgentAction(action, tool_input, text)

        elif includes_answer:
            return AgentFinish(
                {"output": text.split(FINAL_ANSWER_ACTION)[-1].strip()}, text
            )

        if not re.search(r"Action\s*\d*\s*:[\s]*(.*?)", text, re.DOTALL):
            raise Exception(
                f"Could not parse LLM output: `{text}`",
            )
        elif not re.search(
                r"[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)", text, re.DOTALL
        ):
            raise Exception(
                f"Could not parse LLM output: `{text}`"
            )
        else:
            raise Exception(f"Could not parse LLM output: `{text}`")

    def _compose_prompt(self, instruction) -> str:
        """
        Compose the prompt from template, worker description, examples and instruction.
        """
        agent_scratchpad = self._construct_scratchpad(self.intermediate_steps)
        tool_description = self._compose_plugin_description()
        tool_names = ", ".join([plugin.name for plugin in self.plugins])
        if self.prompt_template is None:
            from gentopia.prompt.react import ZeroShotReactPrompt
            self.prompt_template = ZeroShotReactPrompt
        return self.prompt_template.format(
            instruction=instruction,
            agent_scratchpad=agent_scratchpad,
            tool_description=tool_description,
            tool_names=tool_names
        )

    def run(self, instruction, max_iterations=10):
        """
        Run the agent with the given instruction.

        :param instruction: Instruction to run the agent with.
        :type instruction: str
        :param max_iterations: Maximum number of iterations of reasoning steps, defaults to 10.
        :type max_iterations: int, optional
        :return: AgentOutput object.
        :rtype: AgentOutput
        """
        self.clear()
        logging.info(f"Running {self.name + ':' + self.version} with instruction: {instruction}")
        total_cost = 0.0
        total_token = 0

        for _ in range(max_iterations):

            prompt = self._compose_prompt(instruction)
            logging.info(f"Prompt: {prompt}")
            response = self.llm.completion(prompt, stop=["Observation:"])
            if response.state == "error":
                print("Failed to retrieve response from LLM")
                raise ValueError("Failed to retrieve response from LLM")

            logging.info(f"Response: {response.content}")
            total_cost += calculate_cost(self.llm.model_name, response.prompt_token,
                                         response.completion_token)
            total_token += response.prompt_token + response.completion_token
            self.intermediate_steps.append([self._parse_output(response.content), ])
            if isinstance(self.intermediate_steps[-1][0], AgentFinish):
                break
            action = self.intermediate_steps[-1][0].tool
            tool_input = self.intermediate_steps[-1][0].tool_input
            logging.info(f"Action: {action}")
            logging.info(f"Tool Input: {tool_input}")
            result = self._format_function_map()[action](tool_input)
            if isinstance(result, AgentOutput):
                total_cost += result.cost
                total_token += result.token_usage
            logging.info(f"Result: {result}")
            self.intermediate_steps[-1].append(result)
        return AgentOutput(output=response.content, cost=total_cost, token_usage=total_token)

    def stream(self, instruction: Optional[str] = None, output: Optional[BaseOutput] = None, max_iterations: int = 10):
        """
        Stream output the agent with the given instruction.

        :param instruction: Instruction to run the agent with.
        :type instruction: str
        :param output: Output object to stream to.
        :type output: BaseOutput
        :return: AgentOutput object.
        :rtype: AgentOutput
        """
        self.clear()
        total_cost = 0.0
        total_token = 0
        if output is None:
            output = BaseOutput()
        output.thinking(self.name)
        for _ in range(max_iterations):

            prompt = self._compose_prompt(instruction)
            logging.info(f"Prompt: {prompt}")
            response = self.llm.stream_chat_completion([{"role": "user", "content": prompt}], stop=["Observation:"])
            output.done()
            content = ""
            output.print(f"[blue]{self.name}: ")
            for i in response:
                content += i.content
                output.panel_print(i.content, self.name, True)
            output.clear()

            logging.info(f"Response: {content}")
            self.intermediate_steps.append([self._parse_output(content), ])
            if isinstance(self.intermediate_steps[-1][0], AgentFinish):
                break

            action = self.intermediate_steps[-1][0].tool
            tool_input = self.intermediate_steps[-1][0].tool_input
            logging.info(f"Action: {action}")
            logging.info(f"Tool Input: {tool_input}")
            output.update_status("Calling function: {} ...".format(action))
            result = self._format_function_map()[action](tool_input)
            output.done()
            logging.info(f"Result: {result}")
            if isinstance(result, AgentOutput):
                result = result.output
            output.panel_print(result, f"[green] Function Response of [blue]{action}: ")
            self.intermediate_steps[-1].append(result)
        return AgentOutput(output=content, cost=total_cost, token_usage=total_token)

    def clear(self):
        """
        Clear and reset the agent.
        """
        self.intermediate_steps.clear()