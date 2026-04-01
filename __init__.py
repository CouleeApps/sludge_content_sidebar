from binaryninja import core_ui_enabled


if core_ui_enabled():
    from binaryninjaui import Sidebar

    from .sidebar import SludgeContentSidebarWidgetType

    Sidebar.addSidebarWidgetType(SludgeContentSidebarWidgetType())
