section .note.GNU-stack

section .text
	global _sumBetween
_sumBetween:
	; mov	ecx, dword [j]
	; mov	edx, dword [i]
	; mov	esi, dword [n]
	; mov	rdi, d

	; Prologue
	push	rbp
	mov	rbp, rsp

	mov	eax, 0
	cmp	edx, ecx
	jg	_end

	cmp	ecx, esi
	jl	_sumBetween1

	mov	ecx, esi

_sumBetween1:
	cmp	edx, 1
	jl	_sumBetween2

	dec	edx
	jmp	_sumBetween3

_sumBetween2:
	mov	edx, 0

_sumBetween3:
	mov	r8d, edx
	inc	r8d

_sumBetween4:
	cmp	r8d, ecx
	jg	_end

	add	eax, dword [rdi+r8*4]
	inc	r8d
	jmp	_sumBetween4

_end:
	; Epilogue
	mov	rsp, rbp
	pop	rbp
	ret
