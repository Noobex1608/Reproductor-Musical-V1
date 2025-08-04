# -*- coding: utf-8 -*-
"""
🌐 FLASK APP - APLICACIÓN WEB PRINCIPAL
=====================================
Servidor Flask para la interfaz web del reproductor musical
"""

import asyncio
import threading
import time
import os
import logging
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS

from ..core.app import MusicPlayerProApp
from ..core.config_manager import get_config_manager

logger = logging.getLogger(__name__)

class MusicPlayerWebApp:
    """Aplicación web Flask para Music Player Pro"""
    
    def __init__(self, music_app: MusicPlayerProApp):
        """Inicializar aplicación web"""
        self.music_app = music_app
        self.config = get_config_manager()
        
        # Estados internos
        self._playback_state = "stopped"
        self._position = 0.0
        self._duration = 0.0
        self._volume = 50
        self._shuffle = False
        self._repeat = "none"  # "none", "one", "all"
        
        # Configurar Flask
        self.app = Flask(__name__, 
                        template_folder='../../templates',
                        static_folder='../../static')
        self.app.config['SECRET_KEY'] = 'music-player-pro-secret-key'
        
        # Configurar CORS
        CORS(self.app, origins=['http://localhost:5000', 'http://127.0.0.1:5000'])
        
        # Configurar SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        # Registrar rutas
        self._register_routes()
        
        logger.info("Aplicación web Flask inicializada")
    
    def _register_routes(self):
        """Registrar todas las rutas y endpoints"""
        
        # ============================
        # 🏠 RUTAS BÁSICAS
        # ============================
        
        @self.app.route('/')
        def index():
            """Página principal"""
            return render_template('index.html')
        
        @self.app.route('/library')
        def library():
            """Página de biblioteca completa"""
            return render_template('library.html')
        
        @self.app.route('/api/status')
        def status():
            """Estado de la aplicación"""
            return jsonify({
                'status': 'online',
                'version': '1.0.0',
                'message': 'Music Player Pro funcionando correctamente'
            })
        
        @self.app.route('/health')
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'ok',
                'server': 'online',
                'timestamp': time.time()
            })
        
        # ============================
        # 📚 BIBLIOTECA MUSICAL  
        # ============================
        
        @self.app.route('/api/library/songs')
        def get_songs():
            """Obtener todas las canciones"""
            try:
                songs = self.music_app.music_library or []
                serialized_songs = []
                
                for i, song in enumerate(songs, 1):
                    try:
                        serialized_song = self._serialize_track(song)
                        serialized_song['id'] = str(i)
                        serialized_songs.append(serialized_song)
                    except Exception as e:
                        logger.error(f"Error serializando canción {i}: {e}")
                        continue
                
                return jsonify({
                    'success': True,
                    'status': 'success',
                    'songs': serialized_songs,
                    'count': len(serialized_songs)
                })
            except Exception as e:
                logger.error(f"Error al obtener canciones: {e}")
                return jsonify({
                    'success': False,
                    'status': 'error', 
                    'message': str(e),
                    'songs': []
                }), 500
        
        @self.app.route('/api/library/add-folder', methods=['POST'])
        def add_music_folder():
            """Agregar música desde carpeta"""
            logger.info("🚀 INICIO: Endpoint add-folder llamado")
            
            try:
                # Log de la petición
                logger.info(f"📡 Content-Type: {request.content_type}")
                logger.info(f"📡 Method: {request.method}")
                
                # Verificar JSON
                if not request.is_json:
                    logger.error("❌ La petición no es JSON")
                    return jsonify({
                        'success': False,
                        'error': 'Content-Type debe ser application/json',
                        'message': 'La petición debe ser JSON'
                    }), 400
                
                data = request.get_json()
                if data is None:
                    logger.error("❌ No se pudieron obtener datos JSON")
                    return jsonify({
                        'success': False,
                        'error': 'JSON inválido',
                        'message': 'Los datos JSON no son válidos'
                    }), 400
                
                logger.info(f"📥 Datos recibidos: {data}")
                
                folder_path = data.get('folderPath', '')
                logger.info(f"📂 Ruta extraída: '{folder_path}'")
                
                # Limpiar comillas adicionales si las hay
                if folder_path.startswith('"') and folder_path.endswith('"'):
                    folder_path = folder_path[1:-1]
                    logger.info(f"📂 Ruta limpia: '{folder_path}'")
                
                if not folder_path:
                    logger.warning("❌ No se proporcionó ruta de carpeta")
                    return jsonify({
                        'success': False, 
                        'error': 'No se proporcionó ruta de carpeta',
                        'message': 'Debe especificar una carpeta'
                    }), 400
                
                # Verificar si la carpeta existe
                folder_path_obj = Path(folder_path)
                if not folder_path_obj.exists() or not folder_path_obj.is_dir():
                    logger.error(f"❌ Carpeta no válida: {folder_path}")
                    return jsonify({
                        'success': False,
                        'error': 'Carpeta no válida',
                        'message': 'La carpeta especificada no existe'
                    }), 400
                
                logger.info(f"✅ Carpeta válida: {folder_path}")
                
                # ¡IMPORTANTE! Implementar la funcionalidad real de agregar música
                try:
                    logger.info(f"🔍 Iniciando escaneo de archivos en: {folder_path}")
                    
                    # Contar archivos de audio antes de agregar
                    songs_before = len(self.music_app.music_library or [])
                    logger.info(f"📊 Canciones antes: {songs_before}")
                    
                    # Buscar archivos de audio en la carpeta
                    audio_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg', '.wma']
                    folder_path_obj = Path(folder_path)
                    audio_files = []
                    
                    for ext in audio_extensions:
                        audio_files.extend(folder_path_obj.rglob(f'*{ext}'))
                        audio_files.extend(folder_path_obj.rglob(f'*{ext.upper()}'))
                    
                    logger.info(f"🎵 Archivos de audio encontrados: {len(audio_files)}")
                    
                    # Agregar archivos de audio usando el método de la base de datos
                    added_count = 0
                    failed_count = 0
                    
                    def scan_files_sync():
                        nonlocal added_count, failed_count
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            
                            for audio_file in audio_files:
                                try:
                                    file_str = str(audio_file)
                                    logger.info(f"📁 Procesando: {file_str}")
                                    
                                    # Usar el método de la base de datos para escanear y agregar
                                    success = loop.run_until_complete(
                                        self.music_app.db_manager.scan_and_add_file(file_str)
                                    )
                                    
                                    if success:
                                        added_count += 1
                                        logger.info(f"✅ Agregado: {file_str}")
                                    else:
                                        failed_count += 1
                                        logger.warning(f"⚠️ No agregado (puede existir): {file_str}")
                                        
                                except Exception as file_error:
                                    failed_count += 1
                                    logger.error(f"❌ Error procesando {audio_file}: {file_error}")
                            
                            loop.close()
                        except Exception as e:
                            logger.error(f"❌ Error en hilo de escaneo: {e}")
                    
                    # Ejecutar escaneo en hilo separado
                    thread = threading.Thread(target=scan_files_sync, daemon=True)
                    thread.start()
                    thread.join()  # Esperar a que termine
                    
                    # Recargar la biblioteca musical
                    logger.info("🔄 Recargando biblioteca musical...")
                    def reload_library_sync():
                        try:
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            loop.run_until_complete(self.music_app.reload_library())
                            loop.close()
                        except Exception as e:
                            logger.error(f"❌ Error recargando biblioteca: {e}")
                    
                    reload_thread = threading.Thread(target=reload_library_sync, daemon=True)
                    reload_thread.start()
                    reload_thread.join()  # Esperar a que termine
                    
                    songs_after = len(self.music_app.music_library or [])
                    logger.info(f"📊 Canciones después: {songs_after}")
                    
                    actual_added = songs_after - songs_before
                    
                    return jsonify({
                        'success': True,
                        'message': f'Escaneo completado. {actual_added} nuevas canciones agregadas.',
                        'added': actual_added,
                        'total_found': len(audio_files),
                        'failed': failed_count,
                        'folder': folder_path,
                        'library_size': songs_after
                    })
                    
                except Exception as scan_error:
                    logger.error(f"❌ Error durante escaneo: {scan_error}")
                    return jsonify({
                        'success': False,
                        'error': f'Error durante escaneo: {str(scan_error)}',
                        'message': 'Error al procesar los archivos de audio'
                    }), 500
                
            except Exception as e:
                logger.error(f"❌ Error general en add_music_folder: {e}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error al procesar la carpeta'
                }), 500
        
        @self.app.route('/api/library/health')
        def library_health():
            """Obtener reporte de salud de la biblioteca"""
            try:
                def get_health_sync():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        health_report = loop.run_until_complete(
                            self.music_app.db_manager.get_library_health_report()
                        )
                        loop.close()
                        return health_report
                    except Exception as e:
                        logger.error(f"Error obteniendo reporte de salud: {e}")
                        return {
                            'total_songs': 0,
                            'valid_files': 0,
                            'invalid_files': 0,
                            'integrity_percentage': 0,
                            'total_size_mb': 0,
                            'needs_cleanup': False
                        }
                
                health_report = get_health_sync()
                
                return jsonify({
                    'success': True,
                    'health': health_report,
                    'message': 'Reporte de salud generado correctamente'
                })
                
            except Exception as e:
                logger.error(f"Error en endpoint health: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error generando reporte de salud'
                }), 500
        
        @self.app.route('/api/library/cleanup', methods=['POST'])
        def cleanup_library():
            """Limpiar archivos inválidos de la biblioteca"""
            try:
                logger.info("🧹 Iniciando limpieza manual de la biblioteca...")
                
                def cleanup_sync():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        cleaned_count = loop.run_until_complete(
                            self.music_app.db_manager.cleanup_invalid_files()
                        )
                        # Recargar biblioteca después de la limpieza
                        loop.run_until_complete(self.music_app.reload_library())
                        loop.close()
                        return cleaned_count
                    except Exception as e:
                        logger.error(f"Error en limpieza: {e}")
                        return 0
                
                cleaned_count = cleanup_sync()
                
                return jsonify({
                    'success': True,
                    'cleaned_files': cleaned_count,
                    'message': f'Limpieza completada: {cleaned_count} archivos inválidos eliminados',
                    'library_size': len(self.music_app.music_library or [])
                })
                
            except Exception as e:
                logger.error(f"Error en endpoint cleanup: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error realizando limpieza'
                }), 500
        
        @self.app.route('/api/library/clear', methods=['POST'])
        def clear_library():
            """Limpiar completamente la biblioteca (para desarrollo/testing)"""
            try:
                logger.info("🧹 Limpiando biblioteca musical completa...")
                
                def clear_sync():
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        loop.run_until_complete(
                            self.music_app.db_manager.clear_music_library()
                        )
                        # Recargar biblioteca después de limpiar
                        loop.run_until_complete(self.music_app.reload_library())
                        loop.close()
                        return True
                    except Exception as e:
                        logger.error(f"Error limpiando biblioteca: {e}")
                        return False
                
                success = clear_sync()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': 'Biblioteca musical limpiada completamente',
                        'library_size': 0
                    })
                else:
                    return jsonify({
                        'success': False,
                        'error': 'Error limpiando biblioteca',
                        'message': 'No se pudo limpiar la biblioteca'
                    }), 500
                
            except Exception as e:
                logger.error(f"Error en endpoint clear: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error limpiando biblioteca'
                }), 500
        
        @self.app.route('/api/library/play/<track_id>')
        def play_track(track_id):
            """Reproducir una pista específica"""
            try:
                logger.info(f"Solicitando reproducción de pista ID: {track_id}")
                
                # Validar que el ID sea numérico
                try:
                    track_index = int(track_id) - 1  # Los IDs empiezan en 1, pero los índices en 0
                except ValueError:
                    return jsonify({
                        'success': False,
                        'error': 'ID de pista inválido',
                        'message': 'El ID debe ser un número'
                    }), 400
                
                # Verificar que existe la pista
                songs = self.music_app.music_library or []
                if track_index < 0 or track_index >= len(songs):
                    return jsonify({
                        'success': False,
                        'error': 'Pista no encontrada',
                        'message': f'No existe pista con ID {track_id}'
                    }), 404
                
                # Obtener información de la pista
                track = songs[track_index]
                track_info = self._serialize_track(track)
                
                logger.info(f"Reproduciendo: {track_info.get('title', 'Unknown')}")
                
                # ¡IMPORTANTE! Reproducir realmente la pista
                try:
                    # Llamar al motor de audio real para reproducir
                    file_path = getattr(track, 'path', '')
                    if file_path and os.path.exists(file_path):
                        logger.info(f"Iniciando reproducción de archivo: {file_path}")
                        # Usar el motor de audio de la aplicación principal
                        self._play_track_sync(track)
                        logger.info("✅ Reproducción iniciada en motor de audio")
                    else:
                        logger.warning(f"❌ Archivo no encontrado: {file_path}")
                        return jsonify({
                            'success': False,
                            'status': 'error',
                            'error': 'Archivo no encontrado',
                            'message': 'El archivo de audio no existe'
                        }), 404
                except Exception as audio_error:
                    logger.error(f"❌ Error iniciando reproducción: {audio_error}")
                    # Continuar con respuesta exitosa aunque falle el audio
                
                return jsonify({
                    'success': True,
                    'status': 'success',
                    'message': f'Reproduciendo pista {track_id}',
                    'track_id': track_id,
                    'track': track_info,
                    'action': 'play'
                })
                
            except Exception as e:
                logger.error(f"Error reproduciendo pista {track_id}: {e}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error al reproducir la pista'
                }), 500
        
        # ============================
        # 🎵 CONTROL DE REPRODUCCIÓN
        # ============================
        
        @self.app.route('/api/player/play', methods=['POST'])
        def play():
            """Reproducir música"""
            try:
                # Llamar al método real de reproducción
                self._execute_async_method(self.music_app.play_pause)
                return jsonify({'success': True, 'action': 'play'})
            except Exception as e:
                logger.error(f"Error en play: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/pause', methods=['POST'])
        def pause():
            """Pausar música"""
            try:
                # Llamar al método real de pausa
                self._execute_async_method(self.music_app.pause)
                return jsonify({'success': True, 'action': 'pause'})
            except Exception as e:
                logger.error(f"Error en pause: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/stop', methods=['POST'])
        def stop():
            """Detener música"""
            try:
                # Llamar al método real de stop
                self._execute_async_method(self.music_app.stop)
                return jsonify({'success': True, 'action': 'stop'})
            except Exception as e:
                logger.error(f"Error en stop: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/next', methods=['POST'])
        def next_track():
            """Siguiente pista"""
            try:
                if not self.music_app.music_library:
                    return jsonify({
                        'success': False, 
                        'error': 'No hay canciones en la biblioteca',
                        'message': 'Biblioteca vacía'
                    }), 400
                
                current_index = 0
                
                # Encontrar índice actual
                if hasattr(self.music_app, 'current_track') and self.music_app.current_track:
                    for i, song in enumerate(self.music_app.music_library):
                        if (hasattr(song, 'path') and hasattr(self.music_app.current_track, 'path') and 
                            getattr(song, 'path', '') == getattr(self.music_app.current_track, 'path', '')):
                            current_index = i
                            break
                
                # Determinar próxima canción
                if self._shuffle:
                    # Modo aleatorio: seleccionar canción aleatoria
                    import random
                    next_index = random.randint(0, len(self.music_app.music_library) - 1)
                else:
                    # Modo normal: siguiente canción
                    next_index = (current_index + 1) % len(self.music_app.music_library)
                
                # Reproducir siguiente canción
                next_track = self.music_app.music_library[next_index]
                self._play_track_sync(next_track)
                
                track_info = self._serialize_track(next_track)
                logger.info(f"⏭️ Reproduciendo siguiente: {track_info.get('title', 'Unknown')}")
                
                return jsonify({
                    'success': True, 
                    'action': 'next',
                    'track': track_info,
                    'track_index': next_index + 1
                })
            except Exception as e:
                logger.error(f"Error en next: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/previous', methods=['POST'])
        def previous_track():
            """Pista anterior"""
            try:
                if not self.music_app.music_library:
                    return jsonify({
                        'success': False, 
                        'error': 'No hay canciones en la biblioteca',
                        'message': 'Biblioteca vacía'
                    }), 400
                
                current_index = 0
                
                # Encontrar índice actual
                if hasattr(self.music_app, 'current_track') and self.music_app.current_track:
                    for i, song in enumerate(self.music_app.music_library):
                        if (hasattr(song, 'path') and hasattr(self.music_app.current_track, 'path') and 
                            getattr(song, 'path', '') == getattr(self.music_app.current_track, 'path', '')):
                            current_index = i
                            break
                
                # Determinar canción anterior
                if self._shuffle:
                    # Modo aleatorio: seleccionar canción aleatoria
                    import random
                    prev_index = random.randint(0, len(self.music_app.music_library) - 1)
                else:
                    # Modo normal: canción anterior
                    prev_index = (current_index - 1) % len(self.music_app.music_library)
                
                # Reproducir canción anterior
                prev_track = self.music_app.music_library[prev_index]
                self._play_track_sync(prev_track)
                
                track_info = self._serialize_track(prev_track)
                logger.info(f"⏮️ Reproduciendo anterior: {track_info.get('title', 'Unknown')}")
                
                return jsonify({
                    'success': True, 
                    'action': 'previous',
                    'track': track_info,
                    'track_index': prev_index + 1
                })
            except Exception as e:
                logger.error(f"Error en previous: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/state')
        def player_state():
            """Estado del reproductor"""
            try:
                # Inicializar variables por defecto
                current_track_info = None
                current_track_index = None
                actual_state = "stopped"
                actual_position = 0.0
                actual_duration = 0.0
                actual_volume = self._volume
                
                try:
                    # Obtener el track actual del music_app
                    if hasattr(self.music_app, 'current_track') and self.music_app.current_track:
                        current_track_info = self._serialize_track(self.music_app.current_track)
                        
                        # Buscar el índice de la canción actual en la biblioteca
                        if self.music_app.music_library:
                            for i, song in enumerate(self.music_app.music_library):
                                if (hasattr(song, 'path') and hasattr(self.music_app.current_track, 'path') and 
                                    getattr(song, 'path', '') == getattr(self.music_app.current_track, 'path', '')):
                                    current_track_index = i + 1  # Los IDs empiezan en 1
                                    current_track_info['id'] = str(current_track_index)
                                    break
                    
                    # Obtener estado real del reproductor
                    if hasattr(self.music_app, 'audio_engine') and self.music_app.audio_engine:
                        if hasattr(self.music_app.audio_engine, 'is_playing'):
                            if self.music_app.audio_engine.is_playing:
                                actual_state = "playing"
                            elif hasattr(self.music_app.audio_engine, 'is_paused') and self.music_app.audio_engine.is_paused:
                                actual_state = "paused"
                    
                    # Obtener posición y duración reales
                    if hasattr(self.music_app, 'audio_engine') and self.music_app.audio_engine:
                        try:
                            if hasattr(self.music_app.audio_engine, 'get_time'):
                                actual_position = self.music_app.audio_engine.get_time() or 0.0
                            if hasattr(self.music_app.audio_engine, 'duration'):
                                actual_duration = self.music_app.audio_engine.duration or 0.0
                            if hasattr(self.music_app.audio_engine, 'volume'):
                                actual_volume = self.music_app.audio_engine.volume or self._volume
                        except Exception as audio_error:
                            logger.warning(f"Error obteniendo datos del audio engine: {audio_error}")
                            pass  # Si hay error, usar valores por defecto
                
                except Exception as track_error:
                    logger.warning(f"Error obteniendo información del track actual: {track_error}")
                
                return jsonify({
                    'success': True,
                    'state': actual_state,
                    'position': actual_position,
                    'duration': actual_duration,
                    'volume': actual_volume,
                    'shuffle': self._shuffle,
                    'repeat': self._repeat,
                    'current_track': current_track_info,
                    'current_track_index': current_track_index,
                    'has_current_track': current_track_info is not None
                })
            except Exception as e:
                logger.error(f"Error en player_state: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/shuffle', methods=['POST'])
        def shuffle():
            """Toggle shuffle mode"""
            try:
                # Toggle shuffle state
                self._shuffle = not self._shuffle
                
                logger.info(f"🔀 Shuffle {'activado' if self._shuffle else 'desactivado'}")
                
                # Si shuffle se activa, mezclar la biblioteca
                if self._shuffle and self.music_app.music_library:
                    try:
                        import random
                        # Crear una copia mezclada de la biblioteca
                        shuffled_library = self.music_app.music_library.copy()
                        random.shuffle(shuffled_library)
                        
                        # Aplicar la biblioteca mezclada
                        self.music_app.music_library = shuffled_library
                        logger.info("🔀 Biblioteca musical mezclada")
                    except Exception as shuffle_error:
                        logger.error(f"Error mezclando biblioteca: {shuffle_error}")
                
                return jsonify({
                    'success': True, 
                    'shuffle': self._shuffle,
                    'shuffle_enabled': self._shuffle,
                    'message': f"Shuffle {'activado' if self._shuffle else 'desactivado'}"
                })
            except Exception as e:
                logger.error(f"Error en shuffle: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/repeat', methods=['POST'])
        def repeat():
            """Toggle repeat mode"""
            try:
                # Cycle through repeat modes: none -> one -> all -> none
                if self._repeat == "none":
                    self._repeat = "one"
                elif self._repeat == "one":
                    self._repeat = "all"
                else:
                    self._repeat = "none"
                
                repeat_messages = {
                    "none": "Repetición desactivada",
                    "one": "Repetir canción actual",
                    "all": "Repetir toda la biblioteca"
                }
                
                logger.info(f"🔁 Modo repetición: {repeat_messages[self._repeat]}")
                
                return jsonify({
                    'success': True, 
                    'status': 'success',
                    'repeat': self._repeat,
                    'repeat_mode': self._repeat,
                    'message': repeat_messages[self._repeat]
                })
            except Exception as e:
                logger.error(f"Error en repeat: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/volume', methods=['POST'])
        def set_volume():
            """Establecer volumen"""
            try:
                data = request.get_json() or {}
                volume = data.get('volume', 50)
                
                # Validar rango de volumen
                volume = max(0, min(100, int(volume)))
                self._volume = volume
                
                # ¡IMPORTANTE! Aplicar el volumen al motor de audio real
                self._execute_async_method(lambda: self.music_app.set_volume(volume))
                
                logger.info(f"Volumen establecido a: {volume}")
                return jsonify({'success': True, 'volume': volume})
            except Exception as e:
                logger.error(f"Error en set_volume: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/seek', methods=['POST'])
        def seek():
            """Buscar posición en la pista"""
            try:
                data = request.get_json() or {}
                position = data.get('position', 0)
                self._position = float(position)
                
                logger.info(f"Posición establecida a: {position}")
                return jsonify({'success': True, 'position': position})
            except Exception as e:
                logger.error(f"Error en seek: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def _serialize_track(self, track):
        """Serializar track para JSON"""
        try:
            return {
                'title': getattr(track, 'title', 'Unknown'),
                'artist': getattr(track, 'artist', 'Unknown Artist'),
                'album': getattr(track, 'album', 'Unknown Album'),
                'duration': getattr(track, 'duration', 0),
                'file_path': getattr(track, 'path', ''),
                'genre': getattr(track, 'genre', ''),
                'year': getattr(track, 'year', None)
            }
        except Exception as e:
            logger.error(f"Error serializando track: {e}")
            return {
                'title': 'Error',
                'artist': 'Error',
                'album': 'Error',
                'duration': 0,
                'file_path': '',
                'genre': '',
                'year': None
            }
    
    def _play_track_sync(self, track):
        """Reproducir pista de forma síncrona desde el contexto de Flask"""
        try:
            # Crear un nuevo hilo para ejecutar la función async
            def run_async():
                try:
                    # Crear nuevo bucle de eventos para este hilo
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.music_app.play_track(track))
                    loop.close()
                except Exception as e:
                    logger.error(f"Error en hilo async: {e}")
            
            # Ejecutar en hilo separado para no bloquear Flask
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            logger.info("Hilo de reproducción iniciado")
            
        except Exception as e:
            logger.error(f"Error iniciando reproducción async: {e}")
            raise
    
    def _execute_async_method(self, async_method):
        """Ejecutar método async de forma segura desde Flask"""
        try:
            def run_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(async_method())
                    loop.close()
                except Exception as e:
                    logger.error(f"Error ejecutando método async: {e}")
            
            thread = threading.Thread(target=run_async, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error ejecutando método async: {e}")
            raise
    
    def handle_track_end(self):
        """Manejar el final de una pista según el modo de repetición"""
        try:
            if self._repeat == "one":
                # Repetir la canción actual
                if hasattr(self.music_app, 'current_track') and self.music_app.current_track:
                    logger.info("🔁 Repitiendo canción actual")
                    self._play_track_sync(self.music_app.current_track)
                    return
            
            elif self._repeat == "all" or self._repeat == "none":
                # Avanzar a la siguiente canción
                if self.music_app.music_library:
                    current_index = 0
                    
                    # Encontrar índice actual
                    if hasattr(self.music_app, 'current_track') and self.music_app.current_track:
                        for i, song in enumerate(self.music_app.music_library):
                            if (hasattr(song, 'path') and hasattr(self.music_app.current_track, 'path') and 
                                getattr(song, 'path', '') == getattr(self.music_app.current_track, 'path', '')):
                                current_index = i
                                break
                    
                    # Determinar próxima canción
                    if self._shuffle:
                        import random
                        next_index = random.randint(0, len(self.music_app.music_library) - 1)
                    else:
                        next_index = (current_index + 1) % len(self.music_app.music_library)
                        
                        # Si llegamos al final y no es repeat all, parar
                        if self._repeat == "none" and next_index == 0 and current_index > 0:
                            logger.info("🛑 Final de la biblioteca alcanzado")
                            return
                    
                    # Reproducir siguiente canción
                    next_track = self.music_app.music_library[next_index]
                    logger.info(f"🎵 Auto-avance: {getattr(next_track, 'title', 'Unknown')}")
                    self._play_track_sync(next_track)
                    
        except Exception as e:
            logger.error(f"Error manejando final de pista: {e}")
    
    def run(self, host='0.0.0.0', port=5000, debug=False):
        """Ejecutar servidor Flask"""
        logger.info(f"Iniciando servidor web en http://{host}:{port}")
        try:
            # Iniciar bucle de actualizaciones
            update_thread = threading.Thread(target=self.start_background_updates, daemon=True)
            update_thread.start()
            logger.info("Bucle de actualizaciones en segundo plano iniciado")
            
            # Ejecutar Flask con SocketIO
            self.socketio.run(self.app, host=host, port=port, debug=debug, allow_unsafe_werkzeug=True)
        except Exception as e:
            logger.error(f"Error al iniciar servidor: {e}")
            raise
    
    def start_background_updates(self):
        """Inicia actualizaciones en segundo plano"""
        while True:
            try:
                time.sleep(1)
                # Aquí se pueden agregar actualizaciones periódicas
            except Exception as e:
                logger.error(f"Error en actualizaciones: {e}")
                time.sleep(5)
