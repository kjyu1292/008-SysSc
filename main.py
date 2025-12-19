from ctypes import Structure, CDLL, POINTER, c_int32
import os
import time
import numpy as np


TESTING_PARAMETERS = [
	[10,		128,	10_000	],
	[100,		64,	1_000	],
	[1_000,		32,	100	],
	[10_000,	16,	10	],
	[100_000,	8,	10	],
	[1_000_000,	1,	1	]
]


def test_runtime(lib: CDLL):

	for test_case in TESTING_PARAMETERS:

		PROB_SIZE = test_case[0]
		NUM_EPS = test_case[1]
		BATCH_SIZE = test_case[2]
		TOTAL_TIME = 0
	
		for ep in range(1, NUM_EPS+1, 1):

			demand = np.random.randint(
				low = 0, high = 300
				, size = (BATCH_SIZE, PROB_SIZE)
				, dtype = np.int32
			).tolist()

			for i in demand:

				d = (c_int32 * PROB_SIZE)(*i)
				num_elems = PROB_SIZE
				ordering_cost = c_int32(300)
				holding_cost = c_int32(2)
				
				start = time.time()
				try:
					result_ptr = lib.solve(d, num_elems, ordering_cost, holding_cost)
				except Exception as e:
    					print(f"Error type: {type(e).__name__}")  # Error name
    					print(f"Error message: {e}")              # Error message
				TOTAL_TIME += time.time() - start	
				lib.free_mem(result_ptr)

		print(f"Total {(NUM_EPS*BATCH_SIZE):_} problems - size {PROB_SIZE:_}: {round(TOTAL_TIME, 9)} s")
		print(f"Per run of size {PROB_SIZE:_}: {round(TOTAL_TIME/(NUM_EPS*BATCH_SIZE), 9)} s\n")


class custom_arr(Structure):
	_fields_ = [
		('arr', POINTER(c_int32)),
		('n', c_int32)
	]


if __name__ == '__main__':
	base_path = os.getcwd()
	to_so = base_path + "/solver_2.so"
	lib = CDLL(to_so)
	
	lib.solve.argtypes = [POINTER(c_int32), c_int32, c_int32, c_int32]
	lib.solve.restype = POINTER(custom_arr)

	lib.free_mem.argtype = POINTER(custom_arr)
	lib.free_mem.restype = None

	test_runtime(lib = lib)

