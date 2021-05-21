import gc
import importlib
import sys
import time
import types
from collections import defaultdict
from inspect import getattr_static

MAX_TIME = 0.1


def _make_audithook(self):
    def watch_exec(event, obj):  # pragma: no cover
        # Note: Python does not trace audit hooks, so normal use will not show
        # coverage of this function even if it is executed
        if event == "exec":
            (code,) = obj
            self.assimilate(code)

    # The closure is faster than a method on _CodeDB
    return watch_exec


class ConformException(Exception):
    pass


class CodeRegistry:
    def __init__(self):
        self.codes = {}
        self.functions = defaultdict(set)
        self.last_cost = 0
        self.always_use_cache = False

    def setup(self):
        self.collect_all()
        sys.addaudithook(_make_audithook(self))

    def collect_all(self):
        # Collect code objects
        results = []
        for obj in gc.get_objects():
            if isinstance(obj, types.FunctionType):
                results.append((obj, obj.__code__))
            elif getattr_static(obj, "__conform__", None) is not None:
                for x in gc.get_referents(obj):
                    if isinstance(x, types.CodeType):
                        results.append((obj, x))
        for obj, co in results:
            if isinstance((qual := getattr(obj, "__qualname__", None)), str):
                qualpath = [part for part in qual.split(".")[:-1] if part != "<locals>"]
                self.assimilate(co, (co.co_filename, *qualpath))
            self.functions[co].add(obj)

    def assimilate(self, code, path=()):
        if code.co_name == "<module>":  # pragma: no cover
            # Typically triggered by the audit hook
            name = code.co_filename
        elif code.co_name.startswith("<"):
            return
        else:
            name = code.co_name
        if name:
            path = (*path, name)
            self.codes[(*path, code.co_firstlineno)] = code
            self.codes[(*path, None)] = code
        for ct in code.co_consts:
            if isinstance(ct, types.CodeType):
                self.assimilate(ct, path)

    def _get_functions(self, code):
        t = time.time()
        results = [
            fn
            for fn in gc.get_referrers(code)
            if isinstance(fn, types.FunctionType) or hasattr(fn, "__conform__")
        ]
        self.functions[code] = set(results)
        self.last_cost = time.time() - t
        return results

    def get_functions(self, code, use_cache=False):
        use_cache = use_cache or self.always_use_cache or self.last_cost > MAX_TIME
        if use_cache and (results := self.functions[code]):
            return list(results)
        else:
            return self._get_functions(code)

    def update_cache_entry(self, obj, old_code, new_code):
        self.functions[old_code].discard(obj)
        self.functions[new_code].add(obj)

    def find_code(self, *path, filename=None, module=None, lineno=None):
        if module is not None:
            assert filename is None
            filename = importlib.import_module(module).__file__
        assert filename is not None
        path = (filename, *path, lineno)
        return self.codes[path]

    def conform(self, obj1, obj2, use_cache=False):
        if hasattr(obj1, "__conform__"):
            obj1.__conform__(obj2)

        elif isinstance(obj1, types.CodeType):
            for fn in self.get_functions(obj1, use_cache=use_cache):
                self.conform(fn, obj2)

        elif isinstance(obj2, types.FunctionType):
            self.conform(obj1, obj2.__code__)
            obj1.__defaults__ = obj2.__defaults__
            obj1.__kwdefaults__ = obj2.__kwdefaults__

        elif isinstance(obj2, types.CodeType):
            fv1 = obj1.__code__.co_freevars
            fv2 = obj2.co_freevars
            if fv1 != fv2:
                msg = (
                    f"Cannot replace closure `{obj1.__name__}` because the free "
                    f"variables changed. Before: {fv1}; after: {fv2}."
                )
                if ("__class__" in (fv1 or ())) ^ ("__class__" in (fv2 or ())):
                    msg += " Note: The use of `super` entails the `__class__` free variable."
                raise ConformException(msg)
            self.update_cache_entry(obj1, obj1.__code__, obj2)
            obj1.__code__ = obj2

        elif obj2 is None:
            pass

        else:  # pragma: no cover
            raise ConformException(f"Cannot conform {obj1} with {obj2}")
