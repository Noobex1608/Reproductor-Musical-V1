// 🎵 MUSIC PLAYER PRO - CONFIGURATION
// ====================================
// Configuración global de la aplicación web

window.MusicPlayerConfig = {
    // Configuración del servidor
    SERVER: {
        HOST: 'http://127.0.0.1:5000',
        WEBSOCKET_PATH: '/socket.io/',
        TIMEOUT: 10000 // 10 segundos
    },
    
    // Configuración de la API
    API: {
        ENDPOINTS: {
            HEALTH: '/health',
            PLAYER_PLAY: '/api/player/play',
            PLAYER_PAUSE: '/api/player/pause',
            PLAYER_STOP: '/api/player/stop',
            PLAYER_NEXT: '/api/player/next',
            PLAYER_PREVIOUS: '/api/player/previous',
            PLAYER_VOLUME: '/api/player/volume',
            PLAYER_SEEK: '/api/player/seek',
            PLAYER_STATE: '/api/player/state',
            LIBRARY_SONGS: '/api/library/songs',
            LIBRARY_SEARCH: '/api/library/search',
            LIBRARY_PLAY: '/api/library/play',
            VISUALIZER_SPECTRUM: '/api/visualizer/spectrum'
        }
    },
    
    // Configuración del visualizador
    VISUALIZER: {
        UPDATE_INTERVAL: 200, // 5 FPS - más eficiente
        SPECTRUM_BARS: 20,
        CANVAS_WIDTH: 300,
        CANVAS_HEIGHT: 200,
        FALLBACK_ENABLED: true,
        MODES: ['spectrum', 'waveform', 'circular']
    },
    
    // Configuración del reproductor
    PLAYER: {
        UPDATE_INTERVAL: 1000, // 1 segundo
        VOLUME_STEP: 5,
        SEEK_STEP: 10, // segundos
        AUTO_SAVE_SETTINGS: true
    },
    
    // Configuración de la UI
    UI: {
        TOAST_DURATION: 5000, // 5 segundos
        LOADING_MIN_TIME: 500, // Tiempo mínimo de loading
        SEARCH_DEBOUNCE: 300, // Debounce para búsqueda
        ANIMATION_DURATION: 300
    },
    
    // Configuración de almacenamiento local
    STORAGE: {
        KEYS: {
            VOLUME: 'musicplayer_volume',
            THEME: 'musicplayer_theme',
            VISUALIZER_MODE: 'musicplayer_viz_mode',
            LAST_PLAYLIST: 'musicplayer_last_playlist',
            SETTINGS: 'musicplayer_settings'
        }
    },
    
    // Configuración de formato de tiempo
    TIME_FORMAT: {
        SHOW_HOURS: false,
        PAD_MINUTES: true
    },
    
    // Configuración de debug
    DEBUG: {
        ENABLED: true,
        LOG_LEVEL: 'info', // 'debug', 'info', 'warn', 'error'
        SHOW_PERFORMANCE: true
    }
};

// Utidades de configuración
window.MusicPlayerConfig.Utils = {
    // Obtener URL completa de endpoint
    getEndpointUrl: function(endpoint) {
        return this.SERVER.HOST + this.API.ENDPOINTS[endpoint];
    }.bind(window.MusicPlayerConfig),
    
    // Obtener configuración de localStorage
    getStoredSetting: function(key, defaultValue = null) {
        try {
            const stored = localStorage.getItem(this.STORAGE.KEYS[key]);
            return stored ? JSON.parse(stored) : defaultValue;
        } catch (e) {
            console.warn('Error al leer configuración:', e);
            return defaultValue;
        }
    }.bind(window.MusicPlayerConfig),
    
    // Guardar configuración en localStorage
    setStoredSetting: function(key, value) {
        try {
            localStorage.setItem(this.STORAGE.KEYS[key], JSON.stringify(value));
            return true;
        } catch (e) {
            console.error('Error al guardar configuración:', e);
            return false;
        }
    }.bind(window.MusicPlayerConfig),
    
    // Formatear tiempo en MM:SS o HH:MM:SS
    formatTime: function(seconds) {
        if (isNaN(seconds) || seconds < 0) return '0:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0 || this.TIME_FORMAT.SHOW_HOURS) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            const minStr = this.TIME_FORMAT.PAD_MINUTES ? minutes.toString().padStart(2, '0') : minutes.toString();
            return `${minStr}:${secs.toString().padStart(2, '0')}`;
        }
    }.bind(window.MusicPlayerConfig),
    
    // Log con nivel
    log: function(level, message, ...args) {
        if (!this.DEBUG.ENABLED) return;
        
        const levels = ['debug', 'info', 'warn', 'error'];
        const currentLevelIndex = levels.indexOf(this.DEBUG.LOG_LEVEL);
        const messageLevelIndex = levels.indexOf(level);
        
        if (messageLevelIndex >= currentLevelIndex) {
            const timestamp = new Date().toISOString().substr(11, 12);
            const prefix = `[${timestamp}] [${level.toUpperCase()}] MusicPlayer:`;
            
            switch (level) {
                case 'debug':
                    console.debug(prefix, message, ...args);
                    break;
                case 'info':
                    console.info(prefix, message, ...args);
                    break;
                case 'warn':
                    console.warn(prefix, message, ...args);
                    break;
                case 'error':
                    console.error(prefix, message, ...args);
                    break;
            }
        }
    }.bind(window.MusicPlayerConfig)
};

// Configuración inicial basada en localStorage
document.addEventListener('DOMContentLoaded', function() {
    const config = window.MusicPlayerConfig;
    
    // Cargar configuraciones guardadas
    const savedVolume = config.Utils.getStoredSetting('VOLUME', 70);
    const savedVizMode = config.Utils.getStoredSetting('VISUALIZER_MODE', 'spectrum');
    
    // Aplicar configuraciones
    config.PLAYER.DEFAULT_VOLUME = savedVolume;
    config.VISUALIZER.DEFAULT_MODE = savedVizMode;
    
    config.Utils.log('info', 'Configuración cargada:', {
        volume: savedVolume,
        visualizerMode: savedVizMode
    });
});

// Exportar para módulos que lo necesiten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.MusicPlayerConfig;
}
