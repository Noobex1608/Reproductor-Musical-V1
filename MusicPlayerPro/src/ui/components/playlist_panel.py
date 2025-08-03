# -*- coding: utf-8 -*-
"""
🎵 PLAYLIST PANEL - PANEL DE LISTA DE REPRODUCCIÓN
==================================================
Widget para mostrar y gestionar la playlist actual
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from typing import Callable, List, Optional

class PlaylistPanel(ctk.CTkFrame):
    """Widget del panel de playlist"""
    
    def __init__(self, parent, track_selected_callback: Callable):
        super().__init__(parent)
        
        self.track_selected_callback = track_selected_callback
        self.current_playlist = []
        self.current_index = 0
        
        self._create_panel()
    
    def _create_panel(self):
        """Crea el panel de playlist"""
        
        # Título y controles
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        self.title_label = ctk.CTkLabel(
            self.header_frame,
            text="🎵 Lista de Reproducción",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(side="left", padx=5, pady=5)
        
        # Botones de control
        self.controls_frame = ctk.CTkFrame(self.header_frame)
        self.controls_frame.pack(side="right", padx=5, pady=5)
        
        self.clear_button = ctk.CTkButton(
            self.controls_frame,
            text="🗑",
            width=30,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self._clear_playlist
        )
        self.clear_button.pack(side="right", padx=2)
        
        self.save_button = ctk.CTkButton(
            self.controls_frame,
            text="💾",
            width=30,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self._save_playlist
        )
        self.save_button.pack(side="right", padx=2)
        
        # Frame para la lista
        self.list_frame = ctk.CTkFrame(self)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Crear Treeview para la playlist
        self.tree = ttk.Treeview(
            self.list_frame,
            columns=("artist", "duration"),
            show="tree headings",
            selectmode="extended"
        )
        
        # Configurar columnas
        self.tree.heading("#0", text="Título")
        self.tree.heading("artist", text="Artista")
        self.tree.heading("duration", text="Duración")
        
        self.tree.column("#0", width=200, minwidth=120)
        self.tree.column("artist", width=120, minwidth=80)
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
        self.tree.bind("<Button-3>", self._on_right_click)  # Menú contextual
        
        # Frame de información
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        self.info_label = ctk.CTkLabel(
            self.info_frame,
            text="Lista vacía - Añade música",
            font=ctk.CTkFont(size=10)
        )
        self.info_label.pack(pady=5)
        
        # Crear menú contextual
        self._create_context_menu()
    
    def _create_context_menu(self):
        """Crea el menú contextual"""
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Reproducir", command=self._play_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Mover arriba", command=self._move_up)
        self.context_menu.add_command(label="Mover abajo", command=self._move_down)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Eliminar", command=self._remove_selected)
    
    def update_playlist(self, playlist: List, current_index: int = 0):
        """Actualiza la playlist completa"""
        self.current_playlist = playlist
        self.current_index = current_index
        self._populate_tree()
    
    def add_track(self, track):
        """Añade una pista a la playlist"""
        self.current_playlist.append(track)
        self._populate_tree()
    
    def remove_track(self, index: int):
        """Elimina una pista por índice"""
        if 0 <= index < len(self.current_playlist):
            self.current_playlist.pop(index)
            if self.current_index >= index and self.current_index > 0:
                self.current_index -= 1
            self._populate_tree()
    
    def clear_playlist(self):
        """Limpia toda la playlist"""
        self.current_playlist = []
        self.current_index = 0
        self._populate_tree()
    
    def _populate_tree(self):
        """Llena el árbol con la playlist actual"""
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Agregar pistas
        for i, track in enumerate(self.current_playlist):
            duration_str = self._format_duration(track.duration)
            
            # Marcar pista actual
            title = track.title
            if i == self.current_index:
                title = f"🎵 {title}"
            
            item = self.tree.insert(
                "",
                "end",
                text=title,
                values=(track.artist, duration_str),
                tags=(str(i),)  # Guardar índice
            )
            
            # Resaltar pista actual
            if i == self.current_index:
                self.tree.selection_set(item)
                self.tree.see(item)
        
        # Actualizar información
        count = len(self.current_playlist)
        if count > 0:
            total_duration = sum(track.duration for track in self.current_playlist)
            total_duration_str = self._format_duration(total_duration)
            self.info_label.configure(
                text=f"{count} pistas - {total_duration_str}"
            )
        else:
            self.info_label.configure(text="Lista vacía - Añade música")
    
    def _format_duration(self, seconds: float) -> str:
        """Formatea la duración en mm:ss"""
        if seconds <= 0:
            return "0:00"
        
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
    
    def _on_double_click(self, event):
        """Evento de doble clic"""
        self._play_selected()
    
    def _on_enter_key(self, event):
        """Evento de tecla Enter"""
        self._play_selected()
    
    def _on_right_click(self, event):
        """Evento de clic derecho para menú contextual"""
        # Seleccionar item bajo el cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def _play_selected(self):
        """Reproduce la pista seleccionada"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            
            if tags:
                index = int(tags[0])
                if 0 <= index < len(self.current_playlist):
                    track = self.current_playlist[index]
                    self.track_selected_callback(track, index)
    
    def _move_up(self):
        """Mueve la pista seleccionada hacia arriba"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            
            if tags:
                index = int(tags[0])
                if index > 0:
                    # Intercambiar pistas
                    self.current_playlist[index], self.current_playlist[index-1] = \
                        self.current_playlist[index-1], self.current_playlist[index]
                    
                    # Ajustar índice actual si es necesario
                    if self.current_index == index:
                        self.current_index -= 1
                    elif self.current_index == index - 1:
                        self.current_index += 1
                    
                    self._populate_tree()
    
    def _move_down(self):
        """Mueve la pista seleccionada hacia abajo"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            tags = self.tree.item(item, "tags")
            
            if tags:
                index = int(tags[0])
                if index < len(self.current_playlist) - 1:
                    # Intercambiar pistas
                    self.current_playlist[index], self.current_playlist[index+1] = \
                        self.current_playlist[index+1], self.current_playlist[index]
                    
                    # Ajustar índice actual si es necesario
                    if self.current_index == index:
                        self.current_index += 1
                    elif self.current_index == index + 1:
                        self.current_index -= 1
                    
                    self._populate_tree()
    
    def _remove_selected(self):
        """Elimina las pistas seleccionadas"""
        selection = self.tree.selection()
        if selection:
            # Obtener índices a eliminar (en orden descendente)
            indices = []
            for item in selection:
                tags = self.tree.item(item, "tags")
                if tags:
                    indices.append(int(tags[0]))
            
            # Ordenar en orden descendente para eliminar correctamente
            indices.sort(reverse=True)
            
            for index in indices:
                if 0 <= index < len(self.current_playlist):
                    self.remove_track(index)
    
    def _clear_playlist(self):
        """Limpia la playlist"""
        self.clear_playlist()
    
    def _save_playlist(self):
        """Guarda la playlist actual"""
        # Por ahora solo mostrar mensaje
        if self.current_playlist:
            # Aquí se implementaría la lógica de guardado
            print(f"Guardando playlist con {len(self.current_playlist)} pistas")
        else:
            print("No hay pistas para guardar")
    
    def get_selected_indices(self):
        """Obtiene los índices de las pistas seleccionadas"""
        selection = self.tree.selection()
        indices = []
        
        for item in selection:
            tags = self.tree.item(item, "tags")
            if tags:
                indices.append(int(tags[0]))
        
        return sorted(indices)
    
    def select_track(self, index: int):
        """Selecciona una pista por índice"""
        if 0 <= index < len(self.current_playlist):
            items = self.tree.get_children()
            if index < len(items):
                item = items[index]
                self.tree.selection_set(item)
                self.tree.see(item)
