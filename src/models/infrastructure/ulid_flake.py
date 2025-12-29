import time
import random


def generate_ulid_flake() -> int:
    timestamp_ms = int(time.time() * 1000)
    timestamp_bits = timestamp_ms & ((1 << 42) - 1)
    randomness_bits = random.getrandbits(21)
    sign_bit = 0
    ulid_flake = (sign_bit << 63) | (timestamp_bits << 21) | randomness_bits
    return ulid_flake
