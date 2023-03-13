# Copyright (c) 2022 5@xes
# Based on the TabAntiWarping plugin  and licensed under LGPLv3 or higher.

VERSION_QT5 = False
try:
    from PyQt6.QtCore import QT_VERSION_STR
except ImportError:
    VERSION_QT5 = True
    
from . import TabPlus

from UM.i18n import i18nCatalog
i18n_catalog = i18nCatalog("tabplus")

def getMetaData():
    if not VERSION_QT5:
        QmlFile="qml/qml_qt6/CustomTab.qml"
    else:
        QmlFile="qml/qml_qt5/CustomTab.qml"
        
    return {
        "tool": {
            "name": i18n_catalog.i18nc("@label", "Tab Plus"),
            "description": i18n_catalog.i18nc("@info:tooltip", "Add Automatique Tab"),
            "icon": "tool_icon.svg",
            "tool_panel": QmlFile,
            "weight": 11
        }
    }

def register(app):
    return { "tool": TabPlus.TabPlus() }
