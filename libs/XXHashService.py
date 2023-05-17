import base64
from typing import Union
from xxhash import xxh32_intdigest

from libs.MersenneTwister import MersenneTwister


def CalculateHash(name: Union[bytes, str]) -> int:
    if isinstance(name, str):
        name = name.encode("utf8")
    return xxh32_intdigest(name, 0)


def CalculateHashBytes(name: Union[bytes, str]) -> bytes:
    if isinstance(name, str):
        name = name.encode("utf8")
    seed = xxh32_intdigest(name, 0)
    mersenne_twister = MersenneTwister(seed=seed)
    tmp = mersenne_twister.NextBytes(int(3*20/4))
    return base64.b64encode(tmp)
