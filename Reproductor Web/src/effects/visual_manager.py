# -*- coding: utf-8 -*-
"""
✨ VISUAL EFFECTS MANAGER - GESTOR DE EFECTOS VISUALES AVANZADOS
==============================================================
Sistema completo de efectos visuales con:
- Visualizador de espectro 3D en tiempo real
- Partículas reactivas a la música
- Efectos de glassmorphism
- Animaciones suaves
- Shaders personalizados
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import asyncio
import threading
import time
from typing import Dict, List, Optional, Callable, Tuple
import logging
from dataclasses import dataclass
import colorsys
import math

try:
    import moderngl
    MODERNGL_AVAILABLE = True
except ImportError:
    MODERNGL_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class Particle:
    """Partícula para efectos visuales"""
    x: float
    y: float
    vx: float
    vy: float
    size: float
    color: Tuple[float, float, float]
    life: float
    max_life: float
    
    def update(self, dt: float, music_intensity: float = 0.0):
        """Actualiza la partícula"""
        # Movimiento
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        # Reacción a la música
        self.vx += np.random.uniform(-0.1, 0.1) * music_intensity
        self.vy += np.random.uniform(-0.1, 0.1) * music_intensity
        
        # Reducir vida
        self.life -= dt
        
        # Actualizar tamaño basado en vida
        life_ratio = self.life / self.max_life
        self.size = self.size * life_ratio
    
    def is_alive(self) -> bool:
        """Verifica si la partícula está viva"""
        return self.life > 0

class SpectrumVisualizer:
    """Visualizador de espectro 3D"""
    
    def __init__(self, width: int = 800, height: int = 400):
        self.width = width
        self.height = height
        self.is_initialized = False
        
        # Configuración del espectro
        self.num_bars = 64
        self.bar_heights = np.zeros(self.num_bars)
        self.bar_velocities = np.zeros(self.num_bars)
        self.smoothing_factor = 0.8
        
        # Colores
        self.color_palette = self._generate_color_palette()
        
        # Matplotlib setup
        self.fig, self.ax = plt.subplots(figsize=(8, 4), facecolor='black')
        self.ax.set_facecolor('black')
        self.bars = None
        
        # Configurar estilo
        self._setup_plot_style()
    
    def _generate_color_palette(self) -> List[Tuple[float, float, float]]:
        """Genera paleta de colores para el espectro"""
        colors = []
        for i in range(self.num_bars):
            # HSV a RGB para colores vibrantes
            hue = i / self.num_bars
            saturation = 0.8
            value = 0.9
            rgb = colorsys.hsv_to_rgb(hue, saturation, value)
            colors.append(rgb)
        return colors
    
    def _setup_plot_style(self):
        """Configura el estilo del gráfico"""
        self.ax.set_xlim(0, self.num_bars)
        self.ax.set_ylim(0, 1.0)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
        
        # Crear barras iniciales
        self.bars = self.ax.bar(
            range(self.num_bars),
            self.bar_heights,
            color=self.color_palette,
            edgecolor='none',
            alpha=0.8
        )
    
    def update_spectrum(self, spectrum_data: np.ndarray):
        """Actualiza el visualizador con nuevos datos de espectro"""
        if len(spectrum_data) == 0:
            return
        
        # Reducir resolución si es necesario
        if len(spectrum_data) > self.num_bars:
            # Promediar bins para reducir a num_bars
            chunk_size = len(spectrum_data) // self.num_bars
            reduced_spectrum = []
            for i in range(self.num_bars):
                start_idx = i * chunk_size
                end_idx = min((i + 1) * chunk_size, len(spectrum_data))
                chunk = spectrum_data[start_idx:end_idx]
                reduced_spectrum.append(np.mean(chunk))
            spectrum_data = np.array(reduced_spectrum)
        
        # Normalizar datos
        spectrum_data = np.abs(spectrum_data)
        if np.max(spectrum_data) > 0:
            spectrum_data = spectrum_data / np.max(spectrum_data)
        
        # Suavizado
        target_heights = spectrum_data[:self.num_bars]
        
        for i in range(self.num_bars):
            # Interpolación suave
            diff = target_heights[i] - self.bar_heights[i]
            self.bar_velocities[i] = diff * 0.3
            self.bar_heights[i] += self.bar_velocities[i]
            
            # Factor de amortiguamiento
            self.bar_heights[i] *= 0.95
            
            # Actualizar barra visual
            if self.bars:
                self.bars[i].set_height(max(0, self.bar_heights[i]))
                
                # Color dinámico basado en intensidad
                intensity = self.bar_heights[i]
                base_color = self.color_palette[i]
                alpha = 0.3 + intensity * 0.7
                self.bars[i].set_alpha(alpha)

class ParticleSystem:
    """Sistema de partículas reactivo a música"""
    
    def __init__(self, max_particles: int = 500):
        self.max_particles = max_particles
        self.particles: List[Particle] = []
        self.spawn_rate = 10  # partículas por segundo
        self.last_spawn_time = 0
        
        # Configuración
        self.gravity = -9.8
        self.wind_force = 0.0
        self.music_reactivity = 1.0
    
    def update(self, dt: float, music_intensity: float = 0.0, spawn_position: Tuple[float, float] = (0.5, 0.5)):
        """Actualiza el sistema de partículas"""
        current_time = time.time()
        
        # Generar nuevas partículas
        if current_time - self.last_spawn_time > 1.0 / (self.spawn_rate * (1 + music_intensity)):
            if len(self.particles) < self.max_particles:
                self._spawn_particle(spawn_position, music_intensity)
            self.last_spawn_time = current_time
        
        # Actualizar partículas existentes
        for particle in self.particles[:]:
            particle.update(dt, music_intensity)
            
            # Aplicar fuerzas
            particle.vy += self.gravity * dt * 0.01
            particle.vx += self.wind_force * dt
            
            # Eliminar partículas muertas
            if not particle.is_alive() or particle.y < -0.1:
                self.particles.remove(particle)
    
    def _spawn_particle(self, position: Tuple[float, float], music_intensity: float):
        """Genera una nueva partícula"""
        x, y = position
        
        # Velocidad aleatoria con influencia musical
        base_speed = 0.1 + music_intensity * 0.3
        angle = np.random.uniform(0, 2 * np.pi)
        speed = np.random.uniform(base_speed * 0.5, base_speed * 1.5)
        
        vx = np.cos(angle) * speed
        vy = np.sin(angle) * speed + 0.2  # Tendencia hacia arriba
        
        # Tamaño basado en intensidad musical
        size = 0.002 + music_intensity * 0.008
        
        # Color aleatorio con saturación basada en música
        hue = np.random.random()
        saturation = 0.5 + music_intensity * 0.5
        value = 0.8 + music_intensity * 0.2
        color = colorsys.hsv_to_rgb(hue, saturation, value)
        
        # Vida de la partícula
        life = np.random.uniform(1.0, 3.0 + music_intensity * 2.0)
        
        particle = Particle(
            x=x + np.random.uniform(-0.05, 0.05),
            y=y + np.random.uniform(-0.02, 0.02),
            vx=vx,
            vy=vy,
            size=size,
            color=color,
            life=life,
            max_life=life
        )
        
        self.particles.append(particle)
    
    def get_particle_data(self) -> List[Dict]:
        """Obtiene datos de partículas para renderizado"""
        particle_data = []
        
        for particle in self.particles:
            life_ratio = particle.life / particle.max_life
            alpha = life_ratio * 0.8
            
            particle_data.append({
                'x': particle.x,
                'y': particle.y,
                'size': particle.size,
                'color': (*particle.color, alpha),
                'life_ratio': life_ratio
            })
        
        return particle_data

class WaveformVisualizer:
    """Visualizador de forma de onda"""
    
    def __init__(self, width: int = 800, height: int = 200):
        self.width = width
        self.height = height
        self.waveform_data = np.zeros(1024)
        
        # Configuración matplotlib
        self.fig, self.ax = plt.subplots(figsize=(8, 2), facecolor='black')
        self.ax.set_facecolor('black')
        self.line, = self.ax.plot([], [], color='#00d4ff', linewidth=2, alpha=0.8)
        
        self._setup_plot_style()
    
    def _setup_plot_style(self):
        """Configura estilo del gráfico"""
        self.ax.set_xlim(0, len(self.waveform_data))
        self.ax.set_ylim(-1, 1)
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)
        self.ax.spines['bottom'].set_visible(False)
        self.ax.spines['left'].set_visible(False)
    
    def update_waveform(self, audio_data: np.ndarray):
        """Actualiza visualizador de forma de onda"""
        if len(audio_data) > 0:
            # Normalizar y suavizar
            normalized_data = audio_data / (np.max(np.abs(audio_data)) + 1e-8)
            
            # Aplicar ventana para suavizar
            windowed_data = normalized_data * np.hanning(len(normalized_data))
            
            self.waveform_data = windowed_data
            
            # Actualizar línea
            x_data = range(len(windowed_data))
            self.line.set_data(x_data, windowed_data)

class VisualEffectsManager:
    """Gestor principal de efectos visuales"""
    
    def __init__(self):
        self.spectrum_visualizer = None
        self.particle_system = None
        self.waveform_visualizer = None
        
        # Estado
        self.is_running = False
        self.is_initialized = False
        self.visualization_enabled = True
        self.current_intensity = 0.0
        self.visualization_thread = None
        
        # Configuración
        self.fps = 60
        self.effects_enabled = True
        self.current_mode = "spectrum_3d"  # spectrum_3d, particles, waveform, combined
        
        # Callbacks
        self.render_callback: Optional[Callable] = None
        
        # OpenGL context (si está disponible)
        self.gl_context = None
        
        # Lock para thread safety
        self._lock = threading.Lock()
    
    async def initialize(self):
        """Inicializa el gestor de efectos visuales"""
        try:
            logger.info("Inicializando gestor de efectos visuales...")
            
            # Inicializar visualizadores
            self.spectrum_visualizer = SpectrumVisualizer()
            self.particle_system = ParticleSystem()
            self.waveform_visualizer = WaveformVisualizer()
            
            # Inicializar OpenGL si está disponible
            if MODERNGL_AVAILABLE:
                await self._initialize_opengl()
            
            logger.info("✅ Gestor de efectos visuales inicializado")
            self.is_initialized = True
            
        except Exception as e:
            logger.error(f"Error inicializando efectos visuales: {e}")
            raise
    
    async def _initialize_opengl(self):
        """Inicializa contexto OpenGL"""
        try:
            # Crear contexto OpenGL headless para efectos avanzados
            self.gl_context = moderngl.create_standalone_context()
            logger.info("✅ Contexto OpenGL inicializado")
        except Exception as e:
            logger.warning(f"No se pudo inicializar OpenGL: {e}")
            self.gl_context = None
    
    def start_visualization(self):
        """Inicia el sistema de visualización"""
        if not self.is_running:
            self.is_running = True
            self.visualization_thread = threading.Thread(
                target=self._visualization_loop,
                daemon=True
            )
            self.visualization_thread.start()
            logger.info("▶️ Sistema de visualización iniciado")
    
    def stop_visualization(self):
        """Detiene el sistema de visualización"""
        self.is_running = False
        if self.visualization_thread:
            self.visualization_thread.join(timeout=1.0)
        logger.info("⏹️ Sistema de visualización detenido")
    
    def _visualization_loop(self):
        """Loop principal de visualización"""
        last_time = time.time()
        
        while self.is_running:
            try:
                current_time = time.time()
                dt = current_time - last_time
                last_time = current_time
                
                # Actualizar efectos según el modo actual
                with self._lock:
                    if self.current_mode == "particles" or self.current_mode == "combined":
                        self.particle_system.update(dt, self.current_intensity)
                
                # Callback para renderizado
                if self.render_callback:
                    self.render_callback()
                
                # Controlar FPS
                time.sleep(max(0, 1.0 / self.fps - dt))
                
            except Exception as e:
                logger.error(f"Error en loop de visualización: {e}")
                break
    
    def update_spectrum_data(self, spectrum_data: np.ndarray):
        """Actualiza datos de espectro"""
        if not self.effects_enabled:
            return
        
        try:
            with self._lock:
                # Calcular intensidad musical
                if len(spectrum_data) > 0:
                    self.current_intensity = np.mean(spectrum_data) * 2.0
                    self.current_intensity = min(1.0, self.current_intensity)
                
                # Actualizar visualizadores
                if self.current_mode == "spectrum_3d" or self.current_mode == "combined":
                    self.spectrum_visualizer.update_spectrum(spectrum_data)
                
        except Exception as e:
            logger.error(f"Error actualizando espectro: {e}")
    
    def update_waveform_data(self, waveform_data: np.ndarray):
        """Actualiza datos de forma de onda"""
        if not self.effects_enabled:
            return
        
        try:
            with self._lock:
                if self.current_mode == "waveform" or self.current_mode == "combined":
                    self.waveform_visualizer.update_waveform(waveform_data)
                
        except Exception as e:
            logger.error(f"Error actualizando forma de onda: {e}")
    
    def get_spectrum_canvas(self) -> Optional[FigureCanvasTkAgg]:
        """Obtiene canvas de matplotlib para el espectro"""
        if self.spectrum_visualizer and self.spectrum_visualizer.fig:
            return FigureCanvasTkAgg(self.spectrum_visualizer.fig)
        return None
    
    def get_waveform_canvas(self) -> Optional[FigureCanvasTkAgg]:
        """Obtiene canvas de matplotlib para la forma de onda"""
        if self.waveform_visualizer and self.waveform_visualizer.fig:
            return FigureCanvasTkAgg(self.waveform_visualizer.fig)
        return None
    
    def get_particle_data(self) -> List[Dict]:
        """Obtiene datos de partículas para renderizado"""
        if self.particle_system:
            return self.particle_system.get_particle_data()
        return []
    
    def set_visualization_mode(self, mode: str):
        """Establece modo de visualización"""
        valid_modes = ["spectrum_3d", "particles", "waveform", "combined"]
        if mode in valid_modes:
            self.current_mode = mode
            logger.info(f"Modo de visualización cambiado a: {mode}")
        else:
            logger.warning(f"Modo de visualización inválido: {mode}")
    
    def set_effects_enabled(self, enabled: bool):
        """Habilita/deshabilita efectos"""
        self.effects_enabled = enabled
        logger.info(f"Efectos visuales {'habilitados' if enabled else 'deshabilitados'}")
    
    def set_fps(self, fps: int):
        """Establece FPS de visualización"""
        self.fps = max(15, min(120, fps))  # Limitar entre 15-120 FPS
        logger.info(f"FPS de visualización establecido a: {self.fps}")
    
    def set_particle_count(self, count: int):
        """Establece cantidad máxima de partículas"""
        if self.particle_system:
            self.particle_system.max_particles = max(10, min(2000, count))
            logger.info(f"Máximo de partículas establecido a: {count}")
    
    def get_current_intensity(self) -> float:
        """Obtiene intensidad musical actual"""
        return self.current_intensity
    
    # Efectos especiales
    def trigger_explosion_effect(self, position: Tuple[float, float] = (0.5, 0.5)):
        """Trigger efecto de explosión de partículas"""
        if self.particle_system:
            # Generar múltiples partículas en burst
            for _ in range(50):
                self.particle_system._spawn_particle(position, 1.0)
    
    def set_color_palette(self, palette_name: str):
        """Establece paleta de colores"""
        if self.spectrum_visualizer:
            if palette_name == "rainbow":
                self.spectrum_visualizer.color_palette = self.spectrum_visualizer._generate_color_palette()
            # Aquí puedes añadir más paletas
    
    async def cleanup(self):
        """Limpieza de recursos"""
        try:
            # Usar await para la corrutina
            await self.stop_visualization()
            
            if self.gl_context:
                self.gl_context.release()
            
            logger.info("🧹 Gestor de efectos visuales limpiado")
            
        except Exception as e:
            logger.error(f"Error en cleanup de efectos visuales: {e}")
    
    # MÉTODOS ADICIONALES PARA LA APLICACIÓN
    
    async def start_visualization(self):
        """Inicia la visualización"""
        try:
            if not self.is_initialized:
                await self.initialize()
            
            self.visualization_enabled = True
            logger.info("🎨 Visualización iniciada")
            
        except Exception as e:
            logger.error(f"Error iniciando visualización: {e}")
    
    async def stop_visualization(self):
        """Detiene la visualización"""
        try:
            self.visualization_enabled = False
            logger.info("🎨 Visualización detenida")
            
        except Exception as e:
            logger.error(f"Error deteniendo visualización: {e}")
    
    async def pause_visualization(self):
        """Pausa la visualización"""
        await self.stop_visualization()
    
    async def resume_visualization(self):
        """Reanuda la visualización"""
        await self.start_visualization()
    
    async def update_spectrum(self, spectrum_data):
        """Actualiza los datos del espectro (versión async)"""
        try:
            if spectrum_data is not None and self.visualization_enabled:
                # Actualizar datos del espectro para la visualización
                self.current_spectrum = spectrum_data
                
        except Exception as e:
            logger.error(f"Error actualizando espectro: {e}")
    
    def update_spectrum_sync(self, spectrum_data):
        """Actualiza los datos del espectro (versión sincrónica)"""
        try:
            if spectrum_data is not None and self.visualization_enabled:
                # Actualizar datos del espectro para la visualización
                self.current_spectrum = spectrum_data
                
                # Actualizar visualizador si existe
                if hasattr(self, 'visualizer_frame') and self.visualizer_frame:
                    self.visualizer_frame.update_spectrum(spectrum_data)
                
        except Exception as e:
            logger.error(f"Error actualizando espectro: {e}")

# Singleton para acceso global
_visual_manager_instance = None

def get_visual_effects_manager() -> VisualEffectsManager:
    """Obtiene la instancia singleton del gestor de efectos visuales"""
    global _visual_manager_instance
    if _visual_manager_instance is None:
        _visual_manager_instance = VisualEffectsManager()
    return _visual_manager_instance
