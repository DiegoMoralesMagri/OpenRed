#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 Module Internet - OpenRed Network
Composants pour l'accès internet mondial
"""

from .passerelle_internet import (
    RegistryInternet,
    PasserelleInternet, 
    NavigateurWeb,
    installer_passerelle_internet
)

__all__ = [
    'RegistryInternet',
    'PasserelleInternet',
    'NavigateurWeb', 
    'installer_passerelle_internet'
]