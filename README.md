# 008-SysSc
Barebone implementation of dynamic lot-sizing algorithm Wagner-Whitin in C \
Python version: https://gist.github.com/tommyod/7d3ee88b7c08fadab6de1ea1e615a925

Requirements:
Any python intepreter \
GCC compiler

Shared object file: gcc -shared -fPIC -o solver.so solver.c \
Then run: python3 main.py
