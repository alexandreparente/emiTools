from qgis.PyQt.QtCore import QCoreApplication, QVariant, QSizeF
from qgis.core import (
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterFeatureSource,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterField,
    QgsProcessingParameterFolderDestination,
    QgsProcessingParameterFile,
    QgsProject,
    QgsFeatureRequest,
    QgsVectorLayer,
    QgsLayout,
    QgsPrintLayout,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutExporter,
    QgsLayoutItemPicture,
    QgsLayoutSize,
    QgsRectangle,
    QgsExpression,
    QgsFeature,
    QgsReadWriteContext,
    QgsLayoutItem
)

from qgis.PyQt.QtXml import QDomDocument

import os

class emiToolsPhotographicReport(QgsProcessingAlgorithm):

    INPUT_COBERTURA = 'INPUT_COBERTURA'
    INPUT_PONTOS = 'INPUT_PONTOS'
    INPUT_AREAS = 'INPUT_AREAS'
    INPUT_RASTER = 'INPUT_RASTER'
    FIELD_ID = 'FIELD_ID'
    FIELD_PATH = 'FIELD_PATH'
    INPUT_LAYOUT_TEMPLATE = 'INPUT_LAYOUT_TEMPLATE'
    OUTPUT_FOLDER = 'OUTPUT_FOLDER'

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_COBERTURA, 'Camada de cobertura (polígono)', [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_PONTOS, 'Camada de pontos (fotos)', [QgsProcessing.TypeVectorPoint]))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_AREAS, 'Camada de áreas fotografadas (polígono)', [QgsProcessing.TypeVectorPolygon]))

        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT_RASTER, 'Camada de fundo (raster)'))

        self.addParameter(QgsProcessingParameterField(
            self.FIELD_ID, 'Campo de ID da área fotografada (id_p)', parentLayerParameterName=self.INPUT_PONTOS))

        self.addParameter(QgsProcessingParameterField(
            self.FIELD_PATH, 'Campo com caminho da foto (path)', parentLayerParameterName=self.INPUT_PONTOS))

        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_LAYOUT_TEMPLATE,
            'Modelo de layout (.qpt)',
            behavior=QgsProcessingParameterFile.File,
            fileFilter=''))

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER, 'Pasta de saída para os PDFs'))

    def processAlgorithm(self, parameters, context, feedback):
        cobertura_layer = self.parameterAsSource(parameters, self.INPUT_COBERTURA, context)
        pontos_layer = self.parameterAsSource(parameters, self.INPUT_PONTOS, context)
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        id_field = self.parameterAsString(parameters, self.FIELD_ID, context)
        path_field = self.parameterAsString(parameters, self.FIELD_PATH, context)

        #layout_template = self.parameterAsFile(parameters, self.INPUT_LAYOUT_TEMPLATE, context)
        layout_template = '/home/alexandre/Qgis/Teste/teste.qpt'

        feedback.pushInfo(f"Template recebido: {layout_template}")

        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)

        if not os.path.isfile(layout_template):
            feedback.reportError(f"Arquivo .qpt não encontrado: {layout_template}")
            raise QgsProcessingException("Arquivo de layout inválido ou não encontrado.")

        project = QgsProject.instance()

        for feat_cob in cobertura_layer.getFeatures():
            cob_geom = feat_cob.geometry()

            request = QgsFeatureRequest().setFilterRect(cob_geom.boundingBox())
            pontos_relacionados = [f for f in pontos_layer.getFeatures(request) if f.geometry().intersects(cob_geom)]

            if not pontos_relacionados:
                continue

            layout = QgsPrintLayout(project)
            layout.initializeDefaults()
            layout.setName(f"AtlasLayout_{feat_cob.id()}")

            # Carregar layout a partir do template
            template_doc = QDomDocument()
            template_file = open(layout_template, 'r', encoding='utf-8')
            template_doc.setContent(template_file.read())
            template_file.close()

            context_rw = QgsReadWriteContext()
            layout.loadFromTemplate(template_doc, context_rw)

            # Substituir texto no layout_area
            label_area = layout.itemById('layout_area')
            if isinstance(label_area, QgsLayoutItemLabel):
                label_area.setText(f"Área: {feat_cob[id_field]}")
                label_area.adjustSizeToText()

            # Ajustar o mapa layout_mapa
            layout_map = layout.itemById('layout_mapa')
            if isinstance(layout_map, QgsLayoutItemMap):
                layout_map.zoomToExtent(cob_geom.boundingBox())

            # Substituir imagem no layout_imagens (usa a primeira imagem associada)
            image_item = layout.itemById('layout_imagens')
            if isinstance(image_item, QgsLayoutItemPicture):
                for ponto in pontos_relacionados:
                    photo_path = ponto[path_field]
                    if os.path.exists(photo_path):
                        image_item.setPicturePath(photo_path)
                        break  # apenas a primeira imagem

            # Exportar PDF
            output_pdf = os.path.join(output_folder, f"atlas_area_{feat_cob[id_field]}.pdf")
            exporter = QgsLayoutExporter(layout)
            result = exporter.exportToPdf(output_pdf, QgsLayoutExporter.PdfExportSettings())
            if result == QgsLayoutExporter.Success:
                feedback.pushInfo(f"PDF gerado: {output_pdf}")
            else:
                feedback.reportError(f"Erro ao gerar PDF: {output_pdf}")

        return {"OUTPUT": output_folder}

    def name(self):
        return "atlas_pdf_generator"

    def displayName(self):
        return "Gerador de Atlas em PDF"

    def group(self):
        return "Relatórios e Mapas"

    def groupId(self):
        return ""

    def createInstance(self):
        return emiToolsPhotographicReport()
