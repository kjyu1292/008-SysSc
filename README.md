# 008-SysSc
Barebone implementation of dynamic lot-sizing algorithm Wagner-Whitin in C \
Python version: https://gist.github.com/tommyod/7d3ee88b7c08fadab6de1ea1e615a925


Requirements:
Any python intepreter \
GCC compiler


Memory check for source file using Valgrind:
gcc solver.c -g -o t \
valgrind --leak-check=yes --track-origins=yes ./t \
output: \
$
==5475== Memcheck, a memory error detector
==5475== Copyright (C) 2002-2022, and GNU GPL'd, by Julian Seward et al.
==5475== Using Valgrind-3.22.0 and LibVEX; rerun with -h for copyright info
==5475== Command: ./t
==5475== 
InMain Total cost: 2140
InMain Solution[0] 	: 55
InMain Solution[1] 	: 0
InMain Solution[2] 	: 0
InMain Solution[3] 	: 0
InMain Solution[4] 	: 70
InMain Solution[5] 	: 180
InMain Solution[6] 	: 250
InMain Solution[7] 	: 270
InMain Solution[8] 	: 280
InMain Solution[9] 	: 0
InMain Solution[10] 	: 0
InMain Solution[11] 	: 0
==5475== 
==5475== HEAP SUMMARY:
==5475==     in use at exit: 0 bytes in 0 blocks
==5475==   total heap usage: 16 allocs, 16 frees, 1,304 bytes allocated
==5475== 
==5475== All heap blocks were freed -- no leaks are possible
==5475== 
==5475== For lists of detected and suppressed errors, rerun with: -s
==5475== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
$


Shared object file: gcc -shared -fPIC -o solver.so solver.c \
Then run: python3 main.py

