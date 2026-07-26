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

# This will get replaced with a git SHA1 when you do a git archive
__revision__ = "$Format:%H$"

import re
from datetime import date, datetime

# ---------------------------------------------------------------------------
#   Satellite sensor properties dictionary
# ---------------------------------------------------------------------------
#   Pattern: regex string -> { 'name': ..., 'date_format': ..., 'source': ... }
# ---------------------------------------------------------------------------

SATELLITE_PROPERTIES = {
    # Landsat Family
    r"^LC09": {
        "name": "LandSat 9",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    r"^LC08": {
        "name": "LandSat 8",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    r"^LE07": {
        "name": "LandSat 7",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    r"^LT05": {
        "name": "LandSat 5",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    r"^LT04": {
        "name": "LandSat 4",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    r"^LM0[1-3]": {
        "name": "LandSat MSS (1-3)",
        "date_format": "YYYYMMDD",
        "source": "United States Geological Survey (USGS).",
    },
    # Sentinel Family (Copernicus)
    r"^S1[AB]": {
        "name": "Sentinel 1",
        "date_format": "YYYYMMDD",
        "source": "European Union's Earth Observation Programme (COPERNICUS).",
    },
    r"^S2[A-C]": {
        "name": "Sentinel 2",
        "date_format": "YYYYMMDD",
        "source": "European Union's Earth Observation Programme (COPERNICUS).",
    },
    r"^S3[AB]": {
        "name": "Sentinel 3",
        "date_format": "YYYYMMDD",
        "source": "European Union's Earth Observation Programme (COPERNICUS).",
    },
    r"^S5P": {
        "name": "Sentinel 5P",
        "date_format": "YYYYMMDD",
        "source": "European Union's Earth Observation Programme (COPERNICUS).",
    },
    # Pattern for individual bands
    r"^T\d{2}[A-Z]{3}": {
        "name": "Sentinel 2",
        "date_format": "YYYYMMDD",
        "source": "European Union's Earth Observation Programme (COPERNICUS).",
    },
    # NASA Satellites (EOS)
    r"^MOD|MYD": {
        "name": "MODIS",
        "date_format": "JULIAN_y_ddd",
        "source": "National Aeronautics and Space Administration (NASA).",
    },
    r"^A\d{7}\b": {
        "name": "MODIS",
        "date_format": "JULIAN_y_ddd",
        "source": "National Aeronautics and Space Administration (NASA).",
    },
    r"^(VNP|VJ\d{2})": {
        "name": "VIIRS",
        "date_format": "JULIAN_y_ddd",
        "source": "National Aeronautics and Space Administration (NASA).",
    },
    r"^AST_": {"name": "ASTER", "date_format": "MMDDYYYY", "source": "NASA/METI."},
    # Indian Remote Sensing Satellites (IRS)
    r"^L[34]_RS[12]|^AW_RS[12]": {
        "name": "Resourcesat",
        "date_format": "YYYYMMDD",
        "source": "Indian Space Research Organisation (ISRO).",
    },
    r"^C[123]_": {
        "name": "Cartosat",
        "date_format": "YYYYMMDD",
        "source": "Indian Space Research Organisation (ISRO).",
    },
    # Sino-Brazilian Satellite
    r"^CBERS": {
        "name": "CBERS",
        "date_format": "YYYYMMDD",
        "source": "Instituto Nacional de Pesquisas Espaciais (INPE) / China Academy of Space Technology (CAST).",
    },
    r"^CBERS[_-]?4A": {
        "name": "CBERS-4A",
        "date_format": "YYYYMMDD",
        "source": "Instituto Nacional de Pesquisas Espaciais (INPE) / China Academy of Space Technology (CAST).",
    },
    # High-Resolution Commercial Satellites
    r"WV0[1-4]|GE01": {
        "name": "Maxar/DigitalGlobe",
        "date_format": "DDMONYY",
        "source": "Maxar Technologies.",
    },
    r"^IK01": {
        "name": "IKONOS",
        "date_format": "YYYYMMDD",
        "source": "Maxar Technologies.",
    },
    r"^QB02": {
        "name": "QuickBird",
        "date_format": "YYYYMMDD",
        "source": "Maxar Technologies.",
    },
    # Planet
    r"PSScene": {
        "name": "PlanetScope",
        "date_format": "YYYYMMDD",
        "source": "Includes material \u00a9 (2025) Planet Labs Inc. All rights reserved.",
    },
    r"^SkySat": {
        "name": "SkySat",
        "date_format": "YYYYMMDD",
        "source": "Includes material \u00a9 (2025) Planet Labs Inc. All rights reserved.",
    },
    r"_psb_|_pss_": {
        "name": "PlanetScope",
        "date_format": "YYYYMMDD",
        "source": "Includes material \u00a9 (2025) Planet Labs Inc. All rights reserved.",
    },
}


# ---------------------------------------------------------------------------
#   RPA (drone) sensor properties dictionary
#
#   Naming convention:  RPA_<MODEL>_<SENSOR>_<YYYYMMDD>[_<optional suffix>]
#
#   Model codes
#   -----------
#   M2EA   DJI Mavic 2 Enterprise Advanced
#   M3E    DJI Mavic 3 Enterprise
#   M3T    DJI Mavic 3 Thermal (standalone thermal version)
#   M3M    DJI Mavic 3 Multispectral
#   P4MS   DJI Phantom 4 Multispectral
#   P4R    DJI Phantom 4 RTK
#   M300   DJI Matrice 300 RTK
#   M350   DJI Matrice 350 RTK
#   AGR    Generic agricultural drone (e.g. DJI Agras series)
#
#   Sensor codes
#   ------------
#   V   Visible / RGB
#   T   Thermal (thermal infrared)
#   M   Multispectral
#   L   LiDAR
#   H   Hyperspectral
#
#   Examples
#   --------
#   RPA_M2EA_V_20240315   Mavic 2 Enterprise Advanced - visible camera
#   RPA_M2EA_T_20240315   Mavic 2 Enterprise Advanced - thermal camera
#   RPA_M3M_M_20240315    Mavic 3 Multispectral - multispectral camera
#   RPA_M300_L_20240315   Matrice 300 RTK - LiDAR sensor
#   RPA_M350_H_20240315   Matrice 350 RTK - hyperspectral sensor
# ---------------------------------------------------------------------------

RPA_PROPERTIES = {
    # -- DJI Mavic 2 Enterprise Advanced --------------------------------------
    r"^RPA_M2EA_V": {
        "name": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 2 Enterprise Advanced,câmera RGB",
        "date_format": "YYYYMMDD",
        "source": "",
    },
    r"^RPA_M2EA_T": {
        "name": "DJI Mavic 2 Enterprise Advanced (Termal)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 2 Enterprise Advanced – Câmera Termal.",
    },
    # -- DJI Mavic 3 Enterprise ------------------------------------------------
    r"^RPA_M3E_V": {
        "name": "DJI Mavic 3 Enterprise (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Enterprise – Câmera RGB.",
    },
    r"^RPA_M3E_T": {
        "name": "DJI Mavic 3 Enterprise (Termal)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Enterprise – Câmera Termal.",
    },
    # -- DJI Mavic 3 Thermal ----------------------------------------------------
    r"^RPA_M3T_V": {
        "name": "DJI Mavic 3 Thermal (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Thermal – Câmera RGB.",
    },
    r"^RPA_M3T_T": {
        "name": "DJI Mavic 3 Thermal (Termal)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Thermal – Câmera Termal.",
    },
    # -- DJI Mavic 3 Multispectral ----------------------------------------------
    r"^RPA_M3M_V": {
        "name": "DJI Mavic 3 Multispectral (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Multispectral – Câmera RGB.",
    },
    r"^RPA_M3M_M": {
        "name": "DJI Mavic 3 Multispectral (Multiespectral)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Mavic 3 Multispectral – Câmera Multiespectral.",
    },
    # -- DJI Phantom 4 Multispectral ----------------------------------------------
    r"^RPA_P4MS_V": {
        "name": "DJI Phantom 4 Multispectral (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Phantom 4 Multispectral – Câmera RGB.",
    },
    r"^RPA_P4MS_M": {
        "name": "DJI Phantom 4 Multispectral (Multiespectral)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Phantom 4 Multispectral – Câmera Multiespectral.",
    },
    # -- DJI Phantom 4 RTK -----------------------------------------------------
    r"^RPA_P4R_V": {
        "name": "DJI Phantom 4 RTK (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Phantom 4 RTK – Câmera RGB.",
    },
    # -- DJI Matrice 300 RTK -----------------------------------------------------
    r"^RPA_M300_V": {
        "name": "DJI Matrice 300 RTK (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 300 RTK – Câmera RGB.",
    },
    r"^RPA_M300_T": {
        "name": "DJI Matrice 300 RTK (Termal)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 300 RTK – Câmera Termal.",
    },
    r"^RPA_M300_L": {
        "name": "DJI Matrice 300 RTK (LiDAR)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 300 RTK – Sensor LiDAR.",
    },
    r"^RPA_M300_H": {
        "name": "DJI Matrice 300 RTK (Hiperespectral)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 300 RTK – Sensor Hiperespectral.",
    },
    # -- DJI Matrice 350 RTK -----------------------------------------------------
    r"^RPA_M350_V": {
        "name": "DJI Matrice 350 RTK (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 350 RTK – Câmera RGB.",
    },
    r"^RPA_M350_T": {
        "name": "DJI Matrice 350 RTK (Termal)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 350 RTK – Câmera Termal.",
    },
    r"^RPA_M350_L": {
        "name": "DJI Matrice 350 RTK (LiDAR)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 350 RTK – Sensor LiDAR.",
    },
    r"^RPA_M350_H": {
        "name": "DJI Matrice 350 RTK (Hiperespectral)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "DJI Matrice 350 RTK – Sensor Hiperespectral.",
    },
    # -- Generic agricultural drone ------------------------------------------------
    r"^RPA_AGR_V": {
        "name": "Drone Agrícola (Visível)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "de uso agrícola – Câmera RGB.",
    },
    r"^RPA_AGR_M": {
        "name": "Drone Agrícola (Multiespectral)",
        "date_format": "YYYYMMDD",
        "source": "Imagem obtida por Aeronave Remotamente Pilotada (RPA) "
        "de uso agrícola – Câmera Multiespectral.",
    },
}


def get_satellite_logic(filename) -> dict:
    """
    Identifies the satellite from the filename and returns a dictionary of its properties.
    Kept for backwards compatibility. Use get_sensor_logic() for new code.
    """
    for pattern, properties in SATELLITE_PROPERTIES.items():
        if re.search(pattern, filename, re.IGNORECASE):
            return properties
    return None


def get_sensor_logic(filename) -> dict:
    """
    Identifies the sensor (satellite or RPA/drone) from the filename and returns
    a dictionary with 'name', 'source', and 'date_format'.

    RPA filenames are checked first (pattern: RPA_<MODEL>_<SENSOR>_<YYYYMMDD>).
    Falls back to SATELLITE_PROPERTIES for all other filenames.
    """
    for pattern, properties in RPA_PROPERTIES.items():
        if re.search(pattern, filename, re.IGNORECASE):
            return properties
    return get_satellite_logic(filename)


def get_image_date_logic(filename) -> date:
    """
    Extracts the acquisition date from the filename, returning a datetime.date.
    Works for both satellite and RPA filenames.
    """
    info = get_sensor_logic(filename)
    if not info:
        raise ValueError("Could not identify sensor to determine date format.")
    date_format = info["date_format"]

    if date_format == "YYYYMMDD":
        possible_dates_str = re.findall(r"\d{8}", filename)
        vals = []
        for s in possible_dates_str:
            try:
                vals.append(datetime.strptime(s, "%Y%m%d").date())
            except ValueError:
                pass
        if vals:
            return min(vals)

    elif date_format == "JULIAN_y_ddd":
        match = re.search(r"A?(\d{4})(\d{3})", filename, re.IGNORECASE)
        if match:
            year, day_of_year = match.groups()
            return datetime.strptime(f"{year}{day_of_year}", "%Y%j").date()

    elif date_format == "MMDDYYYY":
        possible_dates_str = re.findall(r"\d{8}", filename)
        vals = []
        for s in possible_dates_str:
            for fmt in ("%Y%m%d", "%m%d%Y"):
                try:
                    vals.append(datetime.strptime(s, fmt).date())
                except ValueError:
                    pass
        if vals:
            return min(vals)

    elif date_format == "DDMONYY":
        match = re.search(r"(\d{2}[A-Za-z]{3}\d{2})", filename)
        if match:
            return datetime.strptime(match.group(1).upper(), "%d%b%y").date()

    raise ValueError(
        f"Could not parse date from filename with expected format '{date_format}'."
    )
