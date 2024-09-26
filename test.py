list = [1,2,3,4,5]

try:
    index = list.index(6)
except ValueError:
    print("value error")