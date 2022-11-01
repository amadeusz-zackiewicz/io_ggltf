from io_ggltf import Constants as __c
from . import Register

__fallbackTab = "gglTF Export"
__fallbackPanel = "Export"

class _ButtonMethod(object):
    def __init__(self, function, area: str, tabName: str, panelName: str, label: str):
        self.function = function
        self.area = area
        self.tabName = tabName
        self.panelName = panelName
        self.label = label
        Register.add_button(self)


def Button(where: str, area = __c.BLENDER_AREA_VIEW_3D):
    def _genButton(function):
        split = where.split("/")

        if where == "":
            tab = __fallbackTab
            panel = __fallbackPanel
            label = id
        if len(split) == 1:
            tab = __fallbackTab
            panel = __fallbackPanel
            label = split[0]
        elif len(split) == 2:
            tab = __fallbackTab
            panel = split[0]
            label = split[1]
        elif len(split) >= 3:
            tab = split[0]
            panel = split[1]
            label = split[2]

        return _ButtonMethod(function=function, area=area, tabName=tab, panelName=panel, label=label)

    return _genButton
