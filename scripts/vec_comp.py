test = False
loop_count = 0
while loop_count !=10:

    loop_count += 1
    if test == False:
        loop_count -= 1
        test = True
        print(test)
    print(loop_count)