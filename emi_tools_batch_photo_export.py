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
"""

__author__ = 'Alexandre Parente Lima'
__date__ = '2024-10-10'
__copyright__ = '(C) 2024 by Alexandre Parente Lima'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import shutil

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFolderDestination,
    QgsProcessingException
)

def tr(string):
    return QCoreApplication.translate('@default', string)

class emiToolsBatchPhotoExport(QgsProcessingAlgorithm):

    INPUT_LAYER = 'INPUT_LAYER'
    INPUT_FIELD = 'INPUT_FIELD'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_LAYER,
            tr('Imput layer'),
            [QgsProcessing.TypeVector]
        ))

        self.addParameter(QgsProcessingParameterField(
            self.INPUT_FIELD,
            tr('Field containing photo file paths'),
            parentLayerParameterName=self.INPUT_LAYER,
            type=QgsProcessingParameterField.String
        ))

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER,
            tr('Output folder')
        ))

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        field_name = self.parameterAsString(parameters, self.INPUT_FIELD, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        total = layer.featureCount()
        feedback.setProgress(0)
        count = 0

        for current, feature in enumerate(layer.getFeatures()):
            if feedback.isCanceled():
                break

            value = feature[field_name]
            if not value:
                feedback.pushInfo(f'Feature {feature.id()} has no path in the "{field_name}" field.')
                continue

            photo_path = str(value).strip()
            if not os.path.isfile(photo_path):
                feedback.pushWarning(f'File not found: {photo_path}')
                continue

            filename = os.path.basename(photo_path)
            dest_path = os.path.join(output_folder, filename)

            try:
                shutil.copy2(photo_path, dest_path)
                feedback.pushInfo(f'Copied: {photo_path} -> {dest_path}')
                count += 1
            except Exception as e:
                feedback.pushWarning(f'Error copying {photo_path}: {str(e)}')

            feedback.setProgress(int(100 * (current + 1) / total))

        feedback.pushInfo(f'Finished. {count} files copied to {output_folder}.')
        return {self.OUTPUT_FOLDER: output_folder}

    def name(self):
        return "batchphotoxport"

    def displayName(self):
        return tr("Batch photo export")

    def group(self):
        return tr("Emi Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr("Copies image files listed in a field of a vector layer to a destination folder. Works with all features or only the selected ones, depending on the input layer settings.")

    def createInstance(self):
        return emiToolsBatchPhotoExport()



