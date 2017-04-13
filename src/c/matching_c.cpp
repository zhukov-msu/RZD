#include <stdio.h>
#include <stdlib.h>

static inline unsigned int argmin(unsigned int a, unsigned int b, unsigned int c)
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

int main()
{
    printf("%d\n", 1);
    int i,j;
    int **mat = malloc(953 * sizeof *mat + (953 * (981 * sizeof **mat)));
    int *arr = (int *)malloc(r * c * sizeof(int));
    FILE *file;
    file=fopen("table_c.txt", "r");
    if (file)
    {
        printf("%d\n", mat[1][1]);
    }

    /*for(i = 0; i < 953; i++)
    {
      for(j = 0; j < 981; j++)
      {

  //Use lf format specifier, %c is for character
       if (!fscanf(file, "%d", &mat[i][j]))
           break;
      // mat[i][j] -= '0';
       //printf("%d\n",mat[i][j]); //Use lf format specifier, \n is for new line
      }

    }*/
    fclose(file);
    return 0;
}
