# -*- coding: utf-8 -*-

"""
/***************************************************************************
 emiTools
                                 A QGIS plugin
 This plugin compiles tools used by EMI-PB

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


from qgis.PyQt.QtCore import QVariant
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterNumber,
    QgsProcessingException,
    QgsFeature,
    QgsGeometry,
    QgsFields,
    QgsField,
    QgsWkbTypes,
    QgsFeatureSink,
    NULL
)

from .emi_tools_util import tr


class emiToolsArrayAggregate(QgsProcessingAlgorithm):
    """
    Aggregates features by a selected field.
    Aggregated attributes are stored as arrays
    in fields suffixed with '_list'.
    """

    INPUT = 'INPUT'
    GROUP_FIELD = 'GROUP_FIELD'
    MAX_GROUP_SIZE = 'MAX_GROUP_SIZE'
    OUTPUT = 'OUTPUT'

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                tr('Input layer'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.GROUP_FIELD,
                tr('Group by field'),
                parentLayerParameterName=self.INPUT,
                type=QgsProcessingParameterField.Any
            )
        )

        self.addParameter(
            QgsProcessingParameterNumber(
                self.MAX_GROUP_SIZE,
                tr('Maximum features per group (0 = unlimited)'),
                type=QgsProcessingParameterNumber.Integer,
                defaultValue=0,
                minValue=0,
                optional=True
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                tr('Aggregated layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        source = self.parameterAsSource(parameters, self.INPUT, context)
        group_field_name = self.parameterAsString(parameters, self.GROUP_FIELD, context)
        max_group_size = self.parameterAsInt(parameters, self.MAX_GROUP_SIZE, context)

        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        field_index = source.fields().indexOf(group_field_name)
        if field_index == -1:
            raise QgsProcessingException(
                tr(f"Field '{group_field_name}' not found.")
            )

        source_fields = source.fields()
        output_fields = QgsFields()

        # Primary key (GeoPackage compliant)
        output_fields.append(QgsField('fid', QVariant.Int))

        # Grouping field (original name and type preserved)
        output_fields.append(source_fields.at(field_index))

        # Aggregated fields as real StringList arrays with _list suffix (GeoPackage compliant)
        aggregated_fields = []

        for field in source_fields:
            field_name = field.name()
            if field_name != group_field_name:
                output_fields.append(
                    QgsField(f"{field_name}_list", QVariant.StringList)
                )
                aggregated_fields.append(field_name)

        output_wkb_type = QgsWkbTypes.multiType(source.wkbType())

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            output_fields,
            output_wkb_type,
            source.sourceCrs()
        )

        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        # Group structure:
        # { group_key: { 'geometries': [], 'attributes': { field: [] } } }
        groups = {}

        feature_count = source.featureCount()
        total = 100.0 / feature_count if feature_count else 0

        # Read and group features
        for current, feature in enumerate(source.getFeatures()):
            if feedback.isCanceled():
                break

            group_key = feature.attribute(group_field_name)
            if group_key == NULL:
                group_key = "NULL_GROUP"

            if group_key not in groups:
                groups[group_key] = {
                    'geometries': [],
                    'attributes': {fname: [] for fname in aggregated_fields}
                }

            if feature.hasGeometry():
                groups[group_key]['geometries'].append(feature.geometry())

            for field_name in aggregated_fields:
                value = feature[field_name]
                if value in (None, NULL):
                    groups[group_key]['attributes'][field_name].append("")
                else:
                    groups[group_key]['attributes'][field_name].append(str(value))

            feedback.setProgress(int(current * total * 0.5))

        # Construct aggregated features
        feedback.setProgressText(tr("Constructing aggregated features..."))

        fid_counter = 1
        num_groups = len(groups)

        for count, (group_key, group_data) in enumerate(groups.items(), 1):
            if feedback.isCanceled():
                break

            num_items = len(group_data['geometries'])

            if max_group_size > 0:
                chunk_size = max_group_size
            else:
                chunk_size = num_items

            for i in range(0, num_items, chunk_size):
                end_index = i + chunk_size

                new_feature = QgsFeature()
                new_feature.setFields(output_fields)

                new_feature.setAttribute('fid', fid_counter)
                fid_counter += 1

                subset_geoms = group_data['geometries'][i:end_index]
                if subset_geoms:
                    combined_geom = QgsGeometry.unaryUnion(subset_geoms)

                    if not combined_geom.isMultipart():
                        combined_geom.convertToMultiType()

                    new_feature.setGeometry(combined_geom)

                new_feature.setAttribute(group_field_name, group_key)

                for field_name, values in group_data['attributes'].items():
                    subset_values = values[i:end_index]
                    new_feature.setAttribute(
                        f"{field_name}_list",
                        subset_values
                    )

                sink.addFeature(new_feature, QgsFeatureSink.FastInsert)

            feedback.setProgress(50 + int(count / num_groups * 50))

        return {self.OUTPUT: dest_id}

    def name(self):
        return "emiToolsAggregateArray"

    def displayName(self):
        return tr("Aggregate Rows to Array")

    def group(self):
        return tr("EMI Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr(
            "Aggregates features by a selected field.\n"
            "Aggregated attributes are stored as arrays "
            "in fields suffixed with '_list'.\n"
        )

    def createInstance(self):
        return emiToolsArrayAggregate()
