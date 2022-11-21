import pytest


def _test_scenario(test_type):
    if hasattr(pytest, "config"):
        _config = getattr(pytest, "config")
        if hasattr(_config, test_type) and getattr(_config, test_type):
            return True
    return False


def is_smoke_test():
    return _test_scenario("smoke")


def is_full_test():
    return _test_scenario("full")


def is_remote_test():
    return _test_scenario("remote")


def is_manual_test():
    return _test_scenario("manual")


def is_extra_resource_test():
    return _test_scenario("extra_resource")


full = pytest.mark.full
# def full(fun):
#     return pytest.mark.skipif(not is_full_test(), reason='Skip this full test')(fun)

smoke = pytest.mark.smoke


# def smoke(fun):
#     return pytest.mark.skipif(not is_smoke_test(), reason='Skip this smoke test')(fun)


def smoke_only(fun):
    return pytest.mark.skipif(
        is_full_test() or not is_smoke_test(), reason="Only run in smoke test"
    )(fun)


def manual(fun):
    return pytest.mark.skipif(not is_manual_test(), reason="This is a manual test")(fun)


def not_remote(fun):
    return pytest.mark.skipif(is_remote_test(), reason="this is a local test")(fun)


def remote_only(fun):
    return pytest.mark.skipif(not is_remote_test(), reason="this is a remote test")(fun)


def extra_resource(fun):
    return pytest.mark.skipif(
        not is_extra_resource_test(), reason="This test need extra resource"
    )(fun)
