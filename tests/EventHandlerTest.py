def test(x):
    print("arg was "+str(x))
toDoList = []
args = ["hello"]
toDoList.append({'f': test, 'a': args})
# to run
for item in toDoList:
     item['f']("t")
