from typing import AnyStr
import requests
from bs4 import BeautifulSoup
from gentopia.tools.basetool import *


class WebPageArgs(BaseModel):
    url: str = Field(..., description="a web url to visit. You must make sure that the url is real and correct.")


class WebPage(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "web_page"
    description = "A tool to retrieve web pages through url. Useful when you have a url and need to find detailed information inside."

    args_schema: Optional[Type[BaseModel]] = WebPageArgs

    def _run(self, url: AnyStr) -> str:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            for script in soup(["script", "style"]):
                script.extract()
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            text = ' '.join(line for line in lines if line)[:4096] + '...'
            return text
        except Exception as e:
            return f"Error: {e}\n Probably it is an invalid URL."

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = WebPage()._run("https://bbc.com")
    print(ans)
