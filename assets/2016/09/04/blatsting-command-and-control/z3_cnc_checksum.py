#!/usr/bin/env python3
'''
Proof of concept matching BLATSTING C&C checksum using Z3.
E.g. to detect BLATSTING packets without knowing the 4-byte checksum key.

PYTHONPATH=$HOME/z3/build ./z3_cnc_checksum.py
'''
# W.J. van der Laan 2016. Distributed under the MIT software license.
from z3 import *
import binascii, struct

# C&C packet checksum in Python
def cnc_checksum(arg1, arg2):
    i0 = (arg1[1]<<8) | arg1[0]
    i1 = (arg1[3]<<8) | arg1[2]
    i2 = (arg1[5]<<8) | arg1[4]
    i3 = (arg1[7]<<8) | arg1[6]

    j0 = (arg2[1]<<8) | arg2[0]
    j1 = (arg2[3]<<8) | arg2[2]

    b0 = (((i3 ^ j0) + (i0 ^ j1)) ^ (arg1[7]<<8) ^ arg1[2]) & 0xffff
    b1 = (((i2 ^ j0) + (i1 ^ j1)) ^ (arg1[4]<<8) ^ arg1[5]) & 0xffff
    b2 = (((i1 ^ j0) + (i2 ^ j1)) ^ (arg1[1]<<8) ^ arg1[0]) & 0xffff
    b3 = (((i0 ^ j0) + (i3 ^ j1)) ^ (arg1[6]<<8) ^ arg1[3]) & 0xffff

    return (((b3 ^ b1) << 16) ^ ((b3 * b0) << 5) ^ ((b1 * b2) << 11) ^ b2 ^ b0) & 0xffffffff

# Build Z3 expression for C&C packet checksum
def cnc_checksum_z3(arg1, arg2):
    i0 = Concat(arg1[1], arg1[0])
    i1 = Concat(arg1[3], arg1[2])
    i2 = Concat(arg1[5], arg1[4])
    i3 = Concat(arg1[7], arg1[6])

    j0 = Concat(arg2[1], arg2[0])
    j1 = Concat(arg2[3], arg2[2])

    b0 = ZeroExt(16, ((i3 ^ j0) + (i0 ^ j1)) ^ Concat(arg1[7], arg1[2]))
    b1 = ZeroExt(16, ((i2 ^ j0) + (i1 ^ j1)) ^ Concat(arg1[4], arg1[5]))
    b2 = ZeroExt(16, ((i1 ^ j0) + (i2 ^ j1)) ^ Concat(arg1[1], arg1[0]))
    b3 = ZeroExt(16, ((i0 ^ j0) + (i3 ^ j1)) ^ Concat(arg1[6], arg1[3]))

    return ((b3 ^ b1) << 16) ^ ((b3 * b0) << 5) ^ ((b1 * b2) << 11) ^ b2 ^ b0

def solve_for(a0, target):
    arg1 = [BitVec('arg1'+chr(65+i), 8) for i in range(8)]
    arg2 = [BitVec('arg2'+chr(65+i), 8) for i in range(4)]
    res = cnc_checksum_z3(arg1, arg2)

    s = Solver()
    for i in range(8):
        s.add(arg1[i] == a0[i])
    s.add(res == target)

    if s.check() == sat: # satisfyable: extract answer
        m = s.model()
        return bytes([m[x].as_long() for x in arg2])
    else:
        return None

def hstr(sol):
    return binascii.b2a_hex(sol).decode()

def main():
    import random
    for (arg1,target,exp) in [
            (bytes([0x12,0x34,0x56,0x78,0x01,0x23,0x45,0x67]), 0x45407328, True),
            (bytes([0x12,0x34,0x56,0x78,0x01,0x23,0x45,0x67]), 0xf8a1b128, True),
            (bytes([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]), 0x81ff6720, True),
            (bytes([0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]), 0x81ff6721, False)
            ]:
        sol = solve_for(arg1,target)
        print('%s 0x%08x ' % (hstr(arg1), target), end="")
        if sol is not None:
            print('\x1b[1;33m%s\x1b[0m' % hstr(sol))
            assert(cnc_checksum(arg1, sol) == target)
            assert(exp==True)
        else:
            print('\x1b[1;31mNo solution\x1b[0m')
            assert(exp==False)

    # Now for some randomly generated ones
    exp = False
    positives = 0
    total = 0
    while True:
        if exp:
            arg1 = bytes(random.randint(0,255) for x in range(8))
            arg2 = bytes(random.randint(0,255) for x in range(4))
            target = cnc_checksum(arg1, arg2)
        else:
            arg1 = bytes(random.randint(0,255) for x in range(8))
            target = random.randint(0,0xffffffff)
        sol = solve_for(arg1,target)
        print('%s 0x%08x ' % (hstr(arg1), target), end="")
        if sol is not None:
            print('\x1b[1;33m%s\x1b[0m' % hstr(sol))
            assert(cnc_checksum(arg1, sol) == target)
            positives += 1
        else:
            print('\x1b[1;31mNo solution\x1b[0m')
        total += 1

        if (total % 100)==0 :
            print('%.2f%% false positives (%d of %d)' % (positives*100.0/total, positives, total))

if __name__ == '__main__':
    main()

