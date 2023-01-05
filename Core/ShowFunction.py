import inspect
import re

def Register(func, docURL=None or str):
    func._showInUI = True
    func._docURL = docURL

    signature = str(inspect.signature(func))
    typeMatches = re.findall("\:[^,\)]*", signature)
    returnMatches = re.findall("(?<=\)).*->.*$", signature)

    for match in typeMatches:
        signature = signature.replace(match, "")

    for match in returnMatches:
        signature = signature.replace(match, "")

    func._prettySignature = signature

def scan_module(module):
        def get():
            for name in dir(module):
                moduleAttr = getattr(module, name)
                if inspect.isfunction(moduleAttr):
                    print(moduleAttr)
                    show = getattr(moduleAttr, "_showInUI", 0)
                    print(show)
                    if show == True:
                        yield moduleAttr.__name__, moduleAttr.__doc__, moduleAttr._prettySignature, moduleAttr._docURL
        
        methodsInfo = {}
        for name, docs, signature, url in get():
            methodsInfo[name] = (docs, signature, url)
        return methodsInfo
