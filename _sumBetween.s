section .note.GNU-stack

section .text
	global _sumBetween
_sumBetween:
	; mov		rdi, D
	; mov		esi, dword [num_elems]
	; mov		edx, [i]
	; mov		ecx, [j]

	; Prologue
	push		rbp
	mov		rbp, rsp

	mov		eax, 0
	cmp		edx, ecx
	jg		_endSum

	mov		r8d, ecx		; j = n + ((j-n)&((j-n)>>31))
	sub		r8d, esi
	mov		ecx, r8d
	sar		r8d, 31
	and		ecx, r8d
	add		ecx, esi

	mov		r8d, edx		; i = ((i-1)+((i-1)>>31))&~((i-1)>>31)
	dec		r8d
	mov		edx, r8d
	sar		r8d, 31
	add		r8d, edx
	sar		edx, 31
	not		edx
	and		edx, r8d
	
	mov		r8d, edx
	inc		r8d

_loop:
	cmp		r8d, ecx
	jg		_endSum

	add		eax, dword [rdi+r8*4]
	inc		r8d
	jmp		_loop

_endSum:
	; Epilogue
	mov		rsp, rbp
	pop		rbp
	ret
