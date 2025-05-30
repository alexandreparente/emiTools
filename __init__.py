# -*- coding: utf-8 -*-
"""
/***************************************************************************
 emiTools
                                 A QGIS plugin
 This plugin compiles tools used by EMI-PB
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
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
 This script initializes the plugin, making it known to QGIS.
"""

__author__ = 'Alexandre Parente Lima'
__date__ = '2024-10-10'
__copyright__ = '(C) 2024 by Alexandre Parente Lima'


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load emiTools class from file emiTools.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    from .emi_tools import emiToolsPlugin

    return emiToolsPlugin()


