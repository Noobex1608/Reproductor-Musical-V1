// 🎵 MUSIC PLAYER PRO - VISUALIZER
// ================================
// Visualizador de espectro de frecuencias

class SpectrumVisualizer {
    constructor(canvasId) {
        this.config = window.MusicPlayerConfig;
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas ? this.canvas.getContext('2d') : null;
        
        // Estado del visualizador
        this.isActive = false;
        this.mode = 'spectrum'; // 'spectrum', 'waveform', 'circular'
        this.spectrumData = new Array(this.config.VISUALIZER.SPECTRUM_BARS).fill(0);
        this.smoothedData = new Array(this.config.VISUALIZER.SPECTRUM_BARS).fill(0);
        
        // Configuración de renderizado
        this.smoothingFactor = 0.8;
        this.minHeight = 4;
        this.maxHeight = 200;
        this.barWidth = 0;
        this.barSpacing = 2;
        
        // Animación
        this.animationId = null;
        this.fps = 0;
        this.lastFrameTime = 0;
        this.frameCount = 0;
        
        // Fallback bars
        this.fallbackContainer = document.getElementById('visualizer-fallback');
        this.fallbackBars = [];
        
        this.init();
    }

    // ============================
    // 🚀 INICIALIZACIÓN
    // ============================

    init() {
        if (this.canvas && this.ctx) {
            this.setupCanvas();
            this.initializeColors();
            this.config.Utils.log('info', 'Visualizador Canvas inicializado');
        } else {
            this.setupFallbackBars();
            this.config.Utils.log('info', 'Visualizador Fallback inicializado');
        }
        
        this.setupControls();
        this.start();
    }

    setupCanvas() {
        // Configurar tamaño del canvas
        const container = this.canvas.parentElement;
        const rect = container.getBoundingClientRect();
        
        this.canvas.width = rect.width || this.config.VISUALIZER.CANVAS_WIDTH;
        this.canvas.height = rect.height || this.config.VISUALIZER.CANVAS_HEIGHT;
        
        // Calcular ancho de barras
        this.barWidth = (this.canvas.width - (this.config.VISUALIZER.SPECTRUM_BARS - 1) * this.barSpacing) / this.config.VISUALIZER.SPECTRUM_BARS;
        
        // Configurar contexto
        this.ctx.fillStyle = '#ff6b6b';
        this.ctx.strokeStyle = '#ff6b6b';
        this.ctx.lineWidth = 1;
    }

    setupFallbackBars() {
        if (!this.fallbackContainer) return;
        
        const barsContainer = this.fallbackContainer.querySelector('.spectrum-bars');
        if (!barsContainer) return;
        
        // Limpiar barras existentes
        barsContainer.innerHTML = '';
        
        // Crear barras
        for (let i = 0; i < this.config.VISUALIZER.SPECTRUM_BARS; i++) {
            const bar = document.createElement('div');
            bar.className = 'spectrum-bar';
            bar.style.height = `${this.minHeight}px`;
            barsContainer.appendChild(bar);
            this.fallbackBars.push(bar);
        }
    }

    initializeColors() {
        this.colors = {
            primary: '#ff6b6b',
            secondary: '#4ecdc4',
            gradient: null
        };
        
        if (this.ctx) {
            this.colors.gradient = this.ctx.createLinearGradient(0, this.canvas.height, 0, 0);
            this.colors.gradient.addColorStop(0, this.colors.primary);
            this.colors.gradient.addColorStop(0.6, this.colors.secondary);
            this.colors.gradient.addColorStop(1, '#ffffff');
        }
    }

    setupControls() {
        // Botón de cambio de modo
        const modeBtn = document.getElementById('viz-mode-btn');
        if (modeBtn) {
            modeBtn.addEventListener('click', () => this.cycleMode());
        }
        
        // Botón de mostrar/ocultar
        const toggleBtn = document.getElementById('viz-toggle');
        if (toggleBtn) {
            toggleBtn.addEventListener('click', () => this.toggle());
        }
    }

    // ============================
    // 🎨 RENDERIZADO
    // ============================

    render() {
        if (!this.isActive) return;
        
        // Calcular FPS
        this.calculateFPS();
        
        if (this.canvas && this.ctx) {
            this.renderCanvas();
        } else {
            this.renderFallback();
        }
        
        this.animationId = requestAnimationFrame(() => this.render());
    }

    renderCanvas() {
        // Limpiar canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Renderizar fondo
        this.renderBackground();
        
        // Renderizar según el modo
        switch (this.mode) {
            case 'spectrum':
                this.renderSpectrum();
                break;
            case 'waveform':
                this.renderWaveform();
                break;
            case 'circular':
                this.renderCircular();
                break;
        }
        
        // Renderizar efectos
        this.renderEffects();
    }

    renderSpectrum() {
        this.ctx.fillStyle = this.colors.gradient;
        
        for (let i = 0; i < this.smoothedData.length; i++) {
            const height = Math.max(this.minHeight, this.smoothedData[i] * this.maxHeight / 100);
            const x = i * (this.barWidth + this.barSpacing);
            const y = this.canvas.height - height;
            
            // Barra principal
            this.ctx.fillRect(x, y, this.barWidth, height);
        }
    }

    renderWaveform() {
        this.ctx.strokeStyle = this.colors.secondary;
        this.ctx.lineWidth = 3;
        this.ctx.beginPath();
        
        const centerY = this.canvas.height / 2;
        const amplitude = this.canvas.height / 4;
        
        for (let i = 0; i < this.smoothedData.length; i++) {
            const x = (i / (this.smoothedData.length - 1)) * this.canvas.width;
            const y = centerY + (this.smoothedData[i] - 50) * amplitude / 50;
            
            if (i === 0) {
                this.ctx.moveTo(x, y);
            } else {
                this.ctx.lineTo(x, y);
            }
        }
        
        this.ctx.stroke();
    }

    renderCircular() {
        const centerX = this.canvas.width / 2;
        const centerY = this.canvas.height / 2;
        const radius = Math.min(centerX, centerY) - 20;
        
        this.ctx.strokeStyle = this.colors.primary;
        this.ctx.lineWidth = 2;
        
        for (let i = 0; i < this.smoothedData.length; i++) {
            const angle = (i / this.smoothedData.length) * Math.PI * 2 - Math.PI / 2;
            const barHeight = this.smoothedData[i] * 50 / 100;
            
            const x1 = centerX + Math.cos(angle) * radius;
            const y1 = centerY + Math.sin(angle) * radius;
            const x2 = centerX + Math.cos(angle) * (radius + barHeight);
            const y2 = centerY + Math.sin(angle) * (radius + barHeight);
            
            this.ctx.beginPath();
            this.ctx.moveTo(x1, y1);
            this.ctx.lineTo(x2, y2);
            this.ctx.stroke();
        }
        
        // Círculo central
        this.ctx.beginPath();
        this.ctx.arc(centerX, centerY, radius * 0.3, 0, Math.PI * 2);
        this.ctx.fillStyle = 'rgba(255, 107, 107, 0.1)';
        this.ctx.fill();
    }

    renderBackground() {
        // Fondo con gradiente radial sutil
        const gradient = this.ctx.createRadialGradient(
            this.canvas.width / 2, this.canvas.height / 2, 0,
            this.canvas.width / 2, this.canvas.height / 2, Math.max(this.canvas.width, this.canvas.height) / 2
        );
        
        gradient.addColorStop(0, 'rgba(255, 107, 107, 0.1)');
        gradient.addColorStop(1, 'rgba(10, 10, 11, 0.8)');
        
        this.ctx.fillStyle = gradient;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
    }

    renderEffects() {
        // Efectos de brillo y partículas (opcional)
        if (this.mode === 'spectrum') {
            this.renderGlowEffect();
        }
    }

    renderGlowEffect() {
        this.ctx.shadowColor = this.colors.primary;
        this.ctx.shadowBlur = 10;
        this.ctx.globalCompositeOperation = 'lighter';
        
        // Renderizar barras con glow
        this.ctx.fillStyle = this.colors.primary;
        for (let i = 0; i < this.smoothedData.length; i++) {
            if (this.smoothedData[i] > 50) { // Solo barras altas
                const height = this.smoothedData[i] * this.maxHeight / 100;
                const x = i * (this.barWidth + this.barSpacing);
                const y = this.canvas.height - height;
                
                this.ctx.fillRect(x, y, this.barWidth, height * 0.3);
            }
        }
        
        // Resetear efectos
        this.ctx.shadowBlur = 0;
        this.ctx.globalCompositeOperation = 'source-over';
    }

    renderFallback() {
        if (!this.fallbackBars.length) return;
        
        for (let i = 0; i < this.fallbackBars.length && i < this.smoothedData.length; i++) {
            const height = Math.max(10, this.smoothedData[i] * 150 / 100);
            this.fallbackBars[i].style.height = `${height}px`;
        }
    }

    // ============================
    // 📊 DATOS DEL ESPECTRO
    // ============================

    updateSpectrum(data) {
        if (!data || !Array.isArray(data)) {
            // Generar datos simulados si no hay datos reales
            this.generateFallbackData();
            return;
        }
        
        // Normalizar datos
        const normalizedData = this.normalizeSpectrumData(data);
        
        // Suavizar datos para evitar cambios bruscos
        for (let i = 0; i < normalizedData.length; i++) {
            this.smoothedData[i] = this.smoothedData[i] * this.smoothingFactor + 
                                  normalizedData[i] * (1 - this.smoothingFactor);
        }
    }

    normalizeSpectrumData(data) {
        // Redimensionar a número de barras deseado
        const normalized = new Array(this.config.VISUALIZER.SPECTRUM_BARS);
        const chunkSize = data.length / this.config.VISUALIZER.SPECTRUM_BARS;
        
        for (let i = 0; i < this.config.VISUALIZER.SPECTRUM_BARS; i++) {
            let sum = 0;
            const start = Math.floor(i * chunkSize);
            const end = Math.floor((i + 1) * chunkSize);
            
            for (let j = start; j < end && j < data.length; j++) {
                sum += Math.abs(data[j]);
            }
            
            normalized[i] = Math.min(100, (sum / (end - start)) || 0);
        }
        
        return normalized;
    }

    generateFallbackData() {
        // Datos simulados para cuando no hay audio real
        for (let i = 0; i < this.spectrumData.length; i++) {
            // Simular patrón de frecuencias musicales
            const baseValue = Math.sin(Date.now() * 0.005 + i * 0.5) * 30 + 30;
            const noise = Math.random() * 20;
            this.spectrumData[i] = Math.max(0, Math.min(100, baseValue + noise));
            
            // Suavizar
            this.smoothedData[i] = this.smoothedData[i] * 0.9 + this.spectrumData[i] * 0.1;
        }
    }

    // ============================
    // 🎛️ CONTROLES
    // ============================

    start() {
        if (!this.isActive) {
            this.isActive = true;
            this.render();
            this.updateVisualizerState('active');
            this.config.Utils.log('info', 'Visualizador iniciado');
        }
    }

    stop() {
        if (this.isActive) {
            this.isActive = false;
            if (this.animationId) {
                cancelAnimationFrame(this.animationId);
                this.animationId = null;
            }
            this.updateVisualizerState('inactive');
            this.config.Utils.log('info', 'Visualizador detenido');
        }
    }

    toggle() {
        if (this.isActive) {
            this.stop();
        } else {
            this.start();
        }
    }

    cycleMode() {
        const modes = this.config.VISUALIZER.MODES;
        const currentIndex = modes.indexOf(this.mode);
        const nextIndex = (currentIndex + 1) % modes.length;
        
        this.setMode(modes[nextIndex]);
    }

    setMode(mode) {
        if (this.config.VISUALIZER.MODES.includes(mode)) {
            this.mode = mode;
            this.updateModeDisplay();
            this.config.Utils.setStoredSetting('VISUALIZER_MODE', mode);
            this.config.Utils.log('info', `Modo visualizador: ${mode}`);
        }
    }

    // ============================
    // 🎨 ACTUALIZACIÓN DE UI
    // ============================

    updateVisualizerState(state) {
        const container = document.querySelector('.visualizer-container');
        if (container) {
            container.classList.remove('active', 'inactive', 'loading');
            container.classList.add(state);
        }
    }

    updateModeDisplay() {
        const modeElement = document.getElementById('viz-mode');
        if (modeElement) {
            const modeNames = {
                spectrum: 'Espectro',
                waveform: 'Ondas',
                circular: 'Circular'
            };
            modeElement.textContent = `Modo: ${modeNames[this.mode]}`;
        }
        
        // Actualizar clase del contenedor
        const container = document.querySelector('.visualizer-container');
        if (container) {
            container.classList.remove('mode-spectrum', 'mode-waveform', 'mode-circular');
            container.classList.add(`mode-${this.mode}`);
        }
    }

    calculateFPS() {
        const now = performance.now();
        this.frameCount++;
        
        if (now - this.lastFrameTime >= 1000) {
            this.fps = Math.round((this.frameCount * 1000) / (now - this.lastFrameTime));
            this.frameCount = 0;
            this.lastFrameTime = now;
            
            // Actualizar display de FPS
            const fpsElement = document.getElementById('viz-fps');
            if (fpsElement) {
                fpsElement.textContent = `FPS: ${this.fps}`;
            }
        }
    }

    // ============================
    // 🔧 UTILIDADES
    // ============================

    resize() {
        if (this.canvas && this.ctx) {
            this.setupCanvas();
            this.initializeColors();
        }
    }

    destroy() {
        this.stop();
        this.canvas = null;
        this.ctx = null;
        this.fallbackBars = [];
    }
}

// ============================
// 🌐 INICIALIZACIÓN GLOBAL
// ============================

let visualizer = null;

document.addEventListener('DOMContentLoaded', function() {
    // Crear visualizador
    visualizer = new SpectrumVisualizer('visualizer-canvas');
    window.visualizer = visualizer;
    
    // Configurar actualización de datos del espectro (más inteligente)
    let updateInterval;
    
    const startSpectrumUpdates = () => {
        if (updateInterval) return; // Ya está iniciado
        
        updateInterval = setInterval(async () => {
            // Solo actualizar si el visualizador está activo y visible
            if (!window.musicPlayerAPI || !visualizer.isActive) return;
            
            // Solo actualizar si hay música reproduciéndose
            if (window.musicPlayerApp && window.musicPlayerApp.state.playbackState !== 'playing') {
                visualizer.generateFallbackData(); // Datos estáticos cuando no se reproduce
                return;
            }
            
            try {
                const response = await window.musicPlayerAPI.getSpectrumData();
                if (response.status === 'success' && response.spectrum) {
                    visualizer.updateSpectrum(response.spectrum);
                }
            } catch (error) {
                // Error silencioso, usar datos de fallback
                visualizer.generateFallbackData();
            }
        }, window.MusicPlayerConfig.VISUALIZER.UPDATE_INTERVAL);
    };
    
    const stopSpectrumUpdates = () => {
        if (updateInterval) {
            clearInterval(updateInterval);
            updateInterval = null;
        }
    };
    
    // Iniciar actualizaciones solo cuando sea necesario
    startSpectrumUpdates();
    
    // Exponer métodos de control
    visualizer.startUpdates = startSpectrumUpdates;
    visualizer.stopUpdates = stopSpectrumUpdates;
    
    window.MusicPlayerConfig.Utils.log('info', 'Visualizador configurado');
});

// Redimensionar cuando cambie el tamaño de la ventana
window.addEventListener('resize', function() {
    if (visualizer) {
        setTimeout(() => visualizer.resize(), 100);
    }
});

// Exportar para módulos que lo necesiten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SpectrumVisualizer;
}
