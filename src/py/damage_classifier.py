from sklearn.cluster import DBSCAN
import numpy as np
import os
from xml_loader import load
from matching import Matching
from rail import Path, Rail
from time import time
import pickle

class Classifier:

    def __init__(self, obj_path):
        self.obj_path = obj_path
        self.file_list = [obj_path + '/' + name for name in os.listdir(obj_path)]
        self.matching = Matching()

    @staticmethod
    def preprocess_object(obj: Rail):
        for i, point in enumerate(obj.points):
            if 4 in point.channels:
                point.channels[2].signals = [sig for sig in point.channels[4].signals]
            if 5 in point.channels:
                point.channels[2].signals = [sig for sig in point.channels[5].signals]
            for ch in [0,1,3,4,5,6,7]:
                if ch in point.channels:
                    point.channels.pop(ch, None)
        return obj

    def calculate_matrix(self, precomputed=None):
        start = time()
        self.obj_list = [load(fname) for fname in self.file_list]
        y = [1 if name.endswith('.def') else -1 for name in self.file_list]
        print(type(self.obj_list[0]))
        self.obj_list = [self.preprocess_object(obj.rails[0]) for obj in self.obj_list]
        N = len(self.obj_list)
        xtx = np.zeros((N, N))

        if precomputed:
            with open(precomputed, 'rb') as f:
                dist_matr = pickle.load(file=f)
        else:
            dist_matr = [[0 for i in range(N)] for j in range(N)]
        total = time()
        for i in range(N):
            start = time()
            for j in range(N):
                # print(i, j)
                if i <= j:
                    if not precomputed:
                        dist_matr[i][j] = self.matching.get_distance_table(self.obj_list[i], self.obj_list[j], 2, 5)
                        dist_matr[j][i] = dist_matr[i][j]
                    else:
                        xtx[i, j] = self.matching.gpu_match(dist_matr[i][j], distance=True)
                        xtx[j, i] = xtx[i, j]

            print(time() - start)
        print(time() - total)
        if not precomputed:
            with open('tmp_data/datatest.pkl', 'wb') as f:
                pickle.dump(obj=dist_matr, file=f)
        with open('tmp_data/xtx2.pkl', 'wb') as f:
            pickle.dump(obj=xtx, file=f)


    def featureless_SVM(self):
        pass

cl = Classifier('D:/CMC_MSU/master/science/data/train_data_merge')
cl.calculate_matrix(precomputed='tmp_data/test.pkl')