from urlvalidator import validate_url, ValidationError


def argument_concat(args):
    url = ""
    if len(args) > 1:
        for term in args:
            url += term + " "
    else:
        url = args[0]

    return url


def url_validation(url):
    try:
        validate_url(url)
        return True
    except ValidationError:
        return False
