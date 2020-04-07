"""The module that implements processes for creating and verifying an electronic digital
   signature according to GOST 34.10-2012.

   Author: Evgeny Drobotun (c) 2020
   License: MIT

   Usage:
    - signing:

       import gostcrypto

       private_key = bytearray.fromhex(
                     '7a929ade789bb9be10ed359dd39a72c11b60961f49397eee1d19ce9891ec3b28')
       digest = bytearray.fromhex(
                '2dfbc1b372d89a1188c09c52e0eec61fce52032ab1022e8e67ece6672b043ee5')

       sign_obj = gostcrypto.gostsignature.new(gostcrypto.gostsignature.MODE_256,
                  gostcrypto.gostsignature.CURVES_R_1323565_1_024_2019
                  ['id-tc26-gost-3410-2012-256-paramSetB'])
       signature = sign_obj.sign(private_key, digest)

    - verify:

       import gostcrypto

       public_key = bytearray.fromhex(
                    '7f2b49e270db6d90d8595bec458b50c58585ba1d4e9b788f6689dbd8e56fd80b\
                     26f1b489d6701dd185c8413a977b3cbbaf64d1c593d26627dffb101a87ff77da')
       digest = bytearray.fromhex(
                '2dfbc1b372d89a1188c09c52e0eec61fce52032ab1022e8e67ece6672b043ee5')
       signature = bytearray.fromhex(
                   '41aa28d2f1ab148280cd9ed56feda41974053554a42767b83ad043fd39dc0493\
                    01456c64ba4642a1653c235a98a60249bcd6d3f746b631df928014f6c5bf9c40')

       sign_obj = gostcrypto.gostsignature.new(gostcrypto.gostsignature.MODE_256,
                  gostcrypto.gostsignature.CURVES_R_1323565_1_024_2019
                  ['id-tc26-gost-3410-2012-256-paramSetB'])
       if sign_obj.verify(public_key, digest, signature):
           print('Signature is correct')
       else:
           print('Signature is not correct')

    - generating a public key:

       import gostcrypto

       private_key = bytearray.fromhex(
                     '7a929ade789bb9be10ed359dd39a72c11b60961f49397eee1d19ce9891ec3b28')

       sign_obj = gostcrypto.gostsignature.new(gostcrypto.gostsignature.MODE_256,
                  gostcrypto.gostsignature.CURVES_R_1323565_1_024_2019
                  ['id-tc26-gost-3410-2012-256-paramSetB'])
       public_key = sign_obj.public_key_generate(private_key)

"""
import os
from sys import exit as sys_exit

from gostcrypto.utils import zero_fill
from gostcrypto.utils import bytearray_to_int
from gostcrypto.utils import int_to_bytearray
from gostcrypto.utils import compare
from gostcrypto.utils import compare_to_zero

MODE_256 = 0x01
MODE_512 = 0x02

__all__ = ['GOST34102012', 'new',
           'MODE_256', 'MODE_512',
           'CURVES_R_1323565_1_024_2019']

#Parameters of elliptic curves in accordance with R 1323565.1.024-2019
CURVES_R_1323565_1_024_2019 = {
    'id-tc26-gost-3410-2012-256-paramSetB': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0x97
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0x94
        ])),
        b=0xa6,
        m=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0x6c, 0x61, 0x10, 0x70, 0x99, 0x5a, 0xd1,
            0x00, 0x45, 0x84, 0x1b, 0x09, 0xb7, 0x61, 0xb8,
            0x93
        ])),
        q=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0x6c, 0x61, 0x10, 0x70, 0x99, 0x5a, 0xd1,
            0x00, 0x45, 0x84, 0x1b, 0x09, 0xb7, 0x61, 0xb8,
            0x93
        ])),
        x=0x01,
        y=bytearray_to_int(bytearray([
            0x00, 0x8d, 0x91, 0xe4, 0x71, 0xe0, 0x98, 0x9c,
            0xda, 0x27, 0xdf, 0x50, 0x5a, 0x45, 0x3f, 0x2b,
            0x76, 0x35, 0x29, 0x4f, 0x2d, 0xdf, 0x23, 0xe3,
            0xb1, 0x22, 0xac, 0xc9, 0x9c, 0x9e, 0x9f, 0x1e,
            0x14
        ]))
    ),
    'id-tc26-gost-3410-2012-256-paramSetC': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c,
            0x99
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x0c,
            0x96
        ])),
        b=bytearray_to_int(bytearray([
            0x3e, 0x1a, 0xf4, 0x19, 0xa2, 0x69, 0xa5, 0xf8,
            0x66, 0xa7, 0xd3, 0xc2, 0x5c, 0x3d, 0xf8, 0x0a,
            0xe9, 0x79, 0x25, 0x93, 0x73, 0xff, 0x2b, 0x18,
            0x2f, 0x49, 0xd4, 0xce, 0x7e, 0x1b, 0xbc, 0x8b
        ])),
        m=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x5f, 0x70, 0x0c, 0xff, 0xf1, 0xa6, 0x24,
            0xe5, 0xe4, 0x97, 0x16, 0x1b, 0xcc, 0x8a, 0x19,
            0x8f
        ])),
        q=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x5f, 0x70, 0x0c, 0xff, 0xf1, 0xa6, 0x24,
            0xe5, 0xe4, 0x97, 0x16, 0x1b, 0xcc, 0x8a, 0x19,
            0x8f
        ])),
        x=0x01,
        y=bytearray_to_int(bytearray([
            0x3f, 0xa8, 0x12, 0x43, 0x59, 0xf9, 0x66, 0x80,
            0xb8, 0x3d, 0x1c, 0x3e, 0xb2, 0xc0, 0x70, 0xe5,
            0xc5, 0x45, 0xc9, 0x85, 0x8d, 0x03, 0xec, 0xfb,
            0x74, 0x4b, 0xf8, 0xd7, 0x17, 0x71, 0x7e, 0xfc
        ]))
    ),
    'id-tc26-gost-3410-2012-256-paramSetD': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0x9b, 0x9f, 0x60, 0x5f, 0x5a, 0x85, 0x81,
            0x07, 0xab, 0x1e, 0xc8, 0x5e, 0x6b, 0x41, 0xc8,
            0xaa, 0xcf, 0x84, 0x6e, 0x86, 0x78, 0x90, 0x51,
            0xd3, 0x79, 0x98, 0xf7, 0xb9, 0x02, 0x2d, 0x75,
            0x9b
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0x9b, 0x9f, 0x60, 0x5f, 0x5a, 0x85, 0x81,
            0x07, 0xab, 0x1e, 0xc8, 0x5e, 0x6b, 0x41, 0xc8,
            0xaa, 0xcf, 0x84, 0x6e, 0x86, 0x78, 0x90, 0x51,
            0xd3, 0x79, 0x98, 0xf7, 0xb9, 0x02, 0x2d, 0x75,
            0x98
        ])),
        b=bytearray_to_int(bytearray([
            0x80, 0x5a
        ])),
        m=bytearray_to_int(bytearray([
            0x00, 0x9b, 0x9f, 0x60, 0x5f, 0x5a, 0x85, 0x81,
            0x07, 0xab, 0x1e, 0xc8, 0x5e, 0x6b, 0x41, 0xc8,
            0xaa, 0x58, 0x2c, 0xa3, 0x51, 0x1e, 0xdd, 0xfb,
            0x74, 0xf0, 0x2f, 0x3a, 0x65, 0x98, 0x98, 0x0b,
            0xb9
        ])),
        q=bytearray_to_int(bytearray([
            0x00, 0x9b, 0x9f, 0x60, 0x5f, 0x5a, 0x85, 0x81,
            0x07, 0xab, 0x1e, 0xc8, 0x5e, 0x6b, 0x41, 0xc8,
            0xaa, 0x58, 0x2c, 0xa3, 0x51, 0x1e, 0xdd, 0xfb,
            0x74, 0xf0, 0x2f, 0x3a, 0x65, 0x98, 0x98, 0x0b,
            0xb9
        ])),
        x=0x00,
        y=bytearray_to_int(bytearray([
            0x41, 0xec, 0xe5, 0x57, 0x43, 0x71, 0x1a, 0x8c,
            0x3c, 0xbf, 0x37, 0x83, 0xcd, 0x08, 0xc0, 0xee,
            0x4d, 0x4d, 0xc4, 0x40, 0xd4, 0x64, 0x1a, 0x8f,
            0x36, 0x6e, 0x55, 0x0d, 0xfd, 0xb3, 0xbb, 0x67
        ]))
    ),
    'id-tc26-gost-3410-12-512-paramSetA': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0xc7
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0xc4
        ])),
        b=bytearray_to_int(bytearray([
            0x00, 0xe8, 0xc2, 0x50, 0x5d, 0xed, 0xfc, 0x86,
            0xdd, 0xc1, 0xbd, 0x0b, 0x2b, 0x66, 0x67, 0xf1,
            0xda, 0x34, 0xb8, 0x25, 0x74, 0x76, 0x1c, 0xb0,
            0xe8, 0x79, 0xbd, 0x08, 0x1c, 0xfd, 0x0b, 0x62,
            0x65, 0xee, 0x3c, 0xb0, 0x90, 0xf3, 0x0d, 0x27,
            0x61, 0x4c, 0xb4, 0x57, 0x40, 0x10, 0xda, 0x90,
            0xdd, 0x86, 0x2e, 0xf9, 0xd4, 0xeb, 0xee, 0x47,
            0x61, 0x50, 0x31, 0x90, 0x78, 0x5a, 0x71, 0xc7,
            0x60
        ])),
        m=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0x27, 0xe6, 0x95, 0x32, 0xf4, 0x8d, 0x89,
            0x11, 0x6f, 0xf2, 0x2b, 0x8d, 0x4e, 0x05, 0x60,
            0x60, 0x9b, 0x4b, 0x38, 0xab, 0xfa, 0xd2, 0xb8,
            0x5d, 0xca, 0xcd, 0xb1, 0x41, 0x1f, 0x10, 0xb2,
            0x75
        ])),
        q=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0x27, 0xe6, 0x95, 0x32, 0xf4, 0x8d, 0x89,
            0x11, 0x6f, 0xf2, 0x2b, 0x8d, 0x4e, 0x05, 0x60,
            0x60, 0x9b, 0x4b, 0x38, 0xab, 0xfa, 0xd2, 0xb8,
            0x5d, 0xca, 0xcd, 0xb1, 0x41, 0x1f, 0x10, 0xb2,
            0x75
        ])),
        x=0x03,
        y=bytearray_to_int(bytearray([
            0x75, 0x03, 0xcf, 0xe8, 0x7a, 0x83, 0x6a, 0xe3,
            0xa6, 0x1b, 0x88, 0x16, 0xe2, 0x54, 0x50, 0xe6,
            0xce, 0x5e, 0x1c, 0x93, 0xac, 0xf1, 0xab, 0xc1,
            0x77, 0x80, 0x64, 0xfd, 0xcb, 0xef, 0xa9, 0x21,
            0xdf, 0x16, 0x26, 0xbe, 0x4f, 0xd0, 0x36, 0xe9,
            0x3d, 0x75, 0xe6, 0xa5, 0x0e, 0x3a, 0x41, 0xe9,
            0x80, 0x28, 0xfe, 0x5f, 0xc2, 0x35, 0xf5, 0xb8,
            0x89, 0xa5, 0x89, 0xcb, 0x52, 0x15, 0xf2, 0xa4
        ]))
    ),
    'id-tc26-gost-3410-12-512-paramSetB': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x6f
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x6c
        ])),
        b=bytearray_to_int(bytearray([
            0x68, 0x7d, 0x1b, 0x45, 0x9d, 0xc8, 0x41, 0x45,
            0x7e, 0x3e, 0x06, 0xcf, 0x6f, 0x5e, 0x25, 0x17,
            0xb9, 0x7c, 0x7d, 0x61, 0x4a, 0xf1, 0x38, 0xbc,
            0xbf, 0x85, 0xdc, 0x80, 0x6c, 0x4b, 0x28, 0x9f,
            0x3e, 0x96, 0x5d, 0x2d, 0xb1, 0x41, 0x6d, 0x21,
            0x7f, 0x8b, 0x27, 0x6f, 0xad, 0x1a, 0xb6, 0x9c,
            0x50, 0xf7, 0x8b, 0xee, 0x1f, 0xa3, 0x10, 0x6e,
            0xfb, 0x8c, 0xcb, 0xc7, 0xc5, 0x14, 0x01, 0x16
        ])),
        m=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x49, 0xa1, 0xec, 0x14, 0x25, 0x65, 0xa5,
            0x45, 0xac, 0xfd, 0xb7, 0x7b, 0xd9, 0xd4, 0x0c,
            0xfa, 0x8b, 0x99, 0x67, 0x12, 0x10, 0x1b, 0xea,
            0x0e, 0xc6, 0x34, 0x6c, 0x54, 0x37, 0x4f, 0x25,
            0xbd
        ])),
        q=bytearray_to_int(bytearray([
            0x00, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x01, 0x49, 0xa1, 0xec, 0x14, 0x25, 0x65, 0xa5,
            0x45, 0xac, 0xfd, 0xb7, 0x7b, 0xd9, 0xd4, 0x0c,
            0xfa, 0x8b, 0x99, 0x67, 0x12, 0x10, 0x1b, 0xea,
            0x0e, 0xc6, 0x34, 0x6c, 0x54, 0x37, 0x4f, 0x25,
            0xbd
        ])),
        x=0x02,
        y=bytearray_to_int(bytearray([
            0x1a, 0x8f, 0x7e, 0xda, 0x38, 0x9b, 0x09, 0x4c,
            0x2c, 0x07, 0x1e, 0x36, 0x47, 0xa8, 0x94, 0x0f,
            0x3c, 0x12, 0x3b, 0x69, 0x75, 0x78, 0xc2, 0x13,
            0xbe, 0x6d, 0xd9, 0xe6, 0xc8, 0xec, 0x73, 0x35,
            0xdc, 0xb2, 0x28, 0xfd, 0x1e, 0xdf, 0x4a, 0x39,
            0x15, 0x2c, 0xbc, 0xaa, 0xf8, 0xc0, 0x39, 0x88,
            0x28, 0x04, 0x10, 0x55, 0xf9, 0x4c, 0xee, 0xec,
            0x7e, 0x21, 0x34, 0x07, 0x80, 0xfe, 0x41, 0xbd
        ]))
    ),
    'id-tc26-gost-3410-2012-256-paramSetA': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0x97
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0xc2, 0x17, 0x3f, 0x15, 0x13, 0x98, 0x16,
            0x73, 0xaf, 0x48, 0x92, 0xc2, 0x30, 0x35, 0xa2,
            0x7c, 0xe2, 0x5e, 0x20, 0x13, 0xbf, 0x95, 0xaa,
            0x33, 0xb2, 0x2c, 0x65, 0x6f, 0x27, 0x7e, 0x73,
            0x35
        ])),
        b=bytearray_to_int(bytearray([
            0x29, 0x5f, 0x9b, 0xae, 0x74, 0x28, 0xed, 0x9c,
            0xcc, 0x20, 0xe7, 0xc3, 0x59, 0xa9, 0xd4, 0x1a,
            0x22, 0xfc, 0xcd, 0x91, 0x08, 0xe1, 0x7b, 0xf7,
            0xba, 0x93, 0x37, 0xa6, 0xf8, 0xae, 0x95, 0x13
        ])),
        e=0x01,
        d=bytearray_to_int(bytearray([
            0x06, 0x05, 0xf6, 0xb7, 0xc1, 0x83, 0xfa, 0x81,
            0x57, 0x8b, 0xc3, 0x9c, 0xfa, 0xd5, 0x18, 0x13,
            0x2b, 0x9d, 0xf6, 0x28, 0x97, 0x00, 0x9a, 0xf7,
            0xe5, 0x22, 0xc3, 0x2d, 0x6d, 0xc7, 0xbf, 0xfb
        ])),
        m=bytearray_to_int(bytearray([
            0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x3f, 0x63, 0x37, 0x7f, 0x21, 0xed, 0x98,
            0xd7, 0x04, 0x56, 0xbd, 0x55, 0xb0, 0xd8, 0x31,
            0x9c
        ])),
        q=bytearray_to_int(bytearray([
            0x40, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
            0x0f, 0xd8, 0xcd, 0xdf, 0xc8, 0x7b, 0x66, 0x35,
            0xc1, 0x15, 0xaf, 0x55, 0x6c, 0x36, 0x0c, 0x67
        ])),
        x=bytearray_to_int(bytearray([
            0x00, 0x91, 0xe3, 0x84, 0x43, 0xa5, 0xe8, 0x2c,
            0x0d, 0x88, 0x09, 0x23, 0x42, 0x57, 0x12, 0xb2,
            0xbb, 0x65, 0x8b, 0x91, 0x96, 0x93, 0x2e, 0x02,
            0xc7, 0x8b, 0x25, 0x82, 0xfe, 0x74, 0x2d, 0xaa,
            0x28
        ])),
        y=bytearray_to_int(bytearray([
            0x32, 0x87, 0x94, 0x23, 0xab, 0x1a, 0x03, 0x75,
            0x89, 0x57, 0x86, 0xc4, 0xbb, 0x46, 0xe9, 0x56,
            0x5f, 0xde, 0x0b, 0x53, 0x44, 0x76, 0x67, 0x40,
            0xaf, 0x26, 0x8a, 0xdb, 0x32, 0x32, 0x2e, 0x5c
        ])),
        u=0x0d,
        v=bytearray_to_int(bytearray([
            0x60, 0xca, 0x1e, 0x32, 0xaa, 0x47, 0x5b, 0x34,
            0x84, 0x88, 0xc3, 0x8f, 0xab, 0x07, 0x64, 0x9c,
            0xe7, 0xef, 0x8d, 0xbe, 0x87, 0xf2, 0x2e, 0x81,
            0xf9, 0x2b, 0x25, 0x92, 0xdb, 0xa3, 0x00, 0xe7
        ])),
    ),
    'id-tc26-gost-3410-2012-512-paramSetC': dict(
        p=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xfd,
            0xc7
        ])),
        a=bytearray_to_int(bytearray([
            0x00, 0xdc, 0x92, 0x03, 0xe5, 0x14, 0xa7, 0x21,
            0x87, 0x54, 0x85, 0xa5, 0x29, 0xd2, 0xc7, 0x22,
            0xfb, 0x18, 0x7b, 0xc8, 0x98, 0x0e, 0xb8, 0x66,
            0x64, 0x4d, 0xe4, 0x1c, 0x68, 0xe1, 0x43, 0x06,
            0x45, 0x46, 0xe8, 0x61, 0xc0, 0xe2, 0xc9, 0xed,
            0xd9, 0x2a, 0xde, 0x71, 0xf4, 0x6f, 0xcf, 0x50,
            0xff, 0x2a, 0xd9, 0x7f, 0x95, 0x1f, 0xda, 0x9f,
            0x2a, 0x2e, 0xb6, 0x54, 0x6f, 0x39, 0x68, 0x9b,
            0xd3
        ])),
        b=bytearray_to_int(bytearray([
            0x00, 0xb4, 0xc4, 0xee, 0x28, 0xce, 0xbc, 0x6c,
            0x2c, 0x8a, 0xc1, 0x29, 0x52, 0xcf, 0x37, 0xf1,
            0x6a, 0xc7, 0xef, 0xb6, 0xa9, 0xf6, 0x9f, 0x4b,
            0x57, 0xff, 0xda, 0x2e, 0x4f, 0x0d, 0xe5, 0xad,
            0xe0, 0x38, 0xcb, 0xc2, 0xff, 0xf7, 0x19, 0xd2,
            0xc1, 0x8d, 0xe0, 0x28, 0x4b, 0x8b, 0xfe, 0xf3,
            0xb5, 0x2b, 0x8c, 0xc7, 0xa5, 0xf5, 0xbf, 0x0a,
            0x3c, 0x8d, 0x23, 0x19, 0xa5, 0x31, 0x25, 0x57,
            0xe1
        ])),
        e=0x01,
        d=bytearray_to_int(bytearray([
            0x00, 0x9e, 0x4f, 0x5d, 0x8c, 0x01, 0x7d, 0x8d,
            0x9f, 0x13, 0xa5, 0xcf, 0x3c, 0xdf, 0x5b, 0xfe,
            0x4d, 0xab, 0x40, 0x2d, 0x54, 0x19, 0x8e, 0x31,
            0xeb, 0xde, 0x28, 0xa0, 0x62, 0x10, 0x50, 0x43,
            0x9c, 0xa6, 0xb3, 0x9e, 0x0a, 0x51, 0x5c, 0x06,
            0xb3, 0x04, 0xe2, 0xce, 0x43, 0xe7, 0x9e, 0x36,
            0x9e, 0x91, 0xa0, 0xcf, 0xc2, 0xbc, 0x2a, 0x22,
            0xb4, 0xca, 0x30, 0x2d, 0xbb, 0x33, 0xee, 0x75,
            0x50
        ])),
        m=bytearray_to_int(bytearray([
            0x00, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0x26, 0x33, 0x6e, 0x91, 0x94, 0x1a, 0xac,
            0x01, 0x30, 0xce, 0xa7, 0xfd, 0x45, 0x1d, 0x40,
            0xb3, 0x23, 0xb6, 0xa7, 0x9e, 0x9d, 0xa6, 0x84,
            0x9a, 0x51, 0x88, 0xf3, 0xbd, 0x1f, 0xc0, 0x8f,
            0xb4
        ])),
        q=bytearray_to_int(bytearray([
            0x3f, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
            0xc9, 0x8c, 0xdb, 0xa4, 0x65, 0x06, 0xab, 0x00,
            0x4c, 0x33, 0xa9, 0xff, 0x51, 0x47, 0x50, 0x2c,
            0xc8, 0xed, 0xa9, 0xe7, 0xa7, 0x69, 0xa1, 0x26,
            0x94, 0x62, 0x3c, 0xef, 0x47, 0xf0, 0x23, 0xed
        ])),
        x=bytearray_to_int(bytearray([
            0x00, 0xe2, 0xe3, 0x1e, 0xdf, 0xc2, 0x3d, 0xe7,
            0xbd, 0xeb, 0xe2, 0x41, 0xce, 0x59, 0x3e, 0xf5,
            0xde, 0x22, 0x95, 0xb7, 0xa9, 0xcb, 0xae, 0xf0,
            0x21, 0xd3, 0x85, 0xf7, 0x07, 0x4c, 0xea, 0x04,
            0x3a, 0xa2, 0x72, 0x72, 0xa7, 0xae, 0x60, 0x2b,
            0xf2, 0xa7, 0xb9, 0x03, 0x3d, 0xb9, 0xed, 0x36,
            0x10, 0xc6, 0xfb, 0x85, 0x48, 0x7e, 0xae, 0x97,
            0xaa, 0xc5, 0xbc, 0x79, 0x28, 0xc1, 0x95, 0x01,
            0x48
        ])),
        y=bytearray_to_int(bytearray([
            0x00, 0xf5, 0xce, 0x40, 0xd9, 0x5b, 0x5e, 0xb8,
            0x99, 0xab, 0xbc, 0xcf, 0xf5, 0x91, 0x1c, 0xb8,
            0x57, 0x79, 0x39, 0x80, 0x4d, 0x65, 0x27, 0x37,
            0x8b, 0x8c, 0x10, 0x8c, 0x3d, 0x20, 0x90, 0xff,
            0x9b, 0xe1, 0x8e, 0x2d, 0x33, 0xe3, 0x02, 0x1e,
            0xd2, 0xef, 0x32, 0xd8, 0x58, 0x22, 0x42, 0x3b,
            0x63, 0x04, 0xf7, 0x26, 0xaa, 0x85, 0x4b, 0xae,
            0x07, 0xd0, 0x39, 0x6e, 0x9a, 0x9a, 0xdd, 0xc4,
            0x0f
        ])),
        u=0x12,
        v=bytearray_to_int(bytearray([
            0x46, 0x9a, 0xf7, 0x9d, 0x1f, 0xb1, 0xf5, 0xe1,
            0x6b, 0x99, 0x59, 0x2b, 0x77, 0xa0, 0x1e, 0x2a,
            0x0f, 0xdf, 0xb0, 0xd0, 0x17, 0x94, 0x36, 0x8d,
            0x9a, 0x56, 0x11, 0x7f, 0x7b, 0x38, 0x66, 0x95,
            0x22, 0xdd, 0x4b, 0x65, 0x0c, 0xf7, 0x89, 0xee,
            0xbf, 0x06, 0x8c, 0x5d, 0x13, 0x97, 0x32, 0xf0,
            0x90, 0x56, 0x22, 0xc0, 0x4b, 0x2b, 0xaa, 0xe7,
            0x60, 0x03, 0x03, 0xee, 0x73, 0x00, 0x1a, 0x3d
        ])),
    ),
}

def new(mode, curve):
    """Creates a new signature object and returns it.

       Args:
          :mode: Signature generation or verification modeю
          :curve: Parameters of the elliptic curve.

       Return:
          New signature object.

       Exception:
          ValueError('unsupported signature mode') - in case of unsupported signature mode.
          ValueError('invalid parameters of the elliptic curve') - if the elliptic curve
             parameters are incorrect.
    """
    is_edvards_and_canonical = (
        'e' in curve and 'd' in curve and 'u' in curve and 'v' in curve and
        'x' in curve and 'y' in curve and 'a' in curve and 'b' in curve)
    is_edvards_only = (
        'e' in curve and 'd' in curve and 'u' in curve and 'v' in curve and
        'x' not in curve and 'y' not in curve and 'a' not in curve and 'b' not in curve)
    is_canonical_only = (
        'e' not in curve and 'd' not in curve and 'u' not in curve and 'v' not in curve and
        'x' in curve and 'y' in curve and 'a' in curve and 'b' in curve)
    try:
        if is_edvards_and_canonical:
            result = GOST34102012(mode=mode,
                                  p=curve['p'],
                                  a=curve['a'],
                                  b=curve['b'],
                                  e=curve['e'],
                                  d=curve['d'],
                                  m=curve['m'],
                                  q=curve['q'],
                                  x=curve['x'],
                                  y=curve['y'],
                                  u=curve['u'],
                                  v=curve['v'])
        elif is_edvards_only:
            result = GOST34102012(mode=mode,
                                  p=curve['p'],
                                  a=None,
                                  b=None,
                                  e=curve['e'],
                                  d=curve['d'],
                                  m=curve['m'],
                                  q=curve['q'],
                                  x=None,
                                  y=None,
                                  u=curve['u'],
                                  v=curve['v'])
        elif is_canonical_only:
            result = GOST34102012(mode=mode,
                                  p=curve['p'],
                                  a=curve['a'],
                                  b=curve['b'],
                                  e=None,
                                  d=None,
                                  m=curve['m'],
                                  q=curve['q'],
                                  x=curve['x'],
                                  y=curve['y'],
                                  u=None,
                                  v=None)
    except ValueError as err:
        print(err)
        sys_exit()
    return result

class GOST34102012:
    """Сlass that implements processes for creating and verifying an electronic digital
       signature with GOST 34.10-2012.

       Methods:
          :sign(): creating a signature.
          :verify(): signature verification.
          :public_key_generate(): generating a public key.

    """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, mode, **curve_param):
        #Initialize the signature object
        if mode not in (MODE_256, MODE_512):
            raise ValueError('ValueError: unsupported signature mode')
        self._p = curve_param['p']
        self._a = curve_param['a']
        self._b = curve_param['b']
        self._e = curve_param['e']
        self._d = curve_param['d']
        self._m = curve_param['m']
        self._q = curve_param['q']
        self._x = curve_param['x']
        self._y = curve_param['y']
        self._u = curve_param['u']
        self._v = curve_param['v']
        if self._a is None or self._b is None or self._x is None or self._y is None:
            self._edvards_to_canonical()
        if self._m == self._p:
            raise ValueError('ValueError: invalid parameters of the elliptic curve')
        if mode == MODE_256:
            for i in range(1, 32):
                if self._p ** i % self._q == 1 % self._q:
                    raise ValueError('ValueError: invalid parameters of the elliptic curve')
            if self._q < 2 ** 254 or self._q > 2 ** 256:
                raise ValueError('ValueError: invalid parameters of the elliptic curve')
            self._size = 32
        elif mode == MODE_512:
            for i in range(1, 132):
                if self._p ** 1 % self._q == 1 % self._q:
                    raise ValueError('ValueError: invalid parameters of the elliptic curve')
            if self._q < 2 ** 508 or self._q > 2 ** 512:
                raise ValueError('ValueError: invalid parameters of the elliptic curve')
            self._size = 64
        right_side_equation = self._y * self._y % self._p
        left_side_equation = (self._x ** 3 + self._x * self._a + self._b) % self._p
        if right_side_equation != left_side_equation:
            raise ValueError('ValueError: invalid parameters of the elliptic curve')
    # pylint: enable=too-many-instance-attributes

    @staticmethod
    def _invert(value, n_mod):
        #Function for finding the inverse value in the residue
        #ring (based on the extended Euclid algorithm)
        def gcdex(value, n_mod):
            if n_mod == 0:
                gcd_result = value, 1, 0
            else:
                gcd, x_value, y_value = gcdex(n_mod, value % n_mod)
                gcd_result = gcd, y_value, x_value - y_value * (value // n_mod)
            return gcd_result
        result = gcdex(value, n_mod)[1]
        if result < 0:
            result = result + n_mod
        return result

    def _add(self, x_1, x_2, y_1, y_2):
        #Function for adding two points on a curve
        compare_x = compare(int_to_bytearray(x_1, self._size), int_to_bytearray(x_2, self._size))
        compare_y = compare(int_to_bytearray(y_1, self._size), int_to_bytearray(y_2, self._size))
        if compare_x and compare_y:
            grad = (3 * x_1 * x_1 + self._a) * self._invert(2 * y_1, self._p) % self._p
        else:
            d_x = (x_2 - x_1) % self._p
            d_y = (y_2 - y_1) % self._p
            grad = (d_y * self._invert(d_x, self._p)) % self._p
        x_3 = (grad * grad - x_1 - x_2) % self._p
        y_3 = (grad * (x_1 - x_3) - y_1) % self._p
        return x_3, y_3

    @staticmethod
    def _bits(value):
        #Function for getting the bit representation of a number
        while value:
            yield value & 1
            value = value >> 1

    def _mul_point(self, mul_value, x_op=None, y_op=None):
        #Function for calculating a multiple point of an elliptic curve
        mul_value = mul_value - 1
        if x_op or y_op:
            x_prev = x_op
            y_prev = y_op
        else:
            x_prev = self._x
            y_prev = self._y
        x_next = x_prev
        y_next = y_prev
        for bit in self._bits(mul_value):
            if bit == 1:
                x_next, y_next = self._add(x_next, x_prev, y_next, y_prev)
            x_prev, y_prev = self._add(x_prev, x_prev, y_prev, y_prev)
        return x_next, y_next

    def _edvards_to_canonical(self):
        #Translation function to canonical representation of an elliptic curve from the
        #representation as twisted Edwards curves
        ed_s = (self._e - self._d) * self._invert(4, self._p) % self._p
        ed_t = (self._e + self._d) * self._invert(6, self._p) % self._p
        self._a = (ed_s ** 2 - 3 * ed_t ** 2) % self._p
        self._b = (2 * ed_t ** 3 - ed_t * ed_s ** 2) % self._p
        self._x = ((ed_s * (1 + self._v)) * self._invert(1 - self._v, self._p) + ed_t)\
            % self._p
        self._y = ((ed_s * (1 + self._v)) * self._invert((1 - self._v) * self._u, self._p))\
            % self._p

    def sign(self, private_key, digest, rand_k=None):
        """Creating a signature.

           Args:
              :private_key: Private signature key (as a byte object).
              :digest: Digest for which the signature is calculated.
              :rand_k: Random (pseudo-random) number (as a byte object). By default, it is
                 generated by the function itself)

           Return:
              Signature for provided digest (as a byte object).

           Exception:
              ValueError('invalid random value size') - in case of invalid 'rand_k' size.
        """
        if not isinstance(private_key, (bytes, bytearray)):
            raise ValueError('ValueError: invalid private key value')
        if len(private_key) != self._size:
            raise ValueError('ValueError: invalid private key size')
        sign_e = bytearray_to_int(digest) % self._q
        if compare_to_zero(int_to_bytearray(sign_e, self._size)):
            sign_e = 1
        sign_r = 0
        sign_s = 0
        while compare_to_zero(int_to_bytearray(sign_s, self._size)):
            while compare_to_zero(int_to_bytearray(sign_r, self._size)):
                if rand_k is None:
                    sign_rand_k = os.urandom(self._size)
                    while bytearray_to_int(sign_rand_k) >= self._q:
                        sign_rand_k = os.urandom(self._size)
                else:
                    if len(rand_k) != self._size:
                        private_key = zero_fill(len(private_key))
                        raise ValueError('ValueError: invalid random value size')
                    sign_rand_k = rand_k
                sign_k = bytearray_to_int(sign_rand_k)
                sign_c = self._mul_point(sign_k)
                sign_r = sign_c[0] % self._q
            sign_s = (sign_r * bytearray_to_int(private_key) + sign_k * sign_e) % self._q
        sign_r = int_to_bytearray(sign_r, self._size)
        sign_s = int_to_bytearray(sign_s, self._size)
        private_key = zero_fill(len(private_key))
        return sign_r + sign_s

    def verify(self, public_key, digest, signature):
        """Verify a signature.

           Args:
              :public_key: Private signature key (as a byte object).
              :digest: Digest for which to be checked signature (as a byte object).
              :signature: Signature of the digest being checked (as a byte object).

           Return:
              Signature for provided digest (as a byte object).

           Exception:
              ValueError('Invalid signature size') - if the signature size is incorrect.
        """
        if len(signature) != self._size * 2:
            raise ValueError('ValueError: invalid signature size')
        public_key = bytearray_to_int(public_key[:self._size]),\
                     bytearray_to_int(public_key[self._size:])
        sign_r = bytearray_to_int(signature[:self._size])
        sign_s = bytearray_to_int(signature[self._size:])
        if sign_r <= 0 or sign_r >= self._q or sign_s <= 0 or sign_s >= self._q:
            return False
        sign_e = bytearray_to_int(digest) % self._q
        if compare_to_zero(int_to_bytearray(sign_e, self._size)):
            sign_e = 1
        sign_v = self._invert(sign_e, self._q)
        sign_z_1 = sign_s * sign_v % self._q
        sign_z_2 = self._q - sign_r * sign_v % self._q
        sign_p = self._mul_point(sign_z_1)
        sign_q = self._mul_point(sign_z_2, public_key[0], public_key[1])
        sign_c = self._add(sign_p[0], sign_q[0], sign_p[1], sign_q[1])
        sign_r_check = sign_c[0] % self._q
        return compare(int_to_bytearray(sign_r_check, self._size),
                       int_to_bytearray(sign_r, self._size))

    def public_key_generate(self, private_key):
        """Generating a public key

           Args:
              :private_key: Private signature key (as a byte object).

           Return:
              Public key (as a byte object).

           Exception:
              ValueError('ValueError: invalid private key size') - in case of invalid private
                 key size.
              ValueError('ValueError: invalid private key value') - in case of invalid private
                 key value.
        """
        if not isinstance(private_key, (bytes, bytearray)):
            raise ValueError('ValueError: invalid private key value')
        if len(private_key) != self._size:
            raise ValueError('ValueError: invalid private key size')
        private_key = bytearray_to_int(private_key)
        public_key = self._mul_point(private_key)
        public_key_x = int_to_bytearray(public_key[0], self._size)
        public_key_y = int_to_bytearray(public_key[1], self._size)
        private_key = 0
        return public_key_x + public_key_y
