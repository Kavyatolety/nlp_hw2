from .basetool import BaseTool
from .google_search import GoogleSearch
from .google_scholar import *
from .calculator import Calculator
from .wikipedia import Wikipedia
from .wolfram_alpha import WolframAlpha
from .web_page import WebPage
from .arxiv_search import ArxivSearch
from .weather import *
from .shell import RunShell
from .search_doc import SearchDoc
from .gradio import *
from .code_interpreter import PythonCodeInterpreter
from .file_operation import WriteFile, ReadFile
from .duckduckgo import DuckDuckGo

def load_tools(name: str) -> BaseTool:
    name2tool = {
        "arxiv_search": ArxivSearch,
        "calculator": Calculator,
        "python_code_interpreter": PythonCodeInterpreter,
        "write_file": WriteFile,
        "read_file": ReadFile,
        "google_search": GoogleSearch,
        "text_to_speech": TTS,
        "image_caption": ImageCaption,
        "text_to_image": TextToImage,
        "text_to_video": TextToVideo,
        "image_to_prompt": ImageToPrompt,
        "search_doc": SearchDoc,
        "bash_shell": RunShell,
        "get_future_weather": GetFutureWeather,
        "get_today_weather": GetTodayWeather,
        "wikipedia": Wikipedia,
        "web_page": WebPage,
        "wolfram_alpha": WolframAlpha,
        "duckduckgo": DuckDuckGo,
        "search_author_by_name": SearchAuthorByName,
        "search_author_by_interests": SearchAuthorByInterests,
        "author_uid2paper": AuthorUID2Paper,
        "search_paper": SearchPaper,
        "search_single_paper": SearchSinglePaper,
        "search_related_paper": SearchRelatedPaper,
        "search_cite_paper": SearchCitePaper
    }
    if name not in name2tool:
        raise NotImplementedError
    return name2tool[name]
