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
    QgsLayoutItem,
    QgsLayoutAtlas,
    QgsExpressionContext,
    QgsExpressionContextUtils,
    QgsLayoutObject
)

from PyQt5.QtCore import QByteArray, QTextStream, QIODevice
from qgis.PyQt.QtXml import QDomDocument
from xml.dom.minidom import parseString
from uuid import uuid4
import os
import re
import math


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
            self.INPUT_COBERTURA, 'Camada de cobertura (polígono)', [QgsProcessing.TypeVectorPolygon],
            defaultValue='box'))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_PONTOS, 'Camada de pontos (fotos)', [QgsProcessing.TypeVectorPoint], defaultValue='output_file'))

        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_AREAS, 'Camada de áreas fotografadas (polígono)', [QgsProcessing.TypeVectorPolygon],
            defaultValue='poligonos'))

        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT_RASTER, 'Camada de fundo (raster)', defaultValue='Google Satelite'))

        self.addParameter(QgsProcessingParameterField(
            self.FIELD_ID, 'Campo de ID da área fotografada', parentLayerParameterName=self.INPUT_PONTOS,
            defaultValue='id_p'))

        self.addParameter(QgsProcessingParameterField(
            self.FIELD_PATH, 'Campo com caminho da foto', parentLayerParameterName=self.INPUT_PONTOS,
            defaultValue='photo'))

        self.addParameter(QgsProcessingParameterFile(
            self.INPUT_LAYOUT_TEMPLATE,
            'Modelo de layout (.qpt)',
            behavior=QgsProcessingParameterFile.File,
            extension='qpt', defaultValue='/home/alexandre/Qgis/Teste/teste_2fotos.qpt'))

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER, 'Pasta de saída para os PDFs', defaultValue='/home/alexandre/Qgis/Teste/pdf'))

        self.addParameter(QgsProcessingParameterFolderDestination(
            self.OUTPUT_FOLDER, 'Pasta de saída para os PDFs'))

    def processAlgorithm(self, parameters, context, feedback):
        # Get input parameters
        cobertura_layer = self.parameterAsLayer(parameters, self.INPUT_COBERTURA, context)
        cobertura_source = self.parameterAsSource(parameters, self.INPUT_COBERTURA, context)
        pontos_layer = self.parameterAsVectorLayer(parameters, self.INPUT_PONTOS, context)
        areas_layer = self.parameterAsVectorLayer(parameters, self.INPUT_AREAS, context)
        raster_layer = self.parameterAsRasterLayer(parameters, self.INPUT_RASTER, context)
        id_field = self.parameterAsString(parameters, self.FIELD_ID, context)
        path_field = self.parameterAsString(parameters, self.FIELD_PATH, context)
        layout_template = self.parameterAsFile(parameters, self.INPUT_LAYOUT_TEMPLATE, context)
        output_folder = self.parameterAsString(parameters, self.OUTPUT_FOLDER, context)


        # Verify template file exists
        if not os.path.isfile(layout_template):
            feedback.reportError(f"Arquivo .qpt não encontrado: {layout_template}")
            raise QgsProcessingException("Arquivo de layout inválido ou não encontrado.")

        # Verify output folder exists
        os.makedirs(output_folder, exist_ok=True)

        # Analyze layout template
        project_temp = QgsProject.instance()
        layout_temp = QgsPrintLayout(project_temp)
        layout_temp.initializeDefaults()
        layout_temp.setName("temp_layout")

        template_doc_temp = QDomDocument()
        with open(layout_template, 'r', encoding='utf-8') as file:
            content = file.read()
            if not template_doc_temp.setContent(content):
                raise QgsProcessingException("Erro ao carregar template .qpt")

        context_rw = QgsReadWriteContext()
        layout_temp.loadFromTemplate(template_doc_temp, context_rw)

        #numero de paginas do modelo
        numero_paginas_modelo = layout_temp.pageCollection().pageCount()
        feedback.pushInfo(f"Número de páginas: {numero_paginas_modelo}")

        #numero de imagens do modelo
        numero_imagens_total = sum(
            1 for item in layout_temp.items()
            if isinstance(item, QgsLayoutItemPicture) and item.displayName().startswith("image")
        )

        feedback.pushInfo(f"Número total de imagens com nome iniciando por 'image': {numero_imagens_total}")

        # numero de imagens da pagina 2 do modelo
        # Obter altura da página dinamicamente
        page_height = layout_temp.pageCollection().page(0).sizeWithUnits().height()

        # Índice da página 2 (índice começa em 0)
        page_index = 1
        page_start = page_index * page_height
        page_end = (page_index + 1) * page_height

        # Contar apenas imagens na página 2 cujo nome começa com "image"
        numero_imagens_pagina2 = sum(
            1 for item in layout_temp.items()
            if (
                    isinstance(item, QgsLayoutItemPicture) and
                    page_start <= item.pos().y() < page_end and
                    item.displayName().startswith("image")
            )
        )

        feedback.pushInfo(f"Número de imagens na página 2 com nome iniciando por 'image': {numero_imagens_pagina2}")

        # Verify template has exactly 2 pages
        if numero_paginas_modelo != 2:
            raise QgsProcessingException("O layout deve conter exatamente duas páginas.")


        #Novo projeto

        project = QgsProject.instance()

        # Process each coverage area
        for feat_cob in cobertura_source.getFeatures():
            cob_geom = feat_cob.geometry()

            # Find related photos
            request = QgsFeatureRequest().setFilterRect(cob_geom.boundingBox())
            pontos_relacionados = [f for f in pontos_layer.getFeatures(request)
                                   if f.geometry().intersects(cob_geom)]

            numero_fotos = len(pontos_relacionados)
            feedback.pushInfo(f"Área {feat_cob[id_field]} possui {numero_fotos} foto(s).")

            numero_copias = math.ceil(((numero_fotos - (numero_imagens_total-numero_imagens_pagina2))/numero_imagens_pagina2)-1)

            if not pontos_relacionados:
                continue

            # Create temporary template with duplicated pages
            export_template = os.path.join(output_folder, f"new_layout_template{feat_cob.id()}.qpt")
            new_layout_template = self.duplicar_segunda_pagina_qpt(
                layout_template, numero_copias, export_template, feedback)



            # --- Carrega o layout a partir do QPT ---
            layout = QgsPrintLayout(project)
            layout.initializeDefaults()
            layout.setName(f"Layout_{feat_cob[id_field]}")

            template_doc = QDomDocument()
            with open(new_layout_template, 'r', encoding='utf-8') as f:
                template_content = f.read()
                if not template_doc.setContent(template_content):
                    raise QgsProcessingException("Erro ao carregar template QPT.")

            context_rw = QgsReadWriteContext()
            layout.loadFromTemplate(template_doc, context_rw)

            # Ajusta mapa (zoom e camadas)
            layout_map = layout.itemById('map_001')
            if isinstance(layout_map, QgsLayoutItemMap):
                layout_map.zoomToExtent(cob_geom.boundingBox())
                layout_map.setLayers([pontos_layer, areas_layer, raster_layer])

            # --- Insere as fotos nos itens de imagem ---
            image_items = [
                item for item in layout.items()
                if isinstance(item, QgsLayoutItemPicture) and item.id().startswith("image")
            ]
            image_items.sort(key=lambda item: item.pos().y())

            for i, ponto in enumerate(pontos_relacionados):
                if i >= len(image_items):
                    break
                photo_path = ponto[path_field]
                if os.path.exists(photo_path):
                    image_items[i].setPicturePath(photo_path)

            # --- Prepara o contexto de expressão para etiquetas e DDP ---
            expr_context = QgsExpressionContext()
            expr_context.appendScope(QgsExpressionContextUtils.projectScope(project))
            expr_context.appendScope(QgsExpressionContextUtils.layerScope(cobertura_layer))
            expr_context.setFeature(feat_cob)

            # --- Atualiza expressões de labels e imagens com base no contexto ---
            self.atualizar_expressões_layout(layout, expr_context, feedback)



            # --- Agora exporta o layout para PDF ---
            output_pdf = os.path.join(output_folder, f"atlas_area_{feat_cob[id_field]}.pdf")
            exporter = QgsLayoutExporter(layout)
            export_result = exporter.exportToPdf(output_pdf, QgsLayoutExporter.PdfExportSettings())

            if export_result == QgsLayoutExporter.Success:
                feedback.pushInfo(f"PDF gerado: {output_pdf}")
                feedback.pushInfo(f"Template salvo: {export_template}")
            else:
                feedback.reportError(f"Erro ao gerar PDF: {output_pdf}")

            # Clean up temporary template
            """###
            try:
                os.remove(new_layout_template)
            except Exception as e:
                feedback.pushWarning(f"Erro ao remover template temporário: {str(e)}")
            """

        return {"OUTPUT": output_folder}

    def duplicar_segunda_pagina_qpt(self, caminho_qpt_original, numero_copias, caminho_saida, feedback):
        """
                Duplica a segunda página do template QPT para acomodar mais fotos.

                Args:
                    caminho_qpt_original: Caminho do template original
                    numero_copias: Quantas vezes duplicar a segunda página
                    caminho_saida: Caminho para salvar o novo template
                    feedback: Objeto para mensagens de feedback

                Returns:
                    Caminho para o novo template criado
                """

        doc = QDomDocument()
        with open(caminho_qpt_original, 'r', encoding='utf-8') as f:
            conteudo = f.read()
            if not doc.setContent(conteudo):
                raise QgsProcessingException("Erro ao carregar o QPT.")

        layout_items = doc.elementsByTagName('LayoutItem')
        paginas = []
        elementos = []

        # Classify items into pages and other elements
        for i in range(layout_items.count()):
            item = layout_items.item(i).toElement()
            tipo = item.attribute('type')
            pos = item.attribute('position')

            try:
                y = float(pos.split(',')[1]) if pos and ',' in pos else 0
            except ValueError:
                y = 0

            if tipo == '65638':  # Page item
                paginas.append({'elemento': item, 'y': y})
            else:
                elementos.append({'elemento': item, 'y': y})

        if len(paginas) < 2:
            raise QgsProcessingException("O layout precisa ter ao menos duas páginas.")

        # Get page height from size attribute (e.g., "210,297,mm")
        size_attr = paginas[0]['elemento'].attribute('size')
        try:
            size_parts = size_attr.split(',')
            altura_pagina = float(size_parts[1])
        except Exception as e:
            raise QgsProcessingException(f"Erro ao ler altura da página: {size_attr} - {e}")

        # Calculate spacing between pages
        primeira_y = paginas[0]['y']
        segunda_y = paginas[1]['y']
        espacamento = segunda_y - primeira_y - altura_pagina
        altura_total_pagina = altura_pagina + espacamento

        # Items from second page
        itens_segunda_pagina = [e for e in elementos
                                if segunda_y <= e['y'] < segunda_y + altura_total_pagina]

        # Find PageCollection tag
        page_collection_nodes = doc.elementsByTagName('PageCollection')
        if page_collection_nodes.count() == 0:
            raise QgsProcessingException("Tag <PageCollection> não encontrada no QPT.")
        page_collection = page_collection_nodes.item(0).toElement()

        # Coletar todos os IDs existentes no layout
        existing_ids = set()
        for i in range(layout_items.count()):
            item = layout_items.item(i).toElement()
            item_id = item.attribute('id')
            if item_id:
                existing_ids.add(item_id)

        # Detectar prefixo comum e maior sufixo numérico
        id_pattern = re.compile(r"(.+?)_(\d+)$")
        prefixos = {}
        for item_id in existing_ids:
            m = id_pattern.match(item_id)
            if m:
                prefix, num = m.groups()
                num = int(num)
                if prefix not in prefixos or num > prefixos[prefix]:
                    prefixos[prefix] = num

        layout_element = doc.documentElement()

        # Inserir páginas e elementos duplicados
        for i in range(numero_copias):
            deslocamento_y = (i + 1) * altura_total_pagina

            # Clone da segunda página
            nova_pagina = paginas[1]['elemento'].cloneNode(True).toElement()
            nova_pagina.setAttribute('uuid', str(uuid4()))
            nova_pagina.setAttribute('position', f"0,{segunda_y + deslocamento_y},mm")
            page_collection.appendChild(nova_pagina)

            # Duplicar elementos da segunda página
            for item in itens_segunda_pagina:
                elem = item['elemento'].cloneNode(True).toElement()
                pos = elem.attribute('position')

                if pos and ',' in pos:
                    partes = pos.split(',')
                    try:
                        x = float(partes[0])
                        y = float(partes[1])
                        elem.setAttribute('position', f"{x},{y + deslocamento_y},mm")
                    except Exception as e:
                        feedback.pushWarning(f"Erro ao converter posição '{pos}': {e}")

                elem.setAttribute('uuid', str(uuid4()))

                # Atualizar ID
                old_id = elem.attribute('id')
                if old_id:
                    m = id_pattern.match(old_id)
                    if m:
                        prefix = m.group(1)
                        prefixos[prefix] += 1
                        new_id = f"{prefix}_{prefixos[prefix]:03d}"
                        elem.setAttribute('id', new_id)
                    else:
                        feedback.pushWarning(f"ID '{old_id}' não segue o padrão esperado.")

                layout_element.appendChild(elem)

        # Salvar novo template
        with open(caminho_saida, 'w', encoding='utf-8') as f:
            f.write(doc.toString(2))

        feedback.pushInfo(f"Template modificado salvo em: {caminho_saida}")
        return caminho_saida

    def atualizar_expressões_layout(self, layout, expr_context, feedback=None):
        """
        Atualiza expressões em labels (com [% %]) e imagens (com dataDefinedProperties).
        """
        # 1. Substitui expressões nos rótulos [% campo %]
        for item in layout.items():
            if isinstance(item, QgsLayoutItemLabel):
                texto = item.text()
                if '[%' in texto and '%]' in texto:
                    try:
                        novo_texto = QgsExpression.replaceExpressionText(texto, expr_context)
                        item.setText(novo_texto)
                        if feedback:
                            feedback.pushInfo(f"Label atualizado: {novo_texto}")
                    except Exception as e:
                        if feedback:
                            feedback.pushWarning(f"Erro ao avaliar texto do label: '{texto}' → {e}")

        # 2. Avalia expressões nos dataDefinedProperties das imagens
        for item in layout.items():
            if isinstance(item, QgsLayoutItemPicture):
                ddp = item.dataDefinedProperties()
                if ddp.hasProperty(QgsLayoutObject.SourceUrl):
                    propriedade = ddp.property(QgsLayoutObject.SourceUrl)
                    expr_str = propriedade.expression()
                    try:
                        expr = QgsExpression(expr_str)
                        resultado = expr.evaluate(expr_context)
                        if expr.hasParserError() or expr.hasEvalError():
                            raise Exception(expr.parserErrorString() or expr.evalErrorString())
                        item.setPicturePath(resultado)
                        if feedback:
                            feedback.pushInfo(f"Imagem atualizada com: {resultado}")
                    except Exception as e:
                        if feedback:
                            feedback.pushWarning(f"Erro ao avaliar expressão da imagem: '{expr_str}' → {e}")

    def name(self):
        return "emi_tools_photographic_report"

    def displayName(self):
        return "Relatório Fotográfico EMI Tools"

    def group(self):
        return "Relatórios e Mapas"

    def groupId(self):
        return ""

    def createInstance(self):
        return emiToolsPhotographicReport()