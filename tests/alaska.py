def ice():
    return "berg"


def nice():
    return "berg"


def adder(x):
    def f(y):
        return x + y

    return f


def adderz(z):
    def f(y):
        return z + y

    return f


def muller(x):
    def f(y):
        return x * y

    return f


def divver(x):
    def f(y):
        return y / x

    return f


plus_one = adder(1)
pluz_one = adderz(1)
mul_two = muller(2)
div_three = divver(3)


class Animal:
    def evolve(self):
        return Bear()


class Bear(Animal):
    def teeth(self):
        return "too many"

    def evolve(self):
        return super().evolve()


def snow(x):
    return x * x


def snow2(x):
    return x * x * x


def snow3(x):
    return x * x * x * x
