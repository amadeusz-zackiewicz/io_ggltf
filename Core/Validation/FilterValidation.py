from io_ggltf.Core.Exceptions import FilterExceptions


def validate_filter_arg(arg):
    if type(arg) == None:
        return []
        
    if type(arg) == tuple:
        arg = [arg]

    if type(arg) == list:
        for tup in arg:
            if type(tup) != tuple:
                raise FilterExceptions.IncorrectFilterFormatException(arg)
            if len(tup) != 2:
                raise FilterExceptions.IncorrectFilterFormatException(arg)
            if type(tup[0]) != str or type(tup[1]) != bool:
                raise FilterExceptions.IncorrectFilterFormatException(arg)
        return arg

    raise FilterExceptions.IncorrectFilterTypeException(arg)



    