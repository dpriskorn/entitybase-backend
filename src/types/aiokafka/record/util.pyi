from ._crecords import (
    crc32c_cython as crc32c_cython,
    decode_varint_cython as decode_varint_cython,
    encode_varint_cython as encode_varint_cython,
    size_of_varint_cython as size_of_varint_cython,
)
from aiokafka.util import NO_EXTENSIONS as NO_EXTENSIONS
from collections.abc import Callable as Callable, Iterable

def encode_varint_py(value: int, write: Callable[[int], None]) -> int: ...
def size_of_varint_py(value: int) -> int: ...
def decode_varint_py(buffer: bytearray, pos: int = 0) -> tuple[int, int]: ...
def calc_crc32c_py(memview: Iterable[int]) -> int: ...

calc_crc32c: Callable[[bytes | bytearray], int]
decode_varint: Callable[[bytearray, int], tuple[int, int]]
size_of_varint: Callable[[int], int]
encode_varint: Callable[[int, Callable[[int], None]], int]
calc_crc32c = calc_crc32c_py
decode_varint = decode_varint_py
size_of_varint = size_of_varint_py
encode_varint = encode_varint_py
decode_varint = decode_varint_cython
encode_varint = encode_varint_cython
size_of_varint = size_of_varint_cython
calc_crc32c = crc32c_cython
calc_crc32c = calc_crc32c_py
decode_varint = decode_varint_py
size_of_varint = size_of_varint_py
encode_varint = encode_varint_py
