import pytest

import codefind

from . import alaska
from .alaska import adder, ice, muller, plus_one

plus_two = adder(2)


def ice2():
    return "cream"


def ice3():
    return "box"


def test_get_functions():
    assert codefind.get_functions(ice.__code__) == [ice]


def test_get_functions_closure():
    assert set(codefind.get_functions(plus_one.__code__)) == {
        plus_one,
        plus_two,
    }


def test_get_functions_cache():
    assert codefind.get_functions(alaska.pluz_one.__code__) == [alaska.pluz_one]
    pluz_two = alaska.adderz(2)
    assert codefind.get_functions(alaska.pluz_one.__code__, use_cache=True) == [
        alaska.pluz_one
    ]
    assert set(codefind.get_functions(alaska.pluz_one.__code__)) == {
        pluz_two,
        alaska.pluz_one,
    }


def test_conform():
    assert ice() == "berg"
    codefind.conform(ice, ice2)
    assert ice() == "cream"
    codefind.conform(ice, ice3)
    assert ice() == "box"
    codefind.conform(ice, None)
    assert ice() == "box"


def test_conform_closure():
    mul_three = muller(3)
    assert alaska.mul_two(6) == 12
    assert mul_three(6) == 18
    codefind.conform(alaska.mul_two.__code__, alaska.div_three)
    assert alaska.mul_two(6) == 3
    assert mul_three(6) == 2


def test_bad_conform():
    with pytest.raises(codefind.ConformException):
        # Different set of free variables
        codefind.conform(ice, alaska.plus_one)


def test_bad_conform_different_varnames():
    with pytest.raises(codefind.ConformException):
        # Different set of free variables
        codefind.conform(alaska.pluz_one, alaska.plus_one)


def test_bad_conform_method():
    with pytest.raises(codefind.ConformException):
        # evolve uses super() which is a closure over __class__
        codefind.conform(alaska.Bear.evolve, ice)


def test_custom_conform():
    from . import jackfruit

    assert jackfruit.jack1(3, 4) == 12
    assert jackfruit.jack2(3, 4) == 12

    assert jackfruit.jack1.__code__.co_name == "jack1"
    assert jackfruit.jack2.__code__.co_name == "jack2"

    codefind.conform(jackfruit.jack1.__code__, jackfruit.newjack)

    assert jackfruit.jack1(3, 4) == 7
    assert jackfruit.jack2(3, 4) == 7

    assert jackfruit.jack1.__code__.co_name == "newjack"
    assert jackfruit.jack2.__code__.co_name == "jack2"

    # Trigger a special path in collect_all
    codefind.collect_all()
    assert len(codefind.code_registry.functions[jackfruit.jack1.__code__]) == 3


def test_qualnames():
    reg = codefind.code_registry
    assert reg.codes[alaska.__file__, "nice", 5] is alaska.nice.__code__
    assert reg.codes[alaska.__file__, "nice", None] is alaska.nice.__code__


def test_qualnames_closure():
    reg = codefind.code_registry
    assert (
        reg.codes[alaska.__file__, "adderz", "f", 17]
        is alaska.pluz_one.__code__
    )
    assert (
        reg.codes[alaska.__file__, "adderz", "f", None]
        is alaska.pluz_one.__code__
    )


def test_find_code():
    assert (
        codefind.find_code("adderz", "f", module="tests.alaska")
        is alaska.pluz_one.__code__
    )
    assert (
        codefind.find_code("adderz", "f", filename=alaska.__file__)
        is alaska.pluz_one.__code__
    )
    assert (
        codefind.find_code("adderz", "f", module="tests.alaska", lineno=17)
        is alaska.pluz_one.__code__
    )
    with pytest.raises(KeyError):
        codefind.find_code("adderz", "f", module="tests.alaska", lineno=39)


def test_find_code_after_conform():
    assert (
        codefind.find_code("snow", module="tests.alaska")
        is alaska.snow.__code__
    )

    codefind.conform(alaska.snow, alaska.snow2)

    assert (
        codefind.find_code("snow", module="tests.alaska")
        is alaska.snow2.__code__
    )

    codefind.conform(alaska.snow, alaska.snow3)

    assert (
        codefind.find_code("snow", module="tests.alaska")
        is alaska.snow3.__code__
    )
