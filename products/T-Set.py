s = {1, 2}
s.add(3)  # Добавляет элемент 3 в множество
print(s)  # {1, 2, 3}

s = {1, 2, 3}
s.remove(3)  # Удаляет элемент 3 из множества
print(s)  # {1, 2}

s = {1, 2, 3}
s.discard(3)  # Удаляет элемент 3, если он есть в множестве
print(s)  # {1, 2}

s = {1, 2, 3}
s.clear()  # Очищает множество
print(s)  # set()

s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1.union(s2))  # Возвращает новое множество, содержащее все элементы обоих множеств

s1 = {1, 2, 3}
s2 = {2, 3, 4}
print(s1.intersection(s2))  # Возвращает новое множество, содержащее только общие элементы

s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1.difference(s2))  # Возвращает новое множество, содержащее элементы первого, но не второго множества

s1 = {1, 2, 3}
s2 = {3, 4, 5}
print(s1.symmetric_difference(s2))  # Возвращает новое множество, содержащее элементы, уникальные для каждого множества

s1 = {1, 2}
s2 = {2, 3, 4}
s1.update(s2)  # Добавляет все элементы из второго множества в первое
print(s1)  # {1, 2, 3, 4}

s1 = {1, 2}
s2 = {1, 2, 3}
print(s1.issubset(s2))  # Проверяет, является ли s1 подмножеством s2

s1 = {1, 2, 3}
s2 = {1, 2}
print(s1.issuperset(s2))  # Проверяет, является ли s1 надмножеством s2

s1 = {1, 2, 3}
s2 = s1.copy()  # Создает копию множества
print(s2)  # {1, 2, 3}

# Эти методы полезны, если вы хотите изменить
# существующее множество, а не создавать новое.
s1 = {1, 2, 3}
s2 = {2, 3, 4}
s1.intersection_update(s2)  # Обновляет s1, оставляя только общие элементы с s2
print(s1)  # {2, 3}

s1 = {1, 2, 3}
s2 = {3, 4, 5}
s1.difference_update(s2)  # Удаляет из s1 все элементы, которые есть в s2
print(s1)  # {1, 2}

s1 = {1, 2, 3}
s2 = {3, 4, 5}
s1.symmetric_difference_update(s2)  # Обновляет s1, оставляя элементы, уникальные для каждого множества
print(s1)  # {1, 2, 4, 5}

s = {1, 2, 3}
s.discard(4)  # Удаляет элемент, если он присутствует в множестве; не вызывает ошибку, если элемента нет
print(s)  # {1, 2, 3}

s1 = {1, 2}
s2 = {3, 4}
print(s1.isdisjoint(s2))  # Возвращает True, если множества не имеют общих элементов

s = {1, 2, 3}
s.pop()  # Удаляет и возвращает один произвольный элемент множества; вызывает KeyError, если множество пустое
print(s)

s = {1, 2}
s.add(3)  # Добавляет элемент в множество; не делает ничего, если элемент уже присутствует
print(s)  # {1, 2, 3}
