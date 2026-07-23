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

__revision__ = "$Format:%H$"

from qgis.core import (
    NULL,
    QgsFeatureSink,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterDefinition,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterField,
    QgsVectorLayer,
    QgsWkbTypes,
)

from .emi_tools_util import tr


class emiToolsReplaceGeometry(QgsProcessingAlgorithm):
    TARGET_LAYER = "INPUT"
    TARGET_FIELD = "TARGET_FIELD"
    SOURCE_LAYER = "SOURCE_LAYER"
    SOURCE_FIELD = "SOURCE_FIELD"
    UPDATE_ATTRIBUTES = "UPDATE_ATTRIBUTES"
    OUTPUT = "OUTPUT"

    def flags(self):
        return super().flags() | QgsProcessingAlgorithm.Flag.FlagSupportsInPlaceEdits

    def supportInPlaceEdit(self, layer):

        if not isinstance(layer, QgsVectorLayer):
            return False
        return layer.isValid()

    def initAlgorithm(self, config=None):

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.TARGET_LAYER,
                tr("Target layer"),
                [QgsProcessing.SourceType.TypeVectorAnyGeometry],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.TARGET_FIELD,
                tr("Target field"),
                parentLayerParameterName=self.TARGET_LAYER,
                type=QgsProcessingParameterField.DataType.Any,
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.SOURCE_LAYER,
                tr("Source layer"),
                [QgsProcessing.SourceType.TypeVectorAnyGeometry],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.SOURCE_FIELD,
                tr("Source field"),
                parentLayerParameterName=self.SOURCE_LAYER,
                type=QgsProcessingParameterField.DataType.Any,
            )
        )

        update_attrs_param = QgsProcessingParameterBoolean(
            self.UPDATE_ATTRIBUTES,
            tr("Update other common attributes"),
            defaultValue=False,
        )
        update_attrs_param.setFlags(
            update_attrs_param.flags()
            | QgsProcessingParameterDefinition.Flag.FlagAdvanced
        )
        self.addParameter(update_attrs_param)

        self.addParameter(
            QgsProcessingParameterFeatureSink(self.OUTPUT, tr("Output layer"))
        )

    def processAlgorithm(self, parameters, context, feedback):
        feedback = QgsProcessingMultiStepFeedback(4, feedback)

        target_source = self.parameterAsSource(parameters, self.TARGET_LAYER, context)
        if target_source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.TARGET_LAYER)
            )

        source_source = self.parameterAsSource(parameters, self.SOURCE_LAYER, context)
        if source_source is None:
            raise QgsProcessingException(
                self.invalidSourceError(parameters, self.SOURCE_LAYER)
            )

        target_field_name = self.parameterAsString(
            parameters, self.TARGET_FIELD, context
        )
        source_field_name = self.parameterAsString(
            parameters, self.SOURCE_FIELD, context
        )
        update_attributes = self.parameterAsBoolean(
            parameters, self.UPDATE_ATTRIBUTES, context
        )

        target_fields = target_source.fields()
        source_fields = source_source.fields()

        target_field_idx = target_fields.indexOf(target_field_name)
        source_field_idx = source_fields.indexOf(source_field_name)

        if target_field_idx == -1:
            raise QgsProcessingException(
                tr("Field '{}' not found in the target layer.").format(
                    target_field_name
                )
            )
        if source_field_idx == -1:
            raise QgsProcessingException(
                tr("Field '{}' not found in the source layer.").format(
                    source_field_name
                )
            )

        target_wkb = target_source.wkbType()
        source_wkb = source_source.wkbType()

        if QgsWkbTypes.geometryType(target_wkb) != QgsWkbTypes.geometryType(
            source_wkb
        ) or (
            QgsWkbTypes.isMultiType(source_wkb)
            and not QgsWkbTypes.isMultiType(target_wkb)
        ):
            raise QgsProcessingException(
                tr(
                    "Geometry type mismatch: the target layer is "
                    "'{}' but the source layer is '{}'. Both layers must have "
                    "the same geometry category (point/line/polygon), and a "
                    "multi-part source cannot be used with a single-part target."
                ).format(
                    QgsWkbTypes.displayString(target_wkb),
                    QgsWkbTypes.displayString(source_wkb),
                )
            )

        feedback.setCurrentStep(0)
        feedback.pushInfo(tr("Indexing source layer features..."))

        source_index = {}
        duplicated_keys = set()

        for feature in source_source.getFeatures():
            if feedback.isCanceled():
                break
            key = self._normalize_key(feature.attribute(source_field_idx))
            if key in source_index:
                duplicated_keys.add(key)
                continue
            source_index[key] = feature

        if duplicated_keys:
            raise QgsProcessingException(
                tr(
                    "Duplicate keys found in source layer: {}. Please ensure the "
                    "source layer has unique values in the common field before "
                    "running this algorithm."
                ).format(sorted(duplicated_keys))
            )

        feedback.pushInfo(
            tr(
                "{} unique keys indexed from the source layer (feature count "
                "reported by the source: {})."
            ).format(len(source_index), source_source.featureCount())
        )

        feedback.setCurrentStep(1)
        common_attr_names = []
        if update_attributes:
            source_field_names = {f.name() for f in source_fields}
            common_attr_names = [
                f.name()
                for f in target_fields
                if f.name() in source_field_names and f.name() != target_field_name
            ]
            feedback.pushInfo(
                tr("Common attributes to be updated: {}").format(common_attr_names)
                if common_attr_names
                else tr("No common attributes found besides the join fields.")
            )

        feedback.setCurrentStep(2)
        sink, dest_id = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            target_fields,
            target_source.wkbType(),
            target_source.sourceCrs(),
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        feedback.setCurrentStep(3)
        total = target_source.featureCount() or 1
        matched_count = 0
        unmatched_count = 0

        for current, feature in enumerate(target_source.getFeatures()):
            if feedback.isCanceled():
                break

            key = self._normalize_key(feature.attribute(target_field_idx))
            source_feature = source_index.get(key)

            if source_feature is not None:
                feature.setGeometry(source_feature.geometry())

                if update_attributes:
                    for attr_name in common_attr_names:
                        src_idx = source_fields.indexOf(attr_name)
                        dst_idx = target_fields.indexOf(attr_name)
                        if src_idx != -1 and dst_idx != -1:
                            feature.setAttribute(
                                dst_idx, source_feature.attribute(src_idx)
                            )

                matched_count += 1
            else:
                unmatched_count += 1
                feedback.pushWarning(
                    tr(
                        "No matching feature found in source layer for key '{}' "
                        "(feature id {}). Original geometry kept."
                    ).format(key, feature.id())
                )

            sink.addFeature(feature, QgsFeatureSink.Flag.FastInsert)
            feedback.setProgress(int(current * 100 / total))

        feedback.pushInfo(
            tr(
                "Finished. {} geometries replaced, {} features kept unchanged "
                "(no match)."
            ).format(matched_count, unmatched_count)
        )

        return {self.OUTPUT: dest_id}

    @staticmethod
    def _normalize_key(value):
        """Normalizes a field value for reliable comparison between the two layers
        (e.g. avoids mismatches between '123' and 123.0). Both Python's None and
        QGIS's NULL sentinel (returned by some providers, e.g. PostgreSQL, for
        empty fields) are normalized to the same None value, so an empty/NULL
        common field is treated as a valid (if potentially ambiguous) match key
        rather than being silently ignored."""
        if value is None or value == NULL:
            return None
        return str(value).strip()

    def name(self):
        return "emiToolsReplaceGeometry"

    def displayName(self):
        return tr("Replace feature geometry")

    def group(self):
        return tr("Emi Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr(
            "This algorithm replaces the geometry of features in a target layer with the geometry of "
            "matching features from a source layer, based on a common field between the two layers.\n\n"
            "Features in the target layer that have no matching key in the source layer keep their "
            "original geometry, and a warning is reported.\n\n"
            "Advanced option: 'Update other common attributes' also copies over the values of any "
            "attribute that has the same name in both layers.\n\n"
        )

    def createInstance(self):
        return emiToolsReplaceGeometry()
