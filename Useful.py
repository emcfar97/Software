import sympy

def addition(start, end, num):

    global matrix

    print(f'\nAdd {num}R{sub[start]} to R{sub[end]}')

    matrix = matrix.elementary_row_op(
        'n->n+km', row1=start-1, row=end-1, k=num
        )
    print(matrix)

def multiply(start, num):

    global matrix

    print(f'\nMultiply {num}R{sub[start]}')
    
    matrix = matrix.elementary_row_op(
        'n->kn', row=start-1, k=num
        )
    print(matrix)

def exchange(start, end):

    global matrix

    print(f'\nExchange R{sub[start]} with R{sub[end]}')
    
    matrix = matrix.elementary_row_op(
        'n<->m', row1=start-1, row2=end-1
        )
    print(matrix)

def transpose():

    global matrix

    print('\nTranspose matrix')

    matrix = matrix.transpose()
    print(matrix)

sub = [chr(i) for i in range(8320, 8330)]

matrix = sympy.Matrix([
    ])

print(matrix)
print(matrix.rref())
