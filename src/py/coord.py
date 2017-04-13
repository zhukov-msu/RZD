# coding=utf-8

import numpy as np
import sys

class Coord:

    def __init__(self, km=None, pk=None, mm=None, str_data=''):
        # assert isinstance(self.km, np.uint16)
        # assert isinstance(self.pk, np.byte)
        # assert isinstance(self.mm, np.int32)
        if not str_data:
            self.km = km
            self.pk = pk
            self.mm = mm
        else:
            self.km, self.pk, self.mm = [int(n) for n in str_data.split('|')]

    def __str__(self):
        return 'Coord(km={0}, pk={1}, mm={2})'.format(self.km, self.pk, self.mm)

    def __lt__(self, other):
        return other.__gt__(self)

    def __gt__(self, other):
        if self.km > other.km:
            return True
        if self.km == other.km and self.pk > other.pk:
            return True
        if self.km == other.km and self.pk == other.pk and self.mm > other.mm:
            return True
        return False

    def __eq__(self, other):
        return self.km == other.km and self.mm == other.mm and self.pk == other.pk

    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        if self.__eq__(other):
            return 0
        if self.km != other.km and self.pk != other.pk:
            return sys.maxint
        return abs(self.mm - other.mm)
