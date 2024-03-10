from typing import AnyStr
from googlesearch import search
from pydantic import BaseModel, Field
from gentopia.tools.basetool import BaseTool
import PyPDF2
import requests
from io import BytesIO


class GoogleSearchArgs(BaseModel):
    query: str = Field(..., description="a search query")


class GoogleSearch(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "pdf_extractor"
    description = ("A search engine retrieving top search results as snippets from Google."
                   "Input should be a search query.")

    args_schema = GoogleSearchArgs

    def _run(self, query: AnyStr) -> str:
        search_results = search(query, num=5, stop=5, pause=2.0)
        pdf_texts = []
        for url in search_results:
            if url.endswith(".pdf"):
                pdf_text = self._extract_text_from_pdf(url)
                pdf_texts.append(pdf_text)
        return "\n\n".join(pdf_texts)

    def _extract_text_from_pdf(self, pdf_url: str) -> str:
        response = requests.get(pdf_url)
        pdf_file = BytesIO(response.content)
        text = ""
        with pdf_file, open(pdf_file, "rb") as f:
            reader = PyPDF2.PdfFileReader(f)
            num_pages = reader.numPages
            for page_number in range(num_pages):
                page = reader.getPage(page_number)
                text += page.extractText()
        return text

    async def _arun(self, *args, **kwargs):
        raise NotImplementedError


if __name__ == "__main__":
    ans = GoogleSearch()._run("Attention for transformer")
    print(ans)
