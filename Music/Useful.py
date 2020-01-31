def get_secondary(root, secondary):
    	
	print('Secondary {}s'.format(chr(secondary+8544)))
	for i in range(8545,8551):
		j = ((i+secondary+3)%7)+8544
		print(root, chr(j), chr(i))
	print()
	
# for i in range(7):
# 	get_secondary(chr(8544),i)
