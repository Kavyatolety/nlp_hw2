from datetime import time
from typing import AnyStr

from bs4 import BeautifulSoup
from googlesearch import search
from gentopia.tools.basetool import *
from selenium import webdriver
from selenium.webdriver.common.by import By

class DuckDuckGoArgs(BaseModel):
    query: str = Field(..., description="a search query")


class DuckDuckGo(BaseTool):
    """Tool that adds the capability to query the Google search API."""

    name = "duckduckgo"
    description = ("A search engine retrieving top search results as snippets from DuckDuckGo."
                   "Input should be a search query.")

    args_schema: Optional[Type[BaseModel]] = DuckDuckGoArgs

    def _run(self, query: AnyStr) -> str:
        driver = webdriver.Chrome()
        driver.get(f'https://duckduckgo.com/?q={query}&t=h_&ia=web')
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
        for script in soup(["script", "style"]):
            script.extract()
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = ' '.join(line for line in lines if line)[:2048] + '...'
        return text

        # items = driver.find_element(by=By.CLASS_NAME, value='react-results--main')
        #
        # for item in items.find_elements():
        #     print(item)

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


if __name__ == "__main__":
    ans = DuckDuckGo()._run("Attention for transformer")
    print(ans)
