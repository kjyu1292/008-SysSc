#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
	int32_t* arr;
	int64_t n;
} custom_arr;

void free_mem(custom_arr *s);

extern custom_arr* solve(int32_t* d, int32_t n, int32_t o, int32_t h);

int main() {

	int32_t D[] = {10, 10, 15, 20, 70, 180, 250, 270, 230, 40, 0, 10};
	int32_t num_elems = sizeof(D)/sizeof(D[0]);
	int32_t o = 300;
	int32_t h = 2;

	custom_arr* res = solve(D, num_elems, o, h);
	if (res == 0x0) { printf("Alloc fail!\n"); } else {
	printf("InMain Total cost: %ld\n", res->n);
	for (int32_t i = 0; i < num_elems; i++) {
		printf("InMain Solution[%d] \t: %d\n", i, res->arr[i]);
	}

	free_mem(res);
	}

	return 0;

}

void free_mem(custom_arr *s) {
	if (s->arr != NULL) { free(s->arr); }
	if (s != NULL) { free(s); }
}


