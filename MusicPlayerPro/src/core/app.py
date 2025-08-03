# -*- coding: utf-8 -*-
"""
🎵 MUSIC PLAYER PRO APP - APLICACIÓN PRINCIPAL
==============================================
Núcleo principal del reproductor musical que coordina todos los componentes:
- Gestión del estado de la aplicación
- Coordinación entre módulos
- Control de reproducción
- Manejo de eventos globales
"""

import asyncio
import threading
import os
from typing import Optional, Dict, List, Any, Callable
from pathlib import Path
import logging
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class Track:
    """Información de una pista musical"""
    id: str
    title: str
    artist: str
    album: str
    path: str
    duration: float
    genre: str = ""
    year: int = 0
    track_number: int = 0
    
class PlaybackState:
    """Estado de reproducción"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    LOADING = "loading"

class MusicPlayerProApp:
    """Aplicación principal del reproductor musical"""
    
    def __init__(self, config_manager, db_manager, audio_engine, visual_manager, music_ai):
        # Componentes principales
        self.config_manager = config_manager
        self.db_manager = db_manager
        self.audio_engine = audio_engine
        self.visual_manager = visual_manager
        self.music_ai = music_ai
        
        # Control de cierre
        self._is_shutting_down = False
        
        # Estado de reproducción
        self.playback_state = PlaybackState.STOPPED
        self.current_track: Optional[Track] = None
        self.current_playlist: List[Track] = []
        self.current_index = 0
        self.shuffle_enabled = False
        self.repeat_mode = "none"  # none, one, all
        
        # Información de reproducción
        self.position = 0.0
        self.duration = 0.0
        self.volume = 70
        
        # Callbacks para la UI
        self.ui_callbacks = {
            'track_changed': [],
            'playback_state_changed': [],
            'position_changed': [],
            'volume_changed': [],
            'playlist_changed': []
        }
        
        # Control de bucle principal
        self._running = False
        self._update_task = None
        
        logger.info("Aplicación MusicPlayerPro inicializada")
    
    def register_callback(self, event: str, callback: Callable):
        """Registra callback para eventos de la aplicación"""
        if event in self.ui_callbacks:
            self.ui_callbacks[event].append(callback)
    
    def _emit_event(self, event: str, data: Any = None):
        """Emite evento a todos los callbacks registrados"""
        if self._is_shutting_down:  # No emitir eventos durante el cierre
            return
            
        if event in self.ui_callbacks:
            for callback in self.ui_callbacks[event]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f"Error en callback {event}: {e}")
    
    async def run(self):
        """Ejecuta la aplicación principal"""
        try:
            logger.info("Iniciando aplicación MusicPlayerPro...")
            self._running = True
            
            # Configurar callbacks del motor de audio
            self.audio_engine.position_callback = self._on_position_update
            self.audio_engine.end_reached_callback = self._on_track_ended
            self.audio_engine.spectrum_callback = self._on_spectrum_update
            
            # Iniciar bucle de actualización
            self._update_task = asyncio.create_task(self._update_loop())
            
            # Cargar biblioteca musical
            await self._load_music_library()
            
            logger.info("✅ Aplicación iniciada correctamente")
            
            # Mantener la aplicación ejecutándose
            while self._running:
                await asyncio.sleep(0.1)
                
        except Exception as e:
            logger.error(f"Error en la aplicación principal: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _update_loop(self):
        """Bucle principal de actualización"""
        while self._running:
            try:
                # Actualizar posición de reproducción
                if self.playback_state == PlaybackState.PLAYING:
                    position = await self._get_playback_position()
                    if position != self.position:
                        logger.info(f"📊 Actualizando posición: {position:.1f}s / {self.duration:.1f}s")
                        self.position = position
                        self._emit_event('position_changed', {
                            'position': self.position,
                            'duration': self.duration
                        })
                
                await asyncio.sleep(0.1)  # 10 FPS de actualización
                
            except Exception as e:
                logger.error(f"Error en bucle de actualización: {e}")
                await asyncio.sleep(1)
    
    async def _get_playback_position(self):
        """Obtiene la posición actual de reproducción"""
        try:
            return self.audio_engine.get_time()  # Obtener tiempo en segundos en lugar de porcentaje
        except:
            return 0.0
    
    async def _load_music_library(self):
        """Carga la biblioteca musical desde la base de datos"""
        try:
            logger.info("Cargando biblioteca musical...")
            
            # Obtener todas las pistas de la base de datos
            tracks_data = await self.db_manager.get_all_tracks()
            
            # Convertir a objetos Track
            self.music_library = []
            for track_data in tracks_data:
                track = Track(
                    id=track_data.get('id', ''),
                    title=track_data.get('title', 'Desconocido'),
                    artist=track_data.get('artist', 'Desconocido'),
                    album=track_data.get('album', 'Desconocido'),
                    path=track_data.get('path', ''),
                    duration=track_data.get('duration', 0.0),
                    genre=track_data.get('genre', ''),
                    year=track_data.get('year', 0),
                    track_number=track_data.get('track_number', 0)
                )
                self.music_library.append(track)
            
            logger.info(f"✅ {len(self.music_library)} pistas cargadas")
            
        except Exception as e:
            logger.error(f"Error cargando biblioteca musical: {e}")
            self.music_library = []
    
    async def get_all_tracks(self):
        """Obtiene todas las pistas de la biblioteca"""
        return self.music_library
    
    # CONTROL DE REPRODUCCIÓN
    
    async def play_track(self, track: Track):
        """Reproduce una pista específica"""
        try:
            logger.info(f"Reproduciendo: {track.artist} - {track.title}")
            logger.info(f"🔧 Estado actual: {self.playback_state}")
            
            # Detener pista anterior si hay una reproduciéndose
            if self.playback_state == PlaybackState.PLAYING:
                logger.info(f"⏹️ Deteniendo pista anterior...")
                try:
                    # Stop con timeout para evitar bloqueos
                    await asyncio.wait_for(self.audio_engine.stop_async(), timeout=0.5)
                except asyncio.TimeoutError:
                    logger.warning("⚠️ Timeout deteniendo pista - continuando...")
                except Exception as e:
                    logger.warning(f"⚠️ Error deteniendo pista: {e} - continuando...")
                
                await asyncio.sleep(0.05)  # Pausa mínima
                logger.info(f"✅ Pista anterior detenida")
            
            logger.info(f"🎯 Estableciendo nueva pista como actual...")
            self.current_track = track
            logger.info(f"🔄 Cambiando estado a LOADING...")
            self.playback_state = PlaybackState.LOADING
            logger.info(f"📡 Emitiendo evento de cambio de estado...")
            self._emit_event('playback_state_changed', self.playback_state)
            logger.info(f"✅ Estado establecido correctamente")
            
            # Debug: verificar path de la pista
            logger.info(f"🔍 Verificando path: '{track.path}'")
            if not track.path or not os.path.exists(track.path):
                logger.error(f"❌ Path inválido o archivo no existe: '{track.path}'")
                return
            
            # Cargar y reproducir en el motor de audio
            logger.info(f"📂 Cargando pista desde: {track.path}")
            success = await self.audio_engine.load_track(track.path)
            if success:
                await self.audio_engine.play_async()
                self.playback_state = PlaybackState.PLAYING
                
                # Obtener duración después de un pequeño retraso
                await asyncio.sleep(0.2)
                try:
                    duration = await self.audio_engine.get_duration()
                    self.duration = duration if duration > 0 else 0.0
                    logger.info(f"🕒 Duración obtenida: {self.duration:.1f}s")
                except Exception as e:
                    logger.warning(f"No se pudo obtener duración: {e}")
                    self.duration = 0.0
                
                # Actualizar visualizador
                await self.visual_manager.start_visualization()
                
                # Notificar cambio de pista
                self._emit_event('track_changed', track)
                self._emit_event('playback_state_changed', self.playback_state)
                
                # Actualizar estadísticas en la base de datos
                await self.db_manager.add_play_history(track.id)
                
            else:
                logger.error(f"Error cargando pista: {track.path}")
                self.playback_state = PlaybackState.STOPPED
                self._emit_event('playback_state_changed', self.playback_state)
                
        except Exception as e:
            logger.error(f"Error reproduciendo pista: {e}")
            self.playback_state = PlaybackState.STOPPED
            self._emit_event('playback_state_changed', self.playback_state)
            self._emit_event('playback_state_changed', self.playback_state)
    
    async def play_pause(self):
        """Alterna entre reproducir y pausar"""
        if self.playback_state == PlaybackState.PLAYING:
            await self.pause()
        elif self.playback_state == PlaybackState.PAUSED:
            await self.resume()
        elif self.current_playlist and self.playback_state == PlaybackState.STOPPED:
            await self.play_track(self.current_playlist[self.current_index])
    
    async def pause(self):
        """Pausa la reproducción"""
        if self.playback_state == PlaybackState.PLAYING:
            await self.audio_engine.pause_async()
            self.playback_state = PlaybackState.PAUSED
            await self.visual_manager.pause_visualization()
            self._emit_event('playback_state_changed', self.playback_state)
    
    async def resume(self):
        """Reanuda la reproducción"""
        if self.playback_state == PlaybackState.PAUSED:
            await self.audio_engine.resume_async()
            self.playback_state = PlaybackState.PLAYING
            await self.visual_manager.resume_visualization()
            self._emit_event('playback_state_changed', self.playback_state)
    
    async def stop(self):
        """Detiene la reproducción"""
        await self.audio_engine.stop_async()
        self.playback_state = PlaybackState.STOPPED
        self.position = 0.0
        await self.visual_manager.stop_visualization()
        self._emit_event('playback_state_changed', self.playback_state)
    
    async def next_track(self):
        """Reproduce la siguiente pista"""
        try:
            logger.info("🔄 Intentando cambiar a siguiente pista...")
            
            if not self.current_playlist:
                logger.warning("⚠️ No hay playlist activa")
                return
                
            if self.shuffle_enabled:
                import random
                self.current_index = random.randint(0, len(self.current_playlist) - 1)
                logger.info(f"🔀 Modo aleatorio: índice {self.current_index}")
            else:
                self.current_index += 1
                logger.info(f"➡️ Siguiente pista: índice {self.current_index}")
                
                if self.current_index >= len(self.current_playlist):
                    if self.repeat_mode == "all":
                        self.current_index = 0
                        logger.info("🔁 Reiniciando playlist (repeat all)")
                    else:
                        logger.info("⏹️ Final de playlist alcanzado")
                        await self.stop()
                        return
            
            next_track = self.current_playlist[self.current_index]
            logger.info(f"▶️ Cambiando a: {next_track.artist} - {next_track.title}")
            await self.play_track(next_track)
            
        except Exception as e:
            logger.error(f"❌ Error en next_track: {e}")
            import traceback
            traceback.print_exc()
    
    async def previous_track(self):
        """Reproduce la pista anterior"""
        try:
            logger.info("🔄 Intentando cambiar a pista anterior...")
            
            if not self.current_playlist:
                logger.warning("⚠️ No hay playlist activa")
                return
                
            if self.shuffle_enabled:
                import random
                self.current_index = random.randint(0, len(self.current_playlist) - 1)
                logger.info(f"🔀 Modo aleatorio: índice {self.current_index}")
            else:
                self.current_index -= 1
                logger.info(f"⬅️ Pista anterior: índice {self.current_index}")
                
                if self.current_index < 0:
                    if self.repeat_mode == "all":
                        self.current_index = len(self.current_playlist) - 1
                        logger.info("🔁 Yendo al final de playlist (repeat all)")
                    else:
                        self.current_index = 0
                        logger.info("⏹️ Ya en la primera pista")
                        return
            
            prev_track = self.current_playlist[self.current_index]
            logger.info(f"▶️ Cambiando a: {prev_track.artist} - {prev_track.title}")
            await self.play_track(prev_track)
            
        except Exception as e:
            logger.error(f"❌ Error en previous_track: {e}")
            import traceback
            traceback.print_exc()
    
    async def seek(self, position_percentage: float):
        """Busca una posición específica en la pista (0.0 - 1.0)"""
        await self.audio_engine.seek_async(position_percentage)
        # Actualizar posición en segundos para la UI
        self.position = position_percentage * self.duration
        self._emit_event('position_changed', {
            'position': self.position,
            'duration': self.duration
        })
    
    async def set_volume(self, volume: int):
        """Establece el volumen (0-100)"""
        volume = max(0, min(100, volume))
        self.volume = volume
        await self.audio_engine.set_volume_async(volume)
        self._emit_event('volume_changed', volume)
    
    # GESTIÓN DE PLAYLIST
    
    async def set_playlist(self, tracks: List[Track], start_index: int = 0):
        """Establece una nueva playlist"""
        self.current_playlist = tracks
        self.current_index = start_index
        self._emit_event('playlist_changed', {
            'playlist': tracks,
            'current_index': start_index
        })
    
    async def add_to_queue(self, track: Track):
        """Añade una pista a la cola de reproducción"""
        if not self.current_playlist:
            self.current_playlist = []
        
        self.current_playlist.append(track)
        self._emit_event('playlist_changed', {
            'playlist': self.current_playlist,
            'current_index': self.current_index
        })
    
    def toggle_shuffle(self):
        """Alterna el modo aleatorio"""
        self.shuffle_enabled = not self.shuffle_enabled
        return self.shuffle_enabled
    
    def cycle_repeat_mode(self):
        """Cambia entre modos de repetición"""
        modes = ["none", "one", "all"]
        current_idx = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_idx + 1) % len(modes)]
        return self.repeat_mode
    
    # EVENTOS DE AUDIO
    
    def _on_position_update(self, current_time: float, duration: float = None):
        """Callback para actualización de posición"""
        self.position = current_time
        if duration:
            self.duration = duration
            
        # Emitir evento para actualizar UI
        self._emit_event('position_changed', {
            'position': current_time,
            'duration': self.duration or 0
        })
    
    def _on_track_ended(self):
        """Callback cuando termina una pista"""
        if self.repeat_mode == "one":
            # Repetir la misma pista
            asyncio.create_task(self.play_track(self.current_track))
        else:
            # Siguiente pista
            asyncio.create_task(self.next_track())
    
    def _on_spectrum_update(self, spectrum_data):
        """Callback para datos de espectro"""
        # Enviar datos al visualizador sin async para evitar problemas de event loop
        try:
            if self.visual_manager and self.playback_state == PlaybackState.PLAYING:
                # Usar un método sync o programar para más tarde
                if hasattr(self.visual_manager, 'update_spectrum_sync'):
                    self.visual_manager.update_spectrum_sync(spectrum_data)
                else:
                    # Fallback: programar para el próximo ciclo
                    pass
        except Exception as e:
            logger.warning(f"Error actualizando espectro: {e}")
    
    # BÚSQUEDA Y FILTROS
    
    async def search_tracks(self, query: str) -> List[Track]:
        """Busca pistas por título, artista o álbum"""
        try:
            query = query.lower()
            results = []
            
            for track in self.music_library:
                if (query in track.title.lower() or 
                    query in track.artist.lower() or 
                    query in track.album.lower()):
                    results.append(track)
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    async def get_tracks_by_artist(self, artist: str) -> List[Track]:
        """Obtiene todas las pistas de un artista"""
        return [track for track in self.music_library if track.artist.lower() == artist.lower()]
    
    async def get_tracks_by_album(self, album: str) -> List[Track]:
        """Obtiene todas las pistas de un álbum"""
        return [track for track in self.music_library if track.album.lower() == album.lower()]
    
    async def get_tracks_by_genre(self, genre: str) -> List[Track]:
        """Obtiene todas las pistas de un género"""
        return [track for track in self.music_library if track.genre.lower() == genre.lower()]
    
    # RECOMENDACIONES IA
    
    async def get_recommendations(self, count: int = 10) -> List[Track]:
        """Obtiene recomendaciones basadas en IA"""
        try:
            if not self.music_ai:
                return []
            
            recommendations = await self.music_ai.get_recommendations(
                current_track=self.current_track,
                play_history=await self.db_manager.get_recent_plays(100),
                count=count
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error obteniendo recomendaciones: {e}")
            return []
    
    # LIMPIEZA
    
    async def _cleanup(self):
        """Limpieza al cerrar la aplicación"""
        try:
            logger.info("Cerrando aplicación...")
            self._is_shutting_down = True  # Establecer bandera de cierre
            
            # Detener reproducción
            await self.stop()
            
            # Cancelar tarea de actualización
            if self._update_task:
                self._update_task.cancel()
            
            # Cerrar componentes
            if self.visual_manager:
                await self.visual_manager.cleanup()
            
            if self.audio_engine:
                self.audio_engine.cleanup()
            
            logger.info("✅ Aplicación cerrada correctamente")
            
        except Exception as e:
            logger.error(f"Error en limpieza: {e}")
    
    async def shutdown(self):
        """Cierra la aplicación"""
        self._running = False
