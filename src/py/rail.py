# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals, absolute_import
from coord import Coord
from collections import defaultdict
from datetime import datetime
import math
import sys
from copy import copy


class Path:

    def __init__(self, dir_name='', dir_code='', date=None, move_dir=None, rails=None):
        self.dir_name = dir_name
        self.dir_code = dir_code
        self.date = date
        self.move_dir = move_dir
        self.rails = rails

    def __str__(self):
        return 'Path(dir_name={0}, move_dir={1})'.format(self.dir_name, self.move_dir) \
               + '\n' + str(self.rails)

class Point:

    def __init__(self, coord=None, channels=None, note=None, back_motion=None):

        self.channels = defaultdict(Channel)
        self.coord = coord
        self.note = note
        self.back_motion = back_motion

    def __str__(self):
        return "Coord({0}|{1}|{2}), ".format(self.coord.km, self.coord.pk, self.coord.mm) + "Channels: {0}".format(str(self.channels))




class Channel:

    def __init__(self, num=None, signals=None):
        # assert isinstance(num, int)
        self.num = num
        # assert isinstance(signals, tuple)
        self.signals = signals

    def add_signal(self, amplitude, delay):
        self.signals += [(amplitude, delay)]

    def add_signal_pair(self, pair):
        self.signals += [pair]

    def delay_exists(self, delay):
        for i in range(len(self.signals)):
            if self.signals[i].delay == delay:
                return True
        return False

class Rail:
    global_counter = 0
    def __init__(self, _right=True, _move_dir=True):
        self.right = _right
        self.move_dir = _move_dir
        self.points = []
        self.num_to_mm = []
        self.sysRealCoord = defaultdict(Coord)

    def __str__(self):
        return 'Rail({0}, move_dir={1})'.format("right" if self.right else "left",
                                                self.move_dir)

    def add_note(self, _coord, _note):
        for i, point in enumerate(self.points):
            if (point.coord.km == _coord.km) and \
                    (point.coord.pk == _coord.pk) and \
                    (point.coord.mm == _coord.mm):
                self.points[i].note = _note
                pass


    def make_links_for(self, slave_rail):  # TODO: ТУТ ГДЕ-ТО КОСЯК!!!!!
        # type: (slave_rail) -> list
        # assert slave_rail, Rail
        links = []
        for point in slave_rail.points:
            links.append(self.closest_coord_to(point.coord))
        return links

    def last(self):  # TODO: ТУТ ГДЕ-ТО КОСЯК!!!!!
        p_count = len(self.points)
        if p_count == 0:
            return None
        num_to_mm = [0] * p_count
        points = self.points
        # print(len(points))
        if not self.move_dir:
            for i in reversed(range(len(self.points)-1)):
                deltaMm = 0
                deltaPk = points[i].coord.pk - points[i + 1].coord.pk
                deltaKm = points[i].coord.km - points[i + 1].coord.km
                if deltaKm == 0:
                    if deltaPk == 0:
                        deltaMm = points[i].coord.mm - points[i + 1].coord.mm
                    else:
                        deltaMm = points[i].coord.mm
                else:
                    deltaMm = points[i].coord.mm

                if abs(deltaMm) > 10:
                    deltaMm = 0
                num_to_mm[i] = num_to_mm[i + 1] + deltaMm
            # num_to_mm = num_to_mm + [num_to_mm[-2]]
        else:
            for i in range(1,len(points)):
                # i += 1  # костыль чтобы считалось не с 0, а с 1
                deltaMm = 0
                deltaPk = points[i].coord.pk - points[i-1].coord.pk
                deltaKm = points[i].coord.km - points[i-1].coord.km
                if deltaKm == 0:
                    if deltaPk == 0:
                        deltaMm = points[i].coord.mm - points[i-1].coord.mm
                    else:
                        deltaMm = points[i].coord.mm
                else:
                    deltaMm = points[i].coord.mm

                if abs(deltaMm) > 10:
                    deltaMm = 0
                num_to_mm[i] = num_to_mm[i-1] + deltaMm
        # num_to_mm = num_to_mm + [num_to_mm[-2]]
        # if self.move_dir:
        #     self.num_to_mm = num_to_mm
        # else:
        #     self.num_to_mm = list(reversed(num_to_mm))
        self.num_to_mm = num_to_mm

    def reduce_channels(self):
        reduce_pos = [73, 73, 27, -79, 51, -25, -33, -50]
        reduce_del = [0,   0, 1.149, -1.137,  1.536, -1.179, 0.85, -1.105]
        p_count = len(self.points)
        if p_count == 0:
            return self
        direction = 1 if self.move_dir else -1

        self.last()

        mat = self.closest_mat()
        s_rail = Rail(self.right, self.move_dir)  # куда все таки направление?

        for i in range(p_count):
            s_rail.points += [Point(self.points[i].coord, self.points[i].back_motion)]

        for p_num in range(p_count):
            note = self.points[p_num].note
            ch = self.points[p_num].channels
            ch_nums = ch.keys()
            for ch_num in ch_nums:  # TODO: changed 0 to 1
                cur_signals = ch[ch_num].signals
                sig_count = len(cur_signals)
                for s_num in range(sig_count):

                    delay = cur_signals[s_num][1]
                    shift = int(round(reduce_pos[ch_num] + reduce_del[ch_num] * delay))
                    new_mm = self.num_to_mm[p_num] + direction * shift
                    if new_mm < 0:
                        new_mm = 0
                    elif new_mm >= len(mat):
                        new_mm = len(mat) - 1
                    cntnm = mat[new_mm]  # closedNumToNewMm
                    # if not s_rail.points[cntnm].channels[ch_num].\
                    #         delay_exists(self.points[p_num].channels[ch_num].signals[s_num][1]):
                    #     s_rail.points[cntnm].channels[ch_num].\
                    #         add_signal(self.points[p_num].channels[ch_num].signals[s_num])
                    if not (ch_num in s_rail.points[cntnm].channels.keys()):
                        s_rail.points[cntnm].channels[ch_num] = Channel(ch_num, [self.points[p_num].channels[ch_num].signals[s_num]])
                    else:
                        s_rail.points[cntnm].channels[ch_num].add_signal_pair(self.points[p_num].channels[ch_num].signals[s_num])

            s_rail.points[p_num].note = note

        return s_rail

    def mark_rail(self, min_amplitude = 0):
        start = -1
        list_parts = []
        cnt_points = 0
        cnt_dashes = 0
        for i, point in enumerate(self.points):
            if 3 in point.channels:
                point.channels[2].signals = [sig for sig in point.channels[3].signals]
                del point.channels[3].signals[:]
            for ch in point.channels:
                if ch in [0, 1, 6, 7]:
                    # print([1point for point in point.channels[ch].signals])
                    del point.channels[ch].signals[:]

                # test = [sig for sig in point.channels[ch].signals if sig[0] > 6]
                point.channels[ch].signals = [sig for sig in point.channels[ch].signals if sig[0] > min_amplitude]
                # for sig_num, sig in enumerate(sigs):
                #     if sig[0] < 7:
                #         del sig #point.channels[ch].signals[sig_num]

                        # if (sig[0] >= 12 and sig[0] <= 15 and sig[1] >= 177 and sig[1] <= 181) or \
                                # (sig[0] >= 4 and sig[0] <= 16 and sig[1] >= 79 and sig[1] <= 83):
                    #     del point.channels[ch].signals[sig_num]
            if len(point.channels) == 0:
                cnt_dashes += 1

            else:
                cnt_empty_channels = 0
                for ch in point.channels:
                    if point.channels[ch].signals:
                        if cnt_points == 0:
                            start = i
                            cnt_dashes = 0
                        cnt_points += 1
                        break
                    else:
                        cnt_empty_channels += 1
                if cnt_empty_channels == len(point.channels):
                    cnt_dashes += 1
            if cnt_dashes == 7 and start >= 0:
                if cnt_points >= 5:
                    self.points[start].note = 'es'
                    self.points[i].note = 'ee'
                    rail_to_dump = copy(self)
                    rail_to_dump.points = rail_to_dump.points[start: i+1]
                    list_parts += [Path(move_dir=self.move_dir, rails=[rail_to_dump], date='123', dir_code='123')]
                    self.global_counter += 1
                cnt_dashes = 0
                cnt_points = 0
                start = -1
        return list_parts


    def closest_mat(self):  # TODO: changed range 0 -> 1
        max_value = int(max(self.num_to_mm))
        mat = [0] * max_value
        # print (mat)
        if self.move_dir:
            mat[0] = self.get_closest_num(0, 0)
            for i in range(1, max_value):
                mat[i] = self.get_closest_num(i, mat[i-1])
        else:
            mat[max_value-1] = self.get_closest_num(max_value, 0)
            for i in range(1, max_value):
                mat[max_value-i-1] = self.get_closest_num(max_value-i, mat[max_value-i])
        return mat

    def get_closest_num(self, value, start_idx):  # вроде ок
        k, index, prev_d = 0, 0, 0
        min_d = sys.maxsize
        for i in range(start_idx, len(self.num_to_mm)):
            cur_d = abs(value - self.num_to_mm[i])

            if cur_d < min_d:
                min_d = cur_d
                index = i
            if min_d == 0:
                break

            if prev_d == min_d:
                k += 1
            else:
                k = 0

            if k == 4:
                break

            prev_d = min_d
        return index

    def get_point_num(self, coord):
        cur_point = len(self.points) / 2
        delta = len(self.points) / 4
        k = 1 if self.move_dir else -1
        while True:
            if coord > self.points[cur_point].coord:
                cur_point += k * delta
            elif coord < self.points[cur_point].coord:
                cur_point -= k * delta
            else:
                return cur_point
            if delta > 1:
                delta = delta / 2

    def closest_coord_to(self, a):
        # p_count = len(self.points)
        min_mm = sys.maxint
        idx_min = -1
        for i, point in enumerate(self.points):
            delta_mm = a - point.coord
            if delta_mm <= min_mm:
                min_mm = delta_mm
                idx_min = i
            else:
                break  # TODO: wtf???
        return idx_min
