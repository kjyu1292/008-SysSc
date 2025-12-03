#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef struct {
	int32_t* arr;
	int32_t n;
} custom_arr;

custom_arr* init_arr(int32_t n) {
        custom_arr* s = (custom_arr*) malloc(sizeof(custom_arr));
        s->arr = (int32_t*) calloc(n, sizeof(int32_t));
        s->n = 0;
        return s;
}

void free_mem(custom_arr *s) {
	if (s->arr != NULL) {free(s->arr);}
	if (s != NULL) {free(s);}
}

int32_t sum_between(int32_t* d, int32_t n, register int32_t i, register int32_t j) {
	if (i > j) return 0;
	int32_t sum_ = 0;
	if (j >= n) { j = n; }
	if (i >= 1) { i -= 1; } else { i = 0; }
	register int32_t t = i+1;
	for (t = i+1; t <= j; t++) { sum_ += d[t]; }
	return sum_;
}

custom_arr* solve(int32_t* D, int32_t num_elems, int32_t o, int32_t h) {

	int32_t* F = (int32_t*) calloc(num_elems+1, sizeof(int32_t));
	int32_t* cover_by = (int32_t*) calloc(num_elems, sizeof(int32_t));
	
	register int32_t t_star_star = 0;
	register int32_t i = 0;
	for (i = 0; i < num_elems; i++) {
		if (D[i] == 0) {
			F[i+1] = F[i];
			cover_by[i] = i;
			continue;
		}
		
		register int32_t S_t = 0;
		register int32_t dummy = 0;
		int32_t* min_args = calloc(i - t_star_star + 1, sizeof(int32_t));
		register int32_t current_min = 0x3B9ACA00; //1e9
		register int32_t argmin = 0;
		register int32_t dummy_counter = 0;

		register int32_t j = i;
		for (j = i; j >= t_star_star; j--) {
			S_t += h * sum_between(D, num_elems, j+1, i);
			dummy = S_t + o + F[j];
			min_args[dummy_counter] = dummy;
			if (dummy < current_min) {
				current_min = dummy;
				argmin = dummy_counter;
			}
			dummy_counter += 1;
		}

		register int32_t PHT = i - argmin;
		if (t_star_star < PHT) {
			t_star_star = PHT;
		}

		F[i+1] = min_args[argmin];
		cover_by[i] = i - argmin;

		free(min_args);
	}

	int32_t t = num_elems - 1;
	
	custom_arr* res = init_arr(num_elems);
	res->n = F[num_elems];

	while (1 == 1) {
		int32_t j = cover_by[t];
		for (int32_t k = j; k < t + 1; k++) { res->arr[j] += D[k]; }
		t = j - 1;
		if (j == 0) { break; }
	}

	if (F != NULL) { free(F); }
	if (cover_by != NULL) { free(cover_by); }

	return res;

}

int main() {

	int32_t D[] = {10, 10, 15, 20, 70, 180, 250, 270, 230, 40, 0, 10};
	int32_t num_elems = sizeof(D)/sizeof(D[0]);
	int32_t o = 300;
	int32_t h = 2;

	custom_arr* dummy = solve(D, num_elems, o, h);
	printf("InMain Total cost: %d\n", dummy->n);
	for (int32_t i = 0; i < num_elems; i++) {
		printf("InMain Solution[%d] \t: %d\n", i, dummy->arr[i]);
	}

	free_mem(dummy);

	return 0;

}
