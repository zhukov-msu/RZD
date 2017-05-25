# -*- coding: utf-8 -*-
from __future__ import division
import math
from rail import *
from time import time
import pycuda.gpuarray as gpuarray
import pycuda.driver as cuda
from pycuda.compiler import SourceModule
import pycuda.autoinit
import numpy as np


class Matching:
    def __init__(self, sigma):
        pass
        with open("../cuda/cu_testing.cu", "r") as cuda_source_test:
            src = cuda_source_test.read()

        self.mod = SourceModule(src)
        self.cuda_func = self.mod.get_function("matching")
        self.exp = self.get_exp_table(256, 256, sigma)

    def signal_distance(self, ch1, ch2, first, second):
        if ch1 and ch2:
            res = math.sqrt(first + second - 2 * self.d_calc(ch1, ch2))
            return res
        else:
            return -1

    def d_calc(self, ch1, ch2):
        n1 = len(ch1.signals)
        n2 = len(ch2.signals)
        s = 0
        for i in range(n1):
            for j in range(n2):
                s += ch1.signals[i][0] * ch2.signals[j][0] * \
                    self.exp[ch1.signals[i][1]][ch2.signals[j][1]]
        return s

    # @staticmethod
    def d_calc_same(self, ch1):
        n1 = len(ch1.signals)
        s = 0
        for i in range(n1):
            for j in range(n1): # где то ошибки в неточных значениях
                if i == j:
                    s += ch1.signals[i][0] * ch1.signals[j][0] * \
                         self.exp[ch1.signals[i][1]][ch1.signals[j][1]]
                else:
                    s += 2 * ch1.signals[i][0] * ch1.signals[j][0] * \
                         self.exp[ch1.signals[i][1]][ch1.signals[j][1]]
        return s

    @staticmethod
    def get_exp_table(dim1, dim2, sigma):
        exp = np.zeros((dim1,dim2))
        for i in range(dim1):
            for j in range(dim2):
                exp[i][j] = math.exp(-(math.pow(((i-j)/2./float(sigma)), 2)))  # TODO check float
        return exp


    def get_self(self, thread, ch_num):
        assert isinstance(thread, Rail)
        t_count = len(thread.points)
        my_self = []
        for i in range(t_count):
            if ch_num in thread.points[i].channels.keys():
                my_self += [self.d_calc_same(thread.points[i].channels[ch_num])]
            else:
                my_self += [0]

        return my_self

    def get_distance_table(self, thread1, thread2, ch_num, sigma):
        p1 = len(thread1.points)
        p2 = len(thread2.points)
        if p1 > p2:
            thread1, thread2 = thread2, thread1
            p1, p2 = p2, p1

        table = np.zeros((p1, p2))

        dim1 = 256


        first_self = self.get_self(thread1,ch_num)
        second_self = self.get_self(thread2,ch_num)

        # start = time()
        for i, point1 in enumerate(thread1.points):
            ch1 = ch_num in point1.channels
            for j, point2 in enumerate(thread2.points):
                ch2 = ch_num in point2.channels
                if ch1 and ch2:
                    table[i][j] = self.signal_distance(point1.channels[ch_num], point2.channels[ch_num], first_self[i], second_self[j])

                elif not ch1 and ch2:
                    table[i][j] = second_self[j]
                elif ch1 and not ch2:
                    table[i][j] = first_self[i]
        # print (time() - start)
        return table

    def gpu_match(self, X, distance=True):
        '''
        
        :param X: distance matrix
        :param distance: True if return distance metric, False if matching indices
        :return: 
        '''
        MAXINT = 2147483647
        m, n = X.shape
        D = np.zeros((m + 1, n + 1))
        D[0, 0] = 0
        D[0, :] = MAXINT - 1
        D[:, 0] = MAXINT - 1
        D[1:(m + 1), 1:(n + 1)] = X
        phi = np.zeros((m, n)).astype(np.uint32)
        phi_gpu = gpuarray.to_gpu(phi)
        D = D.astype(np.int32)
        a_gpu = gpuarray.to_gpu(D)
        max_block_size = self.cuda_func.max_threads_per_block
        if max_block_size > D.shape[0]:
            n_threads = D.shape[0]
        else:
            n_threads = max_block_size
        self.cuda_func(a_gpu, phi_gpu, np.int32(m), np.int32(n), block=(n_threads, 1, 1))
        D = a_gpu.get()
        if distance:
            return D[m,n]
        phi = phi_gpu.get()
        j = n
        i = np.argmin(D[1:, n])
        res = D[1:, n][i]
        path = np.array([[i], [j]])
        path1 = []
        links = []
        while j > 1 and i > 1:
            tb = phi[i, j - 1]
            if tb == 1:
                # print(1)
                i -= 1
                j -= 1
            elif tb == 2:
                # print(2, [i,j])
                links += [(i,j-1)]
                i -= 1
            elif tb == 3:
                # print(3, [i,j])
                links += [(i,j-1)]
                j -= 1
            else:
                print(i, j)
                raise Exception("wtf?")

            path = np.insert(path, 0, [i, j-1], axis=1)
            path1 += [(i, j-1)]

        D = D[1:(m + 1), 1:(n + 1)]
        # return path if not distance else float(sum([D[x] for x in links]))/float(np.sum(D))
        try:
            return path if not distance else 1 - (2*float(len(links)) / sum(D.shape))
        except:
            return 0

    @staticmethod
    def dtw_locglob_diss(X, pnt):
        m, n = X.shape
        D = np.zeros((m + 1, n + 1))
        D[0, 0] = 0
        D[0, :] = np.inf
        D[:, 0] = np.inf
        D[1:(m + 1), 1:(n + 1)] = X
        phi = np.zeros((m, n))
        start = time()
        for i in range(0,m):  # почему с 0? тут nan
            for j in range(1,n):
                tmp = [D[i, j], D[i, j + 1] + pnt, D[i + 1, j] + pnt]
                tb = np.argmin(tmp)
                dmin = tmp[tb]
                D[i + 1, j + 1] = D[i + 1, j + 1] + dmin
                phi[i, j] = tb + 1
        print (time()-start)
        j = n
        i = np.argmin(D[1:, n])
        res = D[1:, n][i]
        path = np.array([[i], [j]])
        start = time()
        while j > 1 and i > 1:
            tb = phi[i, j-1]
            if tb == 1:
                i -= 1
                j -= 1
            elif tb == 2:
                i -= 1
            elif tb == 3:
                j -= 1
            else:
                print (i, j)
                raise Exception("wtf?")

            path = np.insert(path, 0, [i, j], axis=1)

        D = D[1:(m + 1), 1:(n + 1)]
