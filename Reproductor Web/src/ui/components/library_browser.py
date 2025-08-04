# -*- coding: utf-8 -*-
"""
📚 LIBRARY BROWSER - NAVEGADOR DE BIBLIOTECA MUSICAL
===================================================
Widget para navegar y mostrar la biblioteca musical
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

class LibraryBrowser(ctk.CTkFrame):
    """Widget para navegar la biblioteca musical"""
    
    def __init__(self, parent, track_selected_callback: Callable):
        super().__init__(parent)
        
        self.track_selected_callback = track_selected_callback
        self.current_tracks = []
        self.all_tracks = []
        
        self._create_browser()
    
    def _create_browser(self):
        """Crea el navegador de biblioteca"""
        
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="📚 Biblioteca Musical",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Frame para filtros
        self.filter_frame = ctk.CTkFrame(self)
        self.filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Dropdown para vista
        self.view_var = ctk.StringVar(value="Todas")
        self.view_dropdown = ctk.CTkOptionMenu(
            self.filter_frame,
            variable=self.view_var,
            values=["Todas", "Artistas", "Álbumes", "Géneros"],
            command=self._on_view_change
        )
        self.view_dropdown.pack(side="left", padx=5, pady=5)
        
        # Botón actualizar
        self.refresh_button = ctk.CTkButton(
            self.filter_frame,
            text="🔄",
            width=30,
            command=self._refresh_library
        )
        self.refresh_button.pack(side="right", padx=5, pady=5)
        
        # Frame para lista
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear Treeview para la lista
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("artist", "album", "duration"),
            show="tree headings",
            selectmode="extended"
        )
        
        # Configurar columnas
        self.tree.heading("#0", text="Título")
        self.tree.heading("artist", text="Artista")
        self.tree.heading("album", text="Álbum")
        self.tree.heading("duration", text="Duración")
        
        self.tree.column("#0", width=200, minwidth=150)
        self.tree.column("artist", width=150, minwidth=100)
        self.tree.column("album", width=150, minwidth=100)
        self.tree.column("duration", width=80, minwidth=60)
        
        # Scrollbar para la lista
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Pack treeview y scrollbar
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Configurar eventos
        self.tree.bind("<Double-1>", self._on_double_click)
        self.tree.bind("<Return>", self._on_enter_key)
        
        # Frame de información
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Cargando biblioteca...",
            font=ctk.CTkFont(size=10)
        )
        self.info_label.pack(pady=5)
    
    def update_library(self, tracks: List):
        """Actualiza la biblioteca con nuevas pistas"""
        self.all_tracks = tracks
        self.current_tracks = tracks
        self._populate_tree()
    
    def show_search_results(self, tracks: List):
        """Muestra resultados de búsqueda"""
        self.current_tracks = tracks
        self._populate_tree()
    
    def show_all_tracks(self):
        """Muestra todas las pistas"""
        self.current_tracks = self.all_tracks
        self._populate_tree()
    
    def _populate_tree(self):
        """Llena el árbol con las pistas actuales"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar pistas
        for track in self.current_tracks:
            duration_str = self._format_duration(track.duration)
            
            self.tree.insert(
                "",
                "end",
                text=track.title,
                values=(track.artist, track.album, duration_str),
                tags=(track.id,)  # Guardar ID de la pista
            )
        
        # Actualizar información
        count = len(self.current_tracks)
        total_duration = sum(track.duration for track in self.current_tracks)
        total_duration_str = self._format_duration(total_duration)
        
        self.info_label.configure(
            text=f"{count} pistas - {total_duration_str}"
        )
    
    def _format_duration(self, seconds: float) -> str:
        """Formatea la duración en mm:ss"""
        if seconds <= 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def _on_view_change(self, view: str):
        """Evento cuando cambia la vista"""
        if view == "Todas":
            self.show_all_tracks()
        elif view == "Artistas":
            self._show_artists_view()
        elif view == "Álbumes":
            self._show_albums_view()
        elif view == "Géneros":
            self._show_genres_view()
    
    def _show_artists_view(self):
        """Muestra vista por artistas"""
        # Agrupar por artista
        artists = {}
        for track in self.all_tracks:
            artist = track.artist
            if artist not in artists:
                artists[artist] = []
            artists[artist].append(track)
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar artistas como nodos padre
        for artist, tracks in sorted(artists.items()):
            artist_node = self.tree.insert(
                "",
                "end",
                text=f"🎤 {artist}",
                values=("", "", f"{len(tracks)} pistas"),
                open=False
            )
            
            # Agregar pistas del artista
            for track in tracks:
                duration_str = self._format_duration(track.duration)
                self.tree.insert(
                    artist_node,
                    "end",
                    text=track.title,
                    values=("", track.album, duration_str),
                    tags=(track.id,)
                )
    
    def _show_albums_view(self):
        """Muestra vista por álbumes"""
        # Agrupar por álbum
        albums = {}
        for track in self.all_tracks:
            album_key = f"{track.artist} - {track.album}"
            if album_key not in albums:
                albums[album_key] = []
            albums[album_key].append(track)
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar álbumes como nodos padre
        for album_key, tracks in sorted(albums.items()):
            album_node = self.tree.insert(
                "",
                "end",
                text=f"💿 {album_key}",
                values=("", "", f"{len(tracks)} pistas"),
                open=False
            )
            
            # Ordenar pistas por número de pista
            tracks.sort(key=lambda x: x.track_number or 0)
            
            # Agregar pistas del álbum
            for track in tracks:
                duration_str = self._format_duration(track.duration)
                track_num = f"{track.track_number:02d}. " if track.track_number else ""
                self.tree.insert(
                    album_node,
                    "end",
                    text=f"{track_num}{track.title}",
                    values=("", "", duration_str),
                    tags=(track.id,)
                )
    
    def _show_genres_view(self):
        """Muestra vista por géneros"""
        # Agrupar por género
        genres = {}
        for track in self.all_tracks:
            genre = track.genre or "Desconocido"
            if genre not in genres:
                genres[genre] = []
            genres[genre].append(track)
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar géneros como nodos padre
        for genre, tracks in sorted(genres.items()):
            genre_node = self.tree.insert(
                "",
                "end",
                text=f"🎵 {genre}",
                values=("", "", f"{len(tracks)} pistas"),
                open=False
            )
            
            # Agregar pistas del género
            for track in tracks:
                duration_str = self._format_duration(track.duration)
                self.tree.insert(
                    genre_node,
                    "end",
                    text=track.title,
                    values=(track.artist, track.album, duration_str),
                    tags=(track.id,)
                )
    
    def _on_double_click(self, event):
        """Evento de doble clic"""
        self._play_selected_track()
    
    def _on_enter_key(self, event):
        """Evento de tecla Enter"""
        self._play_selected_track()
    
    def _play_selected_track(self):
        """Reproduce la pista seleccionada"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            
            if tags:
                track_id = tags[0]
                # Buscar la pista por ID
                track = self._find_track_by_id(track_id)
                if track:
                    self.track_selected_callback(track)
    
    def _find_track_by_id(self, track_id: str):
        """Busca una pista por ID"""
        for track in self.all_tracks:
            if track.id == track_id:
                return track
        return None
    
    def _refresh_library(self):
        """Actualizar biblioteca"""
        self.info_label.configure(text="Actualizando biblioteca...")
        # Aquí se podría implementar la lógica de actualización
        # Por ahora solo refrescamos la vista
        self._populate_tree()
    
    def get_selected_tracks(self):
        """Obtiene las pistas seleccionadas"""
        selection = self.tree.selection()
        tracks = []
        
        for item in selection:
            tags = self.tree.item(item, "tags")
            if tags:
                track_id = tags[0]
                track = self._find_track_by_id(track_id)
                if track:
                    tracks.append(track)
        
        return tracks
