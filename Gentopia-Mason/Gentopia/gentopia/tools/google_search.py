from typing import AnyStr
from googlesearch import search
from gentopia.tools.basetool import *


class GoogleSearchArgs(BaseModel):
    query: str = Field(..., description="a search query")


class GoogleSearch(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "google_search"
    description = ("A search engine retrieving top search results as snippets from Google."
                   "Input should be a search query.")

    args_schema: Optional[Type[BaseModel]] = GoogleSearchArgs

    def _run(self, query: AnyStr) -> str:
        return '\n\n'.join([str(item) for item in search(query, advanced=True)])

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = GoogleSearch()._run("Attention for transformer")
    print(ans)
