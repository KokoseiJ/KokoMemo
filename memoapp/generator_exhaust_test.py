import timeit
from collections import deque


def test_generator(n=1000):
    for i in range(n):
        yield i


def test_for():
    gen = test_generator()
    for _ in gen:
        pass


def test_deque():
    gen = test_generator()
    deque(gen, maxlen=0)


def test_all():
    gen = test_generator()
    all(x or True for x in gen)


def test_list():
    gen = test_generator()
    list(gen)


def test_func(i):
    i * 25565


def test_comp():
    deque((test_func(i) for i in range(10000)), maxlen=0)


def test_map():
    deque(map(test_func, range(10000)), maxlen=0)


print("for: ", timeit.timeit(test_for))
print("deque: ", timeit.timeit(test_deque))
print("all: ", timeit.timeit(test_all))
print("list: ", timeit.timeit(test_list))

print("\ncomp: ", timeit.timeit(test_comp))
print("map: ", timeit.timeit(test_map))
