#!/usr/bin/env python3
"""
Module d'extraction d'informations personnelles pour O-RedMind
==============================================================

Extrait et structure les informations personnelles des conversations
pour construire un vrai profil utilisateur persistant.

Auteur: Système OpenRed 2025
Licence: MIT - Souveraineté Numérique Totale
"""

import re
import json
import time
import logging
from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class PersonalInfo:
    """Information personnelle extraite"""
    category: str  # name, profession, preference, hobby, skill, dislike, etc.
    key: str       # "name", "job", "coffee", etc.
    value: str     # "Diego", "artiste", "n'aime pas", etc.
    confidence: float
    source_text: str
    timestamp: float

class PersonalInfoExtractor:
    """Extracteur d'informations personnelles avec système adaptatif intelligent"""
    
    def __init__(self):
        # PATTERNS PRÉDÉFINIS (FIABLES ET VÉRIFIÉS)
        self.patterns = {
            'name': [
                r"je m'appelle\s+(\w+)",
                r"mon nom est\s+(\w+)",
                r"je suis\s+(\w+)(?:\s|$|,|\.|!)",
                r"salut\s*!?\s*c'est\s+(\w+)(?:\s*!|\s*\.|$)",  # Spécifique aux présentations
            ],
            'profession': [
                r"je suis\s+(professeur|artiste|codeur|développeur|ingénieur|médecin|avocat|étudiant|retraité|entrepreneur)",
                r"je travaille\s+(?:comme|en tant que)?\s*(professeur|artiste|codeur|développeur|ingénieur|médecin|avocat)",
                r"mon métier\s+(?:est|c'est)\s+(professeur|artiste|codeur|développeur|ingénieur|médecin|avocat)",
                r"prof(?:esseur)?\s+(?:d'|de)\s*(\w+)",
                r"(?:dans\s+)?l'(informatique|enseignement|art|médecine|droit|ingénierie)",
            ],
            'preferences': [
                r"j'aime\s+(le|la|les)\s+(\w+)",
                r"j'adore\s+(le|la|les)\s+(\w+)", 
                r"je préfère\s+(le|la|les)\s+(\w+)",
                r"(?:il|elle|ils|elles)\s+aiment?\s+(?:le|la|les)?\s*(\w+)",
                r"(\w+)\s+aime\s+(?:le|la|les)?\s*(\w+)",
            ],
            'dislikes': [
                r"je n'aime pas\s+(le|la|les)\s+(\w+)",
                r"je déteste\s+(le|la|les)\s+(\w+)",
                r"je ne supporte pas\s+(le|la|les)\s+(\w+)",
            ],
            'color_preferences': [
                r"ma couleur préférée\s+(?:est|c'est)\s+(?:le|la)?\s*(\w+)",
                r"j'aime\s+(?:le|la)\s+(rouge|bleu|vert|jaune|noir|blanc|rose|violet|orange|gris)",
                r"je préfère\s+(?:le|la)\s+(rouge|bleu|vert|jaune|noir|blanc|rose|violet|orange|gris)",
            ],
            'family': [
                r"mes?\s+fils?\s+s'appellent?\s+([^.!?]+)",
                r"(?:l'aîné|premier|grand)\s+s'appelle\s+(\w+)",
                r"(?:le\s+)?(?:cadet|second|petit|jeune)\s+s'appelle\s+(\w+)",
                r"j'ai\s+(?:deux|trois|quatre)?\s+(?:fils|enfants?)\s*[:\s]*([^.!?]+)",
                r"(\w+)\s+et\s+(\w+)(?:\s|$|,|\.|!)",
            ],
            'projects': [
                r"créateur\s+(?:d'|de)\s*(\w+)",
                r"fondateur\s+(?:d'|de)\s*(\w+)",
                r"j'ai créé\s+(\w+)",
                r"mon projet\s+(\w+)",
            ],
            'skills': [
                r"je sais\s+(.*)",
                r"je maîtrise\s+(.*)",
                r"je code\s+en\s+(\w+)",
                r"j'utilise\s+(\w+)",
            ]
        }
        
        # SYSTÈME ADAPTATIF INTELLIGENT
        self.adaptive_patterns_file = Path.home() / ".openred" / "adaptive_patterns.json"
        self.candidate_patterns = self._load_candidate_patterns()
        self.validated_patterns = self._load_validated_patterns()
        self.pattern_usage_stats = self._load_pattern_stats()
        
        # CONFIGURATION D'APPRENTISSAGE
        self.validation_threshold = 3  # Minimum d'utilisations pour validation
        self.confidence_threshold = 0.7  # Seuil de confiance IA
        
        # Synonymes et normalisations
        self.profession_synonyms = {
            'prof': 'professeur',
            'dev': 'développeur',
            'développeur': 'développeur',
            'codeur': 'développeur',
            'informatique': 'informaticien',
            'arts plastiques': 'professeur d\'arts plastiques'
        }
    
    def _detect_user_objection(self, text: str) -> bool:
        """Détecte si l'utilisateur fait objection à une information précédente"""
        objection_patterns = [
            r"^non,?\s*",  # "Non, ..."
            r"ce n'est pas\s+(correct|bon|vrai|ça)",
            r"c'est\s+(faux|incorrect|une erreur)",
            r"tu te trompes",
            r"erreur\s*!",
            r"incorrect\s*!",
            r"pas\s+(correct|bon|vrai)",
            r"rectification\s*:",
            r"correction\s*:",
        ]
        
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in objection_patterns)
    
    def _handle_user_objection(self, text: str, previous_context: List[str] = None):
        """Gère l'objection utilisateur avec analyse sophistiquée du type d'erreur"""
        # À améliorer ! - Système de distinction pattern vs valeur
        objection_analysis = self._analyze_objection_type(text, previous_context)
        
        current_time = time.time()
        recent_threshold = 300  # 5 minutes
        
        if objection_analysis['type'] == 'pattern_error':
            # ERREUR DE PATTERN : invalider le pattern défaillant
            logger.warning("🚫 Objection de PATTERN détectée - invalidation du pattern")
            for pattern_id, pattern_data in self.candidate_patterns.items():
                if current_time - pattern_data.get('discovered_at', 0) < recent_threshold:
                    pattern_data['confidence'] *= 0.1  # Invalidation forte
                    pattern_data['pattern_error'] = True  # À améliorer ! - Marquer comme défaillant
                    logger.warning(f"❌ Pattern défaillant invalidé: {pattern_id}")
                    
        elif objection_analysis['type'] == 'value_correction':
            # ERREUR DE VALEUR : garder le pattern, noter la correction
            logger.info("🔄 Objection de VALEUR détectée - correction de données")
            for pattern_id, pattern_data in self.candidate_patterns.items():
                if current_time - pattern_data.get('discovered_at', 0) < recent_threshold:
                    # À améliorer ! - Ne pas pénaliser le pattern, juste noter la correction
                    pattern_data['value_corrections'] = pattern_data.get('value_corrections', 0) + 1
                    logger.info(f"📝 Correction de valeur notée pour: {pattern_id}")
        else:
            # OBJECTION GÉNÉRALE : traitement conservateur
            for pattern_id, pattern_data in self.candidate_patterns.items():
                if current_time - pattern_data.get('discovered_at', 0) < recent_threshold:
                    pattern_data['confidence'] *= 0.5  # Réduction modérée
                    logger.warning(f"⚠️ Pattern suspecté après objection: {pattern_id}")
        
        self._save_adaptive_patterns()
        
    def _analyze_objection_type(self, objection_text: str, previous_context: List[str] = None) -> Dict:
        """
        À améliorer ! - Analyse sophistiquée du type d'objection
        Distingue entre erreur de pattern et erreur de valeur
        """
        text_lower = objection_text.lower()
        
        # INDICATEURS D'ERREUR DE VALEUR (pattern bon, valeur fausse)
        value_error_indicators = [
            r"pas\s+(\w+),?\s+(mais|plutôt|c'est)\s+(\w+)",  # "pas Bubulle, mais Cali"
            r"ne.*pas\s+(\w+),?\s+(c'est|plutôt)\s+(\w+)",   # "ne s'appelle pas Bubulle, c'est Cali"
            r"s'appelle\s+(\w+),?\s+pas\s+(\w+)",            # "s'appelle Cali, pas Bubulle"
            r"en fait.*s'appelle\s+(\w+)",                   # "en fait il s'appelle Cali"
            r"correction.*(\w+)",                            # "correction: Cali"
        ]
        
        # INDICATEURS D'ERREUR DE PATTERN (structure défaillante)
        pattern_error_indicators = [
            r"ce n'est pas mon (nom|métier|job)",            # "ce n'est pas mon nom"
            r"tu te trompes complètement",                   # Erreur totale
            r"ça n'a aucun sens",                            # Pattern absurde
            r"(mon|ma|mes)\s+n'est pas",                     # "Mon n'est pas..."
            r"mauvaise extraction",                          # Extraction défaillante
            r"pattern incorrect",                            # À améliorer ! - Feedback technique
        ]
        
        # Analyse des indicateurs
        for pattern in value_error_indicators:
            if re.search(pattern, text_lower):
                return {
                    'type': 'value_correction',
                    'confidence': 0.8,
                    'suggested_action': 'update_value_keep_pattern'
                }
        
        for pattern in pattern_error_indicators:
            if re.search(pattern, text_lower):
                return {
                    'type': 'pattern_error', 
                    'confidence': 0.9,
                    'suggested_action': 'invalidate_pattern'
                }
        
        # À améliorer ! - Analyse contextuelle plus poussée
        # Analyser les extractions récentes pour déterminer le type d'erreur
        
        return {
            'type': 'general_objection',
            'confidence': 0.5,
            'suggested_action': 'moderate_penalty'
        }
    
    def _extract_multiple_animals(self, text: str, text_lower: str) -> List[PersonalInfo]:
        """Extrait plusieurs animaux depuis une phrase de correction"""
        extracted = []
        
        # Pattern spécifique pour la correction d'animaux
        # "Non, mon chat s'appelle Cali, c'est mon poisson qui s'appelle Bubulle, et mon chien s'appelle Laïka !"
        animal_correction_pattern = r"mon\s+(chat|chien|poisson|oiseau|lapin|hamster)\s+s'appelle\s+(\w+)"
        
        # Pattern pour "c'est mon X qui s'appelle Y"
        animal_correction_pattern2 = r"c'est\s+mon\s+(chat|chien|poisson|oiseau|lapin|hamster)\s+qui\s+s'appelle\s+(\w+)"
        
        # Premier pattern
        matches = re.finditer(animal_correction_pattern, text_lower)
        for match in matches:
            animal_type = match.group(1)
            animal_name = match.group(2)
            
            info = PersonalInfo(
                category='family',
                key=f'nom_du_{animal_type}',
                value=animal_name,
                confidence=0.95,  # Haute confiance pour les corrections explicites
                source_text=text,
                timestamp=time.time()
            )
            extracted.append(info)
            logger.info(f"🐾 Animal extrait: {animal_type} = {animal_name}")
        
        # Deuxième pattern pour "c'est mon X qui s'appelle Y"
        matches2 = re.finditer(animal_correction_pattern2, text_lower)
        for match in matches2:
            animal_type = match.group(1)
            animal_name = match.group(2)
            
            info = PersonalInfo(
                category='family',
                key=f'nom_du_{animal_type}',
                value=animal_name,
                confidence=0.95,
                source_text=text,
                timestamp=time.time()
            )
            extracted.append(info)
            logger.info(f"🐾 Animal extrait (pattern 2): {animal_type} = {animal_name}")
        
        return extracted
    
    def _extract_corrected_values(self, text: str, objection_analysis: Dict) -> List[PersonalInfo]:
        """
        À améliorer ! - Extrait les valeurs corrigées depuis une objection de valeur
        Exemple: "Non, mon chat s'appelle Cali, pas Bubulle"
        """
        extracted = []
        text_lower = text.lower()
        
        # Patterns de correction de valeur
        correction_patterns = [
            r"mon\s+(chat|chien|poisson|oiseau)\s+s'appelle\s+(\w+),?\s+pas\s+(\w+)",  # "mon chat s'appelle Cali, pas Bubulle"
            r"pas\s+(\w+),?\s+(mais|plutôt|c'est)\s+(\w+)",                          # "pas Bubulle, mais Cali"  
            r"en fait,?\s+(?:il|elle|mon\s+\w+)\s+s'appelle\s+(\w+)",                # "en fait, il s'appelle Cali"
            r"correction\s*:\s*(\w+)",                                                # "correction: Cali"
        ]
        
        for pattern in correction_patterns:
            matches = re.finditer(pattern, text_lower)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 2:
                    # À améliorer ! - Logique plus sophistiquée selon le pattern
                    if 'chat' in match.group(0):
                        category = 'family'
                        key = 'nom_du_chat'
                        value = groups[-1]  # Dernière capture = valeur correcte
                    elif 'chien' in match.group(0):
                        category = 'family' 
                        key = 'nom_du_chien'
                        value = groups[-1]
                    else:
                        # Pattern générique
                        category = 'identity'
                        key = 'corrected_value'
                        value = groups[-1]
                    
                    info = PersonalInfo(
                        category=category,
                        key=key,
                        value=value,
                        confidence=0.95,  # Haute confiance pour corrections explicites
                        source_text=text,
                        timestamp=time.time()
                    )
                    extracted.append(info)
                    logger.info(f"🔄 Valeur corrigée extraite: {key} = {value}")
        
        return extracted
    
    def _load_candidate_patterns(self) -> Dict:
        """Charge les patterns candidats depuis le fichier"""
        try:
            if self.adaptive_patterns_file.exists():
                with open(self.adaptive_patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('candidate_patterns', {})
        except Exception as e:
            logger.warning(f"Erreur chargement patterns candidats: {e}")
        return {}
    
    def _load_validated_patterns(self) -> Dict:
        """Charge les patterns validés depuis le fichier"""
        try:
            if self.adaptive_patterns_file.exists():
                with open(self.adaptive_patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('validated_patterns', {})
        except Exception as e:
            logger.warning(f"Erreur chargement patterns validés: {e}")
        return {}
    
    def _load_pattern_stats(self) -> Dict:
        """Charge les statistiques d'usage des patterns"""
        try:
            if self.adaptive_patterns_file.exists():
                with open(self.adaptive_patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('usage_stats', {})
        except Exception as e:
            logger.warning(f"Erreur chargement statistiques: {e}")
        return {}
    
    def _save_adaptive_patterns(self):
        """Sauvegarde tous les patterns adaptatifs"""
        try:
            self.adaptive_patterns_file.parent.mkdir(exist_ok=True, parents=True)
            data = {
                'candidate_patterns': self.candidate_patterns,
                'validated_patterns': self.validated_patterns,
                'usage_stats': self.pattern_usage_stats,
                'last_updated': time.time()
            }
            with open(self.adaptive_patterns_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Erreur sauvegarde patterns adaptatifs: {e}")
    
    def extract_personal_info(self, text: str, previous_context: List[str] = None) -> List[PersonalInfo]:
        """EXTRACTION INTELLIGENTE EN 4 PHASES"""
        extracted_info = []
        text_lower = text.lower()
        
        # PHASE 0 : DÉTECTION D'OBJECTION ET CORRECTION
        if self._detect_user_objection(text):
            logger.info("🚫 Objection utilisateur détectée - analyse sophistiquée")
            # À améliorer ! - Analyse sophistiquée du type d'objection
            objection_analysis = self._analyze_objection_type(text, previous_context)
            self._handle_user_objection(text, previous_context)
            
            # Si c'est une correction de valeur, extraire les nouvelles valeurs
            if objection_analysis['type'] == 'value_correction':
                corrected_values = self._extract_corrected_values(text, objection_analysis)
                if corrected_values:
                    extracted_info.extend(corrected_values)
                    logger.info(f"🔄 {len(corrected_values)} valeurs corrigées extraites")
            
            # Continuer l'extraction pour les nouvelles informations correctes
        
        # PHASE 0.5 : EXTRACTION MULTI-INFORMATIONS DANS UNE PHRASE
        multi_extractions = self._extract_multiple_animals(text, text_lower)
        if multi_extractions:
            extracted_info.extend(multi_extractions)
            return extracted_info
        
        # PHASE 1 : PATTERNS PRÉDÉFINIS (FIABLES)
        logger.info("🔍 Phase 1 : Extraction avec patterns prédéfinis")
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                try:
                    matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                    for match in matches:
                        info = self._process_match(category, match, text, text_lower)
                        if info:
                            extracted_info.append(info)
                            logger.info(f"✅ Pattern prédéfini trouvé: {category} - {info.key} = {info.value}")
                except Exception as e:
                    logger.warning(f"Erreur pattern prédéfini {category}: {e}")
        
        # PHASE 2 : PATTERNS VALIDÉS (PROMUS)
        if self.validated_patterns:
            logger.info("🔍 Phase 2 : Extraction avec patterns validés")
            for pattern_id, pattern_data in self.validated_patterns.items():
                try:
                    pattern = pattern_data['pattern']
                    category = pattern_data['category']
                    matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                    for match in matches:
                        info = self._process_validated_pattern(pattern_data, match, text)
                        if info:
                            extracted_info.append(info)
                            self._update_pattern_usage(pattern_id, True)
                            logger.info(f"✅ Pattern validé utilisé: {pattern_id}")
                except Exception as e:
                    logger.warning(f"Erreur pattern validé {pattern_id}: {e}")
        
        # PHASE 3 : PATTERNS CANDIDATS (EN TEST)
        if self.candidate_patterns and not extracted_info:
            logger.info("🔍 Phase 3 : Test patterns candidats")
            for pattern_id, pattern_data in self.candidate_patterns.items():
                try:
                    pattern = pattern_data['pattern']
                    matches = re.finditer(pattern, text_lower, re.IGNORECASE)
                    for match in matches:
                        info = self._process_candidate_pattern(pattern_data, match, text)
                        if info:
                            extracted_info.append(info)
                            self._update_pattern_usage(pattern_id, True)
                            logger.info(f"🧪 Pattern candidat utilisé: {pattern_id}")
                except Exception as e:
                    logger.warning(f"Erreur pattern candidat {pattern_id}: {e}")
        
        # PHASE 4 : IA PATTERN DISCOVERY (INNOVATION)
        if not extracted_info and self._should_try_ai_discovery(text):
            logger.info("🤖 Phase 4 : Découverte IA de nouveaux patterns")
            ai_discovered = self._ai_pattern_discovery(text, text_lower)
            extracted_info.extend(ai_discovered)
        
        # PROMOTION AUTOMATIQUE DES PATTERNS VALIDÉS
        self._check_pattern_promotion()
        
        return extracted_info
    
    def _should_try_ai_discovery(self, text: str) -> bool:
        """Détermine si l'IA doit essayer de découvrir de nouveaux patterns"""
        # Indicateurs qu'il pourrait y avoir des infos personnelles
        personal_indicators = [
            'mon', 'ma', 'mes', 'j\'ai', 'je suis', 'j\'aime', 'je déteste',
            'nous avons', 'notre', 'chez nous', 'à la maison',
            'préféré', 'favori', 'habitude', 'routine'
        ]
        
        # Le texte doit contenir au moins un indicateur personnel
        return any(indicator in text.lower() for indicator in personal_indicators)
    
    def _ai_pattern_discovery(self, text: str, text_lower: str) -> List[PersonalInfo]:
        """Utilise l'IA pour découvrir de nouveaux patterns informationnels"""
        try:
            # Import local pour éviter la dépendance circulaire
            from ollama_integration import OllamaIntegration
            
            ollama = OllamaIntegration()
            if not ollama.is_connected:
                return []
            
            # S'assurer qu'un modèle est sélectionné
            if not ollama.current_model:
                if not ollama.set_model('mistral:latest'):
                    logger.warning("Impossible de sélectionner un modèle Ollama")
                    return []
            
            # Prompt pour analyse structurelle
            analysis_prompt = f"""
            Analyse ce texte et identifie s'il contient des informations personnelles structurées :
            
            TEXTE: "{text}"
            
            Si tu détectes une information personnelle (nom, préférence, famille, loisir, travail, etc.), 
            réponds UNIQUEMENT au format JSON suivant :
            {{
                "has_info": true,
                "category": "preferences|family|identity|profession|skills|location|other",
                "key": "nom_de_la_propriété",
                "value": "valeur_extraite",
                "confidence": 0.8,
                "pattern_suggestion": "pattern_regex_suggéré"
            }}
            
            Si aucune information personnelle, réponds : {{"has_info": false}}
            
            IMPORTANT: Réponds UNIQUEMENT en JSON, rien d'autre.
            """
            
            response = ""
            for chunk in ollama.chat(analysis_prompt, max_tokens=200, temperature=0.1):
                response += chunk
            
            if response and response.strip():
                try:
                    analysis = json.loads(response.strip())
                    
                    if analysis.get('has_info', False):
                        # Valider et créer un pattern candidat
                        return self._create_candidate_pattern_from_ai(analysis, text)
                        
                except json.JSONDecodeError:
                    logger.warning(f"Réponse IA non-JSON: {response[:100]}")
            
        except Exception as e:
            logger.warning(f"Erreur découverte IA: {e}")
        
        return []
    
    def _create_candidate_pattern_from_ai(self, analysis: Dict, original_text: str) -> List[PersonalInfo]:
        """Crée un pattern candidat basé sur l'analyse IA"""
        try:
            category = analysis['category']
            key = analysis['key']
            value = analysis['value']
            confidence = analysis.get('confidence', 0.7)
            suggested_pattern = analysis.get('pattern_suggestion', '')
            
            # Validation de la pertinence
            if confidence < self.confidence_threshold:
                return []
            
            # Créer l'information extraite
            info = PersonalInfo(
                category=category,
                key=key,
                value=value,
                confidence=confidence,
                source_text=original_text,
                timestamp=time.time()
            )
            
            # Enregistrer comme pattern candidat si un pattern est suggéré
            if suggested_pattern and len(suggested_pattern) > 5:
                pattern_id = f"ai_discovered_{int(time.time())}"
                
                self.candidate_patterns[pattern_id] = {
                    'pattern': suggested_pattern,
                    'category': category,
                    'key_template': key,
                    'discovered_at': time.time(),
                    'usage_count': 1,
                    'success_count': 1,
                    'original_text': original_text,
                    'confidence': confidence
                }
                
                self._save_adaptive_patterns()
                logger.info(f"🧠 Nouveau pattern candidat créé: {pattern_id}")
            
            return [info]
            
        except Exception as e:
            logger.error(f"Erreur création pattern candidat: {e}")
            return []
    
    def _process_validated_pattern(self, pattern_data: Dict, match: re.Match, original_text: str) -> Optional[PersonalInfo]:
        """Traite un match avec un pattern validé"""
        try:
            category = pattern_data['category']
            key_template = pattern_data['key_template']
            
            groups = match.groups()
            if groups:
                value = groups[0] if len(groups) == 1 else groups[-1]  # Prendre la dernière capture
                
                return PersonalInfo(
                    category=category,
                    key=key_template,
                    value=value.strip(),
                    confidence=0.85,  # Confiance élevée pour patterns validés
                    source_text=original_text,
                    timestamp=time.time()
                )
        except Exception as e:
            logger.warning(f"Erreur traitement pattern validé: {e}")
        
        return None
    
    def _process_candidate_pattern(self, pattern_data: Dict, match: re.Match, original_text: str) -> Optional[PersonalInfo]:
        """Traite un match avec un pattern candidat"""
        try:
            category = pattern_data['category']
            key_template = pattern_data['key_template']
            
            groups = match.groups()
            if groups:
                value = groups[0] if len(groups) == 1 else groups[-1]
                
                return PersonalInfo(
                    category=category,
                    key=key_template,
                    value=value.strip(),
                    confidence=0.75,  # Confiance moyenne pour patterns candidats
                    source_text=original_text,
                    timestamp=time.time()
                )
        except Exception as e:
            logger.warning(f"Erreur traitement pattern candidat: {e}")
        
        return None
    
    def _update_pattern_usage(self, pattern_id: str, success: bool):
        """Met à jour les statistiques d'usage d'un pattern"""
        if pattern_id not in self.pattern_usage_stats:
            self.pattern_usage_stats[pattern_id] = {
                'total_usage': 0,
                'success_count': 0,
                'last_used': time.time()
            }
        
        self.pattern_usage_stats[pattern_id]['total_usage'] += 1
        if success:
            self.pattern_usage_stats[pattern_id]['success_count'] += 1
        self.pattern_usage_stats[pattern_id]['last_used'] = time.time()
        
        self._save_adaptive_patterns()
    
    def _check_pattern_promotion(self):
        """Vérifie et promeut les patterns candidats vers patterns validés"""
        patterns_to_promote = []
        patterns_to_remove = []
        
        for pattern_id, pattern_data in self.candidate_patterns.items():
            usage_stats = self.pattern_usage_stats.get(pattern_id, {})
            total_usage = usage_stats.get('total_usage', 0)
            success_count = usage_stats.get('success_count', 0)
            
            # Critères de promotion
            if total_usage >= self.validation_threshold and success_count / total_usage >= 0.8:
                patterns_to_promote.append(pattern_id)
                logger.info(f"🎯 Pattern candidat promu: {pattern_id}")
            
            # Critères de suppression (trop d'échecs)
            elif total_usage >= 5 and success_count / total_usage < 0.3:
                patterns_to_remove.append(pattern_id)
                logger.info(f"🗑️ Pattern candidat supprimé: {pattern_id}")
        
        # Effectuer les promotions
        for pattern_id in patterns_to_promote:
            self.validated_patterns[pattern_id] = self.candidate_patterns[pattern_id]
            del self.candidate_patterns[pattern_id]
        
        # Effectuer les suppressions
        for pattern_id in patterns_to_remove:
            del self.candidate_patterns[pattern_id]
            if pattern_id in self.pattern_usage_stats:
                del self.pattern_usage_stats[pattern_id]
        
        if patterns_to_promote or patterns_to_remove:
            self._save_adaptive_patterns()
    
    def detect_user_objection(self, user_message: str) -> List[str]:
        """Détecte les objections utilisateur à des informations précédemment extraites"""
        objection_patterns = [
            r"(?:ce n'est pas|c'est faux|non,?\s*|erreur|incorrect|mauvais)",
            r"(?:oublie|supprime|efface)\s+(?:ça|cela|cette?\s+info)",
            r"(?:je n'ai jamais dit|tu te trompes|c'est une erreur)",
            r"(?:rectification|correction)\s*:",
            r"(?:en fait|en réalité|plutôt),?\s+",
        ]
        
        objections_found = []
        user_lower = user_message.lower()
        
        for pattern in objection_patterns:
            if re.search(pattern, user_lower):
                objections_found.append(pattern)
        
        return objections_found
    
    def invalidate_recent_patterns(self, user_message: str):
        """Invalide les patterns récents si l'utilisateur fait objection"""
        objections = self.detect_user_objection(user_message)
        
        if objections:
            # Marquer les patterns récents comme suspects
            current_time = time.time()
            recent_threshold = 300  # 5 minutes
            
            for pattern_id, pattern_data in self.candidate_patterns.items():
                if current_time - pattern_data.get('discovered_at', 0) < recent_threshold:
                    # Réduire la confiance du pattern
                    pattern_data['confidence'] *= 0.5
                    logger.warning(f"⚠️ Pattern suspect après objection: {pattern_id}")
            
            self._save_adaptive_patterns()
            logger.info(f"🚫 Objection utilisateur détectée: {len(objections)} patterns invalidés")
    
    def get_adaptive_stats(self) -> Dict:
        """Retourne les statistiques du système adaptatif"""
        return {
            'candidate_patterns_count': len(self.candidate_patterns),
            'validated_patterns_count': len(self.validated_patterns),
            'total_usage_stats': len(self.pattern_usage_stats),
            'patterns_ready_for_promotion': len([
                p for p, data in self.candidate_patterns.items()
                if self.pattern_usage_stats.get(p, {}).get('total_usage', 0) >= self.validation_threshold
            ])
        }
    
    def _adaptive_extraction(self, text: str, text_lower: str) -> List[PersonalInfo]:
        """Extraction adaptative avec apprentissage automatique de patterns"""
        extracted = []
        
        # PATTERNS D'APPRENTISSAGE AUTOMATIQUE
        learning_patterns = [
            # Pattern: "mon/ma/mes [chose] est/sont [valeur]"
            r"mon?\s+(\w+)\s+(?:est|c'est|sont)\s+([^.!?]+)",
            r"ma\s+(\w+)\s+(?:est|c'est)\s+([^.!?]+)",
            r"mes\s+(\w+)\s+(?:sont|c'est)\s+([^.!?]+)",
            
            # Pattern: "j'ai [nombre/quantité] [chose]"
            r"j'ai\s+(?:un|une|deux|trois|quatre|cinq|plusieurs|beaucoup)?\s*([^.!?]+)",
            
            # Pattern: "je [verbe] [complément]"
            r"je\s+(possède|collectionne|pratique|étudie|enseigne|utilise)\s+([^.!?]+)",
            
            # Pattern: "[chose] s'appelle/se nomme [nom]"
            r"(\w+)\s+s'appelle\s+(\w+)",
            r"(\w+)\s+se nomme\s+(\w+)",
            
            # Pattern: "il y a [quantité] [chose] [complément]"
            r"il y a\s+(\w+)\s+([^.!?]+)",
            
            # Pattern: Questions et réponses automatiques
            r"(?:te souviens-tu|tu sais)\s+(?:de|que|si)?\s*([^?]+)\?",
        ]
        
        for pattern in learning_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                info = self._process_adaptive_match(match, text, text_lower)
                if info:
                    extracted.append(info)
        
        # DÉTECTION INTELLIGENTE DE CLÉS-VALEURS
        kv_info = self._extract_key_value_pairs(text, text_lower)
        extracted.extend(kv_info)
        
        return extracted
    
    def _process_adaptive_match(self, match: re.Match, original_text: str, text_lower: str) -> Optional[PersonalInfo]:
        """Traite un match adaptatif et détermine automatiquement la catégorie"""
        try:
            groups = match.groups()
            if len(groups) >= 2:
                key = groups[0].strip()
                value = groups[1].strip()
                
                # VALIDATION PRÉALABLE
                if not self._is_relevant_info(key, value, original_text):
                    return None
                
                # CLASSIFICATION AUTOMATIQUE DE LA CATÉGORIE
                category = self._classify_information(key, value, original_text)
                
                # Si la classification renvoie None, rejeter l'information
                if category is None:
                    return None
                
                # NETTOYAGE ET VALIDATION
                key_clean = self._clean_key(key)
                value_clean = self._clean_value(value)
                
                if key_clean and value_clean and len(value_clean) > 2:
                    return PersonalInfo(
                        category=category,
                        key=key_clean,
                        value=value_clean,
                        confidence=0.7,  # Confiance moyenne pour apprentissage adaptatif
                        source_text=original_text,
                        timestamp=time.time()
                    )
        except Exception as e:
            logger.warning(f"Erreur traitement adaptatif: {e}")
        
        return None
    
    def _classify_information(self, key: str, value: str, text: str) -> str:
        """Classifie automatiquement une information en catégorie avec validation stricte"""
        key_lower = key.lower().strip()
        value_lower = value.lower().strip()
        text_lower = text.lower()
        
        # VALIDATION PRÉALABLE - Rejeter les non-informations
        invalid_patterns = [
            r'^(l|qu|d|t|j|m|s|n|c)\'',  # Contractions
            r'^(ai|as|est|ont|suis|sont|avec|pour|par|dans|sur)$',  # Mots grammaticaux
            r'^(aîné|jeune|fils|enfant|père|mère)$',  # Termes relationnels non-informationnels
        ]
        
        for pattern in invalid_patterns:
            if re.match(pattern, key_lower) or re.match(pattern, value_lower):
                return None  # Rejeter cette information
        
        # CLASSIFICATION PAR MOTS-CLÉS PRÉCIS
        if any(word in key_lower for word in ['nom', 'prénom', 'appelle', 'name']) and any(indicator in text_lower for indicator in ['je m\'appelle', 'je suis', 'mon nom']):
            return 'identity'
        
        if any(word in key_lower for word in ['métier', 'travail', 'profession', 'job']) and any(indicator in text_lower for indicator in ['professeur', 'développeur', 'travaille', 'enseigne']):
            return 'profession'
        
        if 'couleur' in key_lower and 'préféré' in text_lower:
            return 'preferences'
        
        if any(word in key_lower for word in ['fils', 'fille', 'enfant']) and any(indicator in text_lower for indicator in ['s\'appelle', 'se nomme', 'mes enfants', 'mes fils']):
            return 'family'
        
        if any(word in value_lower for word in ['openred', 'oredmind']) or ('créé' in text_lower and 'projet' in text_lower):
            return 'projects'
        
        # CLASSIFICATION PAR CONTEXTE STRICT
        if ('aime' in text_lower or 'préfère' in text_lower) and ('dessiner' in value_lower or 'noir' in value_lower):
            return 'preferences'
        
        # REJET SI AUCUNE CATÉGORIE PRÉCISE
        return None
    
    def _extract_key_value_pairs(self, text: str, text_lower: str) -> List[PersonalInfo]:
        """Extraction intelligente de paires clé-valeur sans patterns prédéfinis"""
        extracted = []
        
        # DÉTECTION DE STRUCTURES INFORMATIONNELLES
        info_patterns = [
            # "Information: valeur"
            r"(\w+)\s*:\s*([^.!?\n]+)",
            
            # "C'est [valeur] mon [clé]"
            r"c'est\s+([^,]+),?\s+mon?\s+(\w+)",
            
            # "Mon [clé], c'est [valeur]"
            r"mon?\s+(\w+),?\s+c'est\s+([^.!?]+)",
            
            # Phrases déclaratives
            r"(\w+(?:\s+\w+)?)\s+(?:est|sont|était|sera)\s+([^.!?]+)",
        ]
        
        for pattern in info_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) == 2:
                    key, value = groups
                    
                    # Validation de pertinence
                    if self._is_relevant_info(key, value, text):
                        category = self._classify_information(key, value, text)
                        
                        extracted.append(PersonalInfo(
                            category=category,
                            key=self._clean_key(key),
                            value=self._clean_value(value),
                            confidence=0.6,  # Confiance plus faible pour extraction libre
                            source_text=text,
                            timestamp=time.time()
                        ))
        
        return extracted
    
    def _is_relevant_info(self, key: str, value: str, text: str) -> bool:
        """Détermine si une paire clé-valeur est pertinente à stocker"""
        key_lower = key.lower().strip()
        value_lower = value.lower().strip()
        
        # Mots à ignorer (considérablement élargi)
        ignore_keys = {
            # Articles et mots grammaticaux
            'qui', 'que', 'quoi', 'comment', 'pourquoi', 'où', 'quand', 
            'le', 'la', 'les', 'un', 'une', 'des', 'du', 'de', 'et', 'ou',
            'avec', 'sans', 'pour', 'par', 'dans', 'sur', 'sous', 'chez',
            'aîné', 'jeune', 'fils', 'enfant', 'père', 'mère', 'parent',
            # Expressions courantes non-informationnelles
            'ai', 'as', 'est', 'suis', 'sont', 'ont', 'peut', 'dois', 'veux',
            'dire', 'faire', 'voir', 'savoir', 'depuis', 'alors', 'donc',
            'bien', 'mal', 'très', 'trop', 'assez', 'plutôt', 'encore',
            'déjà', 'jamais', 'toujours', 'souvent', 'parfois'
        }
        
        ignore_values = {
            'oui', 'non', 'peut-être', 'je', 'tu', 'il', 'elle', 'nous', 'vous', 'ils', 'elles',
            'ai', 'as', 'est', 'suis', 'sont', 'ont', 'avec', 'sans', 'pour', 'par',
            'dit', 'déjà', 'dit qu', 'aime', 'dessiner', 'oublié', 'bien-sûr', 'esteban'
        }
        
        # Filtrage strict
        if key_lower in ignore_keys or value_lower in ignore_values:
            return False
        
        # Longueur minimale plus stricte
        if len(key_lower) < 4 or len(value_lower) < 3:
            return False
        
        # Éviter les patterns grammaticaux non-informationnels
        non_info_patterns = [
            r'^(l|qu|d|t|j|m|s|n)\'',  # Contractions
            r'^\w{1,2}$',  # Mots trop courts
            r'^(ai|as|est|ont|suis|sont)$',  # Verbes être/avoir
        ]
        
        for pattern in non_info_patterns:
            if re.match(pattern, key_lower) or re.match(pattern, value_lower):
                return False
        
        # Doit contenir des indicateurs personnels CONCRETS
        personal_indicators = [
            'mon nom', 'je m\'appelle', 'je suis', 'ma couleur', 'préféré', 
            'j\'aime', 'j\'adore', 'je déteste', 'mes enfants', 'mes fils',
            'ma profession', 'mon métier', 'j\'enseigne', 'je travaille',
            'j\'ai créé', 'mon projet', 'ma création'
        ]
        
        return any(indicator in text.lower() for indicator in personal_indicators)
    
    def _clean_key(self, key: str) -> str:
        """Nettoie et normalise une clé"""
        key = key.strip().lower()
        key = re.sub(r'^(mon|ma|mes|le|la|les)\s+', '', key)
        return key
    
    def _clean_value(self, value: str) -> str:
        """Nettoie et normalise une valeur"""
        value = value.strip()
        value = re.sub(r'\s+', ' ', value)  # Espaces multiples
        return value
    
    def _process_match(self, category: str, match: re.Match, original_text: str, text_lower: str) -> Optional[PersonalInfo]:
        """Traite une correspondance trouvée"""
        try:
            if category == 'name':
                name = match.group(1).capitalize()
                # Filtrage des faux positifs
                invalid_names = {'avec', 'pour', 'sans', 'dans', 'sur', 'chez', 'vers', 'contre'}
                if name.lower() in invalid_names or len(name) < 3:
                    return None
                    
                return PersonalInfo(
                    category='identity',
                    key='name',
                    value=name,
                    confidence=0.9,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'profession':
                profession = match.group(1).lower()
                # Normalisation
                profession = self.profession_synonyms.get(profession, profession)
                return PersonalInfo(
                    category='profession',
                    key='job',
                    value=profession,
                    confidence=0.8,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'preferences':
                groups = match.groups()
                # Gestion des différents patterns de préférences
                if len(groups) >= 2:  # Pattern standard "j'aime le/la [chose]" ou "[nom] aime [chose]"
                    if groups[0] and groups[1]:  # Pattern "[nom] aime [chose]"
                        person = groups[0].capitalize()
                        activity = groups[1]
                        key = f"{person.lower()}_aime"
                        value = activity
                    else:  # Pattern standard "j'aime le/la [chose]"
                        key = groups[1] if groups[1] else groups[0]
                        value = 'aime'
                elif len(groups) == 1:  # Pattern "ils aiment [chose]"
                    key = 'preference_commune'
                    value = groups[0]
                else:
                    return None
                
                return PersonalInfo(
                    category='preferences',
                    key=key,
                    value=value,
                    confidence=0.7,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'dislikes':
                item = match.group(2)
                return PersonalInfo(
                    category='preference',
                    key=item,
                    value='n\'aime pas',
                    confidence=0.8,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'color_preferences':
                color = match.group(1).lower()
                return PersonalInfo(
                    category='preferences',
                    key='couleur_preferee',
                    value=color,
                    confidence=0.9,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'family':
                # Traitement spécial pour les noms d'enfants
                if len(match.groups()) == 2:  # Pattern "Esteban et Gabriel"
                    results = []
                    for name in match.groups():
                        if name and len(name) > 2 and name.capitalize() not in {'Et', 'Ou', 'Avec'}:
                            results.append(PersonalInfo(
                                category='family',
                                key='enfant',
                                value=name.capitalize(),
                                confidence=0.85,
                                source_text=original_text,
                                timestamp=time.time()
                            ))
                    return results[0] if results else None  # Retourne le premier, les autres seront traités
                else:
                    # Extraction de noms multiples dans une phrase
                    names_text = match.group(1)
                    names = re.findall(r'\b[A-Z][a-z]{2,}\b', names_text)
                    if not names:  # Si pas de majuscules, chercher des mots
                        potential_names = re.findall(r'\b\w{3,}\b', names_text.lower())
                        # Filtrer les mots qui ne sont pas des noms
                        common_words = {'pour', 'avec', 'dans', 'sur', 'chez', 'vers', 'contre', 'sans', 'sous'}
                        names = [name for name in potential_names if name not in common_words]
                    
                    if names:
                        return PersonalInfo(
                            category='family',
                            key='enfant',
                            value=names[0].capitalize(),
                            confidence=0.8,
                            source_text=original_text,
                            timestamp=time.time()
                        )
            
            elif category == 'projects':
                project = match.group(1).upper()
                return PersonalInfo(
                    category='project',
                    key='created',
                    value=project,
                    confidence=0.9,
                    source_text=original_text,
                    timestamp=time.time()
                )
            
            elif category == 'skills':
                skill = match.group(1)
                return PersonalInfo(
                    category='skill',
                    key='competence',
                    value=skill,
                    confidence=0.6,
                    source_text=original_text,
                    timestamp=time.time()
                )
        
        except Exception as e:
            logger.warning(f"Erreur traitement match {category}: {e}")
            return None
    
    def _extract_complex_info(self, text: str, text_lower: str) -> List[PersonalInfo]:
        """Extraction d'informations dans des phrases complexes"""
        extracted = []
        
        # Phrases multiples métiers
        multi_job_pattern = r"je suis\s+(professeur.*?),?\s+(artiste.*?),?\s+(?:et\s+)?(codeur|développeur)"
        match = re.search(multi_job_pattern, text_lower)
        if match:
            jobs = [match.group(1), match.group(2), match.group(3)]
            for job in jobs:
                job_clean = self.profession_synonyms.get(job.strip(), job.strip())
                extracted.append(PersonalInfo(
                    category='profession',
                    key='job',
                    value=job_clean,
                    confidence=0.8,
                    source_text=text,
                    timestamp=time.time()
                ))
        
        # Extraction des projets/créations
        creator_pattern = r"créateur\s+(?:d'|de|du)\s*(\w+)"
        match = re.search(creator_pattern, text_lower)
        if match:
            project = match.group(1).upper()
            extracted.append(PersonalInfo(
                category='project',
                key='founder',
                value=project,
                confidence=0.95,
                source_text=text,
                timestamp=time.time()
            ))
        
        return extracted

class PersonalMemoryManager:
    """Gestionnaire de mémoire personnelle avec apprentissage adaptatif"""
    
    def __init__(self, user_id: str, memory_path: Path):
        self.user_id = user_id
        self.memory_file = memory_path / f"personal_profile_{user_id}.json"
        self.extractor = PersonalInfoExtractor()
        self.personal_data = self._load_memory()
        
        # Système d'apprentissage adaptatif
        self.learned_patterns = self._load_learned_patterns()
        self.confidence_threshold = 0.5
    
    def _load_learned_patterns(self) -> Dict[str, List[str]]:
        """Charge les patterns appris automatiquement"""
        patterns_file = self.memory_file.parent / f"learned_patterns_{self.user_id}.json"
        if patterns_file.exists():
            try:
                with open(patterns_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement patterns appris: {e}")
        
        return {}
    
    def _save_learned_patterns(self):
        """Sauvegarde les patterns appris"""
        patterns_file = self.memory_file.parent / f"learned_patterns_{self.user_id}.json"
        patterns_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(patterns_file, 'w', encoding='utf-8') as f:
            json.dump(self.learned_patterns, f, indent=2, ensure_ascii=False)
    
    def update_from_conversation(self, text: str) -> List[PersonalInfo]:
        """Met à jour la mémoire avec apprentissage adaptatif et validation"""
        # DÉTECTION D'OBJECTIONS D'ABORD
        self.extractor.invalidate_recent_patterns(text)
        
        # Extraction classique avec système adaptatif
        extracted_info = self.extractor.extract_personal_info(text)
        
        # Apprentissage de nouveaux patterns si peu d'info extraite
        if len(extracted_info) == 0 and self._looks_like_personal_info(text):
            ai_extracted = self._ai_assisted_extraction(text)
            extracted_info.extend(ai_extracted)
        
        # Apprentissage et amélioration des patterns basé sur les extractions réussies
        self._learn_from_successful_extractions(extracted_info, text)
        
        # Stockage des informations
        for info in extracted_info:
            self._store_personal_info(info)
            
            # Apprentissage de nouveau pattern si confiance élevée
            if info.confidence > 0.8:
                self._learn_new_pattern(text, info)
        
        # Ajout de l'historique conversationnel
        if 'conversation_history' not in self.personal_data:
            self.personal_data['conversation_history'] = []
        
        self.personal_data['conversation_history'].append({
            'text': text[:200],
            'timestamp': time.time(),
            'extracted_info_count': len(extracted_info)
        })
        
        # Garde seulement les 10 dernières interactions
        if len(self.personal_data['conversation_history']) > 10:
            self.personal_data['conversation_history'] = self.personal_data['conversation_history'][-10:]
        
        if extracted_info:
            self._save_memory()
            logger.info(f"💾 {len(extracted_info)} nouvelles informations mémorisées pour {self.user_id}")
        
        return extracted_info
    
    def _looks_like_personal_info(self, text: str) -> bool:
        """Détermine si un texte contient probablement des infos personnelles"""
        personal_indicators = [
            'mon', 'ma', 'mes', 'je suis', 'j\'ai', 'j\'aime', 'j\'adore', 
            'préféré', 's\'appelle', 'couleur', 'métier', 'travail', 'fils', 'fille'
        ]
        
        text_lower = text.lower()
        return any(indicator in text_lower for indicator in personal_indicators)
    
    def _ai_assisted_extraction(self, text: str) -> List[PersonalInfo]:
        """Utilise l'IA pour extraire des informations non détectées par les patterns"""
        extracted = []
        
        # Utilisation de regex intelligente pour détecter des structures
        smart_patterns = [
            # Détection de noms propres comme enfants
            r"avec\s+([A-Z][a-z]+)",
            r"([A-Z][a-z]+)\s+(?:et|,)\s+([A-Z][a-z]+)",
            
            # Détection de préférences implicites
            r"(?:c'est|serait)\s+([^.!?]+)",
            
            # Détection d'âges, dates, etc.
            r"(\d+)\s+(ans?|années?)",
            
            # Structures "X de Y"
            r"(\w+)\s+de\s+([^.!?]+)",
        ]
        
        for pattern in smart_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Analyse contextuelle pour déterminer si c'est pertinent
                context = text[max(0, match.start()-20):match.end()+20]
                
                if self._is_personal_context(context):
                    info = self._create_info_from_match(match, text, pattern)
                    if info:
                        extracted.append(info)
        
        return extracted
    
    def _is_personal_context(self, context: str) -> bool:
        """Vérifie si le contexte indique une information personnelle"""
        personal_keywords = ['je', 'mon', 'ma', 'mes', 'avec', 'famille', 'enfant', 'fils']
        return any(keyword in context.lower() for keyword in personal_keywords)
    
    def _create_info_from_match(self, match: re.Match, text: str, pattern: str) -> Optional[PersonalInfo]:
        """Crée une PersonalInfo à partir d'un match intelligent"""
        groups = match.groups()
        
        if len(groups) == 1:
            value = groups[0]
            
            # Détermine la catégorie selon le contexte
            if re.search(r'[A-Z][a-z]+', value) and 'avec' in text.lower():
                return PersonalInfo(
                    category='family',
                    key='enfant',
                    value=value,
                    confidence=0.75,
                    source_text=text,
                    timestamp=time.time()
                )
        
        elif len(groups) == 2:
            key, value = groups
            category = self.extractor._classify_information(key, value, text)
            
            return PersonalInfo(
                category=category,
                key=self.extractor._clean_key(key),
                value=self.extractor._clean_value(value),
                confidence=0.7,
                source_text=text,
                timestamp=time.time()
            )
        
        return None
    
    def _learn_new_pattern(self, text: str, info: PersonalInfo):
        """Apprend un nouveau pattern basé sur une extraction réussie"""
        # Simplifie le texte pour créer un pattern générique
        text_lower = text.lower()
        
        # Remplace la valeur spécifique par un placeholder
        value_placeholder = text_lower.replace(info.value.lower(), "([^.!?]+)")
        
        # Ajoute le pattern aux patterns appris
        category = info.category
        if category not in self.learned_patterns:
            self.learned_patterns[category] = []
        
        if value_placeholder not in self.learned_patterns[category]:
            self.learned_patterns[category].append(value_placeholder)
            self._save_learned_patterns()
            logger.info(f"🧠 Nouveau pattern appris pour {category}: {value_placeholder[:50]}...")
    
    def _load_memory(self) -> Dict[str, Any]:
        """Charge la mémoire personnelle"""
        if self.memory_file.exists():
            try:
                with open(self.memory_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Erreur chargement mémoire: {e}")
        
        return {
            'identity': {},
            'profession': {},
            'preferences': {},
            'projects': {},
            'skills': {},
            'last_updated': time.time()
        }
    
    def _save_memory(self):
        """Sauvegarde la mémoire personnelle"""
        self.personal_data['last_updated'] = time.time()
        self.memory_file.parent.mkdir(exist_ok=True, parents=True)
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.personal_data, f, indent=2, ensure_ascii=False)
    
    def update_from_conversation(self, text: str) -> List[PersonalInfo]:
        """Met à jour la mémoire à partir d'une conversation"""
        extracted_info = self.extractor.extract_personal_info(text)
        
        for info in extracted_info:
            self._store_personal_info(info)
        
        # Ajout de l'historique conversationnel
        if 'conversation_history' not in self.personal_data:
            self.personal_data['conversation_history'] = []
        
        # Stockage des dernières interactions (limite à 10 pour éviter la surcharge)
        self.personal_data['conversation_history'].append({
            'text': text[:200],  # Première partie du message
            'timestamp': time.time(),
            'extracted_info_count': len(extracted_info)
        })
        
        # Garde seulement les 10 dernières interactions
        if len(self.personal_data['conversation_history']) > 10:
            self.personal_data['conversation_history'] = self.personal_data['conversation_history'][-10:]
        
        if extracted_info:
            self._save_memory()
            logger.info(f"💾 {len(extracted_info)} nouvelles informations mémorisées pour {self.user_id}")
        
        return extracted_info
    
    def _store_personal_info(self, info: PersonalInfo):
        """Stocke une information personnelle"""
        category = info.category
        
        if category not in self.personal_data:
            self.personal_data[category] = {}
        
        # Mise à jour avec confiance
        existing = self.personal_data[category].get(info.key)
        if not existing or info.confidence > existing.get('confidence', 0):
            self.personal_data[category][info.key] = {
                'value': info.value,
                'confidence': info.confidence,
                'source': info.source_text,
                'timestamp': info.timestamp
            }
    
    def get_personal_summary(self) -> str:
        """Génère un résumé personnel pour le contexte IA"""
        summary_parts = []
        
        # Identité
        if 'identity' in self.personal_data and 'name' in self.personal_data['identity']:
            name = self.personal_data['identity']['name']['value']
            summary_parts.append(f"L'utilisateur s'appelle {name}.")
        
        # Professions
        if 'profession' in self.personal_data:
            jobs = [data['value'] for data in self.personal_data['profession'].values()]
            if jobs:
                summary_parts.append(f"Professions: {', '.join(jobs)}.")
        
        # Famille
        if 'family' in self.personal_data:
            children = [data['value'] for data in self.personal_data['family'].values()]
            if children:
                summary_parts.append(f"Enfants: {', '.join(children)}.")
        
        # Projets
        if 'projects' in self.personal_data:
            projects = [data['value'] for data in self.personal_data['projects'].values()]
            if projects:
                summary_parts.append(f"Créateur/Fondateur de: {', '.join(projects)}.")
        
        # Préférences unifiées
        preferences_data = {}
        
        # Préférences générales
        if 'preferences' in self.personal_data:
            for key, data in self.personal_data['preferences'].items():
                preferences_data[key] = data['value']
        
        # Préférences anciennes (format legacy)
        if 'preference' in self.personal_data:
            for key, data in self.personal_data['preference'].items():
                preferences_data[key] = data['value']
        
        # Construction du texte des préférences
        likes = []
        dislikes = []
        colors = []
        
        for key, value in preferences_data.items():
            if key == 'couleur_preferee':
                colors.append(f"couleur préférée: {value}")
            elif value == 'aime':
                likes.append(key)
            elif value == "n'aime pas":
                dislikes.append(key)
        
        if colors:
            summary_parts.extend(colors)
        if likes:
            summary_parts.append(f"Aime: {', '.join(likes)}.")
        if dislikes:
            summary_parts.append(f"N'aime pas: {', '.join(dislikes)}.")
        
        # Gestion des autres catégories (project - format legacy)
        if 'project' in self.personal_data:
            for key, data in self.personal_data['project'].items():
                summary_parts.append(f"A créé: {data['value']}.")
        
        return " ".join(summary_parts) if summary_parts else "Aucune information personnelle mémorisée."
    
    def get_conversation_context(self) -> str:
        """Récupère le contexte des conversations récentes"""
        if 'conversation_history' not in self.personal_data:
            return ""
        
        recent_topics = []
        for interaction in self.personal_data['conversation_history'][-3:]:  # 3 dernières interactions
            text = interaction['text']
            if len(text) > 50:
                recent_topics.append(text[:50] + "...")
            else:
                recent_topics.append(text)
        
        if recent_topics:
            return f"Sujets récents abordés: {', '.join(recent_topics)}"
        return ""

def find_existing_user_profile(memory_path: Path, message: str) -> str:
    """Trouve un profil utilisateur existant basé sur le contenu du message"""
    if not memory_path.exists():
        return None
    
    # Extraction des indices du message
    message_lower = message.lower()
    potential_names = []
    
    # Recherche de noms dans le message
    name_patterns = [
        r"je m'appelle (\w+)",
        r"je suis (\w+)",
        r"mon nom est (\w+)",
        r"c'est (\w+)",
        r"\b(diego)\b",  # Recherche exacte de Diego
        r"\b(openred)\b"
    ]
    
    for pattern in name_patterns:
        matches = re.findall(pattern, message_lower)
        potential_names.extend(matches)
    
    # Mots-clés qui pourraient indiquer Diego
    diego_indicators = [
        "créateur", "fondateur", "professeur", "arts plastiques", 
        "café", "openred", "oredmind", "mon assistant", "ton créateur",
        "mes fils", "esteban", "gabriel", "dessiner", "j'aime", "mes enfants",
        "cadeau", "gabriel", "pourrait faire plaisir", "déjà dit", "oublié",
        "retiennes que", "aîné", "plus jeune"
    ]
    
    # Recherche dans les fichiers de mémoire existants
    best_user_id = None
    best_score = 0
    
    for memory_file in memory_path.glob("personal_profile_*.json"):
        try:
            with open(memory_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Score de correspondance
            score = 0
            user_id = memory_file.stem.replace('personal_profile_', '')
            
            # Vérification des noms (priorité absolue)
            if 'identity' in data and 'name' in data['identity']:
                stored_name = data['identity']['name']['value'].lower()
                if stored_name in message_lower or any(name.lower() == stored_name for name in potential_names):
                    logger.info(f"🔍 Utilisateur reconnu par nom: {stored_name} -> {user_id}")
                    return user_id  # Retour immédiat pour correspondance de nom
            
            # Vérification des projets/créations
            if 'projects' in data or 'project' in data:
                project_section = data.get('projects', data.get('project', {}))
                for key, project_data in project_section.items():
                    if isinstance(project_data, dict) and 'value' in project_data:
                        project_name = project_data['value'].lower()
                        if project_name in message_lower:
                            score += 50
            
            # Vérification des informations familiales (Gabriel, Esteban)
            if 'family' in data:
                for key, family_data in data['family'].items():
                    if isinstance(family_data, dict) and 'value' in family_data:
                        family_name = family_data['value'].lower()
                        if family_name in message_lower:
                            score += 30
            
            # Vérification des mots-clés contextuels pour Diego
            for indicator in diego_indicators:
                if indicator in message_lower:
                    score += 5
            
            # Gardons le meilleur score
            if score > best_score:
                best_score = score
                best_user_id = user_id
        
        except Exception as e:
            logger.error(f"Erreur lecture fichier mémoire {memory_file}: {e}")
    
    # Si on a un score suffisant, retourner l'utilisateur
    if best_score >= 15:  # Seuil plus bas pour détecter Diego plus facilement
        logger.info(f"🔍 Utilisateur reconnu par contexte (score: {best_score}) -> {best_user_id}")
        return best_user_id
    
    logger.info(f"🔍 Aucun utilisateur reconnu pour: {message[:50]}...")
    return None

if __name__ == "__main__":
    # Test du système
    extractor = PersonalInfoExtractor()
    test_text = "Bonjour ! Je m'appelle Diego ! Je n'aime pas le café. Je suis professeur d'arts plastiques, artiste et codeur ! Je suis le créateur d'OpenRed."
    
    infos = extractor.extract_personal_info(test_text)
    for info in infos:
        print(f"📋 {info.category}: {info.key} = {info.value} (confiance: {info.confidence})")