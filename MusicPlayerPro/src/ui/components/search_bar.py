# -*- coding: utf-8 -*-
"""
🔍 SEARCH BAR - BARRA DE BÚSQUEDA
=================================
Widget de búsqueda con autocompletado y filtros
"""

import customtkinter as ctk
from typing import Callable
import threading
import time

class SearchBar(ctk.CTkFrame):
    """Widget de barra de búsqueda"""
    
    def __init__(self, parent, search_callback: Callable):
        super().__init__(parent)
        
        self.search_callback = search_callback
        self.search_delay = 0.5  # Delay en segundos antes de buscar
        self.search_timer = None
        
        self._create_search_bar()
    
    def _create_search_bar(self):
        """Crea la barra de búsqueda"""
        
        # Ícono de búsqueda
        self.search_icon = ctk.CTkLabel(
            self,
            text="🔍",
            font=ctk.CTkFont(size=16)
        )
        self.search_icon.pack(side="left", padx=(10, 5))
        
        # Campo de entrada
        self.search_entry = ctk.CTkEntry(
            self,
            placeholder_text="Buscar música...",
            width=300,
            height=35
        )
        self.search_entry.pack(side="left", padx=5)
        
        # Configurar eventos
        self.search_entry.bind('<KeyRelease>', self._on_key_release)
        self.search_entry.bind('<Return>', self._on_enter)
        
        # Botón limpiar
        self.clear_button = ctk.CTkButton(
            self,
            text="✕",
            width=30,
            height=35,
            font=ctk.CTkFont(size=12),
            command=self._clear_search
        )
        self.clear_button.pack(side="left", padx=(5, 10))
    
    def _on_key_release(self, event):
        """Evento cuando se suelta una tecla"""
        # Cancelar timer anterior si existe
        if self.search_timer:
            self.search_timer.cancel()
        
        # Iniciar nuevo timer para búsqueda con delay
        query = self.search_entry.get().strip()
        if query:
            self.search_timer = threading.Timer(
                self.search_delay,
                lambda: self.search_callback(query)
            )
            self.search_timer.start()
        else:
            # Si está vacío, limpiar resultados inmediatamente
            self.search_callback("")
    
    def _on_enter(self, event):
        """Evento cuando se presiona Enter"""
        # Cancelar timer y buscar inmediatamente
        if self.search_timer:
            self.search_timer.cancel()
        
        query = self.search_entry.get().strip()
        self.search_callback(query)
    
    def _clear_search(self):
        """Limpia la búsqueda"""
        self.search_entry.delete(0, 'end')
        self.search_callback("")
    
    def focus(self):
        """Enfoca la barra de búsqueda"""
        self.search_entry.focus()
    
    def get_query(self):
        """Obtiene la consulta actual"""
        return self.search_entry.get().strip()
    
    def set_query(self, query: str):
        """Establece una consulta"""
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, query)
