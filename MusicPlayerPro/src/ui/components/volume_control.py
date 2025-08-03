# -*- coding: utf-8 -*-
"""
🔊 VOLUME CONTROL - CONTROL DE VOLUMEN
======================================
Widget para controlar el volumen con slider y botón de mute
"""

import customtkinter as ctk
from typing import Callable

class VolumeControl(ctk.CTkFrame):
    """Widget de control de volumen"""
    
    def __init__(self, parent, volume_callback: Callable):
        super().__init__(parent)
        
        self.volume_callback = volume_callback
        self.current_volume = 70
        self.muted = False
        self.volume_before_mute = 70
        
        self._create_controls()
    
    def _create_controls(self):
        """Crea los controles de volumen"""
        
        # Botón de mute
        self.mute_button = ctk.CTkButton(
            self,
            text="🔊",
            width=40,
            height=40,
            font=ctk.CTkFont(size=16),
            command=self._toggle_mute
        )
        self.mute_button.pack(side="left", padx=(10, 5))
        
        # Slider de volumen
        self.volume_slider = ctk.CTkSlider(
            self,
            from_=0,
            to=100,
            width=120,
            command=self._on_volume_change
        )
        self.volume_slider.pack(side="left", padx=5)
        self.volume_slider.set(self.current_volume)
        
        # Label de volumen
        self.volume_label = ctk.CTkLabel(
            self,
            text=f"{self.current_volume}%",
            width=40
        )
        self.volume_label.pack(side="left", padx=(5, 10))
    
    def _on_volume_change(self, value):
        """Callback cuando cambia el volumen"""
        volume = int(value)
        self.current_volume = volume
        
        # Actualizar UI
        self._update_volume_display(volume)
        
        # Si estaba muteado, desactivar mute
        if self.muted:
            self.muted = False
            self._update_mute_button()
        
        # Llamar callback
        self.volume_callback(volume)
    
    def _toggle_mute(self):
        """Alterna entre mute y unmute"""
        if self.muted:
            # Unmute: restaurar volumen anterior
            self.muted = False
            self.volume_slider.set(self.volume_before_mute)
            self.current_volume = self.volume_before_mute
            self.volume_callback(self.current_volume)
        else:
            # Mute: guardar volumen actual y poner a 0
            self.muted = True
            self.volume_before_mute = self.current_volume
            self.volume_slider.set(0)
            self.current_volume = 0
            self.volume_callback(0)
        
        self._update_mute_button()
        self._update_volume_display(self.current_volume)
    
    def _update_mute_button(self):
        """Actualiza el ícono del botón de mute"""
        if self.muted:
            self.mute_button.configure(text="🔇", fg_color="#f44336")
        else:
            self.mute_button.configure(text="🔊", fg_color="transparent")
    
    def _update_volume_display(self, volume):
        """Actualiza la visualización del volumen"""
        self.volume_label.configure(text=f"{volume}%")
        
        # Cambiar ícono según nivel de volumen
        if not self.muted:
            if volume == 0:
                self.mute_button.configure(text="🔇")
            elif volume < 30:
                self.mute_button.configure(text="🔈")
            elif volume < 70:
                self.mute_button.configure(text="🔉")
            else:
                self.mute_button.configure(text="🔊")
    
    def set_volume(self, volume: int):
        """Establece el volumen externamente"""
        volume = max(0, min(100, volume))
        self.current_volume = volume
        self.volume_slider.set(volume)
        self._update_volume_display(volume)
