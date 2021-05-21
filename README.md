
# Codefind

* Find code objects from filename and qualname
* Find all functions that have a certain code
* Change the code of functions
* Used by [jurigged](https://github.com/breuleux/jurigged)


## find_code

```python
from codefind import find_code

def f(x):
    return x + x

def adder(x):
    def f(y):
        return x + y

    return f

add1 = adder(1)

assert find_code("f" filename=__file__) is f.__code__

# Can find inner closures
assert find_code("adder", "f", filename=__file__) is add1.__code__

# Also works with module name
assert find_code("adder", "f", module=__module__) is add1.__code__
```


## get_functions

```python
from codefind import get_functions

def f(x):
    return x + x

def adder(x):
    def f(y):
        return x + y

    return f

add1 = adder(1)
add2 = adder(2)
add3 = adder(3)

assert get_functions(f.__code__) == [f]

# Finds all functions with the same code (in any order)
assert set(get_functions(add1.__code__)) == {add1, add2, add3}
```

## conform

### Simple usage

```python
from codefind import conform

def f(x):
    return x + x

def g(x):
    return x * x

print(f(5))  # 10
conform(f, g)
print(f(5))  # 25
```

### Updating all closures


```python
def adder(x):
    def f(y):
        return x + y

    return f

def muller(x):
    def f(y):
        return x * y

    return f

add1 = adder(1)
add2 = adder(2)
add3 = adder(3)

print(add1(5))  # 6
print(add2(5))  # 7
print(add3(5))  # 8

conform(add1.__code__, muller(0).__code__)

print(add1(5))  # 5
print(add2(5))  # 10
print(add3(5))  # 15
```



