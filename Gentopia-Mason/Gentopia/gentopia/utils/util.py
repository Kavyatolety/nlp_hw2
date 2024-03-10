from gentopia.model.param_model import BaseParamModel

def get_default_client_param_model(model_name: str) -> BaseParamModel:
    """
    Get the default client parameter model.
    :param model_name: The name of the model.
    :type model_name: str
    :return: The default client parameter model.
    :rtype: BaseParamModel
    """
    return None


def check_huggingface():
    try:
        import torch
        import transformers
        import optimum
        import peft
        return True
    except ImportError:
        return False


    

def print_tree(obj, indent=0):
    """
    Print the tree structure of an object.

    :param obj: The object to print the tree structure of.
    :type obj: Any

    :param indent: The indentation level.
    :type indent: int

    :return: None
    :rtype: None
    """
    for attr in dir(obj):
        if not attr.startswith('_'):
            value = getattr(obj, attr)
            if not callable(value):
                if not isinstance(value, dict) and not isinstance(value, list):
                    print('|   ' * indent + '|--', f'{attr}: {value}')
                else:
                    if not value:
                        print('|   ' * indent + '|--', f'{attr}: {value}')
                    print('|   ' * indent + '|--', f'{attr}:')
                if hasattr(value, '__dict__'):
                    print_tree(value, indent + 1)
                elif isinstance(value, list):
                    for item in value:
                        print_tree(item, indent + 1)
                elif isinstance(value, dict):
                    for key, item in value.items():
                        print_tree(item, indent + 1)
