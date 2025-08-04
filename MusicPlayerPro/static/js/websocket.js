// 🎵 MUSIC PLAYER PRO - WEBSOCKET CLIENT
// ======================================
// Cliente WebSocket para actualizaciones en tiempo real

class MusicPlayerWebSocket {
    constructor(api) {
        this.api = api;
        this.config = window.MusicPlayerConfig;
        this.socket = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectDelay = 1000;
        this.callbacks = new Map();
        
        this.init();
    }

    // ============================
    // 🔌 INICIALIZACIÓN
    // ============================

    init() {
        this.connect();
        this.setupHeartbeat();
    }

    connect() {
        try {
            this.config.Utils.log('info', 'Conectando a WebSocket...');
            
            this.socket = io(this.config.SERVER.HOST, {
                path: this.config.SERVER.WEBSOCKET_PATH,
                timeout: this.config.SERVER.TIMEOUT,
                forceNew: true,
                upgrade: true,
                transports: ['websocket', 'polling']
            });

            this.setupEventHandlers();
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al conectar WebSocket:', error);
            this.handleReconnect();
        }
    }

    setupEventHandlers() {
        // Conexión exitosa
        this.socket.on('connect', () => {
            this.config.Utils.log('info', 'WebSocket conectado');
            this.isConnected = true;
            this.reconnectAttempts = 0;
            this.updateConnectionStatus('connected');
            this.emit('connected');
            
            // Solicitar estado inicial
            this.requestUpdate();
        });

        // Desconexión
        this.socket.on('disconnect', (reason) => {
            this.config.Utils.log('warn', 'WebSocket desconectado:', reason);
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
            this.emit('disconnected', reason);
            
            // Reconectar automáticamente si no fue intencional
            if (reason !== 'io client disconnect') {
                this.handleReconnect();
            }
        });

        // Error de conexión
        this.socket.on('connect_error', (error) => {
            this.config.Utils.log('error', 'Error de conexión WebSocket:', error);
            this.isConnected = false;
            this.updateConnectionStatus('error');
            this.emit('error', error);
            this.handleReconnect();
        });

        // Actualización de estado del reproductor
        this.socket.on('state_update', (data) => {
            this.config.Utils.log('debug', 'Actualización de estado recibida:', data);
            this.emit('stateUpdate', data);
        });

        // Datos del espectro
        this.socket.on('spectrum_update', (data) => {
            this.emit('spectrumUpdate', data);
        });

        // Mensajes del servidor
        this.socket.on('message', (data) => {
            this.config.Utils.log('info', 'Mensaje del servidor:', data);
            this.emit('message', data);
        });

        // Respuesta de conexión
        this.socket.on('connected', (data) => {
            this.config.Utils.log('info', 'Confirmación de conexión:', data);
        });
    }

    // ============================
    // 💓 HEARTBEAT
    // ============================

    setupHeartbeat() {
        setInterval(() => {
            if (this.isConnected) {
                this.socket.emit('ping');
            }
        }, 30000); // Ping cada 30 segundos
    }

    // ============================
    // 🔄 RECONEXIÓN
    // ============================

    handleReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            this.config.Utils.log('error', 'Máximo de intentos de reconexión alcanzado');
            this.updateConnectionStatus('failed');
            return;
        }

        this.reconnectAttempts++;
        const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
        
        this.config.Utils.log('info', `Reintentando conexión en ${delay}ms (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        this.updateConnectionStatus('connecting');

        setTimeout(() => {
            if (!this.isConnected) {
                this.connect();
            }
        }, delay);
    }

    // ============================
    // 📡 COMUNICACIÓN
    // ============================

    emit(event, data = null) {
        // Emitir a listeners internos
        if (this.callbacks.has(event)) {
            const callbacks = this.callbacks.get(event);
            callbacks.forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    this.config.Utils.log('error', `Error en callback ${event}:`, error);
                }
            });
        }
    }

    send(event, data = null) {
        if (this.isConnected && this.socket) {
            this.config.Utils.log('debug', `Enviando evento: ${event}`, data);
            this.socket.emit(event, data);
        } else {
            this.config.Utils.log('warn', `No se puede enviar ${event}: no conectado`);
        }
    }

    // ============================
    // 👂 EVENT LISTENERS
    // ============================

    on(event, callback) {
        if (!this.callbacks.has(event)) {
            this.callbacks.set(event, []);
        }
        this.callbacks.get(event).push(callback);
    }

    off(event, callback) {
        if (this.callbacks.has(event)) {
            const callbacks = this.callbacks.get(event);
            const index = callbacks.indexOf(callback);
            if (index !== -1) {
                callbacks.splice(index, 1);
            }
        }
    }

    // ============================
    // 🎵 MÉTODOS ESPECÍFICOS
    // ============================

    requestUpdate() {
        this.send('request_update');
    }

    // ============================
    // 🎨 UI UPDATES
    // ============================

    updateConnectionStatus(status) {
        const indicator = document.getElementById('connection-indicator');
        const text = document.getElementById('connection-text');
        
        if (indicator && text) {
            // Remover clases anteriores
            indicator.classList.remove('connected', 'connecting', 'disconnected', 'error', 'failed');
            
            // Agregar nueva clase y texto
            indicator.classList.add(status);
            
            const statusTexts = {
                connected: 'Conectado',
                connecting: 'Conectando...',
                disconnected: 'Desconectado',
                error: 'Error de conexión',
                failed: 'Conexión fallida'
            };
            
            text.textContent = statusTexts[status] || status;
        }
    }

    // ============================
    // 🔧 UTILIDADES
    // ============================

    getConnectionInfo() {
        return {
            isConnected: this.isConnected,
            reconnectAttempts: this.reconnectAttempts,
            socketId: this.socket?.id || null
        };
    }

    disconnect() {
        if (this.socket) {
            this.config.Utils.log('info', 'Desconectando WebSocket...');
            this.socket.disconnect();
            this.isConnected = false;
            this.updateConnectionStatus('disconnected');
        }
    }

    reconnect() {
        this.disconnect();
        this.reconnectAttempts = 0;
        setTimeout(() => this.connect(), 100);
    }
}

// ============================
// 🌐 INICIALIZACIÓN GLOBAL
// ============================

let musicPlayerWebSocket = null;

document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que la API esté disponible
    if (window.musicPlayerAPI) {
        musicPlayerWebSocket = new MusicPlayerWebSocket(window.musicPlayerAPI);
        window.musicPlayerWebSocket = musicPlayerWebSocket;
        
        window.MusicPlayerConfig.Utils.log('info', 'WebSocket client inicializado');
    } else {
        console.error('API no disponible para WebSocket');
    }
});

// Cleanup al cerrar la página
window.addEventListener('beforeunload', function() {
    if (musicPlayerWebSocket) {
        musicPlayerWebSocket.disconnect();
    }
});

// Exportar para módulos que lo necesiten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MusicPlayerWebSocket;
}
