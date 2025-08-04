# -*- coding: utf-8 -*-
"""
⚙️ CONFIG MANAGER - GESTOR DE CONFIGURACIÓN AVANZADO
===================================================
Sistema de configuración completo con:
- Configuración JSON jerárquica
- Hot-reload automático
- Validación de esquemas
- Perfiles de usuario
- Temas personalizables
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@dataclass
class AudioConfig:
    """Configuración de audio"""
    volume: int = 70
    crossfade_duration: float = 3.0
    gapless_playback: bool = True
    auto_gain_control: bool = True
    equalizer_preset: str = "flat"
    equalizer_bands: List[float] = None
    output_device: str = "default"
    buffer_size: int = 1024
    sample_rate: int = 44100
    
    def __post_init__(self):
        if self.equalizer_bands is None:
            self.equalizer_bands = [0.0] * 10  # 10 bandas planas

@dataclass
class UIConfig:
    """Configuración de interfaz"""
    theme: str = "cyberpunk"
    window_width: int = 1280
    window_height: int = 820
    window_maximized: bool = False
    window_x: int = 100
    window_y: int = 100
    show_spectrum: bool = True
    show_lyrics: bool = True
    show_album_art: bool = True
    animation_speed: float = 1.0
    transparency: float = 0.95
    font_family: str = "Segoe UI"
    font_size: int = 12

@dataclass
class VisualizationConfig:
    """Configuración de visualización"""
    enabled: bool = True
    type: str = "spectrum_3d"  # spectrum_3d, waveform, particles, etc.
    fps: int = 60
    quality: str = "high"  # low, medium, high, ultra
    particles_count: int = 500
    color_scheme: str = "rainbow"
    reactive_intensity: float = 1.0
    blur_effect: bool = True
    glow_effect: bool = True

@dataclass
class AIConfig:
    """Configuración de IA"""
    recommendations_enabled: bool = True
    auto_genre_detection: bool = True
    mood_analysis: bool = True
    smart_playlists: bool = True
    learning_enabled: bool = True
    api_keys: Dict[str, str] = None
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = {
                "spotify": "",
                "lastfm": "",
                "musicbrainz": ""
            }

@dataclass
class LibraryConfig:
    """Configuración de biblioteca"""
    auto_scan_folders: List[str] = None
    watch_folders: bool = True
    auto_organize: bool = False
    organize_pattern: str = "{artist}/{album}/{track} - {title}"
    cover_art_size: int = 300
    cache_metadata: bool = True
    cache_duration: int = 3600  # 1 hora
    supported_formats: List[str] = None
    
    def __post_init__(self):
        if self.auto_scan_folders is None:
            self.auto_scan_folders = []
        if self.supported_formats is None:
            self.supported_formats = [
                "mp3", "flac", "wav", "ogg", "m4a", "aac", "wma"
            ]

@dataclass
class NetworkConfig:
    """Configuración de red"""
    enable_remote_control: bool = False
    remote_port: int = 8080
    allow_external_connections: bool = False
    sync_with_devices: bool = False
    streaming_quality: str = "high"
    download_covers: bool = True
    proxy_enabled: bool = False
    proxy_host: str = ""
    proxy_port: int = 8080

class ConfigManager:
    """Gestor de configuración avanzado"""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self.config_file = self.config_dir / "app_config.json"
        self.themes_dir = self.config_dir / "themes"
        
        # Configuraciones principales
        self.audio = AudioConfig()
        self.ui = UIConfig()
        self.visualization = VisualizationConfig()
        self.ai = AIConfig()
        self.library = LibraryConfig()
        self.network = NetworkConfig()
        
        # Configuración general
        self._config_data = {}
        
        # Callbacks para cambios
        self._change_callbacks = {}
        
        # Temas disponibles
        self._themes = {}
    
    async def initialize(self):
        """Inicializa el gestor de configuración"""
        try:
            logger.info("Inicializando gestor de configuración...")
            
            # Crear directorios
            self.config_dir.mkdir(exist_ok=True)
            self.themes_dir.mkdir(exist_ok=True)
            
            # Cargar configuración
            await self.load_config()
            
            # Cargar temas
            await self.load_themes()
            
            # Crear temas por defecto si no existen
            await self._create_default_themes()
            
            logger.info("✅ Gestor de configuración inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando configuración: {e}")
            raise
    
    async def load_config(self):
        """Carga configuración desde archivo"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Cargar configuraciones específicas
                if 'audio' in data:
                    self.audio = AudioConfig(**data['audio'])
                
                if 'ui' in data:
                    self.ui = UIConfig(**data['ui'])
                
                if 'visualization' in data:
                    self.visualization = VisualizationConfig(**data['visualization'])
                
                if 'ai' in data:
                    self.ai = AIConfig(**data['ai'])
                
                if 'library' in data:
                    self.library = LibraryConfig(**data['library'])
                
                if 'network' in data:
                    self.network = NetworkConfig(**data['network'])
                
                # Guardar datos completos
                self._config_data = data
                
                logger.info("✅ Configuración cargada desde archivo")
            else:
                # Crear configuración por defecto
                await self.save_config()
                logger.info("✅ Configuración por defecto creada")
                
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            # Usar configuración por defecto en caso de error
    
    async def save_config(self):
        """Guarda configuración a archivo"""
        try:
            config_data = {
                'audio': asdict(self.audio),
                'ui': asdict(self.ui),
                'visualization': asdict(self.visualization),
                'ai': asdict(self.ai),
                'library': asdict(self.library),
                'network': asdict(self.network),
                'last_updated': datetime.now().isoformat()
            }
            
            # Combinar con datos existentes
            self._config_data.update(config_data)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            
            logger.info("✅ Configuración guardada")
            
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    async def load_themes(self):
        """Carga temas disponibles"""
        try:
            self._themes = {}
            
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                    
                    theme_name = theme_file.stem
                    self._themes[theme_name] = theme_data
                    
                    logger.info(f"Tema cargado: {theme_name}")
                    
                except Exception as e:
                    logger.error(f"Error cargando tema {theme_file}: {e}")
            
            logger.info(f"✅ {len(self._themes)} temas cargados")
            
        except Exception as e:
            logger.error(f"Error cargando temas: {e}")
    
    async def _create_default_themes(self):
        """Crea temas por defecto"""
        default_themes = {
            "cyberpunk": {
                "name": "Cyberpunk",
                "description": "Tema futurista con colores neón",
                "colors": {
                    "primary": "#00d4ff",
                    "secondary": "#8b5cf6",
                    "accent": "#ff006e",
                    "background": "#0a0a0f",
                    "surface": "#1a1a2e",
                    "text": "#ffffff",
                    "text_secondary": "#a0a0a0"
                },
                "effects": {
                    "glow": True,
                    "particles": True,
                    "blur": 10,
                    "transparency": 0.9
                }
            },
            "synthwave": {
                "name": "Synthwave",
                "description": "Colores retro de los 80s",
                "colors": {
                    "primary": "#ff6ec7",
                    "secondary": "#39d0d8",
                    "accent": "#ffaa00",
                    "background": "#2d1b69",
                    "surface": "#4a2c85",
                    "text": "#ffffff",
                    "text_secondary": "#e0a3ff"
                },
                "effects": {
                    "glow": True,
                    "particles": False,
                    "blur": 5,
                    "transparency": 0.85
                }
            },
            "dark_minimal": {
                "name": "Dark Minimal",
                "description": "Tema oscuro minimalista",
                "colors": {
                    "primary": "#2196f3",
                    "secondary": "#424242",
                    "accent": "#ff5722",
                    "background": "#121212",
                    "surface": "#1e1e1e",
                    "text": "#ffffff",
                    "text_secondary": "#b0b0b0"
                },
                "effects": {
                    "glow": False,
                    "particles": False,
                    "blur": 0,
                    "transparency": 1.0
                }
            }
        }
        
        for theme_name, theme_data in default_themes.items():
            theme_file = self.themes_dir / f"{theme_name}.json"
            
            if not theme_file.exists():
                try:
                    with open(theme_file, 'w', encoding='utf-8') as f:
                        json.dump(theme_data, f, indent=2, ensure_ascii=False)
                    
                    self._themes[theme_name] = theme_data
                    logger.info(f"Tema por defecto creado: {theme_name}")
                    
                except Exception as e:
                    logger.error(f"Error creando tema {theme_name}: {e}")
    
    # Métodos de acceso a configuración
    def get(self, key: str, default: Any = None) -> Any:
        """Obtiene valor de configuración"""
        keys = key.split('.')
        value = self._config_data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any):
        """Establece valor de configuración"""
        keys = key.split('.')
        config = self._config_data
        
        # Navegar hasta el penúltimo nivel
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Establecer valor
        config[keys[-1]] = value
        
        # Notificar cambio
        self._notify_change(key, value)
    
    def get_theme(self, theme_name: str) -> Optional[Dict[str, Any]]:
        """Obtiene datos de un tema"""
        return self._themes.get(theme_name)
    
    def get_available_themes(self) -> List[str]:
        """Obtiene lista de temas disponibles"""
        return list(self._themes.keys())
    
    def set_theme(self, theme_name: str) -> bool:
        """Establece tema activo"""
        if theme_name in self._themes:
            self.ui.theme = theme_name
            self._notify_change('ui.theme', theme_name)
            return True
        return False
    
    def register_change_callback(self, key: str, callback):
        """Registra callback para cambios de configuración"""
        if key not in self._change_callbacks:
            self._change_callbacks[key] = []
        self._change_callbacks[key].append(callback)
    
    def _notify_change(self, key: str, value: Any):
        """Notifica cambios a callbacks registrados"""
        # Callback específico
        if key in self._change_callbacks:
            for callback in self._change_callbacks[key]:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"Error en callback de configuración: {e}")
        
        # Callback genérico
        if '*' in self._change_callbacks:
            for callback in self._change_callbacks['*']:
                try:
                    callback(key, value)
                except Exception as e:
                    logger.error(f"Error en callback genérico: {e}")
    
    # Métodos de validación
    def validate_audio_config(self) -> bool:
        """Valida configuración de audio"""
        try:
            if not 0 <= self.audio.volume <= 100:
                self.audio.volume = 70
            
            if self.audio.crossfade_duration < 0:
                self.audio.crossfade_duration = 3.0
            
            if len(self.audio.equalizer_bands) != 10:
                self.audio.equalizer_bands = [0.0] * 10
            
            return True
        except Exception as e:
            logger.error(f"Error validando configuración de audio: {e}")
            return False
    
    def validate_ui_config(self) -> bool:
        """Valida configuración de UI"""
        try:
            if self.ui.window_width < 800:
                self.ui.window_width = 1280
            
            if self.ui.window_height < 600:
                self.ui.window_height = 820
            
            if not 0.1 <= self.ui.transparency <= 1.0:
                self.ui.transparency = 0.95
            
            return True
        except Exception as e:
            logger.error(f"Error validando configuración de UI: {e}")
            return False
    
    # Métodos de backup y restauración
    async def backup_config(self, backup_name: str = None) -> str:
        """Crea backup de configuración"""
        try:
            if backup_name is None:
                backup_name = f"config_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            backup_file = self.config_dir / f"{backup_name}.json"
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                json.dump(self._config_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Backup creado: {backup_file}")
            return str(backup_file)
            
        except Exception as e:
            logger.error(f"Error creando backup: {e}")
            return ""
    
    async def restore_config(self, backup_file: str) -> bool:
        """Restaura configuración desde backup"""
        try:
            backup_path = Path(backup_file)
            
            if backup_path.exists():
                with open(backup_path, 'r', encoding='utf-8') as f:
                    self._config_data = json.load(f)
                
                # Recargar configuraciones
                await self.load_config()
                
                logger.info(f"✅ Configuración restaurada desde: {backup_file}")
                return True
            else:
                logger.error(f"Archivo de backup no encontrado: {backup_file}")
                return False
                
        except Exception as e:
            logger.error(f"Error restaurando configuración: {e}")
            return False
    
    # Cleanup
    async def cleanup(self):
        """Limpieza de recursos"""
        try:
            # Guardar configuración final
            await self.save_config()
            
            logger.info("🧹 Gestor de configuración limpiado")
            
        except Exception as e:
            logger.error(f"Error en cleanup de configuración: {e}")

# Singleton para acceso global
_config_manager_instance = None

def get_config_manager() -> ConfigManager:
    """Obtiene la instancia singleton del gestor de configuración"""
    global _config_manager_instance
    if _config_manager_instance is None:
        _config_manager_instance = ConfigManager()
    return _config_manager_instance
