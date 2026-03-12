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
import tempfile
import zipfile
from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProject,
                       QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsVectorLayer,
                       QgsVectorFileWriter,
                       QgsMessageLog,
                       Qgis,
                       NULL)


def tr(string):
    """
    Returns a translatable string for the QGIS interface.
    """
    return QCoreApplication.translate('@default', string)


def get_validated_folder(path=None):
    """
    Validates the provided path or creates a temporary one if necessary.
    Ensures the directory exists and is ready for file operations.

    :param path: The suggested path for the output folder.
    :return: Absolute path to a valid, existing directory.
    """
    if not path:
        path = tempfile.mkdtemp(prefix='emi_tools_')

    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except OSError as e:
            QgsMessageLog.logMessage(
                tr(f"Could not create directory {path}: {str(e)}"),
                'emiTools',
                Qgis.MessageLevel.Critical
            )
            path = tempfile.mkdtemp(prefix='emi_tools_fallback_')

    return path


def get_transformation(source_crs, target_authid='EPSG:4326'):
    """
    Returns a coordinate transformation to a target CRS.

    :param source_crs: The source QgsCoordinateReferenceSystem.
    :param target_authid: The authority ID of the target CRS.
    :return: A QgsCoordinateTransform object.
    """
    dest_crs = QgsCoordinateReferenceSystem(target_authid)
    return QgsCoordinateTransform(source_crs, dest_crs, QgsProject.instance())


def create_memory_layer(name, geometry_type, crs_authid, fields):
    """
    Standardizes the creation of memory layers across the plugin.

    :param name: Layer name.
    :param geometry_type: QGIS geometry type (e.g., 'Point', 'LineString', 'Polygon').
    :param crs_authid: CRS string (e.g., 'EPSG:4326').
    :param fields: QgsFields object defining the attributes.
    :return: A ready-to-use QgsVectorLayer.
    """
    uri = f"{geometry_type}?crs={crs_authid}"
    layer = QgsVectorLayer(uri, name, "memory")
    provider = layer.dataProvider()
    provider.addAttributes(fields)
    layer.updateFields()
    return layer


def save_as_vector(layer, file_path, feedback=None):
    """
    Standardizes the export of layers to vector files on disk.
    Automatically detects the appropriate OGR driver based on file extension.

    :param layer: The QgsVectorLayer to be saved.
    :param file_path: Absolute path where the file will be created.
    :param feedback: Optional QgsProcessingFeedback object for UI reporting.
    :return: True if the save operation was successful.
    :raises Exception: If the QgsVectorFileWriter encounters an error.
    """
    extension = os.path.splitext(file_path)[1].lstrip('.')
    driver_name = QgsVectorFileWriter.driverForExtension(extension)

    options = QgsVectorFileWriter.SaveVectorOptions()
    options.driverName = driver_name
    options.fileEncoding = 'UTF-8'
    transform_context = QgsProject.instance().transformContext()

    error = QgsVectorFileWriter.writeAsVectorFormatV3(layer, file_path, transform_context, options)

    if error[0] != QgsVectorFileWriter.NoError:
        error_msg = tr(f"Error saving file {os.path.basename(file_path)}: {error[1]}")
        if feedback:
            feedback.reportError(error_msg)
        raise Exception(error_msg)

    if feedback:
        feedback.pushInfo(tr(f"File saved: {file_path}"))

    return True


def compress_to_zip(files, zip_path, feedback=None):
    """
    Standardizes file compression into a single ZIP archive.
    Ensures that files are stored with relative paths within the archive.

    :param files: List of absolute file paths to include in the ZIP.
    :param zip_path: Absolute path for the resulting .zip file.
    :param feedback: Optional QgsProcessingFeedback object for UI reporting.
    :return: The path to the created ZIP file.
    """
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file in files:
                if os.path.exists(file):
                    zipf.write(file, os.path.basename(file))

        if feedback:
            feedback.pushInfo(tr(f"Compressed file created: {zip_path}"))

    except Exception as e:
        error_msg = tr(f"Failed to create ZIP {os.path.basename(zip_path)}: {str(e)}")
        if feedback:
            feedback.reportError(error_msg)
        raise Exception(error_msg)

    return zip_path


def get_associated_files(file_path):
    """
    Identifies and collects sidecar files associated with specific vector formats.
    Commonly used for ESRI Shapefile components (.shx, .dbf, .prj, etc.).

    :param file_path: Path to the main file (e.g., .shp).
    :return: List of existing associated file paths found on disk.
    """
    extensions = ['shp', 'shx', 'dbf', 'prj', 'cpg', 'qpj']
    base_name = os.path.splitext(file_path)[0]
    ext_original = os.path.splitext(file_path)[1].lower().replace('.', '')

    # If it's not a Shapefile, return only the original file if it exists
    if ext_original != 'shp':
        return [file_path] if os.path.exists(file_path) else []

    # If it is a Shapefile, look for all associated sidecar files
    found_files = []
    for ext in extensions:
        sidecar = f"{base_name}.{ext}"
        if os.path.exists(sidecar):
            found_files.append(sidecar)
    return found_files