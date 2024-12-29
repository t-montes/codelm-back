from utils import gptcall, tgtcall

def llmcall(prompt, model='gpt-4o', system_message=None, **kwargs):
    if model in ['gpt-4o', 'gpt-4o-mini']:
        return gptcall(prompt, model=model, system_message=system_message, **kwargs)
    elif '/' in model:
        return tgtcall(prompt, model=model, system_message=system_message, **kwargs)
    else:
        raise NotImplementedError("Platform not supported")
