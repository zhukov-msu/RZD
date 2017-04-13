# coding=utf-8
import rail
from coord import Coord
from rail import Rail
import os
from xml_loader import *
from matching import Matching
from time import time
import numpy as np
from os import walk
import os
def main():
    # start = time()
    # data_path = "D:/CMC_MSU/master/science/data/"
    # data_dir = "21/sved/"
    # # data_dir = "21/"
    # for (dirpath, dirnames, filenames) in walk(os.path.join(data_path, data_dir)):
    #     for name in filenames:
    #         file_path = os.path.join(dirpath, name)
    #         print(name)
    #         railway = load(file_path)
    #         # railway.rails[0] = railway.rails[0].reduce_channels()
    #         # railway.rails[1] = railway.rails[1].reduce_channels()
    #
    #         for i, rail in enumerate(railway.rails):
    #             railway.rails[i].mark_rail()
    #         # xml_dump(railway, dirpath + 'sved/' + name[:-4] + '_sved.xml')
    #         xml_dump(railway, dirpath + '/marked' + name[:-4] + '_marked.xml')
    #         print(time() - start)


    # master.rails[0].mark_rail()

    # print time() - start
    # table = Matching.get_distance_table(master.rails[0], slave.rails[0], 1, 5)
    # print time() - start
    # Matching.dtw_locglob_diss(table, 0.1)
    # start = time()

    # table = np.loadtxt("table.txt")
    matching = Matching()
    sigRef = np.array([2, 7, 3, 12, 10, 8, 11, 6, 1, -3, -2, 5, 10, 4, -2, -8, 0, 6, 3, 2, 10, 15, 12, 7])
    sigBase = np.array([7, 10, 7, 1, 1, 1, -3, 0, 6, 9, 4, -2])
    dissMatr = np.zeros((sigRef.shape[0], sigBase.shape[0]))
    for i in range(sigRef.shape[0]):
        for j in range(sigBase.shape[0]):
            dissMatr[i, j] = np.int32(abs(sigRef[i] - sigBase[j]))
    test = matching.gpu_match(dissMatr)
    print(test)
    print(sigRef[test[0]])
    print(sigBase[test[1]-1])

    # table = table[0:500, 0:500]
    # np.savetxt("table_c.txt", table.astype(np.int32), fmt='%i')
    # print time()-start
    # table = np.loadtxt("table.txt")
    # print table.shape

    return 0


if __name__ == "__main__":
    main()
