from ctypes import Structure, CDLL, POINTER, c_int32
import os
import time
import numpy as np

class custom_arr(Structure):
	_fields_ = [
		('arr', POINTER(c_int32)),
		('n', c_int32)
	]

if __name__ == '__main__':
	base_path = os.getcwd()
	to_so = base_path + "/solver.so"
	lib = CDLL(to_so)
	
	lib.solve.argtypes = [POINTER(c_int32), c_int32, c_int32, c_int32]
	lib.solve.restype = POINTER(custom_arr)

	lib.free_mem.argtype = POINTER(custom_arr)
	lib.free_mem.restype = None

	#demand = [69, 29, 36, 61, 61, 26, 34, 67, 45, 67, 79, 56]
	#demand = (c_int32 * len(demand))(*demand)
	#num_elems = c_int32(len(demand))
	#ordering_cost = c_int32(105)
	#holding_cost = c_int32(1)
	#
	#result_ptr = lib.solve(demand, num_elems, ordering_cost, holding_cost)
	# #print(type(result_ptr), type(result_ptr.contents.arr))
	#total_cost = result_ptr.contents.n
	#solution = [result_ptr.contents.arr[i] for i in range(len(demand))]
	#lib.free_mem(result_ptr)
	# #print(type(result_ptr), type(result_ptr.contents.arr))

	#print(f"Total cost: {total_cost}")
	#print(f"Solution: {solution}")

	NUM_EPS = 28
	BATCH_SIZE = 10_000
	PROB_SIZE = 52
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
			result_ptr = lib.solve(d, num_elems, ordering_cost, holding_cost)
			TOTAL_TIME += time.time() - start	
			lib.free_mem(result_ptr)
		
		print(f"{ep} - {round(TOTAL_TIME, 9)}")

	print(f"Total {NUM_EPS*BATCH_SIZE} problems - size {PROB_SIZE}: {round(TOTAL_TIME, 9)} s")
	print(f"Per run of size {PROB_SIZE}: {round(TOTAL_TIME/(NUM_EPS*BATCH_SIZE), 9)} s")

