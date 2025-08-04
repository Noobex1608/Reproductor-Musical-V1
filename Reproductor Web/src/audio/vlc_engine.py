# -*- coding: utf-8 -*-
"""
🎵 VLC AUDIO ENGINE - MOTOR DE AUDIO PROFESIONAL
================================================
Motor de audio basado en VLC con todas las características avanzadas:
- Soporte TODOS los formatos
- Ecualizador de 10 bandas
- Efectos profesionales
- Seek preciso
- Análisis de espectro en tiempo real
"""

try:
    import vlc
    VLC_AVAILABLE = True
except ImportError:
    VLC_AVAILABLE = False
    print("⚠️  VLC no disponible - usando motor de audio simulado")

try:
    import librosa
    import scipy.fft
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False
    print("⚠️  Librosa no disponible - análisis de espectro limitado")

import asyncio
import threading
import time
import numpy as np
from typing import Optional, Dict, List, Callable
import logging

logger = logging.getLogger(__name__)

class VLCAudioEngine:
    """Motor de audio profesional basado en VLC"""
    
    def __init__(self):
        self.instance = None
        self.player = None
        self.media = None
        self.equalizer = None
        
        # Estados
        self.is_playing = False
        self.is_paused = False
        self.is_loading = False  # Flag para evitar cambios simultáneos
        self.current_position = 0.0
        self.duration = 0.0
        self.volume = 70
        
        # Configuración de efectos
        self.crossfade_enabled = True
        self.gapless_playback = True
        self.auto_gain_control = True
        
        # Callbacks
        self.position_callback: Optional[Callable] = None
        self.end_reached_callback: Optional[Callable] = None
        self.spectrum_callback: Optional[Callable] = None
        
        # Análisis de espectro
        self.spectrum_data = np.zeros(512)
        self.spectrum_thread = None
        self.spectrum_running = False
        
        # Variables para análisis de audio real
        self.current_audio_path = None
        self.audio_data = None
        self.sample_rate = 22050
        self.audio_loaded = False
        self.background_task = None  # Track del task de carga en background
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    async def initialize(self):
        """Inicializa el motor de audio VLC"""
        try:
            logger.info("Inicializando motor de audio VLC...")
            
            # Crear instancia VLC con opciones SÚPER OPTIMIZADAS para fluidez
            vlc_args = [
                '--intf=dummy',           # Sin interfaz
                '--no-video',             # Solo audio
                '--aout=directsound',     # DirectSound en Windows
                '--file-caching=150',     # Cache MÁS REDUCIDO para menos latencia
                '--quiet',                # Menos logs de VLC
                '--no-osd',              # Sin overlay
                '--audio-time-stretch',  # Time stretching
                '--audio-resampler=src_sinc_fastest',  # Resampler más rápido
                '--no-stats',            # Sin estadísticas
                '--no-lua',              # Sin scripts lua
            ]
            
            self.instance = vlc.Instance(vlc_args)
            self.player = self.instance.media_player_new()
            
            # Configurar eventos
            self._setup_events()
            
            # Inicializar ecualizador
            self._initialize_equalizer()
            
            logger.info("✅ Motor de audio VLC inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando VLC: {e}")
            raise
    
    def _setup_events(self):
        """Configura eventos de VLC"""
        event_manager = self.player.event_manager()
        
        # Evento de fin de reproducción
        event_manager.event_attach(
            vlc.EventType.MediaPlayerEndReached,
            self._on_end_reached
        )
        
        # Evento de cambio de posición
        event_manager.event_attach(
            vlc.EventType.MediaPlayerPositionChanged,
            self._on_position_changed
        )
        
        # Evento de cambio de tiempo
        event_manager.event_attach(
            vlc.EventType.MediaPlayerTimeChanged,
            self._on_time_changed
        )
    
    def _initialize_equalizer(self):
        """Inicializa el ecualizador de 10 bandas"""
        try:
            self.equalizer = vlc.AudioEqualizer()
            
            # Configuración por defecto (flat)
            for i in range(10):
                self.equalizer.set_amp_at_index(0.0, i)
            
            # Aplicar al reproductor
            self.player.set_equalizer(self.equalizer)
            
            logger.info("✅ Ecualizador inicializado")
            
        except Exception as e:
            logger.error(f"Error inicializando ecualizador: {e}")
    
    async def load_track(self, file_path: str) -> bool:
        """Carga una pista de audio - ULTRA OPTIMIZADO PARA CAMBIOS RÁPIDOS"""
        try:
            # Verificación inicial sin bloqueos
            if self.is_loading:
                logger.debug("⚠️ Ya se está cargando una pista, ignorando...")
                return False
            
            # Marcar como cargando ANTES del lock para evitar condiciones de carrera
            self.is_loading = True
            
            try:
                # Cancelar tareas inmediatamente sin lock
                self._cancel_background_tasks_sync()
                
                # Detener espectro primero (más rápido)
                self._stop_spectrum_analysis()
                
                # Lock MÁS CORTO solo para operaciones críticas
                with self._lock:
                    # Detener player de forma directa y rápida
                    try:
                        if self.player:
                            self.player.stop()
                        self.is_playing = False
                        self.is_paused = False
                    except Exception as e:
                        logger.debug(f"Error deteniendo player: {e}")
                    
                    # Crear nueva media inmediatamente
                    self.media = self.instance.media_new(file_path)
                    self.player.set_media(self.media)
                
                # Obtener duración FUERA del lock para no bloquear
                self._get_duration_sync()
                
                logger.info(f"✅ Pista cargada: {file_path}")
                
                # Programar análisis background solo si es necesario
                if self.current_audio_path != file_path or not self.audio_loaded:
                    try:
                        loop = asyncio.get_running_loop()
                        if loop and not loop.is_closed():
                            # Crear task sin await para no bloquear
                            loop.create_task(self._schedule_background_analysis(file_path))
                    except (RuntimeError, AttributeError):
                        pass  # Ignorar errores de loop
                
                return True
                
            finally:
                self.is_loading = False
                
        except Exception as e:
            logger.error(f"Error cargando pista: {e}")
            self.is_loading = False
            return False
    
    async def _schedule_background_analysis(self, file_path: str):
        """Programa análisis de background de forma ultra-segura"""
        try:
            # Verificación mínima del loop
            try:
                loop = asyncio.get_running_loop()
                if not loop or loop.is_closed():
                    return
            except RuntimeError:
                return
            
            # Crear task sin verificaciones complejas
            try:
                self.background_task = loop.create_task(
                    self._load_audio_for_analysis_background(file_path)
                )
                
                # Callback minimalista
                def minimal_callback(task):
                    try:
                        if not task.cancelled() and task.exception():
                            logger.debug(f"Background task error: {task.exception()}")
                    except Exception:
                        pass
                
                self.background_task.add_done_callback(minimal_callback)
                
            except Exception as e:
                logger.debug(f"Error creando task: {e}")
            
        except Exception as e:
            logger.debug(f"Error en schedule: {e}")

    async def _load_audio_for_analysis_background(self, file_path: str):
        """Carga audio en background SÚPER SIMPLIFICADO Y RESISTENTE"""
        try:
            # Verificación robusta del loop
            try:
                loop = asyncio.get_running_loop()
                if not loop or loop.is_closed():
                    logger.debug("Loop cerrado en background analysis")
                    return
            except RuntimeError:
                logger.debug("No hay loop en background analysis")
                return
            
            # Pausa mínima con verificación de cancelación
            try:
                await asyncio.sleep(0.05)
            except asyncio.CancelledError:
                self.audio_loaded = False
                return
            
            # Verificar cancelación de forma más robusta
            if hasattr(self, 'background_task') and self.background_task and self.background_task.cancelled():
                logger.debug("Background task cancelado")
                return
            
            # Verificar que el loop sigue activo antes de continuar
            try:
                current_loop = asyncio.get_running_loop()
                if not current_loop or current_loop.is_closed():
                    logger.debug("Loop cerrado durante análisis")
                    return
            except RuntimeError:
                logger.debug("Loop no disponible durante análisis")
                return
            
            # Cargar datos reales con mejor manejo de errores
            try:
                await self._load_audio_for_analysis(file_path)
            except Exception as e:
                logger.debug(f"Error en load_audio_for_analysis: {e}")
                self.audio_loaded = False
                return
            
            # Verificación final antes de marcar como cargado
            if (self.audio_loaded and 
                hasattr(self, 'background_task') and 
                self.background_task and 
                not self.background_task.cancelled()):
                logger.info("🎵 Análisis real activado")
            
        except asyncio.CancelledError:
            # Normal cuando se cancela
            logger.debug("Background analysis cancelado")
            self.audio_loaded = False
            raise
        except Exception as e:
            # Cualquier otro error - usar datos simulados
            logger.debug(f"Error en análisis background: {e}")
            self.audio_loaded = False
    
    def _get_duration_sync(self):
        """Obtiene la duración de la pista actual (versión síncrona optimizada)"""
        try:
            # Parse la media para obtener información
            self.media.parse()
            
            # Intentar obtener duración inmediatamente
            duration = self.media.get_duration()
            if duration > 0:
                self.duration = duration / 1000.0
                logger.debug(f"🕒 Duración obtenida inmediatamente: {self.duration:.1f}s")
                return
            
            # Si no se obtiene inmediatamente, esperar brevemente con timeout corto
            timeout = 10  # Reducido a 1 segundo máximo
            while timeout > 0:
                duration = self.media.get_duration()
                if duration > 0:
                    self.duration = duration / 1000.0
                    logger.debug(f"🕒 Duración obtenida tras espera: {self.duration:.1f}s")
                    break
                time.sleep(0.1)
                timeout -= 1
            
            # Si aún no se obtiene, usar duración por defecto
            if self.duration <= 0:
                self.duration = 180.0  # 3 minutos por defecto
                logger.warning(f"⚠️ Usando duración por defecto: {self.duration:.1f}s")
                
        except Exception as e:
            logger.warning(f"Error obteniendo duración: {e}")
            self.duration = 180.0  # Fallback
    
    async def _get_duration(self):
        """Obtiene la duración de la pista actual (versión async)"""
        # Parse la media para obtener información
        self.media.parse()
        
        # Esperar a que se obtenga la duración
        timeout = 50  # 5 segundos
        while timeout > 0:
            duration = self.media.get_duration()
            if duration > 0:
                self.duration = duration / 1000.0  # Convertir a segundos
                break
            await asyncio.sleep(0.1)
            timeout -= 1
    
    def play(self) -> bool:
        """Inicia la reproducción"""
        try:
            with self._lock:
                result = self.player.play()
                if result == 0:  # Éxito
                    self.is_playing = True
                    self.is_paused = False
                    
                    # Iniciar análisis de espectro
                    self._start_spectrum_analysis()
                    
                    logger.info("▶️ Reproducción iniciada")
                    return True
                else:
                    logger.error("❌ Error iniciando reproducción")
                    return False
                    
        except Exception as e:
            logger.error(f"Error en play: {e}")
            return False
    
    def pause(self) -> bool:
        """Pausa la reproducción"""
        try:
            with self._lock:
                if not self.is_paused:
                    self.player.pause()
                    self.is_paused = True
                    logger.info("⏸️ Reproducción pausada")
                
                return True
                
        except Exception as e:
            logger.error(f"Error en pause: {e}")
            return False
    
    def resume(self) -> bool:
        """Reanuda la reproducción"""
        try:
            with self._lock:
                if self.is_paused:
                    self.player.pause()  # VLC usa pause() como toggle
                    self.is_paused = False
                    logger.info("▶️ Reproducción reanudada")
                
                return True
                
        except Exception as e:
            logger.error(f"Error en resume: {e}")
            return False
    
    def stop(self) -> bool:
        """Detiene la reproducción - OPTIMIZADO PARA CAMBIOS RÁPIDOS"""
        try:
            # Cancelar tareas primero, FUERA del lock
            self._cancel_background_tasks_sync()
            self._stop_spectrum_analysis()
            
            # Lock MÁS CORTO solo para operaciones VLC
            with self._lock:
                try:
                    self.player.stop()
                except Exception as e:
                    logger.debug(f"Error stop VLC: {e}")
                
                # Actualizar estados rápidamente
                self.is_playing = False
                self.is_paused = False
                self.current_position = 0.0
                
                logger.info("⏹️ Reproducción detenida")
                return True
                
        except Exception as e:
            logger.error(f"Error en stop: {e}")
            return False
    
    def _cancel_background_tasks_sync(self):
        """Cancela tareas de background INMEDIATAMENTE sin esperas"""
        try:
            # Cancelar task principal de forma instantánea
            if hasattr(self, 'background_task') and self.background_task:
                try:
                    if not self.background_task.done():
                        self.background_task.cancel()
                except Exception:
                    pass  # Ignorar errores
                self.background_task = None
            
            # Cancelar task de espectro de forma instantánea
            if hasattr(self, 'spectrum_task') and self.spectrum_task:
                try:
                    if not self.spectrum_task.done():
                        self.spectrum_task.cancel()
                except Exception:
                    pass  # Ignorar errores
                self.spectrum_task = None
                    
        except Exception:
            pass  # Ignorar cualquier error para máxima velocidad
        
        # Limpiar referencias SIEMPRE
        self.background_task = None
        if hasattr(self, 'spectrum_task'):
            self.spectrum_task = None
    
    def seek(self, position: float) -> bool:
        """Busca una posición específica (0.0 - 1.0)"""
        try:
            with self._lock:
                # Asegurar que el valor esté entre 0.0 y 1.0
                position = max(0.0, min(1.0, position))
                self.player.set_position(position)
                self.current_position = position * self.duration
                
                logger.info(f"⏭️ Seek a posición: {position:.2%}")
                return True
                
        except Exception as e:
            logger.error(f"Error en seek: {e}")
            return False
    
    def set_volume(self, volume: int) -> bool:
        """Establece el volumen (0-100)"""
        try:
            with self._lock:
                volume = max(0, min(100, volume))
                self.player.audio_set_volume(volume)
                self.volume = volume
                
                logger.info(f"🔊 Volumen: {volume}%")
                return True
                
        except Exception as e:
            logger.error(f"Error estableciendo volumen: {e}")
            return False
    
    def set_equalizer_band(self, band: int, gain: float) -> bool:
        """Establece ganancia de una banda del ecualizador"""
        try:
            if self.equalizer and 0 <= band < 10:
                # Gain en dB (-20.0 a +20.0)
                gain = max(-20.0, min(20.0, gain))
                self.equalizer.set_amp_at_index(gain, band)
                
                logger.info(f"🎛️ EQ Band {band}: {gain:.1f}dB")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error en ecualizador: {e}")
            return False
    
    def get_equalizer_presets(self) -> List[str]:
        """Obtiene presets disponibles del ecualizador"""
        try:
            presets = []
            preset_count = vlc.libvlc_audio_equalizer_get_preset_count()
            
            for i in range(preset_count):
                preset_name = vlc.libvlc_audio_equalizer_get_preset_name(i)
                if preset_name:
                    presets.append(preset_name.decode('utf-8'))
            
            return presets
            
        except Exception as e:
            logger.error(f"Error obteniendo presets: {e}")
            return []
    
    def load_equalizer_preset(self, preset_name: str) -> bool:
        """Carga un preset del ecualizador"""
        try:
            presets = self.get_equalizer_presets()
            if preset_name in presets:
                preset_index = presets.index(preset_name)
                
                # Crear nuevo ecualizador con el preset
                self.equalizer = vlc.AudioEqualizer.create_from_preset(preset_index)
                self.player.set_equalizer(self.equalizer)
                
                logger.info(f"🎵 Preset cargado: {preset_name}")
                return True
            return False
            
        except Exception as e:
            logger.error(f"Error cargando preset: {e}")
            return False
    
    def _start_spectrum_analysis(self):
        """Inicia el análisis de espectro en tiempo real"""
        if not self.spectrum_running:
            self.spectrum_running = True
            self.spectrum_thread = threading.Thread(
                target=self._spectrum_analysis_loop,
                daemon=True
            )
            self.spectrum_thread.start()
            logger.info("🎵 Análisis de espectro iniciado")
    
    def _stop_spectrum_analysis(self):
        """Detiene el análisis de espectro INMEDIATAMENTE"""
        self.spectrum_running = False
        # NO esperar al thread - let it die naturally para cambios instantáneos
        if self.spectrum_thread and self.spectrum_thread.is_alive():
            # Solo join si es absolutamente necesario y con timeout mínimo
            try:
                self.spectrum_thread.join(timeout=0.01)  # 10ms máximo
            except Exception:
                pass  # Ignorar errores de join
        self.spectrum_thread = None
    
    def _spectrum_analysis_loop(self):
        """Loop de análisis de espectro OPTIMIZADO PARA FLUIDEZ SIN ENTRECORTES"""
        frame_time = 1/20  # 20 FPS en lugar de 25 para menos carga CPU
        last_frame_time = time.time()
        
        while self.spectrum_running and self.is_playing:
            try:
                # Control de timing más suave
                current_time = time.time()
                elapsed = current_time - last_frame_time
                
                if elapsed < frame_time:
                    # Dormir menos tiempo para suavidad
                    time.sleep(frame_time - elapsed)
                    continue
                
                last_frame_time = current_time
                
                # Solo analizar si está reproduciendo y no pausado
                if self.is_playing and not self.is_paused:
                    if self.audio_loaded and self.audio_data is not None:
                        # ✅ ANÁLISIS REAL OPTIMIZADO
                        try:
                            # Posición en el audio con menos queries al player
                            position = self.player.get_position()  # 0.0 - 1.0
                            
                            # Calcular frame en el fragmento de 5 segundos
                            total_frames = len(self.audio_data)
                            # Ciclar por el fragmento para tener análisis continuo
                            current_frame = int((position * 10) % 1.0 * total_frames)
                            
                            # Ventana MÁS GRANDE para menos cálculos (0.3 segundos)
                            window_size = int(self.sample_rate * 0.3)  # 0.3 segundos
                            start_frame = max(0, current_frame - window_size // 2)
                            end_frame = min(total_frames, start_frame + window_size)
                            
                            if end_frame > start_frame and (end_frame - start_frame) > 64:
                                # Extraer ventana de audio
                                audio_window = self.audio_data[start_frame:end_frame]
                                
                                # FFT optimizada con MENOS resolución
                                fft_size = min(128, len(audio_window))  # FFT MÁS PEQUEÑA
                                
                                if len(audio_window) >= fft_size:
                                    # Aplicar ventana rápida
                                    windowed = audio_window[:fft_size] * np.hanning(fft_size)
                                    
                                    # FFT real
                                    fft = np.fft.fft(windowed)
                                    spectrum = np.abs(fft[:fft_size//2])
                                    
                                    # Normalización ultra-rápida
                                    if len(spectrum) > 0:
                                        spectrum_max = np.max(spectrum)
                                        if spectrum_max > 1e-10:
                                            spectrum = spectrum / spectrum_max
                                        
                                        # Escala log rápida
                                        spectrum = np.log10(spectrum + 1e-6)
                                        spectrum = (spectrum + 6) / 6  # Normalizar -6 a 0 -> 0 a 1
                                        spectrum = np.clip(spectrum, 0, 1)
                                        
                                        # Resize a 512 súper rápido
                                        if len(spectrum) != 512:
                                            x_old = np.linspace(0, 1, len(spectrum))
                                            x_new = np.linspace(0, 1, 512)
                                            spectrum = np.interp(x_new, x_old, spectrum)
                                        
                                        self.spectrum_data = spectrum
                                        
                                        # Callback con try/except para evitar bloqueos
                                        if self.spectrum_callback:
                                            try:
                                                self.spectrum_callback(spectrum)
                                            except:
                                                pass
                                        
                                        continue
                        except Exception:
                            # Si falla el análisis real, usar simulado
                            pass
                    
                    # 🎨 ANÁLISIS SIMULADO FLUIDO - Solo si no hay datos reales
                    t = time.time()
                    
                    # Simular espectro musical realista con MENOS cálculos
                    freqs = np.linspace(0, 1, 512)
                    
                    # Bass (graves) - frecuencias bajas
                    bass = np.exp(-freqs * 5) * (0.6 + 0.4 * np.sin(t * 2))
                    
                    # Mids (medios) - frecuencias medias  
                    mids = np.exp(-(freqs - 0.3)**2 * 8) * (0.4 + 0.3 * np.sin(t * 3 + 1))
                    
                    # Highs (agudos) - frecuencias altas
                    highs = np.exp(-(freqs - 0.8)**2 * 15) * (0.3 + 0.2 * np.sin(t * 4 + 2))
                    
                    # Combinar y agregar variación MÁS RÁPIDA
                    spectrum = bass + mids + highs
                    spectrum += np.random.random(512) * 0.05  # MENOS ruido para menos cálculo
                    spectrum = np.clip(spectrum, 0, 1)
                    
                    self.spectrum_data = spectrum
                    
                    if self.spectrum_callback:
                        try:
                            self.spectrum_callback(spectrum)
                        except:
                            pass
                else:
                    # Si no está reproduciendo, dormir más tiempo
                    time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error en spectrum loop: {e}")
                time.sleep(0.1)  # Evitar loop infinito en caso de error
                
            except Exception as e:
                logger.error(f"Error en análisis de espectro: {e}")
                time.sleep(0.1)  # Pausa en caso de error
    
    async def _load_audio_for_analysis(self, file_path: str):
        """Carga el archivo de audio para análisis de espectro - SÚPER OPTIMIZADO Y REAL"""
        try:
            # Evitar cargar el mismo archivo dos veces
            if self.current_audio_path == file_path and self.audio_loaded:
                logger.info("✅ Audio ya cargado para análisis")
                return
            
            if LIBROSA_AVAILABLE:
                logger.info("🎵 Cargando audio para análisis de espectro...")
                
                # Cargar audio ULTRA OPTIMIZADO - solo 5 segundos pero REAL
                def load_audio_super_fast():
                    try:
                        # Solo 5 segundos desde el minuto 1 (parte más representativa)
                        duration = 5.0     # 5 segundos es suficiente
                        offset = 60.0      # Comenzar en el minuto 1 (mejor parte)
                        sr_target = 8000   # Sample rate muy bajo para velocidad máxima
                        
                        audio, sr = librosa.load(
                            file_path, 
                            sr=sr_target,
                            mono=True,
                            duration=duration,
                            offset=offset,
                            res_type='kaiser_fast'  # Resample más rápido
                        )
                        
                        # Si no hay suficiente audio en el minuto 1, probar desde el inicio
                        if len(audio) < sr_target:
                            audio, sr = librosa.load(
                                file_path, 
                                sr=sr_target,
                                mono=True,
                                duration=duration,
                                offset=0.0,  # Desde el inicio
                                res_type='kaiser_fast'
                            )
                        
                        return audio, sr
                    except Exception as e:
                        logger.error(f"Error cargando audio con librosa: {e}")
                        return None, None
                
                # Ejecutar SÚPER RÁPIDO con mejor manejo de errores
                try:
                    loop = asyncio.get_running_loop()
                    if not loop or loop.is_closed():
                        logger.debug("⚠️ Loop cerrado durante carga de audio")
                        audio, sr = None, None
                    else:
                        # Timeout súper corto - 0.5 segundos máximo
                        audio, sr = await asyncio.wait_for(
                            loop.run_in_executor(None, load_audio_super_fast),
                            timeout=0.5
                        )
                except asyncio.TimeoutError:
                    logger.debug("⚠️ Timeout carga rápida - fallback simulado")
                    audio, sr = None, None
                except RuntimeError as e:
                    if "Event loop is closed" in str(e):
                        logger.debug("⚠️ Loop cerrado - fallback simulado")
                    else:
                        logger.debug(f"⚠️ RuntimeError: {e} - fallback simulado")
                    audio, sr = None, None
                except Exception as e:
                    logger.debug(f"⚠️ Error inesperado: {e} - fallback simulado")
                    audio, sr = None, None
                
                if audio is not None and len(audio) > 0:
                    self.audio_data = audio
                    self.sample_rate = sr
                    self.current_audio_path = file_path
                    self.audio_loaded = True
                    logger.info(f"✅ Audio real cargado (súper-rápido): {len(audio)} samples a {sr}Hz")
                else:
                    self.audio_loaded = False
                    self.sample_rate = 8000  # Fallback sample rate
                    logger.warning("⚠️ Fallback a análisis simulado fluido")
            else:
                logger.warning("⚠️ Librosa no disponible - análisis simulado fluido")
                self.audio_loaded = False
                self.sample_rate = 8000
                
        except Exception as e:
            logger.error(f"Error carga audio análisis: {e}")
            self.audio_loaded = False
            self.sample_rate = 8000
    
    def _on_end_reached(self, event):
        """Callback cuando termina la reproducción"""
        self.is_playing = False
        self.is_paused = False
        
        if self.end_reached_callback:
            self.end_reached_callback()
    
    def _on_position_changed(self, event):
        """Callback cuando cambia la posición"""
        if self.duration > 0:
            position = self.player.get_position()
            current_time = position * self.duration  # Tiempo actual en segundos
            self.current_position = current_time
            
            if self.position_callback:
                # Enviar tiempo actual en segundos, no porcentaje
                self.position_callback(current_time, self.duration)
    
    def _on_time_changed(self, event):
        """Callback cuando cambia el tiempo"""
        current_time = self.player.get_time() / 1000.0  # Convertir a segundos
        if current_time > 0:
            self.current_position = current_time
    
    # Getters para información de estado
    def get_position(self) -> float:
        """Obtiene la posición actual (0.0 - 1.0)"""
        return self.player.get_position() if self.player else 0.0
    
    def get_time(self) -> float:
        """Obtiene el tiempo actual en segundos"""
        time = self.current_position
        if time > 0:
            logger.debug(f"🕒 Tiempo actual: {time:.1f}s")
        return time
    
    def get_duration(self) -> float:
        """Obtiene la duración total en segundos"""
        return self.duration
    
    def get_volume(self) -> int:
        """Obtiene el volumen actual"""
        return self.volume
    
    def get_spectrum_data(self) -> np.ndarray:
        """Obtiene datos del espectro actual"""
        return self.spectrum_data.copy()
    
    def is_media_loaded(self) -> bool:
        """Verifica si hay media cargada"""
        return self.media is not None
    
    def cleanup(self):
        """Limpieza ROBUSTA de recursos"""
        try:
            # Cancelar TODAS las tareas de background de forma segura
            self._cancel_background_tasks_sync()
            
            # Detener análisis de espectro
            self._stop_spectrum_analysis()
            
            # Detener reproductor VLC
            if self.player:
                try:
                    self.stop()
                    self.player.release()
                except Exception as e:
                    logger.warning(f"Error liberando player: {e}")
            
            # Liberar instancia VLC
            if self.instance:
                try:
                    self.instance.release()
                except Exception as e:
                    logger.warning(f"Error liberando instancia: {e}")
            
            # Limpiar variables de estado
            self.audio_loaded = False
            self.current_audio_path = None
            
            logger.info("🧹 Motor de audio VLC limpiado")
            
        except Exception as e:
            logger.error(f"Error en cleanup: {e}")
    
    # MÉTODOS ASYNC ADICIONALES PARA LA APLICACIÓN
    
    async def play_async(self):
        """Versión async de play"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.play)
    
    async def pause_async(self):
        """Versión async de pause"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.pause)
    
    async def resume_async(self):
        """Versión async de resume"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.resume)
        return True
    
    async def stop_async(self):
        """Versión async de stop - SIN BLOQUEOS"""
        try:
            # Stop directo sin executor para evitar bloqueos
            self.stop()
            return True
        except Exception as e:
            logger.error(f"Error en stop_async: {e}")
            return False
    
    async def seek_async(self, position: float):
        """Versión async de seek"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.seek, position)
    
    async def set_volume_async(self, volume: int):
        """Versión async de set_volume"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.set_volume, volume)
    
    async def get_duration(self):
        """Versión async de get_duration"""
        try:
            if self.media:
                duration = self.media.get_duration()
                if duration > 0:
                    return duration / 1000.0
            return 0.0
        except:
            return 0.0

# Singleton para acceso global
_vlc_engine_instance = None

def get_vlc_engine() -> VLCAudioEngine:
    """Obtiene la instancia singleton del motor VLC"""
    global _vlc_engine_instance
    if _vlc_engine_instance is None:
        _vlc_engine_instance = VLCAudioEngine()
    return _vlc_engine_instance
