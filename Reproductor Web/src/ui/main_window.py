# -*- coding: utf-8 -*-
"""
🎨 MAIN WINDOW - VENTANA PRINCIPAL DE LA INTERFAZ GRÁFICA
========================================================
Interfaz gráfica moderna del reproductor musical con:
- CustomTkinter para UI moderna
- Diseño responsivo y elegante
- Visualizador integrado
- Controles intuitivos
- Temas personalizables
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import asyncio
import threading
from typing import Optional, Dict, List, Any
from pathlib import Path
import logging
from datetime import timedelta
import json

# Componentes UI personalizados
from .components.player_controls import PlayerControls
from .components.playlist_panel import PlaylistPanel
from .components.library_browser import LibraryBrowser
from .components.visualizer_frame import VisualizerFrame
from .components.volume_control import VolumeControl
from .components.search_bar import SearchBar

logger = logging.getLogger(__name__)

class MainWindow:
    """Ventana principal del reproductor musical"""
    
    def __init__(self, app):
        self.app = app
        self.root = ctk.CTk()
        self._is_closing = False  # Bandera para evitar callbacks después del cierre
        
        # Configuración inicial
        self._setup_window()
        self._setup_theme()
        self._create_ui_components()
        self._setup_callbacks()
        self._setup_layout()
        
        logger.info("Ventana principal inicializada")
    
    def _run_async_safe(self, coro):
        """Ejecuta una corrutina de forma segura desde contexto síncrono"""
        if self._is_closing:  # No ejecutar si la aplicación se está cerrando
            return
            
        try:
            import threading
            import asyncio
            
            def run_in_thread():
                try:
                    # Crear nuevo loop para este hilo
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(coro)
                    loop.close()
                except Exception as e:
                    logger.error(f"Error en operación asíncrona: {e}")
            
            # Ejecutar en hilo separado para no bloquear UI
            thread = threading.Thread(target=run_in_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            logger.error(f"Error ejecutando operación asíncrona: {e}")
    
    def _setup_window(self):
        """Configura la ventana principal"""
        # Título y icono
        self.root.title("🎵 Music Player Pro")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Configurar cierre
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Centrar ventana
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"1400x900+{x}+{y}")
    
    def _setup_theme(self):
        """Configura el tema visual"""
        # Configurar CustomTkinter
        ctk.set_appearance_mode("dark")  # "dark" o "light"
        ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"
        
        # Colores personalizados
        self.colors = {
            'primary': '#1f538d',
            'secondary': '#14375e',
            'accent': '#36719f',
            'background': '#0b1426',
            'surface': '#1a1a2e',
            'text_primary': '#ffffff',
            'text_secondary': '#b8b8b8',
            'success': '#4caf50',
            'warning': '#ff9800',
            'error': '#f44336'
        }
    
    def _create_ui_components(self):
        """Crea todos los componentes de la interfaz"""
        
        # Barra de menú
        self._create_menu_bar()
        
        # Frame principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel superior - Búsqueda y controles
        self.top_panel = ctk.CTkFrame(self.main_frame)
        self.top_panel.pack(fill="x", padx=10, pady=(10, 5))
        
        # Barra de búsqueda
        self.search_bar = SearchBar(self.top_panel, self._on_search)
        self.search_bar.pack(side="left", padx=(10, 20), pady=10)
        
        # Información de la pista actual
        self.track_info_frame = ctk.CTkFrame(self.top_panel)
        self.track_info_frame.pack(side="right", padx=10, pady=10)
        
        self.track_title_label = ctk.CTkLabel(
            self.track_info_frame,
            text="Selecciona una pista",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.track_title_label.pack(padx=10, pady=(10, 0))
        
        self.track_artist_label = ctk.CTkLabel(
            self.track_info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.track_artist_label.pack(padx=10, pady=(0, 10))
        
        # Panel central - División en 3 columnas
        self.center_panel = ctk.CTkFrame(self.main_frame)
        self.center_panel.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Configurar grid
        self.center_panel.grid_columnconfigure(0, weight=1)  # Biblioteca
        self.center_panel.grid_columnconfigure(1, weight=2)  # Visualizador
        self.center_panel.grid_columnconfigure(2, weight=1)  # Playlist
        self.center_panel.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo - Biblioteca musical
        self.library_frame = ctk.CTkFrame(self.center_panel)
        self.library_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        
        self.library_browser = LibraryBrowser(self.library_frame, self._on_track_selected)
        self.library_browser.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel central - Visualizador
        self.visualizer_frame = VisualizerFrame(self.center_panel, self.app.visual_manager)
        self.visualizer_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=10)
        
        # Conectar visualizador al visual manager
        self.app.visual_manager.visualizer_frame = self.visualizer_frame
        
        # Panel derecho - Playlist actual
        self.playlist_frame = ctk.CTkFrame(self.center_panel)
        self.playlist_frame.grid(row=0, column=2, sticky="nsew", padx=(5, 0), pady=10)
        
        self.playlist_panel = PlaylistPanel(self.playlist_frame, self._on_playlist_track_selected)
        self.playlist_panel.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Panel inferior - Controles de reproducción
        self.bottom_panel = ctk.CTkFrame(self.main_frame)
        self.bottom_panel.pack(fill="x", padx=10, pady=(5, 10))
        
        # Controles de reproducción
        self.player_controls = PlayerControls(
            self.bottom_panel,
            self._on_play_pause,
            self._on_previous,
            self._on_next,
            self._on_seek
        )
        self.player_controls.pack(side="left", padx=10, pady=10)
        
        # Control de volumen
        self.volume_control = VolumeControl(self.bottom_panel, self._on_volume_change)
        self.volume_control.pack(side="right", padx=10, pady=10)
        
        # Barra de estado
        self.status_bar = ctk.CTkLabel(
            self.main_frame,
            text="Listo - Carga tu música para comenzar",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        )
        self.status_bar.pack(side="bottom", fill="x", padx=10, pady=(0, 5))
    
    def _create_menu_bar(self):
        """Crea la barra de menú"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Abrir archivos...", command=self._open_files)
        file_menu.add_command(label="Abrir carpeta...", command=self._open_folder)
        file_menu.add_separator()
        file_menu.add_command(label="Importar playlist...", command=self._import_playlist)
        file_menu.add_command(label="Exportar playlist...", command=self._export_playlist)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self._on_closing)
        
        # Menú Reproducción
        playback_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Reproducción", menu=playback_menu)
        playback_menu.add_command(label="Reproducir/Pausar", command=self._on_play_pause)
        playback_menu.add_command(label="Detener", command=self._on_stop)
        playback_menu.add_command(label="Anterior", command=self._on_previous)
        playback_menu.add_command(label="Siguiente", command=self._on_next)
        playback_menu.add_separator()
        playback_menu.add_command(label="Aleatorio", command=self._toggle_shuffle)
        playback_menu.add_command(label="Repetir", command=self._cycle_repeat)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Pantalla completa", command=self._toggle_fullscreen)
        view_menu.add_command(label="Visualizador", command=self._toggle_visualizer)
        view_menu.add_separator()
        view_menu.add_command(label="Tema oscuro", command=self._toggle_theme)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="Ecualizador", command=self._open_equalizer)
        tools_menu.add_command(label="Efectos de audio", command=self._open_audio_effects)
        tools_menu.add_command(label="Configuración", command=self._open_settings)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Atajos de teclado", command=self._show_shortcuts)
        help_menu.add_command(label="Acerca de", command=self._show_about)
    
    def _setup_callbacks(self):
        """Configura los callbacks de la aplicación"""
        # Registrar callbacks en la aplicación
        self.app.register_callback('track_changed', self._on_track_changed)
        self.app.register_callback('playback_state_changed', self._on_playback_state_changed)
        self.app.register_callback('position_changed', self._on_position_changed)
        self.app.register_callback('volume_changed', self._on_volume_changed_callback)
        self.app.register_callback('playlist_changed', self._on_playlist_changed)
        
        # Configurar atajos de teclado
        self._setup_keybindings()
    
    def _setup_keybindings(self):
        """Configura atajos de teclado"""
        self.root.bind('<space>', lambda e: self._on_play_pause())
        self.root.bind('<Right>', lambda e: self._on_next())
        self.root.bind('<Left>', lambda e: self._on_previous())
        self.root.bind('<Up>', lambda e: self._volume_up())
        self.root.bind('<Down>', lambda e: self._volume_down())
        self.root.bind('<Control-o>', lambda e: self._open_files())
        self.root.bind('<Control-f>', lambda e: self.search_bar.focus())
        self.root.bind('<F11>', lambda e: self._toggle_fullscreen())
        self.root.bind('<Escape>', lambda e: self._exit_fullscreen())
    
    def _setup_layout(self):
        """Configura el layout inicial"""
        # Cargar biblioteca musical inicial usando threading
        import threading
        thread = threading.Thread(target=self._load_initial_library_sync)
        thread.daemon = True
        thread.start()
        
        # Configurar estado inicial
        self._update_ui_state()
    
    # EVENTOS DE LA APLICACIÓN
    
    def _on_track_changed(self, track):
        """Callback cuando cambia la pista actual"""
        if track:
            self.track_title_label.configure(text=track.title)
            self.track_artist_label.configure(text=f"{track.artist} - {track.album}")
            self.root.title(f"🎵 {track.artist} - {track.title} | Music Player Pro")
            self.status_bar.configure(text=f"Reproduciendo: {track.artist} - {track.title}")
        else:
            self.track_title_label.configure(text="Selecciona una pista")
            self.track_artist_label.configure(text="")
            self.root.title("🎵 Music Player Pro")
            self.status_bar.configure(text="Listo")
    
    def _on_playback_state_changed(self, state):
        """Callback cuando cambia el estado de reproducción"""
        self.player_controls.update_state(state)
        
        if state == "playing":
            self.status_bar.configure(text="Reproduciendo...")
        elif state == "paused":
            self.status_bar.configure(text="Pausado")
        elif state == "stopped":
            self.status_bar.configure(text="Detenido")
        elif state == "loading":
            self.status_bar.configure(text="Cargando...")
    
    def _on_position_changed(self, data):
        """Callback cuando cambia la posición de reproducción"""
        position = data.get('position', 0)
        duration = data.get('duration', 0)
        
        # Actualizar barra de progreso en PlayerControls
        if hasattr(self, 'player_controls'):
            self.player_controls.update_progress(position, duration)
    
    def _on_volume_changed_callback(self, volume):
        """Callback cuando cambia el volumen"""
        self.volume_control.set_volume(volume)
    
    def _on_playlist_changed(self, data):
        """Callback cuando cambia la playlist"""
        playlist = data.get('playlist', [])
        current_index = data.get('current_index', 0)
        self.playlist_panel.update_playlist(playlist, current_index)
    
    # EVENTOS DE CONTROLES
    
    def _on_play_pause(self):
        """Evento de reproducir/pausar"""
        self._run_async_safe(self.app.play_pause())
    
    def _on_previous(self):
        """Evento de pista anterior"""
        self._run_async_safe(self.app.previous_track())
    
    def _on_next(self):
        """Evento de siguiente pista"""
        self._run_async_safe(self.app.next_track())
    
    def _on_stop(self):
        """Evento de detener"""
        self._run_async_safe(self.app.stop())
    
    def _on_seek(self, position_seconds):
        """Evento de búsqueda en la pista"""
        if self.app.duration > 0:
            # El position_seconds ya viene en segundos desde player_controls
            # Convertir a porcentaje para VLC (0.0 - 1.0)
            seek_percentage = position_seconds / self.app.duration
            seek_percentage = max(0.0, min(1.0, seek_percentage))  # Limitar entre 0-1
            self._run_async_safe(self.app.seek(seek_percentage))
    
    def _on_progress_change(self, value):
        """Evento de cambio en barra de progreso"""
        # Solo buscar si el usuario está arrastrando
        if hasattr(self, '_dragging_progress') and self._dragging_progress:
            self._on_seek(value)
    
    def _on_volume_change(self, volume):
        """Evento de cambio de volumen"""
        self._run_async_safe(self.app.set_volume(int(volume)))
    
    def _on_track_selected(self, track):
        """Evento cuando se selecciona una pista en la biblioteca"""
        # Crear playlist completa y reproducir la pista seleccionada
        async def select_and_play():
            # Obtener todas las pistas de la biblioteca
            all_tracks = await self.app.get_all_tracks()
            
            # Encontrar el índice de la pista seleccionada
            track_index = 0
            for i, t in enumerate(all_tracks):
                if t.id == track.id:
                    track_index = i
                    break
            
            # Establecer playlist completa y comenzar desde la pista seleccionada
            await self.app.set_playlist(all_tracks, track_index)
            await self.app.play_track(track)
        
        self._run_async_safe(select_and_play())
    
    def _on_playlist_track_selected(self, track, index):
        """Evento cuando se selecciona una pista en la playlist"""
        async def select_and_play():
            self.app.current_index = index
            await self.app.play_track(track)
        
        self._run_async_safe(select_and_play())
    
    def _on_search(self, query):
        """Evento de búsqueda"""
        if query:
            self._run_async_safe(self._perform_search(query))
        else:
            self.library_browser.show_all_tracks()
    
    # FUNCIONES DE ARCHIVO
    
    def _open_files(self):
        """Abre archivos de música"""
        filetypes = [
            ("Archivos de audio", "*.mp3;*.flac;*.wav;*.ogg;*.m4a;*.aac"),
            ("MP3", "*.mp3"),
            ("FLAC", "*.flac"),
            ("WAV", "*.wav"),
            ("OGG", "*.ogg"),
            ("Todos los archivos", "*.*")
        ]
        
        files = filedialog.askopenfilenames(
            title="Seleccionar archivos de música",
            filetypes=filetypes
        )
        
        if files:
            # Usar threading en lugar de asyncio
            import threading
            thread = threading.Thread(target=self._import_files_sync, args=(files,))
            thread.daemon = True
            thread.start()
    
    def _open_folder(self):
        """Abre una carpeta de música"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de música")
        if folder:
            # Usar threading en lugar de asyncio
            import threading  
            thread = threading.Thread(target=self._import_folder_sync, args=(folder,))
            thread.daemon = True
            thread.start()
    
    async def _import_files(self, files):
        """Importa archivos a la biblioteca"""
        try:
            self.status_bar.configure(text="Importando archivos...")
            count = 0
            
            for file_path in files:
                try:
                    # Actualizar progreso
                    count += 1
                    try:
                        if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                            self.status_bar.configure(text=f"Procesando... {count}/{len(files)}")
                    except Exception:
                        pass
                    
                    # Extraer metadatos
                    metadata = self._extract_metadata_sync(file_path)
                    if metadata:
                        # Agregar a la base de datos
                        result = await self.app.db_manager.add_song(metadata)
                        if result:
                            logger.info(f"✅ Archivo importado: {metadata['title']}")
                        else:
                            logger.warning(f"No se pudo importar: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error importando {file_path}: {e}")
            
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text=f"Importados {count} archivos")
            except Exception:
                pass  # La ventana ya se cerró
            await self._reload_library()
            
        except Exception as e:
            logger.error(f"Error en importación: {e}")
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text="Error en importación")
            except Exception:
                pass  # La ventana ya se cerró
    
    async def _import_folder(self, folder_path):
        """Importa una carpeta completa"""
        try:
            self.status_bar.configure(text="Escaneando carpeta...")
            
            # Buscar archivos de audio recursivamente
            audio_extensions = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac'}
            files = []
            
            for ext in audio_extensions:
                files.extend(Path(folder_path).rglob(f"*{ext}"))
            
            if files:
                await self._import_files([str(f) for f in files])
            else:
                self.status_bar.configure(text="No se encontraron archivos de audio")
                
        except Exception as e:
            logger.error(f"Error escaneando carpeta: {e}")
            self.status_bar.configure(text="Error escaneando carpeta")
    
    def _import_files_sync(self, files):
        """Versión síncrona de import_files"""
        try:
            self.status_bar.configure(text="Importando archivos...")
            count = 0
            
            for file_path in files:
                try:
                    # Actualizar progreso
                    count += 1
                    try:
                        if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                            self.status_bar.configure(text=f"Procesando... {count}/{len(files)}")
                    except Exception:
                        pass
                    
                    # Procesar archivo de audio
                    success = self._process_audio_file_sync(file_path)
                    if not success:
                        logger.warning(f"No se pudo procesar: {file_path}")
                    
                except Exception as e:
                    logger.error(f"Error importando {file_path}: {e}")
            
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text=f"Importados {count} archivos")
            except Exception:
                pass
            
        except Exception as e:
            logger.error(f"Error en importación: {e}")
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text="Error en importación")
            except Exception:
                pass
    
    def _process_audio_file_sync(self, file_path):
        """Procesa un archivo de audio y lo agrega a la base de datos"""
        try:
            from pathlib import Path
            import os
            
            # Verificar que el archivo exista
            if not os.path.exists(file_path):
                return False
            
            # Extraer metadatos básicos
            metadata = self._extract_metadata_sync(file_path)
            if not metadata:
                return False
            
            # Ejecutar análisis de IA en un hilo
            import threading
            import asyncio
            
            def add_to_db():
                try:
                    # Crear nuevo loop para este hilo
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Agregar a la base de datos
                    result = loop.run_until_complete(self.app.db_manager.add_song(metadata))
                    loop.close()
                    
                    return result is not None
                except Exception as e:
                    logger.error(f"Error agregando a DB: {e}")
                    return False
            
            # Ejecutar en hilo separado para no bloquear UI
            db_thread = threading.Thread(target=add_to_db)
            db_thread.start()
            db_thread.join(timeout=10)  # Timeout de 10 segundos
            
            return True
            
        except Exception as e:
            logger.error(f"Error procesando archivo {file_path}: {e}")
            return False
    
    def _extract_metadata_sync(self, file_path):
        """Extrae metadatos de un archivo de audio"""
        try:
            from pathlib import Path
            import os
            
            # Información básica del archivo
            file_path_obj = Path(file_path)
            file_stats = file_path_obj.stat()
            
            metadata = {
                'file_path': str(file_path),
                'title': file_path_obj.stem,  # Nombre sin extensión
                'artist': 'Artista Desconocido',
                'album': 'Álbum Desconocido',
                'genre': 'Desconocido',
                'duration': 0.0,
                'file_size': file_stats.st_size,
            }
            
            # Intentar extraer metadatos con mutagen
            try:
                from mutagen import File
                audio_file = File(file_path)
                
                if audio_file:
                    # Título
                    if 'TIT2' in audio_file:  # MP3
                        metadata['title'] = str(audio_file['TIT2'][0])
                    elif 'TITLE' in audio_file:  # FLAC/OGG
                        metadata['title'] = str(audio_file['TITLE'][0])
                    
                    # Artista
                    if 'TPE1' in audio_file:  # MP3
                        metadata['artist'] = str(audio_file['TPE1'][0])
                    elif 'ARTIST' in audio_file:  # FLAC/OGG
                        metadata['artist'] = str(audio_file['ARTIST'][0])
                    
                    # Álbum
                    if 'TALB' in audio_file:  # MP3
                        metadata['album'] = str(audio_file['TALB'][0])
                    elif 'ALBUM' in audio_file:  # FLAC/OGG
                        metadata['album'] = str(audio_file['ALBUM'][0])
                    
                    # Género
                    if 'TCON' in audio_file:  # MP3
                        metadata['genre'] = str(audio_file['TCON'][0])
                    elif 'GENRE' in audio_file:  # FLAC/OGG
                        metadata['genre'] = str(audio_file['GENRE'][0])
                    
                    # Año
                    if 'TDRC' in audio_file:  # MP3
                        metadata['year'] = int(str(audio_file['TDRC'][0])[:4])
                    elif 'DATE' in audio_file:  # FLAC/OGG
                        metadata['year'] = int(str(audio_file['DATE'][0])[:4])
                    
                    # Duración
                    if hasattr(audio_file, 'info') and audio_file.info:
                        metadata['duration'] = float(audio_file.info.length)
                        if hasattr(audio_file.info, 'bitrate'):
                            metadata['bitrate'] = audio_file.info.bitrate
                        if hasattr(audio_file.info, 'sample_rate'):
                            metadata['sample_rate'] = audio_file.info.sample_rate
                            
            except Exception as e:
                logger.warning(f"No se pudieron extraer metadatos con mutagen: {e}")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extrayendo metadatos de {file_path}: {e}")
            return None
    
    def _import_folder_sync(self, folder_path):
        """Versión síncrona de import_folder"""
        try:
            self.status_bar.configure(text="Escaneando carpeta...")
            
            # Buscar archivos de audio recursivamente
            audio_extensions = {'.mp3', '.flac', '.wav', '.ogg', '.m4a', '.aac'}
            files = []
            
            for ext in audio_extensions:
                files.extend(Path(folder_path).rglob(f"*{ext}"))
                
            if files:
                self._import_files_sync([str(f) for f in files])
            else:
                try:
                    if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                        self.status_bar.configure(text="No se encontraron archivos de audio")
                except Exception:
                    pass  # La ventana ya se cerró
                
        except Exception as e:
            logger.error(f"Error escaneando carpeta: {e}")
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text="Error escaneando carpeta")
            except Exception:
                pass  # La ventana ya se cerró
    
    # FUNCIONES AUXILIARES
    
    def _format_time(self, seconds):
        """Formatea tiempo en mm:ss"""
        if seconds < 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def _volume_up(self):
        """Sube el volumen"""
        new_volume = min(100, self.app.volume + 5)
        self._run_async_safe(self.app.set_volume(new_volume))
    
    def _volume_down(self):
        """Baja el volumen"""
        new_volume = max(0, self.app.volume - 5)
        self._run_async_safe(self.app.set_volume(new_volume))
    
    async def _perform_search(self, query):
        """Realiza búsqueda en la biblioteca"""
        try:
            results = await self.app.search_tracks(query)
            self.library_browser.show_search_results(results)
            self.status_bar.configure(text=f"Encontradas {len(results)} pistas")
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            self.status_bar.configure(text="Error en búsqueda")
    
    async def _load_initial_library(self):
        """Carga la biblioteca musical inicial"""
        try:
            await self.app._load_music_library()
            self.library_browser.update_library(self.app.music_library)
            self.status_bar.configure(text=f"Biblioteca cargada: {len(self.app.music_library)} pistas")
        except Exception as e:
            logger.error(f"Error cargando biblioteca: {e}")
            self.status_bar.configure(text="Error cargando biblioteca")
    
    def _load_initial_library_sync(self):
        """Versión síncrona de cargar biblioteca inicial"""
        try:
            import asyncio
            import threading
            
            def load_library():
                try:
                    # Crear nuevo loop para este hilo
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    # Cargar biblioteca
                    loop.run_until_complete(self.app._load_music_library())
                    
                    # Actualizar UI
                    if hasattr(self, 'library_browser'):
                        self.library_browser.update_library(self.app.music_library)
                    
                    try:
                        if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                            self.status_bar.configure(text=f"Biblioteca: {len(self.app.music_library)} pistas")
                    except Exception:
                        pass
                    
                    loop.close()
                    
                except Exception as e:
                    logger.error(f"Error cargando biblioteca: {e}")
                    try:
                        if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                            self.status_bar.configure(text="Error cargando biblioteca")
                    except Exception:
                        pass
            
            # Ejecutar en hilo separado
            library_thread = threading.Thread(target=load_library)
            library_thread.start()
            
        except Exception as e:
            logger.error(f"Error en _load_initial_library_sync: {e}")
            try:
                if hasattr(self, 'status_bar') and self.status_bar and self.status_bar.winfo_exists():
                    self.status_bar.configure(text="Error cargando biblioteca")
            except Exception:
                pass
    
    async def _reload_library(self):
        """Recarga la biblioteca musical"""
        await self._load_initial_library()
    
    def _update_ui_state(self):
        """Actualiza el estado de la UI"""
        # Configurar volumen inicial
        self.volume_control.set_volume(self.app.volume)
    
    # EVENTOS DE MENÚ
    
    def _import_playlist(self):
        """Importa una playlist"""
        messagebox.showinfo("Info", "Función de importar playlist no implementada aún")
    
    def _export_playlist(self):
        """Exporta la playlist actual"""
        messagebox.showinfo("Info", "Función de exportar playlist no implementada aún")
    
    def _toggle_shuffle(self):
        """Alterna modo aleatorio"""
        enabled = self.app.toggle_shuffle()
        self.status_bar.configure(text=f"Aleatorio: {'Activado' if enabled else 'Desactivado'}")
    
    def _cycle_repeat(self):
        """Cambia modo de repetición"""
        mode = self.app.cycle_repeat_mode()
        mode_text = {"none": "Desactivado", "one": "Una pista", "all": "Todas"}
        self.status_bar.configure(text=f"Repetir: {mode_text.get(mode, mode)}")
    
    def _toggle_fullscreen(self):
        """Alterna pantalla completa"""
        self.root.attributes('-fullscreen', not self.root.attributes('-fullscreen'))
    
    def _exit_fullscreen(self):
        """Sale de pantalla completa"""
        self.root.attributes('-fullscreen', False)
    
    def _toggle_visualizer(self):
        """Alterna visualizador"""
        messagebox.showinfo("Info", "Función de alternar visualizador no implementada aún")
    
    def _toggle_theme(self):
        """Cambia tema"""
        current = ctk.get_appearance_mode()
        new_mode = "light" if current == "Dark" else "dark"
        ctk.set_appearance_mode(new_mode)
    
    def _open_equalizer(self):
        """Abre ecualizador"""
        messagebox.showinfo("Info", "Ecualizador no implementado aún")
    
    def _open_audio_effects(self):
        """Abre efectos de audio"""
        messagebox.showinfo("Info", "Efectos de audio no implementados aún")
    
    def _open_settings(self):
        """Abre configuración"""
        messagebox.showinfo("Info", "Configuración no implementada aún")
    
    def _show_shortcuts(self):
        """Muestra atajos de teclado"""
        shortcuts = """
        ATAJOS DE TECLADO:
        
        Espacio - Reproducir/Pausar
        ← - Pista anterior
        → - Siguiente pista
        ↑ - Subir volumen
        ↓ - Bajar volumen
        Ctrl+O - Abrir archivos
        Ctrl+F - Buscar
        F11 - Pantalla completa
        Esc - Salir pantalla completa
        """
        messagebox.showinfo("Atajos de teclado", shortcuts)
    
    def _show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = """
        🎵 MUSIC PLAYER PRO
        
        Reproductor musical de próxima generación
        
        Características:
        • Motor de audio VLC profesional
        • Visualizador de espectro 3D
        • IA para recomendaciones
        • Efectos visuales avanzados
        • Soporte todos los formatos
        
        Versión: 1.0.0
        """
        messagebox.showinfo("Acerca de Music Player Pro", about_text)
    
    def _on_closing(self):
        """Evento de cierre de ventana"""
        try:
            self._is_closing = True  # Establecer bandera de cierre
            
            # Cancelar todos los callbacks pendientes de tkinter
            try:
                self.root.after_cancel('all')
            except:
                pass
            
            # Cerrar aplicación sin usar asyncio desde contexto síncrono
            import threading
            
            def shutdown_async():
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(self.app.shutdown())
                    loop.close()
                except Exception as e:
                    logger.error(f"Error en shutdown: {e}")
            
            # Ejecutar shutdown en hilo separado
            shutdown_thread = threading.Thread(target=shutdown_async, daemon=True)
            shutdown_thread.start()
            
            # Cerrar ventana inmediatamente
            self.root.quit()
            self.root.destroy()
            
        except Exception as e:
            logger.error(f"Error cerrando aplicación: {e}")
            self.root.destroy()
    
    def run(self):
        """Inicia el bucle principal de la UI"""
        try:
            logger.info("Iniciando interfaz gráfica...")
            self.root.mainloop()
        except Exception as e:
            logger.error(f"Error en interfaz gráfica: {e}")
            raise
