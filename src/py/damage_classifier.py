from __future__ import division, print_function, unicode_literals, absolute_import
import numpy as np
import os
# from cvxopt import matrix, solvers
from xml_loader import load, xml_dump
from matching import Matching
from rail import Path, Rail
from time import time
import pickle
from svmpy import svm, kernel

class Classifier:

    def __init__(self, obj_path):
        self.obj_path = obj_path
        self.file_list = [obj_path + '/' + name for i, name in enumerate(os.listdir(obj_path))] # if i < 10]
        self.matching = Matching(5)

    @staticmethod
    def preprocess_object(obj):
        # assert obj==Rail
        for i, point in enumerate(obj.points):
            if 4 in point.channels:
                point.channels[2].signals = [sig for sig in point.channels[4].signals]
            if 5 in point.channels:
                point.channels[2].signals = [sig for sig in point.channels[5].signals]
            for ch in [0,1,3,4,5,6,7]:
                if ch in point.channels:
                    point.channels.pop(ch, None)
        return obj

    def calculate_matrix(self, precomputed=None, dump=False):
        start = time()
        self.obj_list = [load(fname) for fname in self.file_list]
        y = [1 if name.endswith('.def') else -1 for name in self.file_list]
        # print(type(self.obj_list[0]))
        self.obj_list = [self.preprocess_object(obj.rails[0]) for obj in self.obj_list]
        for part_num, obj in enumerate(self.obj_list):
            rail = Path(move_dir=obj.move_dir, rails=[obj], date='123', dir_code='123')

            xml_dump(rail,
                     os_path='D:/CMC_MSU/master/science/data/train_data_testing/part{}.xml'
                     .format(str(part_num)))
        N = len(self.obj_list)
        xtx = np.zeros((N, N))

        if precomputed:
            with open(precomputed, 'rb') as f:
                dist_matr = pickle.load(file=f)
        else:
            dist_matr = [[0 for i in range(N)] for j in range(N)]
        total = time()
        start = time()
        for i in range(N):
            for j in range(N):
                # print(i, j)
                if i <= j:
                    if not precomputed:
                        dist_matr[i][j] = self.matching.get_distance_table(self.obj_list[i], self.obj_list[j], 2, 5)
                        dist_matr[j][i] = dist_matr[i][j]
                    # else:
                    xtx[i, j] = self.matching.gpu_match(dist_matr[i][j], distance=True)
                    xtx[j, i] = xtx[i, j]
            if i % 10 == 0:
                print(i, time() - start)
                start = time()
        print(time() - total)
        if not precomputed and dump:
            with open('tmp_data/datatest.pkl', 'wb') as f:
                pickle.dump(obj=dist_matr, file=f)
        if dump:
            # np.save(file='tmp_data/xtx3.pkl', )
            with open('tmp_data/xtx3.pkl', 'wb') as f:
                pickle.dump(obj=xtx, file=f)
        return xtx

    def SVM_train(self, kern, y, C):
        N = len(y)
        n_samples = N
        #     P = matrix(np.dot(np.dot(np.diag(y), kern), np.diag(y)))
        P = matrix(np.outer(y, y) * kern)
        #     G = matrix([([1.0] * N)] * N)
        #     h = matrix([C] * N)
        G_std = matrix(np.diag(np.ones(n_samples) * -1))
        h_std = matrix(np.zeros(n_samples))

        # a_i \leq c
        G_slack = matrix(np.diag(np.ones(n_samples)))
        h_slack = matrix(np.ones(n_samples) * C)
        G = matrix(np.vstack((G_std, G_slack)))
        h = matrix(np.vstack((h_std, h_slack)))
        b = matrix(0.0)
        q = matrix(-1 * np.ones(N))
        A = matrix([float(_y) for _y in y], (1, N))
        sol = solvers.qp(P, q, G, h, A, b)
        return sol

if __name__ == '__main__':
    cl = Classifier('D:/CMC_MSU/master/science/data/train_data_merge')
    k = kernel.Kernel()
    obj_list = [load(fname) for fname in cl.file_list]
    y = [1. if name.endswith('.def') else -1. for name in cl.file_list]
    obj_list = [cl.preprocess_object(obj.rails[0]) for obj in obj_list]
    trainer = svm.SVMTrainer(kernel=k.mykernel(), c=1.0)
    trainer.train(obj_list, y)
    pass
    # cl.calculate_matrix(dump=True)#(precomputed='tmp_data/test.pkl')
    # with open("C:/Users/user/Dropbox/workspace/Python/University/RZD/src/py/tmp_data/xtx3.pkl", 'rb') as f:
    #     data2 = pickle.load(f)
    # obj_path = 'D:/CMC_MSU/master/science/data/train_data_merge'
    # fnames = [obj_path + '/' + x for x in os.listdir(obj_path)]
    # y = [1 if name.endswith('.def') else -1 for name in fnames]
    # defects = np.where(np.array(y) == 1)[0]
    # ans = cl.SVM_train(data2,y,1.0)['x']
    # with open('test_ans_svm.txt', 'w') as f:
    #     f.write(str(ans))