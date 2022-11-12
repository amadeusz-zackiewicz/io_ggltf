import inspect
import re

class _DocsUI(object):

    def __init__(self, method, docsURL=None):
        self._method = method 
        self._url = docsURL
        self.__doc__ = method.__doc__

        signature = str(inspect.signature(method))
        typeMatches = re.findall("\:[^,\)]*", signature)
        returnMatches = re.findall("(?<=\)).*->.*$", signature)

        for match in typeMatches:
            signature = signature.replace(match, "")

        for match in returnMatches:
            signature = signature.replace(match, "")

        self._signature = signature

    def __call__(self, *args, **kwargs):
        return self._method(*args, **kwargs)

    @classmethod
    def scan_module(cls, module):
        def get():
            for name in dir(module):
                method = getattr(module, name)
                if isinstance(method, _DocsUI):
                    yield name, method._method.__doc__, method._signature, method._url
        
        methodsInfo = {}
        for name, docs, signature, url in get():
            methodsInfo[name] = (docs, signature, url)
        return methodsInfo

def ShowInUI(docsURL=None):
    def _docsUI(method):
        return _DocsUI(method=method, docsURL=docsURL)

    return _docsUI