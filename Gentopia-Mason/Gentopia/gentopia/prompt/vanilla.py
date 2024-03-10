from gentopia.prompt import PromptTemplate

VanillaPrompt = PromptTemplate(
    input_variables=["instruction"],
    template="""{instruction}"""
)

FewShotVanillaPrompt = PromptTemplate(
    input_variables=["instruction", "fewshot"],
    template="""{fewshot}
    
{instruction}"""
)
