from itertools import combinations, product, starmap
from operator import add
from collections import Counter

def pair_splittings(elements, k):
    elements = frozenset(elements)
    for A in combinations(elements, k):
        B = tuple(elements - frozenset(A))
        yield (A, B)

def set_pair_splittings(elements, k):
    # deduplicate: always put the first element in the first group.
    n0, *rest = elements
    for A, B in pair_splittings(rest, k - 1):
        yield ((n0,) + A, B)

def even_splittings(elements, num_bins):
    # special case when all bins are the same size.
    bin_size = len(elements) // num_bins
    if num_bins == 1:
        yield (tuple(elements),)
        return

    k = num_bins // 2
    for half1, half2 in set_pair_splittings(elements, k*bin_size):
        for choices1 in even_splittings(half1, k):
            for choices2 in even_splittings(half2, num_bins-k):
                yield choices1 + choices2


def splittings_helper(elements, bin_counts):
    [(size, count)] = bin_counts
    yield from even_splittings(elements, count)
    return

def splittings(elements, bins):
    return splittings_helper(elements, tuple(Counter(bins).items()))


# s = splittings([i for i in range(30)], (6, 6, 6, 6, 6))
s = splittings("ABCDEFGHI", (3, 3, 3))

print("Combinaciones de A, B, C, D, E, F en grupos de 3")
count = 0
for x in s:
    count += 1
    print(x)


import time

st = time.time()
et = time.time()

def fact(N):
    if N == 1:
        return 1
    return N * fact(N-1)

total = fact(6) / (fact(3) * fact(3))
print(f"Formula {total}. Son {count}")


total = fact(30) / (fact(5) * fact(25))

print(f"Las posibilidades totales son: {total}")

count = 0
done = 10
while et-st < 240:
    next(s)
    count += 1
    et = time.time()
    if et-st > done:
        print(f"{done} s - {count} opciones revisadas de {total}: {count / total} %")
        done += 10

print(count)