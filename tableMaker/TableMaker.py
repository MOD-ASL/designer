# TableMaker.py
# Tarik Tosun

from CommandBlock import CommandBlock
from RelativeBlock import RelativeBlock

def series(blocks):
    b = RelativeBlock()
    b.type = 'series'
    b.block_list = blocks
    return b

def parallel(blocks):
    b = RelativeBlock()
    b.type = 'parallel'
    b.block_list = blocks
    return b
