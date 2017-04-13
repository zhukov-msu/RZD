#include <stdio.h>
#include <limits.h>
 
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

__global__ void matching(int *D, unsigned int *phi, int m, int n)
{
    // matrix m x n
    int pnt = 2;
    
    const int tid = threadIdx.x;// + blockDim.x * blockIdx.x;

    if (tid < m)
    {
        int j = 0;
        int reserve = -threadIdx.x + 1;
        for (j = reserve; j < n; j++)
        {   
            if (j >= 1){
                int tmp[3] = {D[(tid * (n+1)) + j], D[(tid * (n+1)) + j + 1]+pnt, D[(tid+1)*(n+1)+j]+pnt};
                int arg = argmin(tmp[0], tmp[1], tmp[2]);
                int dmin = tmp[arg];
                D[(tid+1)*(n+1)+j+1] = D[(tid+1)*(n+1)+j+1] + dmin;
                phi[tid * n + j] = arg + 1;
            }
            __syncthreads();
        }
    }
}

// if (tid == 2){
//     printf("j: %d\n", j);
//     printf("idx: %d %d %d %d\n",(tid * (n+1)) + j + 1, (tid * (n+1)) + j + 2, (tid+1)*(n+1)+j+1, (tid+1)*(n+1)+j+2);
//     printf("tmp: %d %d %d\n",D[(tid * (n+1)) + j], D[(tid * (n+1)) + j + 1], D[(tid+1)*(n+1)+j]);
//     // printf("min: %d\n", tmp[arg]);
//     printf("D[i+1][j+1]: %d\n", D[(tid+1)*(n+1)+j+1]);
// }