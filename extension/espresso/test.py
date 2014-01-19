#!/usr/bin/env python3

import os
import re
from multiprocessing import Pool
from subprocess import check_output

PLAS = [
    'bb_50x5x50_20%_0.pla',
    'bb_50x5x50_20%_1.pla',
    'bb_50x5x50_20%_2.pla',
    'bb_50x5x50_20%_3.pla',
    'bb_50x5x50_20%_4.pla',
    'bb_50x5x50_20%_5.pla',
    'bb_50x5x50_20%_6.pla',
    'bb_50x5x50_20%_7.pla',
    'bb_50x5x50_20%_8.pla',
    'bb_50x5x50_20%_9.pla',

    'bb_50x5x50_50%_0.pla',
    'bb_50x5x50_50%_1.pla',
    'bb_50x5x50_50%_2.pla',
    'bb_50x5x50_50%_3.pla',
    'bb_50x5x50_50%_4.pla',
    'bb_50x5x50_50%_5.pla',
    'bb_50x5x50_50%_6.pla',
    'bb_50x5x50_50%_7.pla',
    'bb_50x5x50_50%_8.pla',
    'bb_50x5x50_50%_9.pla',
]

def test(pla):
    pla_in = os.path.join('test', 'bb_all', pla)
    espresso_output = check_output(['./espresso', pla_in])
    pla_out = os.path.join('test', 'bb_all.out', pla + '.out')
    with open(pla_out) as fin:
        print("checking:", pla_in)
        return fin.read().encode('utf-8') == espresso_output

def main():
    p = Pool(4)
    assert all(p.map(test, PLAS))

if __name__ == '__main__':
    main()
