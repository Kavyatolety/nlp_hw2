from gentopia.llm.llm_info import *


def calculate_cost(model_name: str, prompt_token: int, completion_token: int) -> float:
    """
    Calculate the cost of a prompt and completion.

    :param model_name: The name of the model.
    :type model_name: str
    :param prompt_token: The number of prompt tokens.
    :type prompt_token: int
    :param completion_token: The number of completion tokens.
    :type completion_token: int

    :return: The calculated cost.
    :rtype: float
    """
    # 0 if model_name is not in COSTS
    return COSTS.get(model_name, dict()).get("prompt", 0) * prompt_token \
        + COSTS.get(model_name, dict()).get("completion", 0) * completion_token
