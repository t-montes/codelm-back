from openai import OpenAI as OpenAiClient
from openai._exceptions import ContentFilterFinishReasonError, RateLimitError
import time

gpt_client = OpenAiClient() # OPENAI_API_KEY

def request(prompt, model='gpt-4o', system_message=None, prev_msgs=[], max_retries=3, retry_delay=60, try_count=0, max_tokens=4096, temperature=0, seed=None):
    msgs = prev_msgs
    if system_message:
        msgs.append({"role": "system", "content": system_message})
    msgs.append({"role": "user", "content": prompt})

    try:
        response = gpt_client.chat.completions.create(
            model=model,
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed, # seed for deterministic completions, if set
            messages=msgs
        )
        finish_reason = response.choices[0].finish_reason
        if finish_reason == "content_filter":
            raise ContentFilterFinishReasonError(response.choices[0].content_filter_results)
        return response.choices[0].message.content
    except Exception as e:
        response = ""
        if "Max retries exceeded with url" in f"{e}":
            if try_count >= max_retries:
                raise RateLimitError(f"Max retries exceeded with url: {e}")
            print(f"RETRYING ({try_count})...")
            time.sleep(retry_delay)
            return request(prompt, model, system_message, prev_msgs, max_retries, retry_delay, try_count+1, max_tokens, temperature, seed)
        raise e
