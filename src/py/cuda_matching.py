import pycuda.gpuarray as gpuarray
import pycuda.driver as cuda
import pycuda.autoinit
from pycuda.compiler import SourceModule
import ctypes
from time import time
import numpy as np
from matplotlib import pyplot as plt
from matching import Matching
'''
// printf("%d\\n", tid);
// int * p = (int *)((char *)D + tid * stride) + tid;
// printf("%d %d\\n\\n", m, n);
// printf("[%d][%d]: %d\\n", tid, j, D[(tid * n) + j]);
'''




sigRef = np.array([2, 7, 3, 12, 10, 8, 11, 6, 1, -3, -2, 5, 10, 4, -2, -8, 0, 6, 3, 2, 10, 15, 12, 7])
sigBase = np.array([7, 10, 7, 1, 1, 1, -3, 0, 6, 9, 4, -2])

dissMatr = np.zeros((sigRef.shape[0], sigBase.shape[0]))
for i in range(sigRef.shape[0]):
    for j in range(sigBase.shape[0]):
        dissMatr[i,j] = np.int32(abs(sigRef[i] - sigBase[j]))
MAXINT = 2147483647
# X = dissMatr

time_paral = []
time_cpu = []
with open("cu_testing.cu", "r") as cuda_source_test:
    test = cuda_source_test.read()
mod = SourceModule(test)
func = mod.get_function("matching")
# with open("cu_matching.cu", "r") as cuda_source:
#     mdl = cuda_source.read()
for i in range(1,10):
    X = np.loadtxt("table.txt")
    print (i)
    X = X[0:i*100, 0:i*100]
    # print X
    m, n = X.shape
    D = np.zeros((m + 1, n + 1))
    D[0, 0] = 0
    D[0, :] = MAXINT-1
    D[:, 0] = MAXINT-1
    D[1:(m + 1), 1:(n + 1)] = X

    phi = np.zeros((m, n)).astype(np.uint32)
    D = D.astype(np.int32)

    # a_bytes = a.size * a.dtype.itemsize
    # a_gpu = cuda.mem_alloc(a.nbytes)
    # CPU version
    start = time()
    Matching.dtw_locglob_diss(X,2)
    end = time()
    print (end-start)
    time_cpu += [end-start]
    # GPU version
    start = time()
    a_gpu = gpuarray.to_gpu(D)
    phi_gpu = gpuarray.to_gpu(phi)
    print ("gpu_load", time() - start)
    # print a_gpu
    # func(block=(max_block_size,1,1))
    dim = D.shape[0]
    # print dim
    # kernel_code = kernel_code_template % {
    #     'NDIM': 24
    #     }
    # mod = SourceModule(kernel_code)

    max_block_size = func.max_threads_per_block
    if max_block_size > D.shape[0]:
        n_threads = D.shape[0]
    else:
        n_threads = max_block_size
    print (m,n)
    # func(a_gpu, np.int32(m), np.int32(n), block=(n_threads,1,1))
    start = cuda.Event()
    end = cuda.Event()

    start.record()
    func(a_gpu, phi_gpu, np.int32(m), np.int32(n), block=(n_threads, 1, 1))
    end.record()
    end.synchronize()
    secs = start.time_till(end)*1e-3
    print ("gpu_compute", secs)
    time_paral += [secs]
print (time_paral)
print (time_cpu)
speed = []
for i, elem in enumerate(time_cpu):
    speed += [elem/time_paral[i]]
plt.plot(time_paral)
plt.plot(time_cpu)

plt.show()
print (speed)
plt.plot([x for x in range(100,1000,100)],speed)
plt.show()

# start = time()
a_new = a_gpu.get()
print(a_new)
# phi_new = phi_gpu.get()
# print "gpu_get", time() - start
# np.savetxt("phi.txt", phi_new, fmt='%i')
# print phi
# print phi_new
# # print a_new
# # cuda.memcpy_dtoh(a, a_gpu)
# pass