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
from qgis.PyQt.QtCore import (Qt, QRect, QRectF, QDateTime, QFileInfo)
from qgis.PyQt.QtGui import (QImage, QPainter, QFont, QColor, QFontDatabase)
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.PyQt.QtWidgets import QApplication
from qgis.core import (QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFile,
                       QgsProcessingParameterString,
                       QgsProcessingParameterColor,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingException,
                       QgsProcessingParameterDefinition,
                       QgsExifTools)

from .emi_tools_photo_metadata import get_exif_data, get_translated_metadata_map, get_metadata_keys
from .emi_tools_util import tr, get_validated_folder


class emiToolsStampPhotoRpa(QgsProcessingAlgorithm):
    INPUT_PHOTO = 'INPUT_PHOTO'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    STAMP_IMAGE = 'STAMP_IMAGE'
    INPUT_TEXT = 'INPUT_TEXT'
    METADATA_TO_STAMP = 'METADATA_TO_STAMP'
    FONT_COLOR = 'FONT_COLOR'
    FONT_NAME = 'FONT_NAME'
    POSITION = 'POSITION'
    STAMP_HEIGHT_VALUE = 'STAMP_HEIGHT_VALUE'
    STAMP_HEIGHT_UNIT = 'STAMP_HEIGHT_UNIT'
    MARGIN_VALUE = 'MARGIN_VALUE'

    POSITION_OPTIONS = [
        'Bottom Left',
        'Bottom Right',
        'Top Left',
        'Top Right'
    ]

    UNIT_OPTIONS = [
        'Percentage (%)',
        'Pixels (px)',
        'Centimeters (cm)',
        'Millimeters (mm)',
        'Inches (pol)'
    ]

    def initAlgorithm(self, config=None):
        # Initializes the algorithm's parameters
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_PHOTO,
                tr('Input folder'),
                behavior=QgsProcessingParameterFile.Folder
            )
        )

        self.addParameter(
            QgsProcessingParameterFile(
                self.STAMP_IMAGE,
                tr('SVG Image'),
                extension='svg',
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                self.INPUT_TEXT,
                tr('Text'),
                defaultValue="",
                multiLine=True
            )
        )

        translated_map = get_translated_metadata_map()
        all_known_keys = get_metadata_keys()
        metadata_options_display = [translated_map[key] for key in all_known_keys]

        # Defines which fields are pre-selected by default
        untranslated_defaults = ['model',
                                 'timestamp',
                                 'coordinates',
                                 'altitude']
        default_indices = [all_known_keys.index(key) for key in untranslated_defaults if key in all_known_keys]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.METADATA_TO_STAMP,
                tr('Metadata to stamp'),
                options=metadata_options_display,
                allowMultiple=True,
                defaultValue=default_indices
            )
        )

        # Return the translated options for display to the user
        def get_translated_position_options():
            """Retorna uma lista de opções de posição traduzidas para a interface."""
            return [
                tr('Bottom Left'),
                tr('Bottom Right'),
                tr('Top Left'),
                tr('Top Right')
            ]

        # Calling the function to get the translated options
        self.addParameter(
            QgsProcessingParameterEnum(
                self.POSITION,
                tr('Position of text and image'),
                options=get_translated_position_options(),
                defaultValue=0
            )
        )

        # font parameters
        font_db = QFontDatabase()
        fonts = font_db.families()

        # Get the default font from QGIS
        app = QApplication.instance()
        default_font = app.font().family()

        # Check if the default font is available on the system
        default_font_index = fonts.index(default_font) if default_font in fonts else 0

        # Add the Enum parameter to select the font
        self.addParameter(
            QgsProcessingParameterEnum(
                self.FONT_NAME,
                tr('Font'),
                options=fonts,
                defaultValue=default_font_index
            )
        )

        self.addParameter(
            QgsProcessingParameterColor(
                self.FONT_COLOR,
                tr('Font color'),
                defaultValue=QColor(255, 255, 0)
            )
        )

        # Return the translated options for display to the user
        def get_translated_unit_options():
            """Retorna uma lista de opções de unidades traduzidas para o pylupdate5 capturar."""
            return [
                tr('Percentage (%)'),
                tr('Pixels (px)'),
                tr('Centimeters (cm)'),
                tr('Millimeters (mm)'),
                tr('Inches (pol)')
            ]

        # Advanced parameters
        stamp_height_unit_param = QgsProcessingParameterEnum(
            self.STAMP_HEIGHT_UNIT,
            tr('Stamp height unit'),
            options=get_translated_unit_options(),
            defaultValue=0
        )
        stamp_height_unit_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(stamp_height_unit_param)

        # Height value parameters
        stamp_height_value_param = QgsProcessingParameterNumber(
            self.STAMP_HEIGHT_VALUE,
            tr('Stamp height value'),
            defaultValue=10,
            minValue=0.1,
            maxValue=5000,
            type=QgsProcessingParameterNumber.Double
        )
        stamp_height_value_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(stamp_height_value_param)

        # Margin from edge value parameters
        margin_value_param = QgsProcessingParameterNumber(
            self.MARGIN_VALUE,
            tr('Margin from edge'),
            defaultValue=2,
            minValue=0,
            maxValue=1000,
            type=QgsProcessingParameterNumber.Double
        )
        margin_value_param.setFlags(QgsProcessingParameterDefinition.FlagAdvanced)
        self.addParameter(margin_value_param)

        # Output folder
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                tr('Output folder')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Loads the input raster layers
        input_folder = self.parameterAsString(parameters, self.INPUT_PHOTO, context)

        # List the image files in the folder
        image_extensions = ('.jpg', '.jpeg', '.tif', '.tiff', '.png')
        input_photos = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if
                        f.lower().endswith(image_extensions)]

        # Get and validate output folder utilizando a função centralizada
        output_folder_param = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        output_folder = get_validated_folder(output_folder_param)

        svg_file_path = self.parameterAsFile(parameters, self.STAMP_IMAGE, context)

        # Collects text and style parameters
        input_text = self.parameterAsString(parameters, self.INPUT_TEXT, context)
        font_color = self.parameterAsColor(parameters, self.FONT_COLOR, context)

        # get font
        font_index = self.parameterAsEnum(parameters, self.FONT_NAME, context)
        font_db = QFontDatabase()
        fonts = font_db.families()
        font_name = fonts[font_index]

        # Use the index to access the string (untranslated)
        position_index = self.parameterAsInt(parameters, self.POSITION, context)
        position = self.POSITION_OPTIONS[position_index]

        # Get the user-selected keys
        translated_map = get_translated_metadata_map()
        all_known_keys = get_metadata_keys()
        selected_indices = self.parameterAsEnums(parameters, self.METADATA_TO_STAMP, context)
        internal_keys_to_stamp = [all_known_keys[i] for i in selected_indices]

        # Processes each selected image
        for raster_file_path in input_photos:
            input_qimage = QImage(raster_file_path)

            if input_qimage.isNull():
                feedback.pushWarning(tr("Failed to load input image: {}").format(raster_file_path))
                continue

            # Fetches the full EXIF tag backup ('full_map') to preserve it in the output file.
            exif_data = get_exif_data(raster_file_path, internal_keys_to_stamp, extract_all_tags=False,
                                      include_full_map=True)

            # Transform the input_text into a list of lines while preserving empty paragraphs
            if input_text:
                lines_to_stamp = input_text.splitlines()
            else:
                lines_to_stamp = []

            # Add the selected metadata as separate lines (keeping empty lines if any)
            for key in internal_keys_to_stamp:
                value = exif_data.get(key)
                if value is not None:
                    friendly_name = translated_map.get(key, key)
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                    elif isinstance(value, QDateTime):
                        formatted_value = value.toString("dd-MM-yyyy HH:mm:ss")
                    else:
                        formatted_value = str(value)
                    lines_to_stamp.append(f"{friendly_name}: {formatted_value}")

            self.insert_stamp(input_qimage, svg_file_path, font_color, position, font_name, lines_to_stamp,
                              parameters, context, feedback)
            output_image_path = self.save_image(input_qimage, raster_file_path, output_folder, feedback)

            self.insert_exif_data(output_image_path, exif_data.get('full_map', {}), feedback)
            # A mensagem de "Image saved" foi mantida pois contém o caminho específico gerado internamente
            feedback.pushInfo(tr(f"Image saved at {output_image_path}"))

        return {self.OUTPUT_FOLDER: output_folder}

    def insert_stamp(self, input_qimage, svg_file_path, font_color, position, font_name, lines_to_stamp,
                     parameters, context, feedback):
        painter = QPainter(input_qimage)

        # Input image dimensions
        image_width = input_qimage.width()
        image_height = input_qimage.height()

        # Get unit and values
        height_val = self.parameterAsDouble(parameters, self.STAMP_HEIGHT_VALUE, context)
        unit_idx = self.parameterAsEnum(parameters, self.STAMP_HEIGHT_UNIT, context)
        margin_val = self.parameterAsDouble(parameters, self.MARGIN_VALUE, context)

        # Calculate pixels based on unit
        # 1 meter = 39.3701 inches. dotsPerMeter / 39.3701 = DPI
        dpi = input_qimage.dotsPerMeterX() * 0.0254
        if dpi <= 0:
            dpi = 96  # Standard fallback

        def calculate_pixels(val):
            if unit_idx == 0:  # Percentage (%)
                return (val / 100.0) * image_height
            elif unit_idx == 1:  # Pixels (px)
                return val
            elif unit_idx == 2:  # Centimeters (cm)
                return (val / 2.54) * dpi
            elif unit_idx == 3:  # Millimeters (mm)
                return (val / 25.4) * dpi
            elif unit_idx == 4:  # Inches (pol)
                return val * dpi
            return val

        target_stamp_height = max(calculate_pixels(height_val), 10)
        margin_px = calculate_pixels(margin_val)

        # Ensure that no None entries remain
        full_text_lines = [line if line is not None else '' for line in lines_to_stamp]
        full_text = "\n".join(full_text_lines)

        if (not full_text.strip()) and not svg_file_path:
            painter.end()
            return

        # Dynamically find the best font size to fit the target height
        # Initial guess based on number of lines
        num_lines = max(len(full_text_lines), 1)
        current_font_size = int(target_stamp_height / num_lines)
        font = QFont(font_name, current_font_size)

        # Refine font size to ensure it fits the bounding box height
        while current_font_size > 5:
            font.setPointSize(current_font_size)
            painter.setFont(font)
            # Check bounding rect height
            temp_rect = painter.boundingRect(QRect(0, 0, int(image_width - (2 * margin_px)), int(image_height)),
                                             Qt.AlignLeft, full_text)
            if temp_rect.height() <= target_stamp_height:
                break
            current_font_size -= 1

        painter.setFont(font)
        actual_text_rect_calc = painter.boundingRect(QRect(0, 0, int(image_width - (2 * margin_px)), int(image_height)),
                                                     Qt.AlignLeft, full_text)
        total_text_height = actual_text_rect_calc.height()

        # SVG logic
        svg_width, svg_height = 0, 0
        svg_renderer = None
        if svg_file_path:
            svg_renderer = QSvgRenderer(svg_file_path)
            if svg_renderer.isValid():
                svg_size = svg_renderer.defaultSize()
                if svg_size.height() > 0:
                    svg_aspect_ratio = svg_size.width() / svg_size.height()
                    svg_height = target_stamp_height
                    svg_width = svg_height * svg_aspect_ratio
            else:
                feedback.pushWarning(tr(f"Failed to load SVG file: {svg_file_path}"))
                svg_renderer = None

        h_offset = svg_width + margin_px if svg_renderer else 0
        text_width = image_width - (2 * margin_px) - h_offset

        svg_x, svg_y = 0, 0

        if position == 'Bottom Left':
            alignment = Qt.AlignLeft | Qt.AlignBottom
            base_y = image_height - margin_px - target_stamp_height
            text_x, text_y = margin_px + h_offset, base_y
            if svg_renderer:
                svg_x, svg_y = margin_px, base_y

        elif position == 'Bottom Right':
            alignment = Qt.AlignRight | Qt.AlignBottom
            base_y = image_height - margin_px - target_stamp_height
            text_x, text_y = margin_px, base_y
            if svg_renderer:
                svg_x, svg_y = image_width - margin_px - svg_width, base_y

        elif position == 'Top Left':
            alignment = Qt.AlignLeft | Qt.AlignTop
            base_y = margin_px
            text_x, text_y = margin_px + h_offset, base_y
            if svg_renderer:
                svg_x, svg_y = margin_px, base_y

        else:  # Top Right
            alignment = Qt.AlignRight | Qt.AlignTop
            base_y = margin_px
            text_x, text_y = margin_px, base_y
            if svg_renderer:
                svg_x, svg_y = image_width - margin_px - svg_width, base_y

        final_text_rect = QRect(int(text_x), int(base_y), int(text_width), int(target_stamp_height))
        painter.setPen(QColor(font_color))
        painter.drawText(final_text_rect, alignment, full_text)

        if svg_renderer:
            svg_rect = QRectF(svg_x, svg_y, svg_width, svg_height)
            svg_renderer.render(painter, svg_rect)

        painter.end()

    def insert_exif_data(self, temp_file_path, full_map_exif, feedback):
        if not full_map_exif: return
        exif_tools = QgsExifTools()

        # Iterate over full_map_exif and tag each EXIF tag into the image
        for tag, value in full_map_exif.items():
            try:
                exif_tools.tagImage(temp_file_path, tag, value)
            except Exception as e:
                feedback.pushInfo(tr(f"Could not write tag {tag}: {str(e)}"))

    def save_image(self, input_qimage, raster_file_path, output_folder, feedback):
        raster_file_info = QFileInfo(raster_file_path)
        output_image_path = os.path.join(output_folder,
                                         raster_file_info.baseName() + '_stamped.' + raster_file_info.suffix())

        # Check if the image was loaded correctly
        if input_qimage.isNull():
            raise QgsProcessingException("Failed to load the temporary image.")

        # Save the processed image to the specified output folder
        if input_qimage.save(output_image_path):
            return output_image_path
        else:
            raise QgsProcessingException("Failed to save the processed image.")

    def name(self):
        return "emiToolsStampPhotoRpa"

    def displayName(self):
        return tr("Stamp text and image on the photo")

    def group(self):
        return tr("Emi Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr(
            "This algorithm inscribes text and an optional SVG logo onto JPEG or PNG images using EXIF metadata such as coordinates, altitude, date, and camera model. "
            "The stamp height is defined by the user in %, px or cm, and the font size adjusts automatically. The processed images are saved in the output folder, preserving EXIF data.")

    def createInstance(self):
        return emiToolsStampPhotoRpa()