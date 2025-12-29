extern malloc

section .note.GNU-stack

section .text
	global solve
solve:
        ; mov           rdi, D
        ; mov           esi, dword [num_elems]
        ; mov           edx, [o]
        ; mov           ecx, [h]

	; Prologue
	push		rbp
	mov		rbp, rsp

	; (3*esi+1)<<2 -> (esi<<1+esi+1)<<2 (bytes)
	; F size 4 num esi+1
	; cover_by size 4 num esi
	; min_args size 4 num esi
	xor		rax, rax
	mov		eax, esi
	sal		eax, 1
	add		eax, esi
	add		eax, 1
	sal		eax, 2
	sub		rsp, rax			; rax holds 12*esi+4 bytes

	push		rbx
	push		r12
	push		r13
	push		r14
	push		r15

	mov		r10d, 0
	mov		r11, rbp
	sub		r11, rax
	lea		rbx, dword [r11]		; rbx address of stack var
	sar		eax, 2				; eax now holds 3*esi+1
	xor		r11, r11

_init0:
	cmp		r10d, eax
	jge		_init1

	mov		r11d, r10d
	sal		r11d, 2
	mov		dword [rbx+r11], 0

	inc		r10d
	jmp		_init0

_init1:
	xor		rax, rax

        ; caller-saved regs
        push            rdi
        push            rsi
        push            rdx
        push            rcx

        ; this struct is 16 bytes, rax holds a ptr of 8 bytes
        ; rax+8 holds int64_t n
        mov             rdi, 16
        call            malloc wrt ..plt

        ; pop back
        pop             rcx
        pop             rdx
        pop             rsi
        pop             rdi

        mov             qword [rax], 0                  ; init 0
        mov             qword [rax+8], 0

        push            rax                             ; save (custom_arr*) res
        ; again
        push            rdi
        push            rsi
        push            rdx
        push            rcx

        mov             rdi, rsi
        sal             rdi, 2
        call            malloc wrt ..plt                ; init res->arr
        mov             r10, rax

        ; pop back again
        pop             rcx
        pop             rdx
        pop             rsi
        pop             rdi

        pop             rax                             ; :109 pop back cust_arr* res
        mov             qword [rax], r10                ; res->arr (int32_t)*
        push            rax                             ; rax will be used in loops
        xor             rax, rax                        ; zero out rax, be used later

	mov		r10d, 0				; i
	mov		r11d, 0				; t_star_star
	
_loop1:
	cmp		r10d, esi
	jge		_contSolve

	mov		r12d, r10d
	sal		r12d, 2
	mov		r12d, dword [rdi+r12]
	
	cmp		r12d, 0				; D[i] and  0
	jne		_init2

	sal		r10d, 2
	mov		r12d, dword [rbx+r10]		; F[i]
	mov		dword [rbx+r10+4], r12d		; F[i+1] = F[i]
	sar		r10d, 2
	
	mov		r12d, esi
	add		r12d, 1
	add		r12d, r10d
	sal		r12d, 2
	mov		dword [rbx+r12], r10d		; cover_by[i] = i

	inc		r10d
	jmp		_loop1
	
_init2:
	mov		r12, 0
	mov		r13, 0
	mov		r14, 0x3B9ACA00
	mov		r15, 0
	mov		r9, 0

	mov		r8d, r10d			; j = i

_loop2:
	cmp		r8d, r11d			; j and t_star_star
	jl		_contLoop1

	; start function call
        inc             r8d

        push            rdx
        push            rcx
        push            rbx
        push            r9

        mov             edx, r8d                        ; j+1
        mov             ecx, r10d                       ; i
        call            _sumBetween

        pop             r9
        pop             rbx
        pop             rcx

        ; mul here before pop so that we can preserve rdx/edx
        mul             ecx                             ; h * _sumBetween in eax
        pop             rdx

        dec             r8d
	; end function call

	add		r12d, eax			; S_t += eax in r12d
	mov		r13d, r12d			; dummy = S_t
	add		r13d, edx			; dummy = S_t + o

	sal		r8d, 2
	add		r13d, dword [rbx+r8]		; dummy = S_t + o + F[j]
	sar		r8d, 2

	add		r9d, esi
	add		r9d, esi
	add		r9d, 1
	sal		r9d, 2
	mov		dword [rbx+r9], r13d		; min_args[dum_count] = dummy
	sar		r9d, 2
	sub		r9d, 1
	sub		r9d, esi
	sub		r9d, esi

	cmp		r13d, r14d			; dummy and current_min
	jge		_contLoop2

	mov		r14d, r13d			; current_min = dummy
	mov		r15d, r9d			; argmin = dummy_counter

_contLoop2:
	inc		r9d				; dummy_counter += 1
	dec		r8d				; j--
	jmp		_loop2

_contLoop1:
	mov		r8d, r10d			; ovw j
	sub		r8d, r15d			; PHT = i - argmin

	cmp		r11d, r8d			; t_star_star and PHT
	jge		_contLoop1_1
	
	mov		r11d, r8d			; t_star_star = PHT

_contLoop1_1:
	mov		r14d, r15d			; ovw current_min
	add		r14d, esi
	add		r14d, 1
	add		r14d, esi
	sal		r14d, 2
	mov		r9d, dword [rbx+r14]		; min_ars[argm]|ovw dum_count

	mov		r8d, r10d			; ovw PHT
	sal		r8d, 2
	mov		dword [rbx+r8+4], r9d		; F[i+1] = min_args[argmin]

	sar		r8d, 2
	add		r8d, esi
	add		r8d, 1
	sal		r8d, 2
	mov		r9d, r10d
	sub		r9d, r15d
	mov		dword [rbx+r8], r9d		; cover_by[i] = i - argmin

	inc		r10d
	jmp		_loop1

_contSolve:
	pop		rax				; :96
	mov		r10, qword [rax]		; load addr res->arr to r10
	mov		r8d, esi
	dec		r8d				; t = num_elems - 1

	xor		r9, r9
	mov		r9d, esi
	sal		r9d, 2
	mov		r9d, dword [rbx+r9]		; F[num_elems]
	mov		qword [rax+8], r9		; res->n = F[num_elems]

	mov		r9d, 0

_init3:
	cmp		r9d, esi
	jge		_resLoop1

	mov		r11d, r9d
	sal		r11d, 2
	mov		dword [r10+r11], 0		; initialize 0 for res->arr
	
	inc		r9d
	jmp		_init3

_resLoop1:
	mov		r9d, r8d
	add		r9d, esi
	add		r9d, 1
	;add		r9d, esi
	sal		r9d, 2
	mov		r9d, dword [rbx+r9]		; j = cover_by[t]

	mov		r11d, r9d			; k = j

_resLoop2:
	cmp		r11d, r8d			; k and t
	jg		_contResLoop1

	mov		r12d, r11d
	sal		r12d, 2
	mov		r12d, dword [rdi+r12]		; D[k]

	mov		r13d, r9d
	sal		r13d, 2
	add		dword [r10+r13], r12d		; res->arr[j] += D[k]

	inc		r11d
	jmp		_resLoop2

_contResLoop1:
	mov		r8d, r9d
	dec		r8d				; t = j - 1

	cmp		r9d, 0
	jne		_resLoop1			; j == 0 -> break

end:
        pop		r15
        pop		r14
        pop		r13
        pop		r12
        pop		rbx
        mov		rsp, rbp
        pop		rbp
        ret
	
_sumBetween:
	push		rbp
	mov		rbp, rsp

	mov		eax, 0
	cmp		edx, ecx
	jg		_endSum

	cmp		ecx, esi
	jl		_sumBetween1

	mov		ecx, esi

_sumBetween1:
	cmp		edx, 1
	jl		_sumBetween2

	dec		edx
	jmp		_sumBetween3

_sumBetween2:
	mov		edx, 0

_sumBetween3:
	mov		r9d, edx
	inc		r9d

_sumBetween4:
	cmp		r9d, ecx
	jg		_endSum

	sal		r9d, 2
	add		eax, dword [rdi+r9]
	sar		r9d, 2
	inc		r9d
	jmp		_sumBetween4

_endSum:
	mov		rsp, rbp
	pop		rbp
	ret

