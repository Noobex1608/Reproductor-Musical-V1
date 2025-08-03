# -*- coding: utf-8 -*-
"""
🎨 VISUALIZER FRAME - MARCO DEL VISUALIZADOR
===========================================
Widget que contiene el visualizador de música
"""

import customtkinter as ctk
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import threading
import time
from typing import Optional

class VisualizerFrame(ctk.CTkFrame):
    """Frame del visualizador de música"""
    
    def __init__(self, parent, visual_manager):
        super().__init__(parent)
        
        self.visual_manager = visual_manager
        self.is_active = False
        self.spectrum_data = np.zeros(512)
        
        self._create_visualizer()
        self._setup_animation()
    
    def _create_visualizer(self):
        """Crea el visualizador"""
        
        # Título
        self.title_label = ctk.CTkLabel(
            self,
            text="🎨 Visualizador Musical",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.title_label.pack(pady=(10, 5))
        
        # Controles del visualizador
        self.controls_frame = ctk.CTkFrame(self)
        self.controls_frame.pack(fill="x", padx=10, pady=5)
        
        # Tipo de visualización
        self.viz_type_var = ctk.StringVar(value="Espectro")
        self.viz_type_dropdown = ctk.CTkOptionMenu(
            self.controls_frame,
            variable=self.viz_type_var,
            values=["Espectro", "Onda", "Barras", "Circular"],
            command=self._on_viz_type_change
        )
        self.viz_type_dropdown.pack(side="left", padx=5, pady=5)
        
        # Botón activar/desactivar
        self.toggle_button = ctk.CTkButton(
            self.controls_frame,
            text="▶ Activar",
            width=80,
            command=self._toggle_visualizer
        )
        self.toggle_button.pack(side="right", padx=5, pady=5)
        
        # Frame para matplotlib
        self.canvas_frame = ctk.CTkFrame(self)
        self.canvas_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        # Configurar matplotlib con tema oscuro
        plt.style.use('dark_background')
        
        # Crear figura
        self.fig, self.ax = plt.subplots(figsize=(8, 6), facecolor='#0b1426')
        self.ax.set_facecolor('#1a1a2e')
        
        # Configurar ejes
        self.ax.set_xlim(0, 512)
        self.ax.set_ylim(0, 1)
        self.ax.set_xlabel('Frecuencia', color='white')
        self.ax.set_ylabel('Amplitud', color='white')
        self.ax.tick_params(colors='white')
        
        # Crear canvas
        self.canvas = FigureCanvasTkAgg(self.fig, self.canvas_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        
        # Inicializar línea del espectro
        self.line, = self.ax.plot(np.arange(512), np.zeros(512), 
                                 color='#36719f', linewidth=2)
        
        # Configurar gradiente de colores
        self.colors = plt.cm.plasma(np.linspace(0, 1, 512))
    
    def _setup_animation(self):
        """Configura la animación"""
        self.animation = None
        self.animation_interval = 50  # 20 FPS
    
    def _toggle_visualizer(self):
        """Activa/desactiva el visualizador"""
        if self.is_active:
            self._stop_visualizer()
        else:
            self._start_visualizer()
    
    def _start_visualizer(self):
        """Inicia el visualizador"""
        if not self.is_active:
            self.is_active = True
            self.toggle_button.configure(text="⏸ Detener")
            
            # Iniciar animación
            self.animation = FuncAnimation(
                self.fig, 
                self._update_animation,
                interval=self.animation_interval,
                blit=False,
                cache_frame_data=False
            )
            
            # Iniciar canvas
            self.canvas.draw()
    
    def _stop_visualizer(self):
        """Detiene el visualizador"""
        if self.is_active:
            self.is_active = False
            self.toggle_button.configure(text="▶ Activar")
            
            # Detener animación
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None
            
            # Limpiar visualización
            self._clear_visualization()
    
    def _update_animation(self, frame):
        """Actualiza la animación del visualizador"""
        if not self.is_active:
            return []
        
        viz_type = self.viz_type_var.get()
        
        if viz_type == "Espectro":
            return self._draw_spectrum()
        elif viz_type == "Onda":
            return self._draw_waveform()
        elif viz_type == "Barras":
            return self._draw_bars()
        elif viz_type == "Circular":
            return self._draw_circular()
        
        return []
    
    def _draw_spectrum(self):
        """Dibuja visualización de espectro"""
        # Suavizar datos del espectro
        smoothed_data = self._smooth_spectrum(self.spectrum_data)
        
        # Actualizar línea
        self.line.set_ydata(smoothed_data)
        
        # Cambiar color basado en intensidad
        intensity = np.mean(smoothed_data)
        color_intensity = min(intensity * 2, 1.0)
        color = plt.cm.plasma(color_intensity)
        self.line.set_color(color)
        
        return [self.line]
    
    def _draw_waveform(self):
        """Dibuja forma de onda"""
        # Generar forma de onda simulada basada en espectro
        waveform = np.sin(np.linspace(0, 4*np.pi, 512)) * np.mean(self.spectrum_data)
        noise = np.random.random(512) * 0.1 * np.mean(self.spectrum_data)
        waveform += noise
        
        self.line.set_ydata(waveform + 0.5)
        self.ax.set_ylim(-0.5, 1.5)
        
        return [self.line]
    
    def _draw_bars(self):
        """Dibuja barras de frecuencia"""
        # Limpiar ejes
        self.ax.clear()
        
        # Configurar ejes para barras
        self.ax.set_xlim(0, 64)
        self.ax.set_ylim(0, 1)
        self.ax.set_facecolor('#1a1a2e')
        
        # Reducir datos del espectro para barras
        bar_data = self.spectrum_data[::8][:64]  # Tomar cada 8va muestra
        
        # Crear barras con gradiente de color
        bars = self.ax.bar(range(64), bar_data, 
                          color=self.colors[::8][:64],
                          width=0.8)
        
        return bars
    
    def _draw_circular(self):
        """Dibuja visualización circular"""
        # Limpiar ejes
        self.ax.clear()
        
        # Configurar para gráfico polar
        self.ax = plt.subplot(111, projection='polar')
        self.ax.set_facecolor('#1a1a2e')
        
        # Datos para círculo
        angles = np.linspace(0, 2*np.pi, len(self.spectrum_data), endpoint=False)
        
        # Dibujar círculo de espectro
        self.ax.plot(angles, self.spectrum_data, color='#36719f', linewidth=2)
        self.ax.fill(angles, self.spectrum_data, alpha=0.3, color='#36719f')
        
        return []
    
    def _smooth_spectrum(self, data):
        """Suaviza los datos del espectro"""
        if len(data) < 3:
            return data
        
        # Aplicar filtro de media móvil simple
        window_size = 3
        smoothed = np.convolve(data, np.ones(window_size)/window_size, mode='same')
        
        return smoothed
    
    def _clear_visualization(self):
        """Limpia la visualización"""
        self.line.set_ydata(np.zeros(512))
        self.canvas.draw()
    
    def _on_viz_type_change(self, viz_type):
        """Evento cuando cambia el tipo de visualización"""
        if self.is_active:
            # Reiniciar visualización con nuevo tipo
            self._stop_visualizer()
            self._start_visualizer()
    
    def update_spectrum(self, spectrum_data):
        """Actualiza los datos del espectro"""
        if spectrum_data is not None and len(spectrum_data) > 0:
            # Normalizar datos
            max_val = np.max(spectrum_data)
            if max_val > 0:
                self.spectrum_data = spectrum_data / max_val
            else:
                self.spectrum_data = spectrum_data
        else:
            self.spectrum_data = np.zeros(512)
    
    def start_visualization(self):
        """Inicia la visualización externamente"""
        if not self.is_active:
            self._start_visualizer()
    
    def stop_visualization(self):
        """Detiene la visualización externamente"""
        if self.is_active:
            self._stop_visualizer()
    
    def cleanup(self):
        """Limpia recursos del visualizador"""
        self._stop_visualizer()
        if hasattr(self, 'fig'):
            plt.close(self.fig)
