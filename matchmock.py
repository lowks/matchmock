'''Hamcrest matchers for mock objects'''

from hamcrest.core.base_matcher import BaseMatcher
from hamcrest import contains, equal_to, all_of, anything, has_entry, has_item

__all__ = ['called', 'not_called', 'called_once',
           'called_with', 'called_once_with']


class Call(BaseMatcher):
    '''A matcher that describes a call.

    The positional arguments and keyword arguments are represented with
    individual submatchers.
    '''

    def __init__(self, args, kwargs):
        self.args = args
        self.kwargs = kwargs

    def _matches(self, item):
        return self.args.matches(item[0]) and self.kwargs.matches(item[1])

    def describe_call(self, args, kwargs, desc):
        desc.append_description_of(args)
        desc.append_text(', ')
        desc.append_description_of(kwargs)

    def describe_mismatch(self, item, mismatch_description):
        args, kwargs = item
        self.describe_call(args, kwargs, mismatch_description)

    def describe_to(self, desc):
        self.describe_call(self.args, self.kwargs, desc)


def match_args(args):
    '''Create a matcher for positional arguments'''

    return contains(*args)


def match_kwargs(kwargs):
    '''Create a matcher for keyword arguments'''

    return all_of(*[has_entry(k, v) for k, v in kwargs.items()])


class Called(BaseMatcher):
    '''Matches a mock and asserts the number of calls and parameters'''

    def __init__(self, call, count=None):
        self.call = call
        self.count = count

    def _matches(self, item):
        if self.count is not None and item.call_count != self.count:
            return False

        if self.count == 0:
            return True

        return has_item(self.call).matches(item.call_args_list)

    def describe_mismatch(self, item, mismatch_description):
        if item.call_count == 0 or (self.count is not None and item.call_count != self.count):
            mismatch_description.append_text(
                'was called %s times' % item.call_count)
        else:
            mismatch_description.append_text('was called with ')
            for i, call in enumerate(item.call_args_list):
                if i != 0:
                    mismatch_description.append_text(' and ')

                self.call.describe_mismatch(call, mismatch_description)

    def describe_to(self, desc):
        desc.append_text('Mock called with ')
        self.call.describe_to(desc)
        desc.append_text(' %s times' % self.count)


def called():
    '''Match mock that was called one or more times'''

    return Called(anything())


def not_called():
    '''Match mock that was never called'''

    return Called(anything(), count=0)


def called_once():
    '''Match mock that was called once regardless of arguments'''

    return Called(anything(), count=1)


def called_with(*args, **kwargs):
    '''Match mock has at least one call with the specified arguments'''

    return Called(Call(match_args(args), match_kwargs(kwargs)))


def called_once_with(*args, **kwargs):
    '''Match mock that was called once and with the specified arguments'''

    return Called(Call(match_args(args), match_kwargs(kwargs)), count=1)
