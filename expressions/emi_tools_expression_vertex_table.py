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
 * *
 * This program is free software; you can redistribute it and/or modify  *
 * it under the terms of the GNU General Public License as published by  *
 * the Free Software Foundation; either version 2 of the License, or     *
 * (at your option) any later version.                                   *
 * *
 ***************************************************************************/
"""

__author__ = 'Alexandre Parente Lima'
__date__ = '2024-10-10'
__copyright__ = '(C) 2024 by Alexandre Parente Lima'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from qgis.core import *
from qgis.gui import *


@qgsfunction(args='auto', group='Custom')
def vertex_table(geometry, pagina, tamanho_bloco, feature, parent):
    """
    Generates paginated HTML of vertices.
    Usage: vertex_table($geometry, page_number, items_per_page)
    Ex: vertex_table($geometry, 1, 30) for 1-30
        vertex_table($geometry, 2, 30) for 31-60
    """

    # List to store all flat vertices
    lista_vertices = []

    # Convert to MultiPolygon to standardize the loop
    if not geometry.isMultipart():
        geometry = geometry.asGeometryCollection()[0]  # Force collection structure if necessary

    # Extract structure (Parts -> Rings -> Vertices)
    # Handles QgsGeometry.asMultiPolygon() returning [[point, ...], ...]
    # Structure of asMultiPolygon: [ [ (ext_ring), (int_ring), ... ], ... ]

    try:
        # Try to get as multipolygon
        partes = geometry.asMultiPolygon()
    except:
        # If it fails (e.g. simple polygon), convert it
        temp_geom = QgsGeometry(geometry)
        temp_geom.convertToMultiType()
        partes = temp_geom.asMultiPolygon()

    idx_geral = 0

    # Parts Loop
    for i_parte, parte in enumerate(partes):
        # Rings Loop (0 = Exterior, 1+ = Interior)
        for i_anel, anel in enumerate(parte):
            # Vertices Loop (ignoring the last duplicated vertex in closed polygons)
            total_pontos = len(anel)

            # If it is a closed polygon, the last point is equal to the first, we ignore it in the loop
            # unless the geometry is corrupted and is open
            pontos_uteis = anel[:-1] if total_pontos > 1 and anel[0] == anel[-1] else anel

            for pt in pontos_uteis:
                idx_geral += 1

                # Formats identifier (P1-R0)
                # i_parte + 1 to start from 1
                identificador = f"P{i_parte + 1}-R{i_anel}"

                lista_vertices.append({
                    'id': idx_geral,
                    'ref': identificador,
                    'x': f"{pt.x():.6f}",  # Format here to save processing
                    'y': f"{pt.y():.6f}"
                })

    # --- Pagination Logic ---
    inicio = (pagina - 1) * tamanho_bloco
    fim = inicio + tamanho_bloco

    # Slice the list
    vertices_pagina = lista_vertices[inicio:fim]

    if not vertices_pagina:
        return ""  # Returns empty if there is no data for this page

    # --- Generate HTML ---
    html = """
    <style>
    table { border-collapse: collapse; width: 100%; font-size: 9pt; font-family: Arial; }
    th { background-color: #ddd; border: 1px solid black; padding: 5px; }
    td { border: 1px solid black; padding: 4px; text-align: center; }
    </style>
    <table>
        <thead>
            <tr>
                <th>Point</th>
                <th>Ref</th>
                <th>Longitude (X)</th>
                <th>Latitude (Y)</th>
            </tr>
        </thead>
        <tbody>
    """

    for v in vertices_pagina:
        html += f"""
        <tr>
            <td>{v['id']}</td>
            <td>{v['ref']}</td>
            <td>{v['x']}</td>
            <td>{v['y']}</td>
        </tr>
        """

    html += "</tbody></table>"

    return html