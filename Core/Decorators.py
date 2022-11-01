class _DocsUI(object):

    def __init__(self, method, docsURL=None):
        self._method = method 
        self._url = docsURL         
    
    def __call__(self, obj, *args, **kwargs):
        return self._method(obj, *args, **kwargs)

    @classmethod
    def scan_module(cls, module):
        def get():
            for name in dir(module):
                method = getattr(module, name)
                if isinstance(method, _DocsUI):
                    yield name, method._method.__doc__, method._url
        
        methodsInfo = {}
        for name, docs, url in get():
            methodsInfo[name] = (docs, url)
        return methodsInfo

def ShowInUI(docsURL=None):
    def _docsUI(method):
        return _DocsUI(method=method, docsURL=docsURL)

    return _docsUI