from enum import Enum


class Status(Enum):
    Emailed = "emailed"  # ex 2000
    NotFound = "NotFound"  # ex404
    Requested = "Meeting time requested"
    Loading_error = "Loading error"
    Complicated = "complicated"
    book_error = "book error"
    TUNNEL_CONNECTION_FAILED = "ERR_TUNNEL_CONNECTION_FAILED"
    OK = "200"
    AUTH = 'AUTH006 concurrency limit reached',
    email_from_intro = 'email_from_intro',
    error = 'error',
    error_422 = 'error_422',
    fail = 'fail',
    no_available_events ='no available events',
    no_hours = 'no_hours',
    timeout = 'timeout',
    title_error = 'title_error',
    unavailable = 'unavailable'

    @staticmethod
    def in_values(item):
        for e in Status:
            if e.value == item:
                return True
        return False

    @staticmethod
    def in_names(item):
        for e in Status:
            if e.name == item:
                return True
        return False


def extract_name_from_intro(intro):
    full_name = intro.replace("Request a meeting with", "").strip() if intro is not None else None
    full_name = full_name.replace("Meet with", "").strip() if intro is not None else None
    full_name = full_name.replace("Find a time to talk with", "").strip() if intro is not None else None
    full_name = full_name.replace("Find a time to meet with", "").strip() if intro is not None else None
    full_name = full_name.replace("Find a time to meet", "").strip() if intro is not None else None
    full_name = full_name.replace("Meeting with", "").strip() if intro is not None else None
    full_name = full_name.replace("Schedule a meeting with ", "").strip() if intro is not None else None
    return full_name


def first_last(full_name: str):
    if full_name is None:
        first, last = "", ""
        return first, last
    arr = full_name.split(" ")
    if len(arr) == 0:
        first, last = arr[0], ""
        return first, last

    if len(arr) == 1:
        first, last = arr[0], ""
        return first, last

    if len(arr) == 2:
        first, last = arr[0], arr[1],
        return first, last

    if len(arr) > 2:
        first, last = arr[0], full_name.replace(arr[0], "")
        return first, last


if __name__ == '__main__':
    print(list(Status))
    print(Status['OK'])
    some_var = Status.OK
    print(some_var in Status)
    for e in Status:
        print(e.value)

    print(Status.in_values("OK"))
    print(Status.in_values("200"))

    print(Status.in_names("OK"))
    print(Status.in_names("200"))
