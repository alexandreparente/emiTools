# -*- coding: utf-8 -*-

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsVectorFileWriter,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterField,
                       QgsProcessingParameterBoolean,
                       QgsProcessingMultiStepFeedback,
                       QgsProcessingParameterFolderDestination,
                       QgsProject,
                       QgsVectorLayer,
                       QgsFeature,
                       QgsProcessingException,
                       QgsWkbTypes)

import os
import zipfile

def tr(string):
    return QCoreApplication.translate('@default', string)

class emiToolsExportKmlRpa(QgsProcessingAlgorithm):

    output_folder = 'output_folder'

    def initAlgorithm(self, config=None):
        # Input layer parameter using QgsProcessingParameterFeatureSource
        self.addParameter(QgsProcessingParameterFeatureSource('layer', tr('Layer name:'), 
                    [QgsProcessing.TypeVectorPolygon, QgsProcessing.TypeVectorLine]))
        
        # Input field parameter to select a field for naming the exported files
        self.addParameter(QgsProcessingParameterField('export_field', tr('Field to use for export file names:'), '', 'layer', optional=True))

        # Output folder parameter
              
        default_output_folder = os.path.expanduser("~")      
        self.addParameter(QgsProcessingParameterFolderDestination(self.output_folder, tr('Output folder'), defaultValue=default_output_folder))
        
        # Option to compress the output
        self.addParameter(QgsProcessingParameterBoolean('compress_output', tr('Compress output file copy (.zip)'), 
                    defaultValue=False))

        # Option to load the output into the project
        self.addParameter(QgsProcessingParameterBoolean('load_output', tr('Open output files after executing the algorithm'), 
                    defaultValue=True))

    def processAlgorithm(self, parameters, context, feedback):
        feedback = QgsProcessingMultiStepFeedback(1, feedback)

        # Get the input layer as a feature source
        layer = self.parameterAsSource(parameters, 'layer', context)
        if layer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, 'layer'))


        # Get the field selected by the user
        export_field = self.parameterAsString(parameters, 'export_field', context)
        
        # Use parameterAsString instead of parameterAsFile
        output_folder = self.parameterAsString(parameters, 'output_folder', context)

        if not output_folder:  # Check if output_folder is empty
            output_folder = tempfile.mkdtemp()  # Create a temporary folder

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        
        compress_output = self.parameterAsBoolean(parameters, 'compress_output', context)
        load_output = self.parameterAsBoolean(parameters, 'load_output', context)

        
        # List to hold the output file names for loading later
        output_files = []
        # Processes the features in batches
        features = list(layer.getFeatures())        
        # Define the batch size
        batch_size = 10 
    
        for batch_start in range(0, len(features), batch_size):
         
        # Iterates over the features and exports each one as an individual KML file.          
            for i in range(batch_start, min(batch_start + batch_size, len(features))):
                feature = features[i]
                
                # Uses the field value for naming or a default name
                field_value = feature[export_field] if export_field else f"{layer.sourceName()}_{i+1}"

                #Gets the geometry of the feature and ensures it is valid
                geometry = feature.geometry()
                if not geometry or geometry.isEmpty():
                    feedback.pushInfo(f"Skipping feature {i+1}: No valid geometry found.")
                    continue

                geometries = [geometry] if not geometry.isMultipart() else geometry.asGeometryCollection()

                # Processes each part of the geometry 
                for j, singlepart_geometry in enumerate(geometries):            
                    # Adjusts the file name for multipart
                    part_suffix = f"_{j+1}" if geometry.isMultipart() else ""
                    
                    # Determines the geometry type of the feature
                    geometry_type = singlepart_geometry.wkbType()
                    
                    
                    temp_layer = None
                    # Creates a temporary layer depending on the geometry type
                    if QgsWkbTypes.geometryType(geometry_type) == QgsWkbTypes.LineGeometry:
                        temp_layer = QgsVectorLayer("LineString?crs=EPSG:4326", f"{field_value}{part_suffix}", "memory")
                    elif QgsWkbTypes.geometryType(geometry_type) == QgsWkbTypes.PolygonGeometry:
                        temp_layer = QgsVectorLayer("Polygon?crs=EPSG:4326", f"{field_value}{part_suffix}", "memory")
                    else:
                        raise QgsProcessingException(f"Unsupported geometry type: {QgsWkbTypes.displayString(geometry_type)}")

                    #Adds the feature to the temporary layer
                    temp_layer_data_provider = temp_layer.dataProvider()
                    temp_layer_data_provider.addAttributes(layer.fields())
                    
                    # Updates the layer fields after adding the attributes
                    temp_layer.updateFields()

                    
                    #Creates a new feature with the singlepart geometry
                    new_feature = QgsFeature()
                    new_feature.setGeometry(singlepart_geometry)
                    new_feature.setAttributes(feature.attributes())
                    temp_layer_data_provider.addFeature(new_feature)

                    #Defines options to save the layer (writeAsVectorFormatV3)
                    options = QgsVectorFileWriter.SaveVectorOptions()
                    options.driverName = 'KML'
                    options.fileEncoding = 'UTF-8'
                    options.fieldNameSource = QgsVectorFileWriter.Original

                    #Ensures that the correct coordinate transformation is used.
                    transform_context = QgsProject.instance().transformContext()
                    
                    # Writes the feature to a KML file
                    output_file = os.path.join(output_folder, f"{field_value}{part_suffix}.kml")
                    error = QgsVectorFileWriter.writeAsVectorFormatV3(temp_layer, output_file, transform_context, options)

                    if error[0] != QgsVectorFileWriter.NoError:
                        raise QgsProcessingException(f"Error saving KML file: {error[0]}")
                    
                    #Removes the <Folder> tags and adds the <name> tag
                    self.edit_kml_tags(output_file, f"{field_value}{part_suffix}")
                    
                    #Add file name for loading later
                    output_files.append(output_file)

        for file in output_files:
            feedback.pushInfo(f"Saved file: {file}")
        
        # Print the total number of strings (files) generated
        feedback.pushInfo(f"Total number of saved files: {len(output_files)}")

        #Compresses the files
        if compress_output:
            for output_file in output_files:
                self.compress_files(output_file)

        #Loads all KML files into the project at once
        if load_output:
            self.load_output_files(output_files)
            
        return {self.output_folder: output_folder}
        
        
    def load_output_files (self, output_files):  
       #Using the addMapLayers method to reduce the number of calls to QGIS when many layers need to be loaded
       layers_to_add = []
       for output_file in output_files:
           layers_to_add.append(QgsVectorLayer(output_file, os.path.basename(output_file), "ogr"))
       QgsProject.instance().addMapLayers(layers_to_add)


    def compress_files(self, output_file):
          
        base_name = os.path.splitext(output_file)[0]  # Remove a extensão .kml
        zip_output_file = base_name + "_kml.zip"  # Adiciona .zip ao nome base
    
        # Create the .zip file and add the original file
        with zipfile.ZipFile(zip_output_file, 'w') as zipf:
            zipf.write(output_file, os.path.basename(output_file))
           

    def edit_kml_tags(self, kml_file, field_value):
        with open(kml_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        with open(kml_file, 'w', encoding='utf-8') as file:
            for line in lines:
                if '<Folder>' in line or '</Folder>' in line:
                    continue
                if '<Placemark>' in line:
                    file.write(line)
                    file.write(f"<name>{field_value}</name>\n")
                else:
                    file.write(line)

    def name(self):
        return tr("Export KML to RPA")

    def displayName(self):
        return tr("Export KML to RPA")

    def group(self):
        return tr("Emi Functions")

    def groupId(self):
        return ""

    def createInstance(self):
        return emiToolsExportKmlRpa()

