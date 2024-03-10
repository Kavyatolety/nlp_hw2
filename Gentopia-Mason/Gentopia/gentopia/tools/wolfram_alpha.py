import os
from typing import AnyStr

import wolframalpha
from gentopia.tools.basetool import *


class CustomWolframAlphaAPITool:
    def __init__(self):
        self.app_id = os.getenv("WOLFRAM_ALPHA_APPID")
        self.wolfram_client = wolframalpha.Client(self.app_id)

    def run(self, query: str) -> str:
        """Run query through WolframAlpha and parse result."""
        res = self.wolfram_client.query(query)

        try:
            answer = next(res.results).text
        except StopIteration:
            return "Wolfram Alpha wasn't able to answer it"

        if answer is None or answer == "":
            return "No good Wolfram Alpha Result was found"
        else:
            return f"Answer: {answer}"


class WolframAlphaArgs(BaseModel):
    query: str = Field(..., description="a query or equations to be solved.")


class WolframAlpha(BaseTool):
    name = "wolfram_alpha"
    description = "A WolframAlpha search engine. Useful when you need to search for scientific knowledge or solve a Mathematical and Algebraic equation."
    args_schema: Optional[Type[BaseModel]] = WolframAlphaArgs

    def _run(self, query: AnyStr) -> AnyStr:
        tool = CustomWolframAlphaAPITool()
        evidence = tool.run(query).replace("Answer:", "").strip()
        return evidence

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = WolframAlpha()._run("What is Mars?")
    print(ans)
