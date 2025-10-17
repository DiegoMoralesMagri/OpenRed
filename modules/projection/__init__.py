#!/usr/bin/env python3
"""
🔮 OpenRed Network - Module Projection
Système de projection anti-copie révolutionnaire
"""

from .format_orn import FormatProjectionORN, GenerateurProjection, ReconstituteurProjection, GestionnaireProjections
from .protection import MoteurAntiCopie
from .interface import FenetreProjectionSecurisee

__all__ = [
    'FormatProjectionORN',
    'GenerateurProjection',
    'ReconstituteurProjection', 
    'GestionnaireProjections',
    'MoteurAntiCopie',
    'FenetreProjectionSecurisee'
]

__version__ = '1.0.0'
__author__ = 'OpenRed Network'
__description__ = 'Système de projection anti-copie révolutionnaire pour OpenRed Network'