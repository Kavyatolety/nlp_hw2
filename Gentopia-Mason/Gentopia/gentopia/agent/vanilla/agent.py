from typing import List, Union, Optional

from gentopia.agent.base_agent import BaseAgent
from gentopia.llm import OpenAIGPTClient
from gentopia.utils.util import check_huggingface
if check_huggingface():
    from gentopia.llm import HuggingfaceLLMClient
from gentopia.llm.base_llm import BaseLLM
from gentopia.model.agent_model import AgentType
from gentopia.output.base_output import BaseOutput
from gentopia.prompt.vanilla import *
from gentopia.utils.cost_helpers import *
from gentopia.utils.text_helpers import *


class VanillaAgent(BaseAgent):
    """VanillaAgent class inherited from BaseAgent. Use this agent to run vanilla LLMs with no additional plugins.

    :param name: Name of the agent, defaults to "VanillaAgent".
    :type name: str, optional
    :param type: Type of the agent, defaults to AgentType.vanilla.
    :type type: AgentType, optional
    :param version: Version of the agent.
    :type version: str
    :param description: Description of the agent.
    :type description: str
    :param target_tasks: List of target tasks for the agent.
    :type target_tasks: list[str]
    :param llm: Language model that the agent uses.
    :type llm: BaseLLM
    :param prompt_template: Template used to create prompts for the agent, defaults to None.
    :type prompt_template: PromptTemplate, optional
    :param examples: Fewshot examplars used for the agent, defaults to None.
    :type examples: Union[str, List[str]], optional
    """

    name: str = "VanillaAgent"
    type: AgentType = AgentType.vanilla
    version: str
    description: str
    target_tasks: list[str]
    llm: BaseLLM
    prompt_template: PromptTemplate = None
    examples: Union[str, List[str]] = None

    def _compose_fewshot_prompt(self) -> str:
        """Compose few-shot prompt based on examples.

        :return: Few-shot prompt.
        :rtype: str
        """
        if self.examples is None:
            return ""
        if isinstance(self.examples, str):
            return self.examples
        else:
            return "\n\n".join([e.strip("\n") for e in self.examples])

    def _compose_prompt(self, instruction: str) -> str:
        """Compose prompt based on instruction and few-shot examples.

        :param instruction: Instruction for the agent.
        :type instruction: str
        :return: Prompt for the agent.
        :rtype: str
        """
        fewshot = self._compose_fewshot_prompt()
        if self.prompt_template is not None:
            if "fewshot" in self.prompt_template.input_variables:
                return self.prompt_template.format(fewshot=fewshot, instruction=instruction)
            else:
                return self.prompt_template.format(instruction=instruction)
        else:
            if self.examples is None:
                return VanillaPrompt.format(instruction=instruction)
            else:
                return FewShotVanillaPrompt.format(fewshot=fewshot, instruction=instruction)

    def run(self, instruction: str, output: Optional[BaseOutput] = None) -> AgentOutput:
        """Run the agent given an instruction.

        :param instruction: Instruction for the agent.
        :type instruction: str
        :param output: Output object to print the results, defaults to None.
        :type output: Optional[BaseOutput], optional
        :return: AgentOutput object containing the output, cost and token usage.
        :rtype: AgentOutput
        """
        prompt = self._compose_prompt(instruction)
        if output is None:
            output = BaseOutput()
        output.thinking(self.name)
        response = self.llm.completion(prompt)
        output.done()
        output.print(response.content)
        total_cost = calculate_cost(self.llm.model_name, response.prompt_token,
                                    response.completion_token)
        total_token = response.prompt_token + response.completion_token

        return AgentOutput(
            output=response.content,
            cost=total_cost,
            token_usage=total_token)

    def stream(self, instruction: str, output: Optional[BaseOutput] = None):
        """Stream the agent given an instruction.

        :param instruction: Instruction for the agent.
        :type instruction: str
        :param output: Output object to print the results, defaults to None.
        :type output: Optional[BaseOutput], optional
        """
        prompt = self._compose_prompt(instruction)
        if output is None:
            output = BaseOutput()
        output.thinking(self.name)
        if isinstance(self.llm, OpenAIGPTClient):
            response = self.llm.stream_chat_completion([{"role": "user", "content": prompt}])
        elif isinstance(self.llm, HuggingfaceLLMClient):
            #TODO: Is there a better way to format chat message for open LLMs? For example, 'user:\nAI:\n'
            response = self.llm.stream_chat_completion(prompt)
        else:
            raise ValueError("LLM type not currently supported.")
        output.done()
        output.print(f"[blue]{self.name}: ")
        for i in response:
            output.panel_print(i.content, self.name, True)
        output.clear()
