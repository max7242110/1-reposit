"""Role definitions for the system (TZ section 24)."""

from __future__ import annotations

ROLES = {
    "admin": {
        "name": "Администратор",
        "permissions": [
            "brands.add_brand", "brands.change_brand", "brands.delete_brand", "brands.view_brand",
            "brands.add_brandoriginclass", "brands.change_brandoriginclass",
            "brands.delete_brandoriginclass", "brands.view_brandoriginclass",
            "methodology.add_methodologyversion", "methodology.change_methodologyversion",
            "methodology.delete_methodologyversion", "methodology.view_methodologyversion",
            "methodology.add_criteriongroup", "methodology.change_criteriongroup",
            "methodology.delete_criteriongroup", "methodology.view_criteriongroup",
            "methodology.add_criterion", "methodology.change_criterion",
            "methodology.delete_criterion", "methodology.view_criterion",
            "catalog.add_acmodel", "catalog.change_acmodel",
            "catalog.delete_acmodel", "catalog.view_acmodel",
            "catalog.add_modelrawvalue", "catalog.change_modelrawvalue",
            "catalog.delete_modelrawvalue", "catalog.view_modelrawvalue",
            "catalog.add_modelregion", "catalog.change_modelregion",
            "catalog.delete_modelregion", "catalog.view_modelregion",
            "catalog.add_equipmenttype", "catalog.change_equipmenttype",
            "catalog.view_equipmenttype",
            "scoring.view_calculationrun", "scoring.view_calculationresult",
            "core.view_auditlog",
        ],
    },
    "editor": {
        "name": "Редактор",
        "permissions": [
            "brands.view_brand",
            "methodology.view_methodologyversion", "methodology.view_criteriongroup",
            "methodology.view_criterion",
            "catalog.add_acmodel", "catalog.change_acmodel", "catalog.view_acmodel",
            "catalog.add_modelrawvalue", "catalog.change_modelrawvalue", "catalog.view_modelrawvalue",
            "catalog.add_modelregion", "catalog.change_modelregion", "catalog.view_modelregion",
            "scoring.view_calculationrun", "scoring.view_calculationresult",
            "core.view_auditlog",
        ],
    },
    "data_entry": {
        "name": "Оператор ввода",
        "permissions": [
            "brands.view_brand",
            "methodology.view_criterion",
            "catalog.view_acmodel",
            "catalog.add_modelrawvalue", "catalog.change_modelrawvalue", "catalog.view_modelrawvalue",
        ],
    },
    "lab": {
        "name": "Лаборатория",
        "permissions": [
            "brands.view_brand",
            "methodology.view_criterion",
            "catalog.view_acmodel",
            "catalog.add_modelrawvalue", "catalog.change_modelrawvalue", "catalog.view_modelrawvalue",
        ],
    },
    "viewer": {
        "name": "Наблюдатель",
        "permissions": [
            "brands.view_brand",
            "methodology.view_methodologyversion", "methodology.view_criteriongroup",
            "methodology.view_criterion",
            "catalog.view_acmodel", "catalog.view_modelrawvalue", "catalog.view_modelregion",
            "scoring.view_calculationrun", "scoring.view_calculationresult",
            "core.view_auditlog",
        ],
    },
}
