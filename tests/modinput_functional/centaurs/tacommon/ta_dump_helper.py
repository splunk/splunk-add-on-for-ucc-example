import pickle
import decorator
import types
import copy
import pytest_splunk_addon.helmut.util.rip
import pytest_splunk_addon.helmut.splunk.base
import logging
import thread
import sys

dump_prefix = "dump.pickle"


def _should_remove(obj):
    return isinstance(
        obj,
        (
            types.GeneratorType,
            types.FileType,
            thread.LockType,
            logging.Logger,
            logging.FileHandler,
            types.FunctionType,
            helmut.util.rip.RESTInPeace,
            helmut.splunk.base.Splunk,
            types.ModuleType,
        ),
    ) or callable(obj)


def remove_unpickleable_obj2(obj, seen=None):
    if seen is None:
        seen = []

    if _should_remove(obj):
        return None

    try:
        pickle.dumps(obj)
    except (pickle.PickleError, TypeError):
        pass
    else:
        return obj

    if id(obj) in seen:
        # already in the list, return None now
        return None
    seen.append(id(obj))

    if isinstance(obj, (list, tuple, set)):
        _obj = []
        for v in obj:
            _v = remove_unpickleable_obj2(v, seen)
            _obj.append(_v)
        if isinstance(obj, tuple):
            _obj = tuple(_obj)
        elif isinstance(obj, set):
            _obj = set(_obj)
        return _obj

    if isinstance(obj, dict):
        _obj = {}
        for k, v in obj.items():
            if isinstance(k, basestring):
                _k = k
            else:
                _k = remove_unpickleable_obj2(k, seen)
            _v = remove_unpickleable_obj2(v, seen)
            _obj[_k] = _v
        return _obj

    if hasattr(obj, "__getstate__"):
        # TODO
        # can not handle __getstate__, remove this obj
        return None

    if not hasattr(obj, "__dict__"):
        return None

    _obj = copy.copy(obj)
    for key, value in _obj.__dict__.items():
        _value = remove_unpickleable_obj2(value, seen)
        setattr(_obj, key, _value)

    return _obj


def dump_object(func):
    def wrapper(_func, *args, **kwargs):
        try:
            _func(*args, **kwargs)
        except AssertionError as e:
            c = args[0]
            d = copy.copy(c)
            # can't pickle generator, file, lock objects
            seen = []
            d2 = remove_unpickleable_obj2(d, seen)
            file_name = f"{dump_prefix}.{c.__class__.__name__}.{_func.__name__}"
            with open(file_name, "w") as f:
                pickle.dump(d2, f)
            raise e

    return decorator.decorator(wrapper, func)


def dump_object_class(cls):
    for key, value in cls.__dict__.items():
        if callable(value) and key.startswith("test"):
            value = dump_object(value)
            setattr(cls, key, value)
    return cls


def load_object(file_name):
    with open(file_name) as f:
        return pickle.load(f)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("you mast pass the file path as the first parameter")
        sys.exit(1)
    file_path = sys.argv[1]
    d = load_object(file_path)
    print(d)
