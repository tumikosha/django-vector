"""
    version .1.0
    Module to calculate the execution time of my_code. Result stores in global variable
    Also function decorator `@speed()` allows you to add cache and execution time parameters to any function
    USAGE:
        with measure_execution_time("code_execution_time"):
            time.sleep(2)
            print("Inside the context")

        global code_execution_time
        print("global variable `code_execution_time`:", code_execution_time)

    See main section for `@speed()` examples
"""
import time
from contextlib import contextmanager
from datetime import datetime


class TrialContextManager:
    """ Trial content manager to ignore all errors in my_code """

    def __enter__(self): pass

    def __exit__(self, *args): return True


trial = TrialContextManager()
TRIAL = TrialContextManager()


def speed(**params):
    def speedometer(func):
        def wrapper(*args, **kwargs):
            global cache
            cache = {} if 'cache' not in globals() else cache
            # print(params)
            add_exec_time_flag = False
            cache_flag = False
            comment = ""
            if kwargs.get('cache', False):
                cache_flag = True  # kwargs.get('mem')
                del kwargs['cache']
            if kwargs.get('print', False):
                print_flag = kwargs.get('print')
                del kwargs['print']
            else:
                with TRIAL:
                    del kwargs['print']
                print_flag = None
            if kwargs.get('add_exec_time', False):
                del kwargs['add_exec_time']
                add_exec_time_flag = True
            else:
                with TRIAL:
                    del kwargs['add_exec_time']
                add_exec_time_flag = None
            if kwargs.get('sleep'):
                time.sleep(kwargs.get('sleep'))
                del kwargs['sleep']
            else:
                with TRIAL:
                    del kwargs['sleep']
                sleep = 0

            key = func.__name__ + "#".join(args) + str(kwargs)
            if key in cache:
                start_time = datetime.now()
                result = cache.get(key)
                end_time = datetime.now()
                comment = "from cache"
            else:
                start_time = datetime.now()
                result = func(*args, **kwargs)
                end_time = datetime.now()
                if cache_flag:
                    comment = ""
                    cache[key] = result

            time_difference = (end_time - start_time)  # * 1000
            if print_flag is not None:
                # print(f">> '{func.__name__}' time:{time_difference:.{print_flag}f} result {comment}: {result}")
                print(f">> '{func.__name__}' execution_time: {time_difference} result {comment}: {result}")
            # if params.get('result', None) is None:
            if add_exec_time_flag:
                return result, time_difference
            else:
                return result

        return wrapper

    return speedometer


@speed()
def example_function(name):
    time.sleep(1)
    print(name)
    return name


@contextmanager
def speedometer(global_var_name, verbose=True):
    # start_time = time.time()
    start_time = datetime.now()
    try:
        yield
    finally:
        end_time = datetime.now()
        td = end_time - start_time
        globals()[global_var_name] = td
        if verbose:
            print(f"■ {global_var_name}    ■ {td}   ■  end_time:   {datetime.now()}")


measure_execution_time = speedometer


class time_this_scope():
    """Context manager to measure how much time was spent in the target scope."""

    def __init__(self, verbose=True, label=""):
        self.t0 = None
        self.dt = None
        self.label = label
        self.verbose = verbose

    def __enter__(self):
        self.t0 = time.perf_counter()
        self.start_time = datetime.now()

    def __exit__(self, type=None, value=None, traceback=None):
        self.dt = (time.perf_counter() - self.t0)  # Store the desired value.
        end_time = datetime.now()
        self.diff = end_time - self.start_time
        if self.verbose is True:
            print(f"Scope took {self.dt * 1000: 0.1f} milliseconds.")
            print(f"■ {self.label}    ■ {self.diff}   ■  end_time:   {datetime.now()}")


print(f"[x] Module {__name__} loaded")

if __name__ == '__main__':
    timer = time_this_scope()
    with timer:
        time.sleep(0.100)

    print(timer.diff)


    with speedometer("result"):
        time.sleep(2)
        print("Inside the context")
    # or alternative
    with measure_execution_time("code_execution_time"):
        time.sleep(2)
        print("Inside the context")

    global code_execution_time
    print("global variable `code_execution_time`:", code_execution_time)

    example_function("AAA", cache="memory", sleep=1, add_exec_time=True, print=True)
    example_function("AAA", cache="memory", sleep=1, add_exec_time=True, print=False)
    example_function("AAA", cache="memory", sleep=1, add_exec_time=True)
    example_function("AAA", cache="memory", sleep=1, add_exec_time=False)
    example_function("AAA", cache="memory", sleep=1, )
    example_function("AAA", cache="memory", sleep=False, )
    a = example_function("AAA", cache="memory", sleep=5, )
    print(a)
