import os
import time
from collections import defaultdict
from types import SimpleNamespace

import openai
import math

from util import metadata

openai.api_key = os.environ["OPENAI_API_KEY"]


def logprobs_to_probs(probs):
    return [math.exp(x) for x in probs]


def total_logprob(response):
    logprobs = response['logprobs']['token_logprobs']
    logprobs = [i for i in logprobs if not math.isnan(i)]
    return sum(logprobs)


@metadata(usage_count=defaultdict(int), override=defaultdict(lambda: False))
def _request_limiter(engine):
    limits = {
        "ada": 5000,
        "babbage": 1000,
        "curie": 500,
        "davinci": 100
    }
    _request_limiter.meta["usage_count"][engine] += 1

    if (not _request_limiter.meta["override"]["engine"]
            and _request_limiter.meta["usage_count"][engine] > limits.get(engine, 1000)):

        resp = input(f"{engine} has been used {_request_limiter.meta['usage_count'][engine]} times.\n"
                     f" Are you sure you want to continue and turn off limits? Type {engine} to resume:\n")
        if resp.lower().strip() == engine:
            _request_limiter.meta["override"]["engine"] = True
        else:
            print("STOPPING RESPONSE GENERATION. Quit the program or allow it to finish")
            raise PermissionError(f"{engine} has run too many times: {_request_limiter.meta['usage_count'][engine]}")


def query(prompt, engine="ada", temperature=0.0, attempts=3, delay=1, max_tokens=200, stop=["\n"]):
    try:
        _request_limiter(engine)
    except PermissionError as e:
        return SimpleNamespace(choices=[defaultdict(int)])

    if attempts < 1:
        raise TimeoutError
    try:
        return openai.Completion.create(
            engine=engine,
            prompt=prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            echo=False,
            top_p=1,
            n=1,
            stop=stop,
            timeout=15,
        )
    except Exception as e:
        print(f"Failed to query, {attempts} attempts remaining, delay={delay}")
        print(e)
        time.sleep(delay)
        return query(prompt, engine, attempts=attempts-1, delay=delay*2)


def main():
    pass
    # while True:
    #     print(query("", "ada").choices[0]["text"])


if __name__ == "__main__":
    main()

