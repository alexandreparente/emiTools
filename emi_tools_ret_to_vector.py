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

import json
import os
import zipfile

from qgis.core import (
    QgsFeature,
    QgsField,
    QgsFields,
    QgsJsonUtils,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterBoolean,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFile,
    QgsProcessingParameterFolderDestination,
    QgsProject,
    QgsVectorFileWriter,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

from .emi_tools_util import tr

# Prefixes used by SICAR to name the data file bundled inside the .RET zip
# (state acronym, e.g. "PB-", or the "CAR" prefix used for some exports).
_SICAR_UF_PREFIXES = (
    "DF-",
    "GO-",
    "MT-",
    "MS-",
    "MG-",
    "SP-",
    "PR-",
    "SC-",
    "RS-",
    "ES-",
    "RJ-",
    "BA-",
    "SE-",
    "AL-",
    "PE-",
    "PB-",
    "RN-",
    "CE-",
    "PI-",
    "MA-",
    "TO-",
    "PA-",
    "AP-",
    "RR-",
    "AM-",
    "AC-",
    "RO-",
)

# Max text length used for the concatenated summary fields. Kept at 254 so
# the output stays compatible with the ESRI Shapefile driver.
_TEXT_FIELD_LEN = 254


def _truncate(value, feedback, field_label):
    """Truncates a text value to _TEXT_FIELD_LEN, warning via feedback if
    truncation actually happened."""
    if value and len(value) > _TEXT_FIELD_LEN:
        feedback.pushWarning(
            tr(
                f"Field '{field_label}' exceeded {_TEXT_FIELD_LEN} characters and was truncated to maintain Shapefile compatibility."
            )
        )
        return value[:_TEXT_FIELD_LEN]
    return value or ""


# Configuration table for the property-level cadastral attributes attached
# to every generated layer, following the same "one config dict, easy to
# maintain" pattern used by METADATA_CONF in emi_tools_photo_metadata.py.
#
# Each entry maps the OUTPUT FIELD NAME (<=10 chars, Shapefile-safe) to:
#   - section: top-level key in the parsed JSON ("imovel", "cadastrante",
#     "origem", or a list section like "documentos")
#   - index: only for list sections - which item to read (default 0).
#     Assumes SICAR keeps a stable item order within that list; if a
#     property has no item at that index, the field is just left empty.
#   - subsection: optional nested dict inside the section/item (e.g. the
#     address, or a document's "detalheDocumentoPropriedade")
#   - key: the key to read inside section/subsection
#   - list_value_index: only if the value at "key" is itself a list (e.g.
#     "respostas": ["Sim"]) - which element to take (default 0)
#   - type: python type used to coerce the value (str, int or float)
#
# To track a new field from the SICAR JSON, just add a line here - no other
# code needs to change.


ATTRIBUTE_CONF = {
    # --- imovel ---
    "imo_nome": {"section": "imovel", "key": "nome", "type": str},
    "imo_tipo": {"section": "imovel", "key": "tipo", "type": str},
    "mun_cod": {"section": "imovel", "key": "codigoMunicipio", "type": int},
    "cep": {"section": "imovel", "key": "cep", "type": str},
    "telefone": {"section": "imovel", "key": "telefone", "type": str},
    "zona": {"section": "imovel", "key": "zonaLocalizacao", "type": str},
    "mod_fiscal": {"section": "imovel", "key": "modulosFiscais", "type": float},
    "email": {"section": "imovel", "key": "email", "type": str},
    "id_pai": {"section": "imovel", "key": "idPai", "type": str},
    # imovel.enderecoCorrespondencia (nested one level)
    "end_log": {
        "section": "imovel",
        "subsection": "enderecoCorrespondencia",
        "key": "logradouro",
        "type": str,
    },
    "end_num": {
        "section": "imovel",
        "subsection": "enderecoCorrespondencia",
        "key": "numero",
        "type": str,
    },
    "end_bairro": {
        "section": "imovel",
        "subsection": "enderecoCorrespondencia",
        "key": "bairro",
        "type": str,
    },
    "end_comp": {
        "section": "imovel",
        "subsection": "enderecoCorrespondencia",
        "key": "complemento",
        "type": str,
    },
    # --- cadastrante ---
    "cad_cpf": {"section": "cadastrante", "key": "cpf", "type": str},
    "cad_nome": {"section": "cadastrante", "key": "nome", "type": str},
    "cad_nasc": {"section": "cadastrante", "key": "dataNascimento", "type": str},
    "cad_mae": {"section": "cadastrante", "key": "nomeMae", "type": str},
    # --- origem (protocolo) ---
    "protocolo": {"section": "origem", "key": "codigoProtocolo", "type": str},
    "status": {"section": "origem", "key": "status", "type": str},
    "dt_protoc": {"section": "origem", "key": "dataProtocolo", "type": str},
    # --- proprietariosPosseirosConcessionarios[0] (fixed index, not a summary) ---
    "prop_nome": {
        "section": "proprietariosPosseirosConcessionarios",
        "index": 0,
        "key": "nome",
        "type": str,
    },
    "prop_cpf": {
        "section": "proprietariosPosseirosConcessionarios",
        "index": 0,
        "key": "cpfCnpj",
        "type": str,
    },
    "prop_tipo": {
        "section": "proprietariosPosseirosConcessionarios",
        "index": 0,
        "key": "tipo",
        "type": str,
    },
    "prop_nasc": {
        "section": "proprietariosPosseirosConcessionarios",
        "index": 0,
        "key": "dataNascimento",
        "type": str,
    },
    "prop_mae": {
        "section": "proprietariosPosseirosConcessionarios",
        "index": 0,
        "key": "nomeMae",
        "type": str,
    },
    # --- documentos[0] (fixed index, not a summary) ---
    "doc_tipo": {"section": "documentos", "index": 0, "key": "tipo", "type": str},
    "doc_denom": {
        "section": "documentos",
        "index": 0,
        "key": "denominacao",
        "type": str,
    },
    "doc_area": {
        "section": "documentos",
        "index": 0,
        "key": "area",
        "type": str,
    },  # texto: SICAR usa vírgula decimal (ex: "232,4688")
    "doc_tipdoc": {
        "section": "documentos",
        "index": 0,
        "key": "tipoDocumentoPropriedade",
        "type": str,
    },
    "doc_matr": {
        "section": "documentos",
        "index": 0,
        "subsection": "detalheDocumentoPropriedade",
        "key": "numeroMatricula",
        "type": str,
    },
    "doc_livro": {
        "section": "documentos",
        "index": 0,
        "subsection": "detalheDocumentoPropriedade",
        "key": "livro",
        "type": str,
    },
    "doc_folha": {
        "section": "documentos",
        "index": 0,
        "subsection": "detalheDocumentoPropriedade",
        "key": "folha",
        "type": str,
    },
    "doc_dtreg": {
        "section": "documentos",
        "index": 0,
        "subsection": "detalheDocumentoPropriedade",
        "key": "dataRegistro",
        "type": str,
    },
    "info_cod": {"section": "informacoes", "index": 0, "key": "codigo", "type": str},
    "info_resp": {
        "section": "informacoes",
        "index": 0,
        "key": "respostas",
        "list_value_index": 0,
        "type": str,
    },
}


def _qvariant_for_type(py_type):
    """Maps a python type used in ATTRIBUTE_CONF to the matching QVariant."""
    if py_type is int:
        return QVariant.Int
    if py_type is float:
        return QVariant.Double
    return QVariant.String


def _resolve_value(dados, conf):
    """
    Reads the raw value described by an ATTRIBUTE_CONF entry out of the
    parsed SICAR JSON.

    :return: The raw value (still uncoerced), or None if any step along the
        path is missing (empty list, index out of range, missing key, ...).
    """
    node = dados.get(conf["section"])

    if isinstance(node, list):
        index = conf.get("index", 0)
        node = node[index] if 0 <= index < len(node) else None

    if not isinstance(node, dict):
        return None

    if "subsection" in conf:
        node = node.get(conf["subsection"])
        if not isinstance(node, dict):
            return None

    value = node.get(conf["key"])

    if isinstance(value, list):
        list_index = conf.get("list_value_index", 0)
        value = value[list_index] if 0 <= list_index < len(value) else None

    return value


def _coerce_value(raw_value, py_type, feedback, field_name):
    """Coerces a raw JSON value to the type declared in ATTRIBUTE_CONF,
    falling back to a safe default (0 / "") if missing or unconvertible."""
    if raw_value is None:
        return 0 if py_type in (int, float) else ""

    try:
        if py_type is str:
            return _truncate(str(raw_value), feedback, field_name)
        if py_type is int and not isinstance(raw_value, int):
            return int(raw_value)
        if py_type is float and not isinstance(raw_value, float):
            return float(raw_value)
        return raw_value
    except (TypeError, ValueError):
        return 0 if py_type in (int, float) else ""


class emiToolsRetToVector(QgsProcessingAlgorithm):
    INPUT_RET = "INPUT_RET"
    OUTPUT_FOLDER = "OUTPUT_FOLDER"
    OUTPUT_FORMAT = "OUTPUT_FORMAT"
    LOAD_OUTPUTS = "LOAD_OUTPUTS"

    def initAlgorithm(self, config=None):

        # Parameter to select the .RET file exported from SICAR.
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT_RET,
                tr("SICAR .RET file"),
                behavior=QgsProcessingParameterFile.File,
                fileFilter="Arquivos RET (*.RET *.ret)",
            )
        )

        # Destination folder
        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER, tr("Output folder")
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                self.OUTPUT_FORMAT,
                tr("Output file extension"),
                options=QgsVectorFileWriter.supportedFormatExtensions(),
                defaultValue=0,
            )
        )

        self.addParameter(
            QgsProcessingParameterBoolean(
                self.LOAD_OUTPUTS,
                tr("Load generated layers into the project"),
                defaultValue=True,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        feedback = QgsProcessingMultiStepFeedback(3, feedback)

        ret_file = self.parameterAsFile(parameters, self.INPUT_RET, context)
        if not ret_file or not os.path.exists(ret_file):
            raise QgsProcessingException(tr("Invalid or missing .RET file."))

        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)
        os.makedirs(output_folder, exist_ok=True)

        output_format = self.parameterAsEnum(parameters, self.OUTPUT_FORMAT, context)
        output_ext = QgsVectorFileWriter.supportedFormatExtensions()[output_format]
        driver_name = QgsVectorFileWriter.driverForExtension(output_ext)
        load_outputs = self.parameterAsBoolean(parameters, self.LOAD_OUTPUTS, context)

        feedback.setCurrentStep(0)
        feedback.pushInfo(tr("Reading .RET file..."))
        try:
            with zipfile.ZipFile(ret_file, "r") as zip_ref:
                sicar_name = next(
                    (
                        name
                        for name in zip_ref.namelist()
                        if name.startswith(_SICAR_UF_PREFIXES) or name.startswith("CAR")
                    ),
                    None,
                )
                if not sicar_name:
                    raise QgsProcessingException(
                        tr(
                            "SICAR file not found inside the .RET. Expected a file "
                            "starting with a state acronym (e.g. 'PB-') or the 'CAR' prefix."
                        )
                    )
                with zip_ref.open(sicar_name) as f:
                    dados = json.load(f)
        except zipfile.BadZipFile:
            raise QgsProcessingException(
                tr(
                    "The .RET file is not a valid SICAR export (expected a zip archive)."
                )
            )

        if feedback.isCanceled():
            return {}

        feedback.setCurrentStep(1)
        common_fields, common_values = self._build_common_attributes(dados, feedback)

        feedback.setCurrentStep(2)
        written_layers = []
        geo_items = dados.get("geo", [])
        total = len(geo_items) or 1

        for i, item in enumerate(geo_items):
            if feedback.isCanceled():
                break
            feedback.setProgress(int(i / total * 100))

            tipo = item.get("tipo", "SEM_TIPO")
            geo_json = item.get("geoJson")

            geometry = QgsJsonUtils.geometryFromGeoJson(json.dumps(geo_json))
            if geometry is None or geometry.isEmpty():
                feedback.pushWarning(
                    tr(f"Skipping layer '{tipo}': geometry is invalid or empty.")
                )
                continue

            qgis_geom_type = QgsWkbTypes.displayString(geometry.wkbType())

            fields = QgsFields()
            fields.append(QgsField("tipo", QVariant.String, len=100))
            fields.append(QgsField("area", QVariant.Double))
            for field in common_fields:
                fields.append(field)

            layer = QgsVectorLayer(f"{qgis_geom_type}?crs=EPSG:4326", tipo, "memory")
            provider = layer.dataProvider()
            provider.addAttributes(fields)
            layer.updateFields()

            feature = QgsFeature(layer.fields())
            feature.setGeometry(geometry)
            feature.setAttributes([tipo, item.get("area", 0)] + common_values)
            provider.addFeature(feature)
            layer.updateExtents()

            output_path = os.path.join(output_folder, f"{tipo}.{output_ext}")
            error = QgsVectorFileWriter.writeAsVectorFormatV3(
                layer,
                output_path,
                QgsProject.instance().transformContext(),
                self._save_options(driver_name),
            )

            if error[0] != QgsVectorFileWriter.NoError:
                feedback.reportError(tr(f"Error saving '{tipo}': {error[1]}"))
                continue

            feedback.pushInfo(tr(f"Saved: {output_path}"))
            written_layers.append((tipo, output_path))

        feedback.pushInfo(
            tr(
                f"{len(written_layers)} of {len(geo_items)} layer(s) written successfully."
            )
        )

        if load_outputs:
            layers_to_add = []
            for tipo, path in written_layers:
                vlayer = QgsVectorLayer(path, tipo, "ogr")
                if vlayer.isValid():
                    layers_to_add.append(vlayer)
                else:
                    feedback.pushWarning(tr(f"Could not reload layer: {tipo}"))
            if layers_to_add:
                QgsProject.instance().addMapLayers(layers_to_add)

        return {self.OUTPUT_FOLDER: output_folder}

    def _build_common_attributes(self, dados, feedback):
        """Builds the property-level attribute fields/values shared by every
        output layer, entirely driven by ATTRIBUTE_CONF (module level) - a
        single loop, in dict order. Add a line there to track a new field;
        no other code needs to change.

        :return: (fields, values) - a list of QgsField and the matching
            list of attribute values, in the same order as ATTRIBUTE_CONF.
        """
        fields = []
        values = []

        for field_name, conf in ATTRIBUTE_CONF.items():
            py_type = conf["type"]
            raw_value = _resolve_value(dados, conf)

            field = QgsField(field_name, _qvariant_for_type(py_type))
            if py_type is str:
                field.setLength(_TEXT_FIELD_LEN)
            fields.append(field)
            values.append(_coerce_value(raw_value, py_type, feedback, field_name))

        return fields, values

    def _save_options(self, driver_name):
        options = QgsVectorFileWriter.SaveVectorOptions()
        options.driverName = driver_name
        options.fileEncoding = "UTF-8"
        return options

    def name(self):
        return "emiToolsRetToVector"

    def displayName(self):
        return tr("Convert SICAR .RET to vector layers")

    def group(self):
        return tr("Emi Tools")

    def groupId(self):
        return ""

    def shortHelpString(self):
        return tr(
            "Converts a SICAR .RET export into individual vector layers. "
            "Each geometry type is saved as a separate vector file, and all generated "
            "layers receive the property's cadastral information as attribute fields. "
        )

    def createInstance(self):
        return emiToolsRetToVector()
