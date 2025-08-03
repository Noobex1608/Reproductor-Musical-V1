# -*- coding: utf-8 -*-
"""
🤖 MUSIC AI - INTELIGENCIA ARTIFICIAL MUSICAL
============================================
Sistema de IA completo para análisis musical:
- Detección automática de género y BPM
- Análisis de mood y características acústicas
- Recomendaciones inteligentes
- Playlists automáticas
- Aprendizaje de preferencias del usuario
"""

import numpy as np
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math

try:
    import librosa
    import librosa.display
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("librosa no disponible - algunas funciones de IA estarán limitadas")

try:
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class AudioFeatures:
    """Características de audio extraídas"""
    # Características básicas
    duration: float
    tempo: float  # BPM
    key: int  # 0-11 (C, C#, D, etc.)
    mode: int  # 0=menor, 1=mayor
    
    # Características tímbricas
    spectral_centroid: float
    spectral_rolloff: float
    spectral_bandwidth: float
    zero_crossing_rate: float
    
    # Características rítmicas
    beat_strength: float
    rhythm_regularity: float
    
    # MFCC (Mel-frequency cepstral coefficients)
    mfcc: List[float]
    
    # Características de alto nivel
    danceability: float
    energy: float
    valence: float  # Positividad musical
    acousticness: float
    instrumentalness: float
    liveness: float
    speechiness: float
    loudness: float

@dataclass
class MoodAnalysis:
    """Análisis de mood de una canción"""
    primary_mood: str  # happy, sad, energetic, calm, aggressive, melancholic
    mood_confidence: float
    secondary_moods: List[Tuple[str, float]]
    emotional_valence: float  # -1 (negativo) a +1 (positivo)
    arousal: float  # 0 (calmado) a 1 (excitado)

@dataclass
class GenreClassification:
    """Clasificación de género musical"""
    primary_genre: str
    confidence: float
    genre_probabilities: Dict[str, float]
    subgenre: Optional[str] = None

class AudioAnalyzer:
    """Analizador de audio usando librosa"""
    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
        self.n_mfcc = 13
        
        # Modelos pre-entrenados (simulados para este ejemplo)
        self.genre_model = None
        self.mood_model = None
        
        # Cache de análisis
        self.analysis_cache = {}
    
    async def analyze_audio_file(self, file_path: str) -> Optional[AudioFeatures]:
        """Analiza un archivo de audio completo"""
        if not LIBROSA_AVAILABLE:
            logger.warning("librosa no disponible - análisis limitado")
            return self._basic_analysis(file_path)
        
        try:
            # Cargar audio
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            
            # Análisis básico
            duration = len(y) / sr
            
            # Análisis de tempo y beat
            tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            
            # Análisis de tonalidad
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
            key = self._estimate_key(chroma)
            mode = self._estimate_mode(chroma)
            
            # Características espectrales
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=self.hop_length)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr, hop_length=self.hop_length)
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr, hop_length=self.hop_length)
            zero_crossing_rate = librosa.feature.zero_crossing_rate(y, hop_length=self.hop_length)
            
            # MFCC
            mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc, hop_length=self.hop_length)
            
            # Características de alto nivel
            features = AudioFeatures(
                duration=duration,
                tempo=float(tempo),
                key=key,
                mode=mode,
                spectral_centroid=float(np.mean(spectral_centroids)),
                spectral_rolloff=float(np.mean(spectral_rolloff)),
                spectral_bandwidth=float(np.mean(spectral_bandwidth)),
                zero_crossing_rate=float(np.mean(zero_crossing_rate)),
                beat_strength=self._calculate_beat_strength(y, beats, sr),
                rhythm_regularity=self._calculate_rhythm_regularity(beats),
                mfcc=np.mean(mfccs, axis=1).tolist(),
                danceability=self._calculate_danceability(tempo, beat_strength=0.5),
                energy=self._calculate_energy(y),
                valence=self._calculate_valence(chroma, tempo),
                acousticness=self._calculate_acousticness(spectral_centroids, zero_crossing_rate),
                instrumentalness=self._calculate_instrumentalness(mfccs),
                liveness=self._calculate_liveness(y, sr),
                speechiness=self._calculate_speechiness(spectral_centroids, zero_crossing_rate),
                loudness=self._calculate_loudness(y)
            )
            
            return features
            
        except Exception as e:
            logger.error(f"Error analizando audio {file_path}: {e}")
            return None
    
    def _basic_analysis(self, file_path: str) -> AudioFeatures:
        """Análisis básico sin librosa"""
        # Análisis muy básico usando información del archivo
        try:
            from mutagen import File
            audio_file = File(file_path)
            
            duration = 0.0
            if audio_file is not None and audio_file.info:
                duration = audio_file.info.length
            
            # Valores por defecto
            return AudioFeatures(
                duration=duration,
                tempo=120.0,  # BPM promedio
                key=0,
                mode=1,
                spectral_centroid=1000.0,
                spectral_rolloff=2000.0,
                spectral_bandwidth=1500.0,
                zero_crossing_rate=0.1,
                beat_strength=0.5,
                rhythm_regularity=0.5,
                mfcc=[0.0] * 13,
                danceability=0.5,
                energy=0.5,
                valence=0.5,
                acousticness=0.5,
                instrumentalness=0.5,
                liveness=0.1,
                speechiness=0.1,
                loudness=-10.0
            )
            
        except Exception as e:
            logger.error(f"Error en análisis básico: {e}")
            return None
    
    def _estimate_key(self, chroma: np.ndarray) -> int:
        """Estima la tonalidad musical"""
        # Perfil de tonalidades (Krumhansl-Schmuckler)
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Promediar chroma a lo largo del tiempo
        chroma_mean = np.mean(chroma, axis=1)
        
        # Correlación con perfiles
        major_correlations = []
        minor_correlations = []
        
        for i in range(12):
            # Rotar perfil para cada tonalidad
            major_rotated = np.roll(major_profile, i)
            minor_rotated = np.roll(minor_profile, i)
            
            major_correlations.append(np.corrcoef(chroma_mean, major_rotated)[0, 1])
            minor_correlations.append(np.corrcoef(chroma_mean, minor_rotated)[0, 1])
        
        # Encontrar la mejor correlación
        best_major = np.argmax(major_correlations)
        best_minor = np.argmax(minor_correlations)
        
        if major_correlations[best_major] > minor_correlations[best_minor]:
            return best_major
        else:
            return best_minor
    
    def _estimate_mode(self, chroma: np.ndarray) -> int:
        """Estima el modo (mayor/menor)"""
        # Simplificado: basado en la presencia de la tercera
        chroma_mean = np.mean(chroma, axis=1)
        
        # Índices de tercera mayor (4 semitonos) vs menor (3 semitonos)
        major_third_strength = chroma_mean[4]
        minor_third_strength = chroma_mean[3]
        
        return 1 if major_third_strength > minor_third_strength else 0
    
    def _calculate_beat_strength(self, y: np.ndarray, beats: np.ndarray, sr: int) -> float:
        """Calcula la fuerza del beat"""
        if len(beats) < 2:
            return 0.0
        
        # Calcular energía en los beats
        beat_frames = librosa.time_to_frames(beats, sr=sr, hop_length=self.hop_length)
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length, frame_length=2048)
        
        if len(beat_frames) > len(rms[0]):
            beat_frames = beat_frames[:len(rms[0])]
        
        beat_energies = rms[0, beat_frames]
        return float(np.mean(beat_energies))
    
    def _calculate_rhythm_regularity(self, beats: np.ndarray) -> float:
        """Calcula la regularidad del ritmo"""
        if len(beats) < 3:
            return 0.0
        
        intervals = np.diff(beats)
        regularity = 1.0 - (np.std(intervals) / np.mean(intervals))
        return max(0.0, min(1.0, regularity))
    
    def _calculate_danceability(self, tempo: float, beat_strength: float) -> float:
        """Calcula la danzabilidad"""
        # Rango óptimo de tempo para bailar (90-140 BPM)
        tempo_factor = 1.0 - abs(tempo - 115) / 115
        tempo_factor = max(0.0, tempo_factor)
        
        danceability = (tempo_factor * 0.6) + (beat_strength * 0.4)
        return max(0.0, min(1.0, danceability))
    
    def _calculate_energy(self, y: np.ndarray) -> float:
        """Calcula la energía musical"""
        rms = np.sqrt(np.mean(y**2))
        return max(0.0, min(1.0, rms * 10))  # Normalizar aproximadamente
    
    def _calculate_valence(self, chroma: np.ndarray, tempo: float) -> float:
        """Calcula la valencia (positividad)"""
        # Basado en modo y tempo
        chroma_mean = np.mean(chroma, axis=1)
        major_strength = chroma_mean[0] + chroma_mean[4] + chroma_mean[7]  # Acorde de Do mayor
        minor_strength = chroma_mean[0] + chroma_mean[3] + chroma_mean[7]  # Acorde de Do menor
        
        mode_valence = major_strength / (major_strength + minor_strength + 1e-8)
        tempo_valence = min(1.0, tempo / 140.0)  # Tempos rápidos = más positivo
        
        return (mode_valence * 0.7) + (tempo_valence * 0.3)
    
    def _calculate_acousticness(self, spectral_centroids: np.ndarray, zcr: np.ndarray) -> float:
        """Calcula el nivel acústico"""
        # Menos centroide espectral y menos ZCR = más acústico
        centroid_norm = 1.0 - (np.mean(spectral_centroids) / 4000.0)
        zcr_norm = 1.0 - (np.mean(zcr) / 0.2)
        
        return max(0.0, min(1.0, (centroid_norm + zcr_norm) / 2.0))
    
    def _calculate_instrumentalness(self, mfccs: np.ndarray) -> float:
        """Calcula el nivel instrumental"""
        # Basado en la variabilidad de los MFCC (voz = más variable)
        mfcc_var = np.var(mfccs, axis=1)
        vocal_indicator = np.mean(mfcc_var[1:5])  # MFCC 1-4 son buenos para detectar voz
        
        return max(0.0, min(1.0, 1.0 - vocal_indicator))
    
    def _calculate_liveness(self, y: np.ndarray, sr: int) -> float:
        """Calcula el nivel de grabación en vivo"""
        # Basado en reverberación y ruido de audiencia
        # Simplificado: usar variabilidad de energía
        rms = librosa.feature.rms(y=y, hop_length=self.hop_length)
        energy_var = np.var(rms)
        
        return max(0.0, min(1.0, energy_var * 100))
    
    def _calculate_speechiness(self, spectral_centroids: np.ndarray, zcr: np.ndarray) -> float:
        """Calcula el nivel de habla"""
        # Características típicas del habla
        centroid_speech = np.mean(spectral_centroids) / 2000.0  # Normalizar
        zcr_speech = np.mean(zcr) / 0.1  # ZCR alto indica habla
        
        return max(0.0, min(1.0, (centroid_speech + zcr_speech) / 2.0))
    
    def _calculate_loudness(self, y: np.ndarray) -> float:
        """Calcula el loudness en dB"""
        rms = np.sqrt(np.mean(y**2))
        if rms > 0:
            return 20 * np.log10(rms)
        return -60.0  # Silencio

class MoodClassifier:
    """Clasificador de mood musical"""
    
    def __init__(self):
        # Definición de moods
        self.mood_definitions = {
            'happy': {
                'valence_range': (0.6, 1.0),
                'energy_range': (0.5, 1.0),
                'tempo_range': (100, 160),
                'mode_preference': 1  # Mayor
            },
            'sad': {
                'valence_range': (0.0, 0.4),
                'energy_range': (0.0, 0.5),
                'tempo_range': (60, 100),
                'mode_preference': 0  # Menor
            },
            'energetic': {
                'valence_range': (0.4, 1.0),
                'energy_range': (0.7, 1.0),
                'tempo_range': (120, 180),
                'mode_preference': 1
            },
            'calm': {
                'valence_range': (0.3, 0.7),
                'energy_range': (0.0, 0.4),
                'tempo_range': (60, 90),
                'mode_preference': None
            },
            'aggressive': {
                'valence_range': (0.2, 0.8),
                'energy_range': (0.8, 1.0),
                'tempo_range': (140, 200),
                'mode_preference': 0
            },
            'melancholic': {
                'valence_range': (0.0, 0.3),
                'energy_range': (0.2, 0.6),
                'tempo_range': (70, 110),
                'mode_preference': 0
            }
        }
    
    def classify_mood(self, features: AudioFeatures) -> MoodAnalysis:
        """Clasifica el mood de una canción"""
        mood_scores = {}
        
        for mood, definition in self.mood_definitions.items():
            score = self._calculate_mood_score(features, definition)
            mood_scores[mood] = score
        
        # Encontrar mood primario
        primary_mood = max(mood_scores, key=mood_scores.get)
        confidence = mood_scores[primary_mood]
        
        # Moods secundarios
        secondary_moods = [(mood, score) for mood, score in mood_scores.items() 
                          if mood != primary_mood and score > 0.3]
        secondary_moods.sort(key=lambda x: x[1], reverse=True)
        
        # Calcular valencia emocional y arousal
        emotional_valence = (features.valence - 0.5) * 2  # Convertir a -1,1
        arousal = features.energy
        
        return MoodAnalysis(
            primary_mood=primary_mood,
            mood_confidence=confidence,
            secondary_moods=secondary_moods[:3],  # Top 3
            emotional_valence=emotional_valence,
            arousal=arousal
        )
    
    def _calculate_mood_score(self, features: AudioFeatures, definition: Dict) -> float:
        """Calcula score de similaridad con un mood"""
        score = 0.0
        factors = 0
        
        # Valencia
        if 'valence_range' in definition:
            val_min, val_max = definition['valence_range']
            if val_min <= features.valence <= val_max:
                score += 1.0
            else:
                # Penalizar por distancia
                distance = min(abs(features.valence - val_min), abs(features.valence - val_max))
                score += max(0.0, 1.0 - distance * 2)
            factors += 1
        
        # Energía
        if 'energy_range' in definition:
            energy_min, energy_max = definition['energy_range']
            if energy_min <= features.energy <= energy_max:
                score += 1.0
            else:
                distance = min(abs(features.energy - energy_min), abs(features.energy - energy_max))
                score += max(0.0, 1.0 - distance * 2)
            factors += 1
        
        # Tempo
        if 'tempo_range' in definition:
            tempo_min, tempo_max = definition['tempo_range']
            if tempo_min <= features.tempo <= tempo_max:
                score += 1.0
            else:
                distance = min(abs(features.tempo - tempo_min), abs(features.tempo - tempo_max))
                score += max(0.0, 1.0 - distance / 50.0)  # 50 BPM tolerance
            factors += 1
        
        # Modo
        if 'mode_preference' in definition and definition['mode_preference'] is not None:
            if features.mode == definition['mode_preference']:
                score += 1.0
            else:
                score += 0.3  # Partial credit
            factors += 1
        
        return score / factors if factors > 0 else 0.0

class GenreClassifier:
    """Clasificador de género musical"""
    
    def __init__(self):
        # Definiciones simplificadas de géneros
        self.genre_definitions = {
            'rock': {
                'tempo_range': (110, 150),
                'energy_range': (0.6, 1.0),
                'loudness_range': (-8, -3),
                'danceability_range': (0.3, 0.7)
            },
            'pop': {
                'tempo_range': (100, 130),
                'energy_range': (0.5, 0.9),
                'danceability_range': (0.5, 0.9),
                'valence_range': (0.4, 0.8)
            },
            'electronic': {
                'tempo_range': (120, 140),
                'energy_range': (0.7, 1.0),
                'danceability_range': (0.7, 1.0),
                'instrumentalness_range': (0.5, 1.0)
            },
            'classical': {
                'acousticness_range': (0.7, 1.0),
                'instrumentalness_range': (0.8, 1.0),
                'speechiness_range': (0.0, 0.1),
                'liveness_range': (0.0, 0.3)
            },
            'jazz': {
                'acousticness_range': (0.4, 0.9),
                'instrumentalness_range': (0.3, 0.9),
                'tempo_range': (80, 160),
                'energy_range': (0.3, 0.8)
            },
            'hip_hop': {
                'speechiness_range': (0.3, 1.0),
                'tempo_range': (70, 140),
                'danceability_range': (0.5, 1.0),
                'energy_range': (0.4, 0.9)
            }
        }
    
    def classify_genre(self, features: AudioFeatures) -> GenreClassification:
        """Clasifica el género de una canción"""
        genre_scores = {}
        
        for genre, definition in self.genre_definitions.items():
            score = self._calculate_genre_score(features, definition)
            genre_scores[genre] = score
        
        # Normalizar scores
        total_score = sum(genre_scores.values())
        if total_score > 0:
            genre_probabilities = {genre: score/total_score for genre, score in genre_scores.items()}
        else:
            genre_probabilities = {genre: 1.0/len(genre_scores) for genre in genre_scores}
        
        # Género primario
        primary_genre = max(genre_probabilities, key=genre_probabilities.get)
        confidence = genre_probabilities[primary_genre]
        
        return GenreClassification(
            primary_genre=primary_genre,
            confidence=confidence,
            genre_probabilities=genre_probabilities
        )
    
    def _calculate_genre_score(self, features: AudioFeatures, definition: Dict) -> float:
        """Calcula score de similaridad con un género"""
        score = 0.0
        factors = 0
        
        feature_values = {
            'tempo': features.tempo,
            'energy': features.energy,
            'loudness': features.loudness,
            'danceability': features.danceability,
            'valence': features.valence,
            'acousticness': features.acousticness,
            'instrumentalness': features.instrumentalness,
            'speechiness': features.speechiness,
            'liveness': features.liveness
        }
        
        for feature_name, range_key in [
            ('tempo', 'tempo_range'),
            ('energy', 'energy_range'),
            ('loudness', 'loudness_range'),
            ('danceability', 'danceability_range'),
            ('valence', 'valence_range'),
            ('acousticness', 'acousticness_range'),
            ('instrumentalness', 'instrumentalness_range'),
            ('speechiness', 'speechiness_range'),
            ('liveness', 'liveness_range')
        ]:
            if range_key in definition:
                feature_value = feature_values[feature_name]
                range_min, range_max = definition[range_key]
                
                if range_min <= feature_value <= range_max:
                    score += 1.0
                else:
                    # Penalizar por distancia
                    distance = min(abs(feature_value - range_min), abs(feature_value - range_max))
                    if feature_name == 'tempo':
                        score += max(0.0, 1.0 - distance / 50.0)
                    else:
                        score += max(0.0, 1.0 - distance * 2)
                
                factors += 1
        
        return score / factors if factors > 0 else 0.0

class MusicAI:
    """Sistema principal de IA musical"""
    
    def __init__(self):
        self.audio_analyzer = AudioAnalyzer()
        self.mood_classifier = MoodClassifier()
        self.genre_classifier = GenreClassifier()
        
        # Cache de análisis
        self.analysis_cache = {}
        
        # Modelos de recomendación
        self.recommendation_model = None
        self.user_preferences = {}
        
        # Configuración
        self.cache_duration = 3600  # 1 hora
    
    async def initialize(self):
        """Inicializa el sistema de IA musical"""
        try:
            logger.info("Inicializando sistema de IA musical...")
            
            # Cargar preferencias del usuario
            await self._load_user_preferences()
            
            # Inicializar modelos de recomendación
            await self._initialize_recommendation_models()
            
            logger.info("✅ Sistema de IA musical inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando IA musical: {e}")
            raise
    
    async def analyze_song(self, file_path: str) -> Dict[str, Any]:
        """Análisis completo de una canción"""
        try:
            # Verificar cache
            cache_key = f"{file_path}_{Path(file_path).stat().st_mtime}"
            if cache_key in self.analysis_cache:
                return self.analysis_cache[cache_key]
            
            # Análisis de características de audio
            features = await self.audio_analyzer.analyze_audio_file(file_path)
            if not features:
                return {}
            
            # Clasificación de mood
            mood_analysis = self.mood_classifier.classify_mood(features)
            
            # Clasificación de género
            genre_classification = self.genre_classifier.classify_genre(features)
            
            # Compilar resultados
            analysis_result = {
                'file_path': file_path,
                'timestamp': datetime.now().isoformat(),
                'audio_features': asdict(features),
                'mood_analysis': asdict(mood_analysis),
                'genre_classification': asdict(genre_classification),
                'analysis_version': '1.0'
            }
            
            # Guardar en cache
            self.analysis_cache[cache_key] = analysis_result
            
            logger.info(f"✅ Canción analizada: {Path(file_path).name}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analizando canción {file_path}: {e}")
            return {}
    
    async def get_recommendations(self, current_song: Dict[str, Any], num_recommendations: int = 10) -> List[Dict[str, Any]]:
        """Obtiene recomendaciones basadas en la canción actual"""
        # Esta sería la implementación de recomendaciones
        # Por ahora, retorna lista vacía
        return []
    
    async def create_smart_playlist(self, seed_songs: List[str], target_mood: str, duration_minutes: int = 60) -> List[str]:
        """Crea playlist inteligente basada en canciones semilla y mood objetivo"""
        # Implementación de playlist inteligente
        return []
    
    async def _load_user_preferences(self):
        """Carga preferencias del usuario"""
        try:
            preferences_file = Path("data/user_preferences.json")
            if preferences_file.exists():
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    self.user_preferences = json.load(f)
            else:
                self.user_preferences = {
                    'favorite_genres': [],
                    'preferred_moods': [],
                    'tempo_preference': 120,
                    'energy_preference': 0.5,
                    'valence_preference': 0.5
                }
                await self._save_user_preferences()
        except Exception as e:
            logger.error(f"Error cargando preferencias: {e}")
    
    async def _save_user_preferences(self):
        """Guarda preferencias del usuario"""
        try:
            preferences_file = Path("data/user_preferences.json")
            preferences_file.parent.mkdir(exist_ok=True)
            
            with open(preferences_file, 'w', encoding='utf-8') as f:
                json.dump(self.user_preferences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error guardando preferencias: {e}")
    
    async def _initialize_recommendation_models(self):
        """Inicializa modelos de recomendación"""
        # Aquí se inicializarían modelos de ML más complejos
        pass
    
    def update_user_preferences(self, song_analysis: Dict[str, Any], liked: bool):
        """Actualiza preferencias basadas en feedback del usuario"""
        if not song_analysis:
            return
        
        try:
            features = song_analysis.get('audio_features', {})
            genre = song_analysis.get('genre_classification', {}).get('primary_genre')
            mood = song_analysis.get('mood_analysis', {}).get('primary_mood')
            
            if liked:
                # Incrementar preferencia por este género/mood
                if genre and genre not in self.user_preferences['favorite_genres']:
                    self.user_preferences['favorite_genres'].append(genre)
                
                if mood and mood not in self.user_preferences['preferred_moods']:
                    self.user_preferences['preferred_moods'].append(mood)
                
                # Ajustar preferencias de características
                tempo = features.get('tempo', 120)
                energy = features.get('energy', 0.5)
                valence = features.get('valence', 0.5)
                
                # Promedio ponderado hacia la nueva preferencia
                self.user_preferences['tempo_preference'] = (
                    self.user_preferences['tempo_preference'] * 0.9 + tempo * 0.1
                )
                self.user_preferences['energy_preference'] = (
                    self.user_preferences['energy_preference'] * 0.9 + energy * 0.1
                )
                self.user_preferences['valence_preference'] = (
                    self.user_preferences['valence_preference'] * 0.9 + valence * 0.1
                )
            
            # Guardar preferencias actualizadas
            asyncio.create_task(self._save_user_preferences())
            
        except Exception as e:
            logger.error(f"Error actualizando preferencias: {e}")
    
    async def get_recommendations(self, current_track=None, play_history=None, count=10):
        """Obtiene recomendaciones basadas en IA"""
        try:
            # Por ahora devolver lista vacía
            # En implementación completa aquí iría la lógica de IA
            logger.info(f"Generando {count} recomendaciones...")
            return []
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}")
            return []
    
    async def cleanup(self):
        """Limpieza de recursos"""
        try:
            # Guardar preferencias finales
            await self._save_user_preferences()
            
            logger.info("🧹 Sistema de IA musical limpiado")
            
        except Exception as e:
            logger.error(f"Error en cleanup de IA musical: {e}")

# Singleton para acceso global
_music_ai_instance = None

def get_music_ai() -> MusicAI:
    """Obtiene la instancia singleton del sistema de IA musical"""
    global _music_ai_instance
    if _music_ai_instance is None:
        _music_ai_instance = MusicAI()
    return _music_ai_instance
