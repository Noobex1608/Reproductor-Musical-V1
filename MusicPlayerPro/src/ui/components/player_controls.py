# -*- coding: utf-8 -*-
"""
🎵 PLAYER CONTROLS - CONTROLES DEL REPRODUCTOR
=============================================
Controles principales de reproducción: play/pause, anterior, siguiente, etc.
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional

class PlayerControls(ctk.CTkFrame):
    """Widget de controles del reproductor"""
    
    def __init__(self, parent, play_pause_callback: Callable, 
                 previous_callback: Callable, next_callback: Callable,
                 seek_callback: Optional[Callable] = None):
        super().__init__(parent)
        
        self.play_pause_callback = play_pause_callback
        self.previous_callback = previous_callback
        self.next_callback = next_callback
        self.seek_callback = seek_callback
        
        self.is_playing = False
        self.shuffle_enabled = False
        self.repeat_mode = "none"  # none, one, all
        
        # Variables para la barra de progreso
        self.current_position = 0.0
        self.total_duration = 0.0
        self.is_seeking = False
        
        self._create_controls()
        self._create_progress_bar()
    
    def _create_controls(self):
        """Crea los controles de reproducción"""
        
        # Botón anterior
        self.prev_button = ctk.CTkButton(
            self,
            text="⏮",
            width=50,
            height=40,
            font=ctk.CTkFont(size=16),
            command=self.previous_callback
        )
        self.prev_button.pack(side="left", padx=5)
        
        # Botón play/pause
        self.play_pause_button = ctk.CTkButton(
            self,
            text="▶",
            width=60,
            height=50,
            font=ctk.CTkFont(size=20),
            command=self.play_pause_callback
        )
        self.play_pause_button.pack(side="left", padx=10)
        
        # Botón siguiente
        self.next_button = ctk.CTkButton(
            self,
            text="⏭",
            width=50,
            height=40,
            font=ctk.CTkFont(size=16),
            command=self.next_callback
        )
        self.next_button.pack(side="left", padx=5)
        
        # Botón aleatorio
        self.shuffle_button = ctk.CTkButton(
            self,
            text="🔀",
            width=40,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self._toggle_shuffle
        )
        self.shuffle_button.pack(side="left", padx=(20, 5))
        
        # Botón repetir
        self.repeat_button = ctk.CTkButton(
            self,
            text="🔁",
            width=40,
            height=40,
            font=ctk.CTkFont(size=14),
            command=self._toggle_repeat
        )
        self.repeat_button.pack(side="left", padx=5)
    
    def update_state(self, state: str):
        """Actualiza el estado visual de los controles"""
        if state == "playing":
            self.is_playing = True
            self.play_pause_button.configure(text="⏸")
        elif state in ["paused", "stopped"]:
            self.is_playing = False
            self.play_pause_button.configure(text="▶")
        elif state == "loading":
            self.play_pause_button.configure(text="⏳")
    
    def _toggle_shuffle(self):
        """Alterna modo aleatorio"""
        self.shuffle_enabled = not self.shuffle_enabled
        if self.shuffle_enabled:
            self.shuffle_button.configure(fg_color="#1f538d")
        else:
            self.shuffle_button.configure(fg_color="transparent")
    
    def _toggle_repeat(self):
        """Alterna modo de repetición"""
        modes = ["none", "one", "all"]
        current_idx = modes.index(self.repeat_mode)
        self.repeat_mode = modes[(current_idx + 1) % len(modes)]
        
        if self.repeat_mode == "none":
            self.repeat_button.configure(text="🔁", fg_color="transparent")
        elif self.repeat_mode == "one":
            self.repeat_button.configure(text="🔂", fg_color="#1f538d")
        elif self.repeat_mode == "all":
            self.repeat_button.configure(text="🔁", fg_color="#1f538d")
    
    def _create_progress_bar(self):
        """Crea la barra de progreso"""
        # Frame para la barra de progreso
        self.progress_frame = ctk.CTkFrame(self.master)
        self.progress_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        # Tiempo actual
        self.current_time_label = ctk.CTkLabel(
            self.progress_frame, 
            text="0:00",
            width=50
        )
        self.current_time_label.pack(side="left", padx=(10, 5))
        
        # Barra de progreso
        self.progress_slider = ctk.CTkSlider(
            self.progress_frame,
            from_=0,
            to=100,
            number_of_steps=1000,
            command=self._on_progress_change
        )
        self.progress_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.progress_slider.bind("<Button-1>", self._on_progress_click)
        self.progress_slider.bind("<ButtonRelease-1>", self._on_progress_release)
        
        # Tiempo total
        self.total_time_label = ctk.CTkLabel(
            self.progress_frame,
            text="0:00",
            width=50
        )
        self.total_time_label.pack(side="right", padx=(5, 10))
    
    def _on_progress_click(self, event):
        """Inicia el seeking"""
        self.is_seeking = True
    
    def _on_progress_release(self, event):
        """Termina el seeking y busca la posición"""
        self.is_seeking = False
        if self.seek_callback:
            # Convertir porcentaje a tiempo en segundos
            percentage = self.progress_slider.get()
            seek_time = (percentage / 100.0) * self.total_duration
            self.seek_callback(seek_time)
    
    def _on_progress_change(self, value):
        """Actualiza el tiempo mientras se arrastra el slider"""
        if self.is_seeking and self.total_duration > 0:
            # Actualizar tiempo mostrado mientras arrastra
            seek_time = (value / 100.0) * self.total_duration
            time_str = self._format_time(seek_time)
            self.current_time_label.configure(text=time_str)
    
    def update_progress(self, current_time: float, total_time: float):
        """Actualiza la barra de progreso"""
        if not self.is_seeking:  # No actualizar si está siendo arrastrada
            self.current_position = current_time
            self.total_duration = total_time
            
            # Actualizar etiquetas de tiempo
            self.current_time_label.configure(text=self._format_time(current_time))
            self.total_time_label.configure(text=self._format_time(total_time))
            
            # Actualizar slider
            if total_time > 0:
                percentage = (current_time / total_time) * 100
                self.progress_slider.set(percentage)
            else:
                self.progress_slider.set(0)
    
    def _format_time(self, seconds: float) -> str:
        """Formatea tiempo en segundos a MM:SS"""
        if seconds < 0:
            seconds = 0
        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes}:{seconds:02d}"
