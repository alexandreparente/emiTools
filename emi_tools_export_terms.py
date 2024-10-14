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

# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsVectorFileWriter,
                       QgsProcessingAlgorithm, 
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField, 
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterEnum, 
                       QgsProcessingParameterBoolean,
                       QgsProcessingException, 
                       QgsProject, QgsVectorLayer,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingFeatureSource,
                       QgsProcessingParameterVectorLayer,
                       QgsVectorDataProvider,
                       QgsField,
                       QgsWkbTypes,
                       QgsFeature)
                       
import os
import zipfile
import tempfile
from datetime import datetime


def tr(string):
    return QCoreApplication.translate('@default', string)

class emiToolsExportTerms(QgsProcessingAlgorithm):

    output_folder = 'output_folder'

    def initAlgorithm(self, config=None):
        # Input layer parameter   
        self.addParameter(QgsProcessingParameterFeatureSource('layer', tr('Layer name1:'), [QgsProcessing.TypeVectorPolygon]))
        
        # Parameter to select the field for the embargo term number
        self.addParameter(QgsProcessingParameterField('num_tei_field', tr('Embargo term field:'), parentLayerParameterName='layer', type=QgsProcessingParameterField.String, defaultValue='numero_tad'))

        # Parameter to select the field for the embargo term series        
        self.addParameter(QgsProcessingParameterField('serie_tei_field', tr('Embargo term series field:'), parentLayerParameterName='layer', type=QgsProcessingParameterField.String, defaultValue='serie_tad'))
        
        # Setting the default output folder to the user's home directory        
        default_output_folder = os.path.expanduser("~")      
        self.addParameter(QgsProcessingParameterFolderDestination(self.output_folder, tr('Output folder'), defaultValue=default_output_folder))
        
        # Parameter to choose the output format        
        self.addParameter(QgsProcessingParameterEnum('output_format', tr('Output file format:'), options=['ESRI Shapefile', 'GeoPackage', 'Keyhole Markup Language'], defaultValue=0))
        
        # Add parameter to export all features to a single file        
        self.addParameter(QgsProcessingParameterBoolean('export_all_to_single', tr('Export all features to a single file'), defaultValue=False))
        
        # Parameter to compress the output file
        self.addParameter(QgsProcessingParameterBoolean('compress_output', tr('Compress output file copy (.zip)'), defaultValue=False))
        
        # Parameter to load the output file        
        self.addParameter(QgsProcessingParameterBoolean('load_output', tr('Open output files after executing the algorithm'), defaultValue=True))

    def processAlgorithm(self, parameters, context, feedback):
        feedback = QgsProcessingMultiStepFeedback(1, feedback)

        # Get the input layer as a feature source
        layer = self.parameterAsSource(parameters, 'layer', context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, 'layer'))

        # Get parameters
        extracted_features = list(layer.getFeatures())

        num_tei_field = parameters['num_tei_field']
        serie_tei_field = parameters['serie_tei_field']
        export_all_to_single = self.parameterAsBoolean(parameters, 'export_all_to_single', context)
        output_format = self.parameterAsEnum(parameters, 'output_format', context)
        compress_output = self.parameterAsBoolean(parameters, 'compress_output', context)

        # Get output folder
        output_folder = self.parameterAsString(parameters, 'output_folder', context)
        if not output_folder:
            output_folder = tempfile.mkdtemp()
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Check for duplicate features
        self.check_duplicates(extracted_features, num_tei_field)

        # Create a temporary layer
        temp_layer = self.temp_layer(layer, extracted_features, context)

        # Remove unnecessary fields and rename others
        self.remover_fields(temp_layer, num_tei_field, serie_tei_field)

        # Rename the fields
        self.rename_fields(temp_layer, num_tei_field, serie_tei_field)
      
        output_files = []
        today_str = "lote" + datetime.today().strftime('%Y%m%d')

        # Export all to a single file or individual files
        if export_all_to_single:
            output_files.extend(self.export_single_file(temp_layer, output_folder, today_str, output_format,feedback))
        else:
            output_files.extend(self.export_individual_files(temp_layer, output_folder, output_format,feedback))

        # Compress files if option is checked
        if compress_output:
            self.compress_files(output_files, output_format, output_folder, feedback)

        # Load output files into the project
        if self.parameterAsBoolean(parameters, 'load_output', context):
            self.load_output_files(output_files)

        return {self.output_folder: output_folder}

    def temp_layer(self, layer, extracted_features, context):
        # Checks if the layer is a QgsProcessingFeatureSource
        if isinstance(layer, QgsProcessingFeatureSource):
            # Gets the source name and the associated layer
            source_name = layer.sourceName()
            source_layer = QgsProject.instance().mapLayersByName(source_name)

            if not source_layer:
                raise QgsProcessingException(self.invalidSourceError({'layer': layer}, 'layer'))

            source_layer = source_layer[0]

        # Gets the geometry type and CRS of the original layer.
        geometry_type = source_layer.wkbType()
        crs = source_layer.crs().authid()

        # Creates a temporary layer in memory
        temp_layer = QgsVectorLayer(f'{QgsWkbTypes.displayString(geometry_type)}?crs={crs}', 'Temporary Layer',
                                    'memory')

        # Copies the fields from the original layer
        temp_layer_provider = temp_layer.dataProvider()
        temp_layer_provider.addAttributes(source_layer.fields())
        temp_layer.updateFields()

        # Adds the extracted features to the temporary layer
        temp_layer_provider.addFeatures(extracted_features)

        return temp_layer

    def check_duplicates(self, extracted_features, num_tei_field):
        tad_numbers = [f[num_tei_field] for f in extracted_features]
        duplicated_tads = {tad_number: tad_numbers.count(tad_number) for tad_number in set(tad_numbers) if tad_numbers.count(tad_number) > 1}
        if duplicated_tads:
            raise QgsProcessingException(tr(f"Duplicate embargo term numbers found: {list(duplicated_tads.keys())}"))

    def remover_fields(self, temp_layer, num_tei_field, serie_tei_field):
        # Fields that should be kept
        fields_to_keep = [num_tei_field, serie_tei_field]
        provider = temp_layer.dataProvider()

        # Collect indexes of fields to be removed
        fields_to_remove = [temp_layer.fields().indexOf(field.name()) for field in temp_layer.fields() if field.name() not in fields_to_keep]
        
        # Remove the fields
        if fields_to_remove:
            provider.deleteAttributes(fields_to_remove)
            
        # Update the layer's fields
        temp_layer.updateFields()

    def rename_fields(self, temp_layer, num_tei_field, serie_tei_field):
    
        # Renaming dictionary
        field_renames = {
            num_tei_field: 'NUM_TEI',
            serie_tei_field: 'SERIE_TEI'
        }
        provider = temp_layer.dataProvider()
        
        # Rename the fields
        for old_name, new_name in field_renames.items():
            if temp_layer.fields().indexOf(old_name) != -1:
                provider.renameAttributes({temp_layer.fields().indexOf(old_name): new_name})
                
        # Update the layer's fields
        temp_layer.updateFields()

    def export_single_file(self, layer, output_folder, today_str, output_format,feedback):
        output_files = []
        output_file = os.path.join(output_folder, f"TEI_{today_str}_sicafi.{self.get_extension(output_format)}")
        QgsVectorFileWriter.writeAsVectorFormat(layer, output_file, "UTF-8", layer.crs(), self.get_output_format_string(output_format))
        output_files.append(output_file)
        feedback.pushInfo(tr(f"Save file: {output_file}"))  
          
        return output_files
        
    def export_individual_files(self, layer, output_folder, output_format, feedback):
        output_files = []

        # Load all features at once
        features = list(layer.getFeatures())  
        total_features = len(features)
        
        # Use a set to track processed TAD numbers
        processed_tad_numbers = set()
    
        for i, feature in enumerate(features):
        
            output_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", f"Extracted_{i + 1}", "memory")
            provider = output_layer.dataProvider()
            provider.addAttributes(layer.fields())    
            output_layer.updateFields()
            
            # Retrieve the value of 'NUM_TEI' to generate the file name
            tad_number = feature[layer.fields().indexOf('NUM_TEI')]    
            
            # Add the feature to the temporary layer
            provider.addFeature(feature)
    
            # Generate the output file path
            output_file = os.path.join(output_folder, f"TEI_{tad_number}_sicafi.{self.get_extension(output_format)}")
            
            # Export the temporary layer as a file
            QgsVectorFileWriter.writeAsVectorFormat(output_layer, output_file, "UTF-8", output_layer.crs(), self.get_output_format_string(output_format))
            output_files.append(output_file)
            
            # Print the saved file info
            feedback.pushInfo(f"Saved file: {output_file}")

            # Clear/Create the temporary layer for each feature in the batch
            output_layer = None

        #Apparently, this is causing a memory error
        # #Print the strings (files) generated
        #for file in output_files:
        #    feedback.pushInfo(f"Saved file: {file}")
       
        # Print the total number of saved files
        feedback.pushInfo(f"Total number of saved files: {len(output_files)}")
               
        return output_files


    def load_output_files(self, list_output_files):
        layers_to_add = []
        for output_file in list_output_files:
            layer_name = os.path.basename(output_file)
            layer = QgsVectorLayer(output_file, layer_name, "ogr")
            if not layer.isValid():
                raise QgsProcessingException(f"Failed to load layer: {layer_name}")
            layers_to_add.append(layer)
        QgsProject.instance().addMapLayers(layers_to_add)


    def compress_files(self, output_files, output_format, output_folder, feedback):
        #Define the associated extensions based on the output format
        if output_format == 0:  # ESRI Shapefile
            associated_extensions = ['shp', 'shx', 'dbf', 'prj', 'cpg']
            file_extension = 'shp'
        elif output_format == 1:  # GeoPackage
            associated_extensions = ['gpkg']
            file_extension = 'gpkg'
        elif output_format == 2:  # KML
            associated_extensions = ['kml']
            file_extension = 'kml'
        
        for output_file in output_files:
            base_name = os.path.splitext(os.path.basename(output_file))[0]
            
            #Add the file extension before the '.zip' 
            zip_output_file = os.path.join(output_folder, f"{base_name}_{file_extension}.zip")
        
            #Identify the associated files that need to be compressed 
            associated_files = [os.path.join(output_folder, f"{base_name}.{ext}") for ext in associated_extensions if os.path.exists(os.path.join(output_folder, f"{base_name}.{ext}"))]
            
            #If there are associated files, create the .zip file
            if associated_files:
                with zipfile.ZipFile(zip_output_file, 'w') as zipf:
                    for file in associated_files:
                        zipf.write(file, os.path.basename(file))
            
                # Notify that the file has been compressed
                feedback.pushInfo(tr(f"Compressed files: {zip_output_file}"))

              
    
    def get_extension(self, output_format):
        if output_format == 0:  # ESRI Shapefile
            return "shp"
        elif output_format == 1:  # GeoPackage
            return "gpkg"
        elif output_format == 2:  # KML
            return "kml"

    def get_output_format_string(self, output_format):
        if output_format == 0:
            return "ESRI Shapefile"
        elif output_format == 1:
            return "GPKG"
        elif output_format == 2:
            return "KML"                
  
    def get_extension(self, output_format):
        if output_format == 0:
            return "shp"
        elif output_format == 1:
            return "gpkg"
        elif output_format == 2:
            return "kml"

    def get_output_format_string(self, output_format):
        if output_format == 0:
            return "ESRI Shapefile"
        elif output_format == 1:
            return "GPKG"
        elif output_format == 2:
            return "KML"

    def name(self):
        return "emiToolsExportTerms"

    def displayName(self):
        return tr("Export Terms to Sicafi")

    def group(self):
        return tr("Emi Functions")

    def createInstance(self):
        return emiToolsExportTerms()

    def createInstance(self):
        return emiToolsExportTerms()
        
