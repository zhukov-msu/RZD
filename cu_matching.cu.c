#include <stdio.h>

__device__ static inline unsigned int argmin(unsigned int a, unsigned int b, unsigned int c)
{ 
    if (a < b)
    {
        if (a < c) 
             return 0; 
        else 
             return 2;
    }

    if (b < c)
        return 1;
    else return 2;
}

__global__ void matching(int *D, int *phi, int m, int n)
{
    // matrix m x n
    int pnt = 2;
    const int tid = threadIdx.x;// + blockDim.x * blockIdx.x;
    if (tid == 0)
    {
        int j = 0;
        for (j = 0; j < n; j++)
        {
            int tmp[3] = { D[(tid * n) + j], D[(tid+1)*n+j] + pnt, D[(tid * n) + j + 1] + pnt };
            int arg = argmin(tmp[0], tmp[1], tmp[2]);
            int dmin = tmp[arg];
            D[((tid+1) * n) + j + 1] = D[((tid+1) * n) + j + 1] + dmin;
            phi[(tid * n) + j] = arg + 1;
        }
    }
    else
    if (tid < m)
    {
        int j = 0;
        for (j = 0; j < n; j++)
        {
            while(1)
            {
                if (phi[(tid-1) * n + j])
                {
                    int tmp[3] = {D[(tid * n) + j], D[(tid+1)*n+j] + pnt, D[(tid * n) + j + 1] + pnt};
                    int arg = argmin(tmp[0], tmp[1], tmp[2]);
                    int dmin = tmp[arg];
                    D[((tid+1) * n) + j + 1] = D[((tid+1) * n) + j + 1] + dmin;
                    phi[(tid * n) + j] = arg + 1;
                    break;
                }
            }
        }
    }
}