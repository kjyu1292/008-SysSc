# 008-SysSc
Python version: https://gist.github.com/tommyod/7d3ee88b7c08fadab6de1ea1e615a925 \
v1.0: Barebone implementation of dynamic lot-sizing algorithm Wagner-Whitin with source code in low- and high-level languages, interfacing using surface-level language Python \
v1.1: Implement branchless practice in C in a commonly used function to reduce jumping \
v2.0: Reduce heap alloc in loops, extern an x86 assembly function that is called within a nested loop \
v2.1: Implement branchless practice in x86 in a commonly used function to reduce jumping \
v3.0: Implement the whole logic in assembly and wrap it in C \
v3.1: Implement branchless practice in v3.0

Requirements: \
Any python intepreter \
GCC compiler, or others as long as you edit script file \
NASM compiler, or others as long as you edit script file \
Valgrind for memory checking

Run: \
All version, to grant access: chmod +x script_{} \
v1.0: .\script solver \
v2.0: .\script_2 _sumBetween solver_2 \
v3.0: .\script_3 _solve solver_3

Average runtime:
| PROB_SIZE  | v1.0 | v1.1 | v2.0 | v2.1 | v3.0 | v3.1 |
| ------------- | ------------- | ------------- | ------------- | ------------- | ------------- | ------------- |
| 10  | 2e-6  | 1.2e-6  | 1e-6  | 1e-6  | 1e-6  | 998e-9  |
| 100  | 6e-6  | 4.6e-6  | 3e-6  | 3e-6  | 3e-6  |2.9e-6  |
| 1_000  | 50e-6  | 37e-6  | 24e-6  | 22e-6  | 22e-6  | 21e-6  |
| 10_000  | 475e-6  | 360e-6  | 243e-6  | 218e-6  | 209e-6  | 201e-6  |
| 100_000  | 5.5e-3  | 3.6e-3  | 2.5e-3  | 2.1e-3  | 2.1e-3  | 2e-3  |
| 1_000_000  | 55e-3  | 42e-3 | (*)  | (*) | (*)  | (*)  | (*)  |

&#42; Stack overflow, must keep it within 8MB





