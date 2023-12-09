class TrialContextManager:
    """ Trial content manager to ignore all errors in my_code """
    def __enter__(self): pass
    def __exit__(self, *args): return True


trial = TrialContextManager()
TRIAL = TrialContextManager()


with trial: a = 1 / 0  # will be not executed and no exception is raised
