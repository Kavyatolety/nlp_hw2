from gentopia.model.agent_model import AgentOutput


def regularize_block(block):
    """
    Regularize a block by stripping and adding a newline character at the end.

    :param block: The block of text to be regularized.
    :type block: str

    :return: The regularized block with a newline character at the end.
    :rtype: str
    """
    return block.strip("\n") + "\n"


def get_plugin_response_content(output) -> str:
    """
    Get the content of a plugin response.

    :param output: The output from a plugin.
    :type output: Any

    :return: The content of the plugin response as a string.
    :rtype: str
    """
    if isinstance(output, AgentOutput):
        return output.output
    # if isinstance(output, list) and len(output) == 1: # remove list token introduced in thread parallel.
    #     return str(output[0])
    else:
        return str(output)
