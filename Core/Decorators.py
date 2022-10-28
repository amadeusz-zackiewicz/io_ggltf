class ShowInUI(object):

    def __init__(self, method):
        self._method = method          
    
    def __call__(self, obj, *args, **kwargs):
        return self._method(obj, *args, **kwargs)

    @classmethod
    def scan_module(cls, module):
        def get():
            for name in dir(module):
                method = getattr(module, name)
                if isinstance(method, ShowInUI):
                    yield name, method.__doc__
        
        methodsInfo = {}
        for name, docs in get():
            methodsInfo[name] = docs
        return methodsInfo