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

from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, QgsProcessingParameterMultipleLayers,
                       QgsProcessingParameterFolderDestination, QgsProcessingParameterFile,
                       QgsProcessingParameterString, QgsProcessingParameterColor, QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber, QgsProcessingException, QgsRasterLayer, QgsProject,QgsExifTools,
                       QgsCoordinateFormatter, QgsFields, QgsField, QgsFeature, QgsVectorLayer, QgsPoint, QgsGeometry,QgsPointXY)
from qgis.PyQt.QtCore import Qt, QFileInfo, QCoreApplication, QRect, QRectF, QDateTime, QVariant
from qgis.PyQt.QtGui import QImage, QPainter, QFont, QColor, QFontMetrics, QFontDatabase
from qgis.PyQt.QtSvg import QSvgRenderer
from qgis.PyQt.QtWidgets import QApplication

import os
import tempfile

def tr(string):
    return QCoreApplication.translate('@default', string)

class emiToolsStampImagemRpa(QgsProcessingAlgorithm):
    # Definition of input and output parameters
    INPUT_IMAGE = 'INPUT_IMAGE'  # Input images
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'  # Output folder
    STAMP_IMAGE = 'STAMP_IMAGE'  # SVG image to be stamped
    INPUT_TEXT = 'INPUT_TEXT'  # Main text to be inserted into the image
    OPERATION_NAME = 'OPERATION_NAME'  # Operation name to be inserted into the image
    FONT_COLOR = 'FONT_COLOR'  # Font color
    FONT_SIZE = 'FONT_SIZE'  # Font size
    FONT_NAME = 'FONT_NAME'
    POSITION = 'POSITION'
    POSITION_OPTIONS = ['Bottom Left', 'Bottom Right', 'Top Left', 'Top Right']
    
        
    def initAlgorithm(self, config=None):
        # Initializes the algorithm's parameters
        self.addParameter(QgsProcessingParameterMultipleLayers(self.INPUT_IMAGE, tr('Input Images'), layerType=QgsProcessing.TypeRaster))
        self.addParameter(QgsProcessingParameterFile(self.STAMP_IMAGE, tr('Stamp SVG Image'), extension='svg', optional=True))
        self.addParameter(QgsProcessingParameterString(self.INPUT_TEXT, tr('Main text to be inserted into the image'), defaultValue="IBAMA"))
        self.addParameter(QgsProcessingParameterString(self.OPERATION_NAME, tr('Secondary text to be inserted into the image'), optional=True))
        
        # Get the available fonts on the system using QFontDatabase
        font_db = QFontDatabase()
        fonts = font_db.families()
        
        # Get the default font from QGIS
        app = QApplication.instance()
        default_font = app.font().family() 

        # Check if the default font is available on the system
        default_font_index = fonts.index(default_font) if default_font in fonts else 0
        
        # Add the Enum parameter to select the font
        self.addParameter(QgsProcessingParameterEnum(self.FONT_NAME,tr('Select Font'), options=fonts,defaultValue=default_font_index))                     
        
        self.addParameter(QgsProcessingParameterColor(self.FONT_COLOR, tr('Font color'), defaultValue=QColor(255, 255, 0)))
        self.addParameter(QgsProcessingParameterNumber(self.FONT_SIZE, tr('Font size'), defaultValue=60, minValue=1, maxValue=500))
        
        # Return the translated options for display to the user
        def positionOptions():
           return [
               tr('Bottom Left'), 
               tr('Bottom Right'), 
               tr('Top Left'), 
               tr('Top Right')
           ]
                
        # Calling the function to get the translated options   
        self.addParameter(QgsProcessingParameterEnum(
            self.POSITION,
            tr('Position of text and image'),
            options=positionOptions(),  
            defaultValue=0  
        ))       

        self.addParameter(QgsProcessingParameterFolderDestination(self.OUTPUT_FOLDER, tr('Output folder')))

    def processAlgorithm(self, parameters, context, feedback):
        # Loads the input raster layers
        input_images = self.parameterAsLayerList(parameters, self.INPUT_IMAGE, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        svg_file_path = self.parameterAsFile(parameters, self.STAMP_IMAGE, context)

        # Collects text and style parameters
        input_text = self.parameterAsString(parameters, self.INPUT_TEXT, context)
        operation_name = self.parameterAsString(parameters, self.OPERATION_NAME, context)
        font_color = self.parameterAsColor(parameters, self.FONT_COLOR, context)
        font_size = self.parameterAsInt(parameters, self.FONT_SIZE, context)
        
        # get font
        font_index = self.parameterAsEnum(parameters, self.FONT_NAME, context)
        font_db = QFontDatabase()
        fonts = font_db.families()
        font_name = fonts[font_index]        
        
        # Use the index to access the string (untranslated) 
        position_index = self.parameterAsInt(parameters, self.POSITION, context)
        position = self.POSITION_OPTIONS[position_index]

        # Initializes the list before use
        coordinates_list = []

        # Processes each selected image
        for input_image in input_images:

            raster_file_path = input_image.dataProvider().dataSourceUri()
            input_qimage = QImage(raster_file_path)

            if input_qimage.isNull():
                raise QgsProcessingException(tr("Failed to load input image."))
            
            full_map_exif, exif_latitude, exif_longitude, exif_model_str, exif_datetime_str, exif_coordinates_str, exif_altitude_str = self.get_exif_data(raster_file_path, feedback)

            self.insert_stamp(input_qimage, output_folder, input_text, operation_name,
                     exif_model_str, exif_datetime_str, exif_coordinates_str, exif_altitude_str, svg_file_path,
                     font_color, font_size, position, font_name, full_map_exif, feedback)
                      
            output_image_path = self.save_image(input_qimage, raster_file_path ,output_folder, feedback)
          
            self.insert_exif_data(output_image_path, full_map_exif, feedback)

            feedback.pushInfo(tr(f"Image saved at {output_image_path}"))


            # Adds the coordinates to the list
            coordinates_list.append((exif_latitude,
                                     exif_longitude,
                                     input_image.name(),
                                     output_image_path,
                                     exif_model_str,
                                     exif_datetime_str,
                                     exif_coordinates_str,
                                     exif_altitude_str))

        # Creates and loads the point layer with the coordinates
        self.create_points_layer(coordinates_list)

        return {self.OUTPUT_FOLDER: output_folder}

    def get_raster_layer(self, parameters, context, feedback):
        # Gets the input raster layer
        input_image = self.parameterAsRasterLayer(parameters, self.INPUT_IMAGE, context)
        if input_image is None or not input_image.isValid():
            raise QgsProcessingException(tr("No valid raster layer provided."))
        return input_image  

    def get_exif_data(self, temp_file_path, feedback):
        # Instantiates QgsExifTools
        exif_tools = QgsExifTools()

        # Checks if the image contains a valid geotag
        if not exif_tools.hasGeoTag(temp_file_path):
            feedback.pushInfo("No valid geotag found.")
            return "", "", "", "", "", "", ""

        full_map_exif = exif_tools.readTags (temp_file_path)

        # Gets the geographic coordinates
        geo_tag_result = exif_tools.getGeoTag(temp_file_path)
        exif_coordinates = geo_tag_result[0]  # Coordenadas geográficas

        # Gets the EXIF date
        exif_datetime = exif_tools.readTag(temp_file_path, 'Exif.Photo.DateTimeOriginal')
        if isinstance(exif_datetime, QDateTime):
            exif_datetime_str = exif_datetime.toString("yyyy-MM-dd HH:mm:ss")
        else:
            exif_datetime_str = ""
         
        # Gets the EXIF model
        exif_model_str = exif_tools.readTag(temp_file_path, 'Exif.Image.Model')
        if not exif_model_str:
            exif_model_str = ""

        # Gets the EXIF altitude
        if exif_tools.readTag(temp_file_path, 'Exif.GPSInfo.GPSAltitude'):
            exif_altitude_str = f"{exif_tools.readTag(temp_file_path, 'Exif.GPSInfo.GPSAltitude')} m"
        else:
            exif_altitude_str = ""
         
        
        # Formats the coordinates
        if exif_coordinates and isinstance(exif_coordinates, QgsPoint):
            exif_latitude = exif_coordinates.y()
            exif_longitude = exif_coordinates.x()

            latitude_dms = QgsCoordinateFormatter.formatY(exif_latitude, QgsCoordinateFormatter.FormatDegreesMinutesSeconds,2)
            longitude_dms = QgsCoordinateFormatter.formatX(exif_longitude, QgsCoordinateFormatter.FormatDegreesMinutesSeconds, 2)

            exif_coordinates_str = f"{latitude_dms}, {longitude_dms}"

        else:
            exif_coordinates_str = ""

        return full_map_exif, exif_latitude, exif_longitude, exif_model_str, exif_datetime_str, exif_coordinates_str, exif_altitude_str

    def insert_stamp(self, input_qimage, output_folder, input_text, operation_name,
                     exif_model_str, exif_datetime_str, exif_coordinates_str, exif_altitude_str, svg_file_path,
                     font_color, font_size, position, font_name, full_map_exif, feedback):

        painter = QPainter(input_qimage)

        # Input image dimensions
        image_width = painter.device().width()
        image_height = painter.device().height()

        # Set font
        font = QFont(font_name, font_size)
        painter.setFont(font)


        # Concatenate all texts into a single string, separating by line breaks
        full_text_lines = [input_text]
        if operation_name:
            full_text_lines.append(operation_name)

        # Add EXIF information
        full_text_lines.extend([exif_model_str, exif_datetime_str, exif_coordinates_str, exif_altitude_str])

        # Create the final string with line breaks
        full_text = "\n".join(full_text_lines)

        # Calculate the total text height based on the number of lines
        font_metrics = QFontMetrics(font)
        total_text_height = font_metrics.lineSpacing() * len(full_text_lines)  # Total de linhas

        #offset of text and image
        image_offset = 50

        if svg_file_path:
            # Load the SVG file
            svg_renderer = QSvgRenderer(svg_file_path)
            if not svg_renderer.isValid():
                raise QgsProcessingException(tr(f"Failed to load SVG file: {svg_file_path}"))

            # Calculate SVG dimensions
            svg_size = svg_renderer.defaultSize()
            svg_aspect_ratio = svg_size.height() / svg_size.width()
            svg_rwidth = total_text_height * svg_aspect_ratio

        if position == 'Bottom Left':
            alignment = Qt.AlignLeft
            if svg_file_path:
                svg_rect = QRectF(float(image_offset), float(image_height - total_text_height - image_offset),
                                  float(total_text_height), float(svg_rwidth))
                text_rect = QRect(total_text_height + 2 * image_offset, image_height - image_offset - total_text_height,
                                  image_width - total_text_height - 2 * image_offset, total_text_height)
            else:
                text_rect = QRect(image_offset, image_height - image_offset - total_text_height,
                              image_width - 2 * image_offset, total_text_height)

        elif position == 'Bottom Right':
            alignment = Qt.AlignRight
            if svg_file_path:
                svg_rect = QRectF(float(image_width - total_text_height - image_offset),
                                  float(image_height - total_text_height - image_offset), float(total_text_height),
                                  float(svg_rwidth))
                text_rect = QRect(50, image_height - total_text_height - image_offset,
                                  image_width - total_text_height - 3 * image_offset,
                                  total_text_height)
            else:
                text_rect = QRect(image_offset, image_height - image_offset - total_text_height, image_width - 2 * image_offset, total_text_height)
                                  
        elif position == 'Top Left':
            alignment = Qt.AlignLeft
            if svg_file_path:
                svg_rect = QRectF(float(image_offset), float(image_offset), float(total_text_height), float(svg_rwidth))
                text_rect = QRect(total_text_height + 2 * image_offset, image_offset,
                                  image_width - total_text_height - 2 * image_offset, total_text_height)
            else:
                text_rect = QRect(image_offset, image_offset, image_width - 2 * image_offset, total_text_height)
        elif position == 'Top Right':
            alignment = Qt.AlignRight
            if svg_file_path:
                svg_rect = QRectF(float(image_width - total_text_height - image_offset), float(image_offset),
                                  float(total_text_height),
                                  float(svg_rwidth))
                text_rect = QRect(image_offset, image_offset, image_width - total_text_height - 3 * image_offset,
                                  total_text_height)
            else:
                text_rect = QRect(image_offset, image_offset, image_width - 2 * image_offset, total_text_height)
                
        # Set the text color and draw it in the defined position
        painter.setPen(QColor(font_color))
        painter.drawText(text_rect, alignment, full_text)  # Remover o argumento incorreto Qt.TextWordWrap


        if svg_file_path:
            # Render the SVG image in the calculated position
            svg_renderer.render(painter, svg_rect)

        painter.end()
        

    def insert_exif_data(self, temp_file_path, full_map_exif, feedback):

        # Create an instance of QgsExifTools
        exif_tools = QgsExifTools()

        # Iterate over full_map_exif and tag each EXIF tag into the image
        for tag, value in full_map_exif.items():
            try:
                exif_tools.tagImage(temp_file_path, tag, value)
            except Exception as e:
                feedback.pushInfo(tr(f"Failed to tag {tag}: {str(e)}"))
       

    def save_image(self, input_qimage, raster_file_path ,output_folder, feedback):
        # Construct the output file path
        raster_file_info = QFileInfo(raster_file_path)
        output_image_path = os.path.join(output_folder, raster_file_info.baseName() + '_stamped.' + raster_file_info.suffix())
    
        # Check if the output directory exists, and if not, create it
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
       
        # Check if the image was loaded correctly
        if input_qimage.isNull():
            raise QgsProcessingException("Failed to load the temporary image.")
    
        # Save the processed image to the specified output folder
        if input_qimage.save(output_image_path):
            return output_image_path
        else:
            raise QgsProcessingException("Failed to save the processed image.")        
           

    def create_points_layer(self, coordinates_list):
        # Create fields for the attribute table
        fields = QgsFields()
        fields.append(QgsField("ID", QVariant.Int))
        fields.append(QgsField("Latitude", QVariant.Double))
        fields.append(QgsField("Longitude", QVariant.Double))
        fields.append(QgsField("Image Name", QVariant.String))
        fields.append(QgsField("Path", QVariant.String))
        fields.append(QgsField("Model", QVariant.String))
        fields.append(QgsField("DateTime", QVariant.String))
        fields.append(QgsField("Coordinates", QVariant.String))
        fields.append(QgsField("Altitude", QVariant.String))

        # Create the point layer
        point_layer = QgsVectorLayer("Point?crs=EPSG:4326", "Pontos Imagens", "memory")
        provider = point_layer.dataProvider()
        provider.addAttributes(fields)
        point_layer.updateFields()

        # Check if the coordinates list is not empty
        if coordinates_list:
            for idx, (
            exif_latitude, exif_longitude, image_name, output_image_path, model, datetime_str, coordinates_str, altitude_str) in enumerate(
                    coordinates_list, start=1):
                # Check if coordinates are valid
                if exif_latitude is not None and exif_longitude is not None:
                    point = QgsPointXY(exif_longitude, exif_latitude)  # Usa QgsPointXY para criar o ponto
                    feature = QgsFeature()
                    feature.setGeometry(QgsGeometry.fromPointXY(point))  # Cria a geometria do ponto
                    # Assign attribute values
                    feature.setAttributes([
                        idx,  # ID
                        exif_latitude,  # Latitude
                        exif_longitude,  # Longitude
                        image_name,  # Image Name
                        output_image_path, # Path
                        model,  # Model
                        datetime_str,  # DateTime
                        coordinates_str,  # Coordinates
                        altitude_str  # Altitude
                    ])
                    provider.addFeature(feature)

        point_layer.updateExtents()

        # Adds the layer to the project
        QgsProject.instance().addMapLayer(point_layer)


    def name(self):
        return "emiToolsStampImagemRpa"

    def displayName(self):
        return tr("Insert stamp on image")

    def group(self):
        return tr("Emi Functions")

    def groupId(self):
        return ""

    #def shortHelpString(self):
    #    return tr("This algorithm Insert stamp on image.")

    def createInstance(self):
        return emiToolsStampImagemRpa()
