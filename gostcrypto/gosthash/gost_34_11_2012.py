#The GOST cryptographic functions.
#
#Author: Evgeny Drobotun (c) 2020
#License: MIT

"""
The GOST hashing functions.

The module that implements the 'Streebog' hash calculation algorithm
in accordance with GOST 34.11-2012 with a hash size of 512 bits and
256 bits.  The module includes the GOST34112012 class, the GOSTHashError
class and several General functions.
"""
from copy import deepcopy
from struct import pack
from struct import unpack

from gostcrypto.utils import add_xor
from gostcrypto.utils import S_BOX

__all__ = (
    'GOST34112012',
    'new',
    'GOSTHashError'
)

_BLOCK_SIZE = 64

_V_0 = bytearray(_BLOCK_SIZE)
_V_512 = bytearray([
    0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
])

_TAU = (
    0, 8, 16, 24, 32, 40, 48, 56,
    1, 9, 17, 25, 33, 41, 49, 57,
    2, 10, 18, 26, 34, 42, 50, 58,
    3, 11, 19, 27, 35, 43, 51, 59,
    4, 12, 20, 28, 36, 44, 52, 60,
    5, 13, 21, 29, 37, 45, 53, 61,
    6, 14, 22, 30, 38, 46, 54, 62,
    7, 15, 23, 31, 39, 47, 55, 63,
)

_A = (
    0x8e20faa72ba0b470, 0x47107ddd9b505a38,
    0xad08b0e0c3282d1c, 0xd8045870ef14980e,
    0x6c022c38f90a4c07, 0x3601161cf205268d,
    0x1b8e0b0e798c13c8, 0x83478b07b2468764,
    0xa011d380818e8f40, 0x5086e740ce47c920,
    0x2843fd2067adea10, 0x14aff010bdd87508,
    0x0ad97808d06cb404, 0x05e23c0468365a02,
    0x8c711e02341b2d01, 0x46b60f011a83988e,
    0x90dab52a387ae76f, 0x486dd4151c3dfdb9,
    0x24b86a840e90f0d2, 0x125c354207487869,
    0x092e94218d243cba, 0x8a174a9ec8121e5d,
    0x4585254f64090fa0, 0xaccc9ca9328a8950,
    0x9d4df05d5f661451, 0xc0a878a0a1330aa6,
    0x60543c50de970553, 0x302a1e286fc58ca7,
    0x18150f14b9ec46dd, 0x0c84890ad27623e0,
    0x0642ca05693b9f70, 0x0321658cba93c138,
    0x86275df09ce8aaa8, 0x439da0784e745554,
    0xafc0503c273aa42a, 0xd960281e9d1d5215,
    0xe230140fc0802984, 0x71180a8960409a42,
    0xb60c05ca30204d21, 0x5b068c651810a89e,
    0x456c34887a3805b9, 0xac361a443d1c8cd2,
    0x561b0d22900e4669, 0x2b838811480723ba,
    0x9bcf4486248d9f5d, 0xc3e9224312c8c1a0,
    0xeffa11af0964ee50, 0xf97d86d98a327728,
    0xe4fa2054a80b329c, 0x727d102a548b194e,
    0x39b008152acb8227, 0x9258048415eb419d,
    0x492c024284fbaec0, 0xaa16012142f35760,
    0x550b8e9e21f7a530, 0xa48b474f9ef5dc18,
    0x70a6a56e2440598e, 0x3853dc371220a247,
    0x1ca76e95091051ad, 0x0edd37c48a08a6d8,
    0x07e095624504536c, 0x8d70c431ac02a736,
    0xc83862965601dd1b, 0x641c314b2b8ee083,
)

_C = [bytearray([
    0x07, 0x45, 0xa6, 0xf2, 0x59, 0x65, 0x80, 0xdd,
    0x23, 0x4d, 0x74, 0xcc, 0x36, 0x74, 0x76, 0x05,
    0x15, 0xd3, 0x60, 0xa4, 0x08, 0x2a, 0x42, 0xa2,
    0x01, 0x69, 0x67, 0x92, 0x91, 0xe0, 0x7c, 0x4b,
    0xfc, 0xc4, 0x85, 0x75, 0x8d, 0xb8, 0x4e, 0x71,
    0x16, 0xd0, 0x45, 0x2e, 0x43, 0x76, 0x6a, 0x2f,
    0x1f, 0x7c, 0x65, 0xc0, 0x81, 0x2f, 0xcb, 0xeb,
    0xe9, 0xda, 0xca, 0x1e, 0xda, 0x5b, 0x08, 0xb1
]), bytearray([
    0xb7, 0x9b, 0xb1, 0x21, 0x70, 0x04, 0x79, 0xe6,
    0x56, 0xcd, 0xcb, 0xd7, 0x1b, 0xa2, 0xdd, 0x55,
    0xca, 0xa7, 0x0a, 0xdb, 0xc2, 0x61, 0xb5, 0x5c,
    0x58, 0x99, 0xd6, 0x12, 0x6b, 0x17, 0xb5, 0x9a,
    0x31, 0x01, 0xb5, 0x16, 0x0f, 0x5e, 0xd5, 0x61,
    0x98, 0x2b, 0x23, 0x0a, 0x72, 0xea, 0xfe, 0xf3,
    0xd7, 0xb5, 0x70, 0x0f, 0x46, 0x9d, 0xe3, 0x4f,
    0x1a, 0x2f, 0x9d, 0xa9, 0x8a, 0xb5, 0xa3, 0x6f
]), bytearray([
    0xb2, 0x0a, 0xba, 0x0a, 0xf5, 0x96, 0x1e, 0x99,
    0x31, 0xdb, 0x7a, 0x86, 0x43, 0xf4, 0xb6, 0xc2,
    0x09, 0xdb, 0x62, 0x60, 0x37, 0x3a, 0xc9, 0xc1,
    0xb1, 0x9e, 0x35, 0x90, 0xe4, 0x0f, 0xe2, 0xd3,
    0x7b, 0x7b, 0x29, 0xb1, 0x14, 0x75, 0xea, 0xf2,
    0x8b, 0x1f, 0x9c, 0x52, 0x5f, 0x5e, 0xf1, 0x06,
    0x35, 0x84, 0x3d, 0x6a, 0x28, 0xfc, 0x39, 0x0a,
    0xc7, 0x2f, 0xce, 0x2b, 0xac, 0xdc, 0x74, 0xf5
]), bytearray([
    0x2e, 0xd1, 0xe3, 0x84, 0xbc, 0xbe, 0x0c, 0x22,
    0xf1, 0x37, 0xe8, 0x93, 0xa1, 0xea, 0x53, 0x34,
    0xbe, 0x03, 0x52, 0x93, 0x33, 0x13, 0xb7, 0xd8,
    0x75, 0xd6, 0x03, 0xed, 0x82, 0x2c, 0xd7, 0xa9,
    0x3f, 0x35, 0x5e, 0x68, 0xad, 0x1c, 0x72, 0x9d,
    0x7d, 0x3c, 0x5c, 0x33, 0x7e, 0x85, 0x8e, 0x48,
    0xdd, 0xe4, 0x71, 0x5d, 0xa0, 0xe1, 0x48, 0xf9,
    0xd2, 0x66, 0x15, 0xe8, 0xb3, 0xdf, 0x1f, 0xef
]), bytearray([
    0x57, 0xfe, 0x6c, 0x7c, 0xfd, 0x58, 0x17, 0x60,
    0xf5, 0x63, 0xea, 0xa9, 0x7e, 0xa2, 0x56, 0x7a,
    0x16, 0x1a, 0x27, 0x23, 0xb7, 0x00, 0xff, 0xdf,
    0xa3, 0xf5, 0x3a, 0x25, 0x47, 0x17, 0xcd, 0xbf,
    0xbd, 0xff, 0x0f, 0x80, 0xd7, 0x35, 0x9e, 0x35,
    0x4a, 0x10, 0x86, 0x16, 0x1f, 0x1c, 0x15, 0x7f,
    0x63, 0x23, 0xa9, 0x6c, 0x0c, 0x41, 0x3f, 0x9a,
    0x99, 0x47, 0x47, 0xad, 0xac, 0x6b, 0xea, 0x4b
]), bytearray([
    0x6e, 0x7d, 0x64, 0x46, 0x7a, 0x40, 0x68, 0xfa,
    0x35, 0x4f, 0x90, 0x36, 0x72, 0xc5, 0x71, 0xbf,
    0xb6, 0xc6, 0xbe, 0xc2, 0x66, 0x1f, 0xf2, 0x0a,
    0xb4, 0xb7, 0x9a, 0x1c, 0xb7, 0xa6, 0xfa, 0xcf,
    0xc6, 0x8e, 0xf0, 0x9a, 0xb4, 0x9a, 0x7f, 0x18,
    0x6c, 0xa4, 0x42, 0x51, 0xf9, 0xc4, 0x66, 0x2d,
    0xc0, 0x39, 0x30, 0x7a, 0x3b, 0xc3, 0xa4, 0x6f,
    0xd9, 0xd3, 0x3a, 0x1d, 0xae, 0xae, 0x4f, 0xae
]), bytearray([
    0x93, 0xd4, 0x14, 0x3a, 0x4d, 0x56, 0x86, 0x88,
    0xf3, 0x4a, 0x3c, 0xa2, 0x4c, 0x45, 0x17, 0x35,
    0x04, 0x05, 0x4a, 0x28, 0x83, 0x69, 0x47, 0x06,
    0x37, 0x2c, 0x82, 0x2d, 0xc5, 0xab, 0x92, 0x09,
    0xc9, 0x93, 0x7a, 0x19, 0x33, 0x3e, 0x47, 0xd3,
    0xc9, 0x87, 0xbf, 0xe6, 0xc7, 0xc6, 0x9e, 0x39,
    0x54, 0x09, 0x24, 0xbf, 0xfe, 0x86, 0xac, 0x51,
    0xec, 0xc5, 0xaa, 0xee, 0x16, 0x0e, 0xc7, 0xf4
]), bytearray([
    0x1e, 0xe7, 0x02, 0xbf, 0xd4, 0x0d, 0x7f, 0xa4,
    0xd9, 0xa8, 0x51, 0x59, 0x35, 0xc2, 0xac, 0x36,
    0x2f, 0xc4, 0xa5, 0xd1, 0x2b, 0x8d, 0xd1, 0x69,
    0x90, 0x06, 0x9b, 0x92, 0xcb, 0x2b, 0x89, 0xf4,
    0x9a, 0xc4, 0xdb, 0x4d, 0x3b, 0x44, 0xb4, 0x89,
    0x1e, 0xde, 0x36, 0x9c, 0x71, 0xf8, 0xb7, 0x4e,
    0x41, 0x41, 0x6e, 0x0c, 0x02, 0xaa, 0xe7, 0x03,
    0xa7, 0xc9, 0x93, 0x4d, 0x42, 0x5b, 0x1f, 0x9b
]), bytearray([
    0xdb, 0x5a, 0x23, 0x83, 0x51, 0x44, 0x61, 0x72,
    0x60, 0x2a, 0x1f, 0xcb, 0x92, 0xdc, 0x38, 0x0e,
    0x54, 0x9c, 0x07, 0xa6, 0x9a, 0x8a, 0x2b, 0x7b,
    0xb1, 0xce, 0xb2, 0xdb, 0x0b, 0x44, 0x0a, 0x80,
    0x84, 0x09, 0x0d, 0xe0, 0xb7, 0x55, 0xd9, 0x3c,
    0x24, 0x42, 0x89, 0x25, 0x1b, 0x3a, 0x7d, 0x3a,
    0xde, 0x5f, 0x16, 0xec, 0xd8, 0x9a, 0x4c, 0x94,
    0x9b, 0x22, 0x31, 0x16, 0x54, 0x5a, 0x8f, 0x37
]), bytearray([
    0xed, 0x9c, 0x45, 0x98, 0xfb, 0xc7, 0xb4, 0x74,
    0xc3, 0xb6, 0x3b, 0x15, 0xd1, 0xfa, 0x98, 0x36,
    0xf4, 0x52, 0x76, 0x3b, 0x30, 0x6c, 0x1e, 0x7a,
    0x4b, 0x33, 0x69, 0xaf, 0x02, 0x67, 0xe7, 0x9f,
    0x03, 0x61, 0x33, 0x1b, 0x8a, 0xe1, 0xff, 0x1f,
    0xdb, 0x78, 0x8a, 0xff, 0x1c, 0xe7, 0x41, 0x89,
    0xf3, 0xf3, 0xe4, 0xb2, 0x48, 0xe5, 0x2a, 0x38,
    0x52, 0x6f, 0x05, 0x80, 0xa6, 0xde, 0xbe, 0xab
]), bytearray([
    0x1b, 0x2d, 0xf3, 0x81, 0xcd, 0xa4, 0xca, 0x6b,
    0x5d, 0xd8, 0x6f, 0xc0, 0x4a, 0x59, 0xa2, 0xde,
    0x98, 0x6e, 0x47, 0x7d, 0x1d, 0xcd, 0xba, 0xef,
    0xca, 0xb9, 0x48, 0xea, 0xef, 0x71, 0x1d, 0x8a,
    0x79, 0x66, 0x84, 0x14, 0x21, 0x80, 0x01, 0x20,
    0x61, 0x07, 0xab, 0xeb, 0xbb, 0x6b, 0xfa, 0xd8,
    0x94, 0xfe, 0x5a, 0x63, 0xcd, 0xc6, 0x02, 0x30,
    0xfb, 0x89, 0xc8, 0xef, 0xd0, 0x9e, 0xcd, 0x7b
]), bytearray([
    0x20, 0xd7, 0x1b, 0xf1, 0x4a, 0x92, 0xbc, 0x48,
    0x99, 0x1b, 0xb2, 0xd9, 0xd5, 0x17, 0xf4, 0xfa,
    0x52, 0x28, 0xe1, 0x88, 0xaa, 0xa4, 0x1d, 0xe7,
    0x86, 0xcc, 0x91, 0x18, 0x9d, 0xef, 0x80, 0x5d,
    0x9b, 0x9f, 0x21, 0x30, 0xd4, 0x12, 0x20, 0xf8,
    0x77, 0x1d, 0xdf, 0xbc, 0x32, 0x3c, 0xa4, 0xcd,
    0x7a, 0xb1, 0x49, 0x04, 0xb0, 0x80, 0x13, 0xd2,
    0xba, 0x31, 0x16, 0xf1, 0x67, 0xe7, 0x8e, 0x37
])]


def new(name: str, data: bytearray = bytearray(b'')) -> 'GOST34112012':
    """
    Create a new hashing object and returns it.

    Parameters
    - name: the string with the name of the hashing algorithm ('streebog256'
    for the GOST R 34.11-2012 algorithm with the resulting hash length of
    32 bytes or 'streebog512' with the resulting hash length of 64 bytes.
    - data: the data from which to get the hash (as a byte object).  If this
    argument is passed to a function, you can immediately use the 'digest'
    (or 'hexdigest') method to calculate the MAC value after calling 'new'.
    If the argument is not passed to the function, then you must use the
    'update(data)' method before the 'digest' (or 'hexdigest') method.

    Return: new hashing object.

    Exception
    - GOSTHashError('unsupported hash type'): in case of invalid value 'name'.
    - GOSTHashError('invalid data value'): in case where the data is not byte
    object.
    """
    if name not in ('streebog512', 'streebog256'):
        raise GOSTHashError('GOSTHashError: unsupported hash type')
    return GOST34112012(name, data)


class GOST34112012:
    """
    Class that implements the hash calculation algorithm.

    Methods
    - update(): update the hash object with the bytes-like object.
    - copy(): returns a copy ('clone') of the hash object.
    - digest(): returns the digest of the data passed to the 'update()' method so
    far.
    - hexdigest(): returns a digest of the hexadecimal data passed so far to the
    'update()' method.
    - reset(): resets the values of all class attributes.

    Attributes
    - digest_size: an integer value the size of the resulting hash in bytes.
    - block_size: an integer value the internal block size of the hash algorithm
    in bytes.
    - name: a text string value the name of the hashing algorithm.
    """

    def __init__(self, name: str, data: bytearray) -> None:
        """Initialize the hashing object."""
        self._name = name
        self._buff = bytearray(b'')
        self._num_block = 0
        self._pad_block_size = 0
        self._hash_h = bytearray(_BLOCK_SIZE)
        self._hash_n = bytearray(_BLOCK_SIZE)
        self._hash_sigma = bytearray(_BLOCK_SIZE)
        if self._name == 'streebog256':
            self._hash_h = bytearray(_BLOCK_SIZE * b'\x01')
        if data != bytearray(b''):
            self.update(data)

    @staticmethod
    def _hash_add_512(op_a: bytearray, op_b: bytearray) -> bytearray:
        op_a = bytearray(op_a)
        op_b = bytearray(op_b)
        op_c = 0
        result = bytearray(_BLOCK_SIZE)
        for i in range(_BLOCK_SIZE):
            op_c = op_a[i] + op_b[i] + (op_c >> 8)
            result[i] = op_c & 0xff
        return result

    @staticmethod
    def _hash_p(data: bytearray) -> bytearray:
        result = bytearray(_BLOCK_SIZE)
        for i in range(_BLOCK_SIZE - 1, -1, -1):
            result[i] = data[_TAU[i]]
        return result

    @staticmethod
    def _hash_s(data: bytearray) -> bytearray:
        result = bytearray(_BLOCK_SIZE)
        for i in range(_BLOCK_SIZE - 1, -1, -1):
            result[i] = S_BOX[data[i]]
        return result

    @staticmethod
    def _hash_l(data: bytearray) -> bytearray:
        result = []
        for i in range(8):
            internal = unpack('<Q', data[i * 8:i * 8 + 8])[0]
            result_64 = 0
            for j in range(_BLOCK_SIZE - 1, -1, -1):
                if internal & 1:
                    result_64 = result_64 ^ _A[j]
                internal = internal >> 1
            result.append(pack('<Q', result_64))
        return b''.join(result)

    def _hash_get_key(self, k: bytearray, i: int) -> bytearray:
        key = bytearray(_BLOCK_SIZE)
        key = add_xor(k, _C[i])
        key = self._hash_s(key)
        key = self._hash_p(key)
        key = self._hash_l(key)
        return key

    def _hash_e(self, k: bytearray, data: bytearray) -> bytearray:
        internal = add_xor(k, data)
        for i in range(12):
            internal = self._hash_s(internal)
            internal = self._hash_p(internal)
            internal = self._hash_l(internal)
            k = self._hash_get_key(k, i)
            internal = add_xor(internal, k)
        return internal

    def _hash_g(self, hash_h: bytearray, hash_n: bytearray,
                data: bytearray) -> bytearray:
        k = add_xor(hash_n, hash_h)
        k = self._hash_s(k)
        k = self._hash_p(k)
        k = self._hash_l(k)
        internal = self._hash_e(k, data)
        internal = add_xor(internal, hash_h)
        result = add_xor(internal, data)
        return result

    def update(self, data: bytearray) -> None:
        """
        Update the hash object with the bytes-like object.

        Parameters
        - data: The string from which to get the hash. Repeated calls are
        equivalent to a single call with the concatenation of all the
        arguments: 'm.update(a)'; 'm.update(b)' is equivalent to
        'm.update(a+b)'.

        Exception
        - GOSTHashError('invalid data value'): in case where the data is not
        byte object.
        """
        if not isinstance(data, (bytes, bytearray)):
            raise GOSTHashError('invalid data value')
        data = self._buff + data
        self._num_block = len(data) // _BLOCK_SIZE
        for i in range(0, self._num_block * _BLOCK_SIZE, _BLOCK_SIZE):
            block = data[i:i + _BLOCK_SIZE]
            self._hash_h = self._hash_g(self._hash_h, self._hash_n, block)
            self._hash_n = self._hash_add_512(self._hash_n, _V_512)
            self._hash_sigma = self._hash_add_512(self._hash_sigma, block)
        self._pad_block_size = _BLOCK_SIZE - len(data) % _BLOCK_SIZE
        if self._pad_block_size < _BLOCK_SIZE:
            self._buff = data[-(_BLOCK_SIZE - self._pad_block_size):]

    def hash_final(self) -> None:
        """Complete the hash calculation after the data update."""
        self._pad_block_size = _BLOCK_SIZE - len(self._buff)
        internal = bytearray(_BLOCK_SIZE)
        internal[1] = (((_BLOCK_SIZE - self._pad_block_size) * 8) >> 8) & 0xff
        internal[0] = ((_BLOCK_SIZE - self._pad_block_size) * 8) & 0xff
        if self._pad_block_size <= _BLOCK_SIZE:
            self._buff = self._buff + b'\x01'
            self._buff = self._buff + b'\x00' * (self._pad_block_size - 1)

        self._hash_h = self._hash_g(self._hash_h, self._hash_n, self._buff)
        self._hash_n = self._hash_add_512(self._hash_n, internal)
        self._hash_sigma = self._hash_add_512(self._hash_sigma, self._buff)
        self._hash_h = self._hash_g(self._hash_h, _V_0, self._hash_n)
        self._hash_h = self._hash_g(self._hash_h, _V_0, self._hash_sigma)

    def get_hash(self) -> bytearray:
        """Return the value of the _hasha_h attribute."""
        return self._hash_h[-self.digest_size:]

    def digest(self) -> bytearray:
        """
        Return the digest of the data.

        This method can be called after applying the 'update ()' method, or
        after calling the 'new()' function with the data passed to it for
        hash calculation.
        """
        temp = self.copy()
        temp.hash_final()
        return temp.get_hash()

    def hexdigest(self) -> str:
        """
        Return the digest of the data.

        This method can be called after applying the 'update ()' method, or
        after calling the 'new()' function with the data passed to it for
        hash calculation.  The result is represented as a hexadecimal string
        as a double-sized string object (digest_size * 2).
        """
        return self.digest().hex()

    def reset(self) -> None:
        """Reset the values of all class attributes."""
        self._buff = bytearray(b'')
        self._num_block = 0
        self._pad_block_size = 0
        self._hash_h = bytearray(_BLOCK_SIZE)
        self._hash_n = bytearray(_BLOCK_SIZE)
        self._hash_sigma = bytearray(_BLOCK_SIZE)
        if self._name == 'streebog256':
            self._hash_h = bytearray(_BLOCK_SIZE * b'\x01')

    def copy(self) -> 'GOST34112012':
        """
        Return a duplicate (“clone”) of the hash object.

        This function can be used to efficiently compute the digests of data
        sharing a common initial substring.
        """
        return deepcopy(self)

    @property
    def digest_size(self):
        """
        Return the size of the resulting hash in bytes.

        For the 'streebog256' algorithm, this value is 32, for the 'streebog512'
        algorithm, this value is 64.
        """
        if self._name == 'streebog512':
            result = 64
        else:
            result = 32
        return result

    @property
    def block_size(self):
        """
        Return the value of the internal block size of the hashing algorithm.

        For the 'streebog256' algorithm and the 'streebog512' algorithm, this
        value is 64.
        """
        return _BLOCK_SIZE

    @property
    def name(self):
        """
        Return the string value the name of the hashing algorithm.

        Respectively 'streebog256' or 'streebog512'.
        """
        return self._name


class GOSTHashError(Exception):
    """
    The class that implements exceptions.

    Exceptions
    - unsupported hash type
    - invalid data value
    """

    def __init__(self, msg: str) -> None:
        """
        Initialize exception.

        Parameters
        - msg: message to output when an exception occurs.
        """
        self.msg = msg
