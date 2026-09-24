# -*- coding: utf-8 -*-

"""
/***************************************************************************
 emiTools
                                 A QGIS plugin
 This plugin compiles tools used by EMI-PB

                              -------------------
        begin                : 2024-10-10
        copyright            : (C) 2024 by Alexandre Parente Lima
        email                : alexandre.parente@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = "Alexandre Parente Lima"
__date__ = "2024-10-10"
__copyright__ = "(C) 2024 by Alexandre Parente Lima"

__revision__ = "$Format:%H$"

import os

from qgis.core import QgsApplication, QgsExpression
from qgis.PyQt.QtCore import QCoreApplication, QLocale, QSettings, QTranslator

from .emi_tools_provider import emiToolsProvider
from .expressions import discover_functions


class emiToolsPlugin(object):
    def __init__(self):
        self.provider = None

        # Initialize the plugin path directory
        self.plugin_dir = os.path.dirname(__file__)

        # Automatically discover every expression function defined inside
        # the `expressions` package, instead of maintaining a manual list
        self.expression_functions = discover_functions()

        # Gets the locale configured in the system.
        settings = QSettings()
        locale = settings.value("locale/userLocale", QLocale.system().name())

        # Initialize locale
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "emiTools_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

    def initProcessing(self):
        """Init Processing provider for QGIS >= 3.8."""
        self.provider = emiToolsProvider()
        QgsApplication.processingRegistry().addProvider(self.provider)

    def initGui(self):
        self.initProcessing()
        for expr in self.expression_functions:
            if not QgsExpression.isFunctionName(expr.name()):
                QgsExpression.registerFunction(expr)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
        for expr in self.expression_functions:
            if QgsExpression.isFunctionName(expr.name()):
                QgsExpression.unregisterFunction(expr.name())
