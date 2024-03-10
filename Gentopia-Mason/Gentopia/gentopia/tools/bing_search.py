import os
from enum import Enum
from typing import AnyStr

import requests
from bs4 import BeautifulSoup

from .basetool import *


class BingAPI:
    """
    A class for performing searches on the Bing search engine.

    Attributes
    ----------
    bing_api : BingAPI
        The Bing API to use for performing searches.

    Methods
    -------
    __init__(self, subscription_key: str) -> None:
        Initialize the BingSearch instance with the given subscription key.
    search_top3(self, key_words: str) -> List[str]:
        Perform a search on the Bing search engine with the given keywords and return the top 3 search results.
    load_page_index(self, idx: int) -> str:
        Load the detailed page of the search result at the given index.
    """
    def __init__(self, subscription_key : str) -> None:
        """
        Initialize the BingSearch instance with the given subscription key.

        Parameters
        ----------
        subscription_key : str
            The subscription key to use for the Bing API.
        """
        self._headers = {
            'Ocp-Apim-Subscription-Key': subscription_key
        }
        self._endpoint = "https://api.bing.microsoft.com/v7.0/search"
        self._mkt = 'en-US'
    
    def search(self, key_words : str, max_retry : int = 3):
        for _ in range(max_retry):
            try:
                result = requests.get(self._endpoint, headers=self._headers, params={'q': key_words, 'mkt': self._mkt }, timeout=10)
            except Exception:
                # failed, retry
                continue

            if result.status_code == 200:
                result = result.json()
                # search result returned here
                return result
            else:
                # failed, retry
                continue
        raise RuntimeError("Failed to access Bing Search API.")
    
    def load_page(self, url : str, max_retry : int = 3) -> Tuple[bool, str]:
        for _ in range(max_retry):
            try:
                res = requests.get(url, timeout=15)
                if res.status_code == 200:
                    res.raise_for_status()
                else:
                    raise RuntimeError("Failed to load page, code {}".format(res.status_code))
            except Exception:
                # failed, retry
                res = None
                continue
            res.encoding = res.apparent_encoding
            content = res.text
            break
        if res is None:
            return False, "Timeout for loading this page, Please try to load another one or search again."
        try:
            soup = BeautifulSoup(content, 'html.parser')
            paragraphs = soup.find_all('p')
            page_detail = ""
            for p in paragraphs:
                text = p.get_text().strip()
                page_detail += text
            return True, page_detail
        except Exception:
            return False, "Timeout for loading this page, Please try to load another one or search again."


class CONTENT_TYPE(Enum):
    SEARCH_RESULT = 0
    RESULT_TARGET_PAGE = 1


class ContentItem:
    def __init__(self, type: CONTENT_TYPE, data):
        self.type = type
        self.data = data


class SessionData:
    content = []
    curResultChunk = 0


class BingSearch(BaseTool):
    api_key: str = os.getenv("BING_API_KEY")
    search_engine: BingAPI = BingAPI(api_key)
    session_data: SessionData = SessionData()


class BingSearchTop3(BingSearch):
    """Tool that adds the cability to query Bing search API,
    return top-3 search results
    """

    name = "BingSearchTop3"
    description = "search from Bing and return top-3 results." \
                  "Input should be a search query."
    args_schema: Optional[Type[BaseModel]] = create_model("BingSearchTop3Args", query=(str, ...))

    def _run(self, query: AnyStr) -> AnyStr:
        top3 = self.search_all(query)[:3]
        output = ""
        for idx, item in enumerate(top3):
            output += "page: " + str(idx+1) + "\n"
            output += "title: " + item['name'] + "\n"
            output += "summary: " + item['snippet'] + "\n"
        return output

    def search_all(self, key_words: str) -> list:
        """Search key_words, return a list of class SearchResult.
        Keyword arguments:
        key_words -- key words want to search
        """
        result = self.search_engine.search(key_words)
        self.session_data.content = []
        self.session_data.content.append(ContentItem(CONTENT_TYPE.SEARCH_RESULT, result))
        self.session_data.curResultChunk = 0
        return self.session_data.content[-1].data["webPages"]["value"]

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


class BingSearchLoadPage(BingSearch):
    """select one page from the results of BingSearchTop3 and
       check the details3
    """

    name = "BingSearchLoadPage"
    description = "Load page details of the search results from BingsearchTop3" \
                  "Input should be an index starting from 1."
    args_schema: Optional[Type[BaseModel]] = create_model("BingSearchLoadPageArgs", idx=(int, ...))

    def _run(self, idx: int) -> AnyStr:
        href, text = self.load_page(idx-1)
        if len(text) > 500:
            return text[:500]
        else:
            return text

    def load_page(self, idx : int) -> AnyStr:
        top = self.session_data.content[-1].data["webPages"]["value"]
        ok, content = self.search_engine.load_page(top[idx]['url'])
        if ok:
            return top[idx]['url'], content
        else:
            return " ", "Timeout for loading this page, Please try to load another one or search again."

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError


        
if __name__ == "__main__":
    ans1 = BingSearchTop3()._run("What is the weather today?")
    print(ans1)
    ans2 = BingSearchLoadPage()._run(1)
    print(ans2)
