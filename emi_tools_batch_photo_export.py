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
    QgsProcessingParameterBoolean,
    QgsProcessingException
)

from .emi_tools_util import tr, get_validated_folder


class emiToolsBatchPhotoExport(QgsProcessingAlgorithm):
    INPUT_LAYER = 'INPUT_LAYER'
    INPUT_FIELD = 'INPUT_FIELD'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    MOVE_FILES = 'MOVE_FILES'
    OVERWRITE = 'OVERWRITE'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                tr('Input layer'),
                [QgsProcessing.TypeVector]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.INPUT_FIELD,
                tr('Field containing photo path'),
                parentLayerParameterName=self.INPUT_LAYER,
                type=QgsProcessingParameterField.String
            )
        )

        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                tr('Output folder')
            )
        )

        # Advanced options - MOVE_FILES
        move_param = QgsProcessingParameterBoolean(
            self.MOVE_FILES,
            tr('Move files instead of copying'),
            defaultValue=False
        )
        move_param.setFlags(QgsProcessingParameterBoolean.FlagAdvanced)
        self.addParameter(move_param)

        # Advanced options - OVERWRITE
        overwrite_param = QgsProcessingParameterBoolean(
            self.OVERWRITE,
            tr('Overwrite existing files'),
            defaultValue=False
        )
        overwrite_param.setFlags(QgsProcessingParameterBoolean.FlagAdvanced)
        self.addParameter(overwrite_param)

    def processAlgorithm(self, parameters, context, feedback):
        layer = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        field_name = self.parameterAsString(parameters, self.INPUT_FIELD, context)
        move_files = self.parameterAsBoolean(parameters, self.MOVE_FILES, context)
        overwrite = self.parameterAsBoolean(parameters, self.OVERWRITE, context)

        # Get and validate output folder
        output_folder_param = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        output_folder = get_validated_folder(output_folder_param)

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

            # Check if file exists and handle overwrite logic
            if os.path.exists(dest_path) and not overwrite:
                feedback.pushInfo(f'Skipped (already exists): {filename}')
                continue

            try:
                if move_files:
                    shutil.move(photo_path, dest_path)
                    feedback.pushInfo(f'Moved: {photo_path} -> {dest_path}')
                else:
                    shutil.copy2(photo_path, dest_path)
                    feedback.pushInfo(f'Copied: {photo_path} -> {dest_path}')

                count += 1
            except Exception as e:
                action = "moving" if move_files else "copying"
                feedback.pushWarning(f'Error {action} {photo_path}: {str(e)}')

            feedback.setProgress(int(100 * (current + 1) / total))

        feedback.pushInfo(f'Finished. {count} files processed to {output_folder}.')
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
        return tr(
            "This algorithm copies or moves image files listed in a field of a vector layer to a destination folder.")

    def createInstance(self):
        return emiToolsBatchPhotoExport()