from krita import DockWidgetFactory, DockWidgetFactoryBase
from .smallselectiondocker import SmallSelectionButtonsDocker

DOCKER_ID = 'small_selection_buttons'


dock_widget_factory = DockWidgetFactory(DOCKER_ID,
                        DockWidgetFactoryBase.DockRight,
                        SmallSelectionButtonsDocker)

Krita.instance().addDockWidgetFactory(dock_widget_factory)



