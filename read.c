#include <stdbool.h>
#include <ctype.h>
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <time.h>

int64_t argmin(int64_t a, int64_t b, int64_t c)
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

int64_t **read_matrix(const char *filename, int64_t *m, int64_t *n)
{
	FILE *file = fopen(filename, "r");
	int c;
	int64_t rows = 0;
	int64_t numbers_in_row = 0;
	bool is_first_iteration = true;
	int64_t **matrix = NULL;
	char buf[1024];

	while ((c = fgetc(file)) != EOF) {
		int j = 0;
		rows++;
		matrix = (int64_t **)realloc(matrix, rows * sizeof(int64_t *));
		matrix[rows - 1] = NULL;
		//if it is not the first iteration we know how much space we need
		if (!is_first_iteration) {
			matrix[rows - 1] =
				(int64_t *)malloc(numbers_in_row * sizeof(int64_t));
		}
		while (c != '\n') {
			//waiting for the first digit
			while (!isdigit(c))
				c = fgetc(file);
			int k = 0;
			//got the the first digit, reading the number
			while (isdigit(c)) {
				buf[k] = c;
				k++;
				c = fgetc(file);
			}
			buf[k] = '\0';
			int64_t number = atoi(buf);
			//on first iteration we dont know yet how many numbers are there
			//in the row so we need to count them and do realloc every time
			if (is_first_iteration) {
				numbers_in_row++;
				int size = sizeof(int64_t) * numbers_in_row;
				matrix[rows - 1] = (int64_t *)realloc(matrix[rows - 1], size);
			}
			j++;
			matrix[rows - 1][j - 1] = number;
		}
		if (is_first_iteration)
			is_first_iteration = false;
	}
	printf("finished reading %lld x %lld matrix\n", rows, numbers_in_row);
	fclose(file);
	*m = rows;
	*n = numbers_in_row;

	return matrix;
}

int main()
{
	int64_t m, n;
	int64_t **D = read_matrix("table_c.txt", &m, &n);

	/* for (int i = 0; i < m; ++i) { */
	/* 	for (int j = 0; j < n; ++j) */
	/* 		printf("%lld ", matrix[i][j]); */
	/* 	putchar('\n'); */
	/* } */
	time_t start_t = time(NULL);
    int64_t *arr = (int64_t *)malloc(m * n * sizeof(int64_t));

    int i, j, count = 0;
    /*for (i = 0; i <  m; i++)
      for (j = 0; j < n; j++)
         *(arr + i*m + j) = ++count;*/


	for (i = 0; i < m-1; ++i)
        for (j = 0; j < n-1; ++j)
        {
            //printf("%d ", D[i][j]);
            int tmp[3] = {D[i][j], D[i][j+1]+2, D[i+1][j]+2};
            int arg = argmin(tmp[0], tmp[1], tmp[2]);
            int dmin = tmp[arg];
            D[i+1][j+1] = D[i+1][j+1] + dmin;
            *(arr + i*m + j) = arg+1;
        }
    time_t end_t = time(NULL);
    printf("The loop used %f seconds.\n", difftime(end_t, start_t));
    //for (i = 0; i < m; ++i)
	//	free(D[i]);
	//free(D);

	return 0;
}
