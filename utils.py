def parseTimedelta(str):
    """ A simple time parser"""
    granules = {'s': 1, 'm': 60, 'h': 60*60, 'd': 24*60*60}
    sample = 0
    number = []
    for c in str:
        if c.isdigit():
            number.append(c)
        else:
            try:
                sample = granules[c]
                break
            except KeyError:
                raise KeyError('Valid keys are s (second), m (minute), h (hour), d (day)')
    number = int("".join(number))
    return number*sample
