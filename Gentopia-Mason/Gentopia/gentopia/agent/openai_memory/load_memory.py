from typing import AnyStr

from gentopia.memory.api import MemoryWrapper
from gentopia.tools.basetool import *

# This tools is only used in openai_memory agent.
# DO NOT use this tool in other agent.
class LoadMemory(BaseTool):
    """A tool to recall the history of conversations. aka long term memory retrieval.

    :param name: The name of the tool.
    :type name: str
    :param description: A brief description of the tool.
    :type description: str
    :param args_schema: Schema for arguments, defaults to a model with "text" of type str.
    :type args_schema: Optional[Type[BaseModel]]
    :param memory: An instance of MemoryWrapper.
    """
    name = "load_memory"
    description = "A tool to recall the history of conversations. If you find that you do not have some information you need, you can invoke this tool with the related query string to get more information."

    args_schema: Optional[Type[BaseModel]] = create_model("LoadMemoryArgs", text=(str, ...))
    memory: MemoryWrapper

    def _run(self, text: AnyStr) -> AnyStr:
        return self.memory.load_history(text)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError
