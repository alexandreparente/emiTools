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

__author__ = 'Alexandre Parente Lima'
__date__ = '2024-10-10'
__copyright__ = '(C) 2024 by Alexandre Parente Lima'

__revision__ = '$Format:%H$'

import os
import xml.etree.ElementTree as ET
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingParameterFolderDestination,
                       QgsProject,
                       QgsVectorLayer,
                       QgsProcessingException,
                       QgsWkbTypes,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem)

from .emi_tools_util import tr, get_validated_folder, get_transformation


class emiToolsExportKmlRpa(QgsProcessingAlgorithm):
    # Definition of input and output parameters
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config=None):
        # Input layer parameter using QgsProcessingParameterFeatureSource
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                'layer',
                tr('Input layer'),
                [QgsProcessing.TypeVectorPolygon, QgsProcessing.TypeVectorLine]
            )
        )

        # Input field parameter to select a field for naming the exported files
        self.addParameter(
            QgsProcessingParameterField(
                'export_field',
                tr('Export file name field'),
                '', 'layer', optional=True
            )
        )

        # Output folder parameter
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                tr('Output folder')
            )
        )

        # Option to load the output into the project
        self.addParameter(
            QgsProcessingParameterBoolean(
                'load_output',
                tr('Open output files after executing the algorithm'),
                defaultValue=True
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsSource(parameters, 'layer', context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, 'layer'))

        # Get the field selected by the user
        export_field = self.parameterAsString(parameters, 'export_field', context)
        load_output = self.parameterAsBool(parameters, 'load_output', context)

        # Get and validate output folder
        output_folder_param = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        output_folder = get_validated_folder(output_folder_param)

        output_files = []
        # Use centralized transformation utility
        transform = get_transformation(layer.sourceCrs(), 'EPSG:4326')

        features = layer.getFeatures()
        total_features = layer.featureCount()

        for i, feature in enumerate(features):
            if feedback.isCanceled():
                break

            # Sanitize filename
            raw_value = feature[export_field] if export_field and feature[
                export_field] else f"{layer.sourceName()}_{feature.id()}"
            field_value = str(raw_value).replace('.', '_').replace('/', '_').replace('\\', '_')

            geom = feature.geometry()
            if not geom or geom.isEmpty():
                continue

            geom.transform(transform)
            parts = [geom] if not geom.isMultipart() else geom.asGeometryCollection()

            for j, part in enumerate(parts):
                suffix = f"_{j + 1}" if len(parts) > 1 else ""
                file_name = f"{field_value}{suffix}"
                output_path = os.path.join(output_folder, f"{file_name}.kml")

                try:
                    self.save_kml(part, file_name, output_path)
                    output_files.append(output_path)
                except Exception as e:
                    # O feedback de erro de escrita KML
                    feedback.reportError(f"Error writing {file_name}: {e}")

            feedback.setProgress((i + 1) / total_features * 100 if total_features else 0)

        if load_output:
            self.load_layers(output_files)

        return {self.OUTPUT_FOLDER: output_folder}

    def save_kml(self, geom, name, path):
        """Creates a DJI Pilot compatible KML using standard ElementTree."""
        kml = ET.Element('kml', xmlns="http://www.opengis.net/kml/2.2")
        doc = ET.SubElement(kml, 'Document')
        placemark = ET.SubElement(doc, 'Placemark')
        ET.SubElement(placemark, 'name').text = name

        g_type = QgsWkbTypes.geometryType(geom.wkbType())

        if g_type == QgsWkbTypes.PolygonGeometry:
            poly_elem = ET.SubElement(placemark, 'Polygon')
            poly_obj = geom.get()

            # Exterior
            ext = ET.SubElement(ET.SubElement(poly_elem, 'outerBoundaryIs'), 'LinearRing')
            ET.SubElement(ext, 'coordinates').text = " ".join(
                [f"{v.x()},{v.y()},0" for v in poly_obj.exteriorRing().vertices()])

            # Interior
            for i in range(poly_obj.numInteriorRings()):
                inner = ET.SubElement(ET.SubElement(poly_elem, 'innerBoundaryIs'), 'LinearRing')
                ET.SubElement(inner, 'coordinates').text = " ".join(
                    [f"{v.x()},{v.y()},0" for v in poly_obj.interiorRing(i).vertices()])

        elif g_type == QgsWkbTypes.LineGeometry:
            line_elem = ET.SubElement(placemark, 'LineString')
            ET.SubElement(line_elem, 'coordinates').text = " ".join(
                [f"{v.x()},{v.y()},0" for v in geom.get().vertices()])

        tree = ET.ElementTree(kml)
        tree.write(path, encoding='utf-8', xml_declaration=True)

    def load_layers(self, files):
        layers = [QgsVectorLayer(f, os.path.basename(f), "ogr") for f in files]
        QgsProject.instance().addMapLayers([l for l in layers if l.isValid()])

    def name(self):
        return "ExportKMLstoDrone"

    def displayName(self):
        return tr("Export KML files to DJI Pilot")

    def group(self):
        return tr("Emi Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr(
            "This algorithm exports each feature from a polygon or line layer to a separate KML file, compatible with software DJI Pilot.<br> To ensure compatibility with the DJI Pilot app, the &lt;Folder&gt; tag ( automatically added by QGIS to structure KML content) is removed, as it is not supported by the application.")

    def createInstance(self):
        return emiToolsExportKmlRpa()