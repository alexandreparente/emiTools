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

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

from qgis.core import QgsMessageLog, QgsProject
from qgis.utils import qgsfunction


def get_layer_custom_property_logic(layer_name: str, property_key: str):
    """
    Returns the value of a 'Custom Property' from a layer in the project.
    """

    layers = QgsProject.instance().mapLayersByName(layer_name)

    if not layers:
        QgsMessageLog.logMessage(
            f"Function 'get_layer_custom_property' could not find layer: {layer_name}",
            "Python Functions",
        )
        return None

    # Get the first layer found with this name
    layer = layers[0]

    property_value = layer.customProperty(property_key)
    return property_value


@qgsfunction(args="auto", group="EMI Tools")
def get_layer_custom_property(layer_name, property_key, feature, parent):
    """
    Returns the value of a 'Custom Property' from a specific layer in the project.

    <h4>Syntax</h4>
    <p><b style="color:#0a6099;">get_layer_custom_property</b>
    (<i style="color:#bf0c0c;">string</i>, <i style="color:#bf0c0c;">string</i>)</p>

    <h4>Arguments</h4>
    <p><b>layer_name</b> (<i style="color:#bf0c0c;">string</i>): Name of the project layer.</p>
    <p><b>property_key</b> (<i style="color:#bf0c0c;">string</i>): Name of the custom property to retrieve.</p>

    <h4>Example</h4>
    <p>get_layer_custom_property('my_layer', 'my_property') -> 'property'</p>
    <p>get_layer_custom_property('Image previews','planet/previewItemIds') -> '["PSScene:20251006_131906_03_24f6", "PSScene:20251006_131903_99_24f6"]'</p>
    <p>get_image_date(from_json(  get_layer_custom_property('Image previews','planet/previewItemIds'))[0]) -> QDate('2017-01-05')</p>
    """

    return get_layer_custom_property_logic(layer_name, property_key)
