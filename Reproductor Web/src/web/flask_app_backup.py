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
from pathlib import Path
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit

from ..core.app import MusicPlayerProApp
from ..core.config_manager import get_config
from .utils import setup_logging

logger = setup_logging(__name__)

class MusicPlayerWebApp:
    """Aplicación web Flask para Music Player Pro"""
    
    def __init__(self, music_app: MusicPlayerProApp):
        """Inicializar aplicación web"""
        self.music_app = music_app
        self.config = get_config()
        
        # Estados internos
        self._playback_state = "stopped"
        self._position = 0.0
        self._duration = 0.0
        self._volume = 50
        
        # Configurar Flask
        self.app = Flask(__name__, 
                        template_folder='../../templates',
                        static_folder='../../static')
        self.app.config['SECRET_KEY'] = 'music-player-pro-secret-key'
        
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
        
        @self.app.route('/api/status')
        def status():
            """Estado de la aplicación"""
            return jsonify({
                'status': 'online',
                'version': '1.0.0',
                'message': 'Music Player Pro funcionando correctamente'
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
                
                # Por ahora retornamos éxito simulado
                return jsonify({
                    'success': True,
                    'message': 'Funcionalidad de agregar carpeta funcionando (simulado)',
                    'added': 0,
                    'folder': folder_path
                })
                
            except Exception as e:
                logger.error(f"❌ Error general en add_music_folder: {e}")
                import traceback
                logger.error(f"❌ Traceback: {traceback.format_exc()}")
                return jsonify({
                    'success': False,
                    'error': str(e),
                    'message': 'Error al procesar la carpeta'
                }), 500
        
        # ============================
        # 🎵 CONTROL DE REPRODUCCIÓN
        # ============================
        
        @self.app.route('/api/player/play', methods=['POST'])
        def play():
            """Reproducir música"""
            try:
                return jsonify({'success': True, 'action': 'play'})
            except Exception as e:
                logger.error(f"Error en play: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
        
        @self.app.route('/api/player/pause', methods=['POST'])
        def pause():
            """Pausar música"""
            try:
                return jsonify({'success': True, 'action': 'pause'})
            except Exception as e:
                logger.error(f"Error en pause: {e}")
                return jsonify({'success': False, 'error': str(e)}), 500
    
    def _serialize_track(self, track):
        """Serializar track para JSON"""
        try:
            return {
                'title': getattr(track, 'title', 'Unknown'),
                'artist': getattr(track, 'artist', 'Unknown Artist'),
                'album': getattr(track, 'album', 'Unknown Album'),
                'duration': getattr(track, 'duration', 0),
                'file_path': getattr(track, 'file_path', ''),
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
