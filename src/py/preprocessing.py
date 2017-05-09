from xml_loader import *
from os import walk
import os
def preproc():
    sved = False
    data_path = "D:\\CMC_MSU\\master\\science\\data\\"
    # sved_dir = "21\\sved"
    sved_dir = "train_data2\\sved"
    data_dir = "21"
    if sved:
        cur_dir = os.path.join(data_path, data_dir)
    else:
        cur_dir = os.path.join(data_path, sved_dir)
    marked_dir = os.path.join(cur_dir, 'marked')

    if not os.path.exists(marked_dir):
        os.makedirs(marked_dir)
    if sved:
        for (dirpath, dirnames, filenames) in walk(cur_dir):
            for name in filenames:
                file_path = os.path.join(dirpath, name)
                print(name)
                railway = load(file_path)
                railway.rails[0] = railway.rails[0].reduce_channels()
                railway.rails[1] = railway.rails[1].reduce_channels()
                xml_dump(railway, os.path.join(cur_dir, 'sved', name[:-4] + '_sved.xml'))
            break
    else:
        for (dirpath, dirnames, filenames) in walk(cur_dir):
            for j, name in enumerate(filenames):
                file_path = os.path.join(dirpath, name)
                print(name)
                railway = load(file_path)

                for i, rail in enumerate(railway.rails):
                    list_parts = railway.rails[i].mark_rail(min_amplitude=1)
                    for part_num, part in enumerate(list_parts):
                        print(part_num)
                        xml_dump(part,
                                 os_path = 'D:/CMC_MSU/master/science/data/train_data2/part{}.xml'
                                 .format(name.split('.')[0] + '_' + ('r' if rail.right else 'l') + '-' + str(part_num)))
                        # .format(name.split('.')[0] + '_' + 'right' if rail.right else 'left' + '-' + str(part_num)))

                xml_dump(railway, os.path.join(marked_dir, name[:-4] + '_marked.xml'))
                # print(time() - start)
                # print(j)
                # if j > 5:
                #     break
            break

preproc()