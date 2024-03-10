from typing import AnyStr, Any
import arxiv
from gentopia.tools.basetool import *


class ArxivSearchArgs(BaseModel):
    query: str = Field(..., description="a search query.")


class ArxivSearch(BaseTool):
    """Tool that adds the capability to query Axiv search api"""

    name = "arxiv_search"
    description = (
        "Search engine from Arxiv.org "
        "It returns several relevant paper Titles, Authors and short Summary."
        "Input should be a search query."
    )
    args_schema: Optional[Type[BaseModel]] = ArxivSearchArgs
    top_k: int = 5
    maxlen_per_page = 2000

    def _run(self, query: AnyStr) -> AnyStr:
        # arxiv_exceptions: Any  # :meta private:
        top_k_results = self.top_k
        doc_content_chars_max = self.maxlen_per_page
        ARXIV_MAX_QUERY_LENGTH = 300
        try:
            results = arxiv.Search(
                query[: ARXIV_MAX_QUERY_LENGTH], max_results=top_k_results
            ).results()
        # except arxiv_exceptions as ex:
        except Exception as ex:
            return f"Arxiv exception: {ex}"
        docs = [
            f"Published: {result.updated.date()}\nTitle: {result.title}\n"
            f"Authors: {', '.join(a.name for a in result.authors)}\n"
            f"Summary: {result.summary}"
            for result in results
        ]
        if docs:
            return "\n\n".join(docs)[: doc_content_chars_max]
        else:
            return "No Arxiv Result was found"

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = ArxivSearch()._run("Attention for transformer")
    print(ans)
