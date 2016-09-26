import sys
if sys.version_info.major == 2:
    import __builtin__ as builtins
else:
    import builtins
import functools

from mock import patch, mock_open


class patch_open(object):

    def __init__(self, read_data):
        self.open_patch = patch.object(
            builtins,
            'open',
            mock_open(read_data=read_data),
        )

    def __call__(self, fn):
        if hasattr(fn, 'patchings'):
            fn.patchings.append(self)
            return fn

        @functools.wraps(fn)
        def wrapped_func(*args, **kwargs):
            extra_args = []
            entered_patchers = []
            exc_info = tuple()

            try:
                for patching in wrapped_func.patchings:
                    arg = patching.__enter__()
                    entered_patchers.append(patching)
                    extra_args.append(arg)

                args += tuple(extra_args)
                func_res = fn(*args, **kwargs)
                return func_res
            except:
                if (
                    patching not in entered_patchers and
                    hasattr(patching, 'is_local')
                ):
                    # the patcher may have been started, but an exception
                    # raised whilst entering one of its additional_patchers
                    entered_patchers.append(patching)
                # Pass the exception to __exit__
                exc_info = sys.exc_info()
                # re-raise the exception
                raise
            finally:
                for patching in reversed(entered_patchers):
                    patching.__exit__(*exc_info)

        wrapped_func.patchings = [self]
        return wrapped_func

    def __enter__(self):
        return self.open_patch.__enter__()

    def __exit__(self, *args):
        self.open_patch.__exit__(*args)
