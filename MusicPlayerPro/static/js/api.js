// 🎵 MUSIC PLAYER PRO - API CLIENT
// =================================
// Cliente API para comunicación con el backend Flask

class MusicPlayerAPI {
    constructor() {
        this.config = window.MusicPlayerConfig;
        this.baseUrl = this.config.SERVER.HOST;
        this.timeout = this.config.SERVER.TIMEOUT;
    }

    // ============================
    // 🔧 MÉTODOS AUXILIARES
    // ============================

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            timeout: this.timeout
        };

        const requestOptions = { ...defaultOptions, ...options };

        try {
            this.config.Utils.log('debug', `API Request: ${requestOptions.method} ${url}`, requestOptions);

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);

            const response = await fetch(url, {
                ...requestOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();
            this.config.Utils.log('debug', `API Response: ${url}`, data);

            return data;

        } catch (error) {
            this.config.Utils.log('error', `API Error: ${url}`, error);
            
            if (error.name === 'AbortError') {
                throw new Error('Timeout: La solicitud tardó demasiado tiempo');
            }
            
            throw error;
        }
    }

    async makePostRequest(endpoint, data = {}) {
        return this.makeRequest(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    // ============================
    // 🏥 HEALTH CHECK
    // ============================

    async checkHealth() {
        try {
            const response = await this.makeRequest('/health');
            return response.status === 'ok';
        } catch (error) {
            return false;
        }
    }

    // ============================
    // 🎵 CONTROL DE REPRODUCCIÓN
    // ============================

    async play() {
        return this.makePostRequest('/api/player/play');
    }

    async pause() {
        return this.makePostRequest('/api/player/pause');
    }

    async stop() {
        return this.makePostRequest('/api/player/stop');
    }

    async next() {
        return this.makePostRequest('/api/player/next');
    }

    async previous() {
        return this.makePostRequest('/api/player/previous');
    }

    async setVolume(volume) {
        if (typeof volume !== 'number' || volume < 0 || volume > 100) {
            throw new Error('El volumen debe estar entre 0 y 100');
        }

        return this.makePostRequest('/api/player/volume', { volume });
    }

    async seek(position) {
        if (typeof position !== 'number' || position < 0) {
            throw new Error('La posición debe ser un número positivo');
        }

        return this.makePostRequest('/api/player/seek', { position });
    }

    // ============================
    // 📊 ESTADO DEL REPRODUCTOR
    // ============================

    async getPlayerState() {
        return this.makeRequest('/api/player/state');
    }

    // ============================
    // 📚 BIBLIOTECA MUSICAL
    // ============================

    async getSongs() {
        return this.makeRequest('/api/library/songs');
    }

    async searchSongs(query) {
        if (!query || typeof query !== 'string') {
            return this.getSongs();
        }

        const encodedQuery = encodeURIComponent(query.trim());
        return this.makeRequest(`/api/library/search?q=${encodedQuery}`);
    }

    async playTrack(trackId) {
        if (!trackId) {
            throw new Error('ID de pista requerido');
        }

        return this.makeRequest(`/api/library/play/${encodeURIComponent(trackId)}`);
    }

    // ============================
    // 📊 VISUALIZADOR
    // ============================

    async getSpectrumData() {
        return this.makeRequest('/api/visualizer/spectrum');
    }

    // ============================
    // 🎛️ MÉTODOS DE CONVENIENCIA
    // ============================

    async togglePlayPause() {
        try {
            const state = await this.getPlayerState();
            
            if (state.status === 'success' && state.player_state) {
                const isPlaying = state.player_state.state === 'playing';
                return isPlaying ? await this.pause() : await this.play();
            } else {
                return await this.play();
            }
        } catch (error) {
            this.config.Utils.log('warn', 'Error al obtener estado, intentando play', error);
            return await this.play();
        }
    }

    async adjustVolume(delta) {
        try {
            const state = await this.getPlayerState();
            
            if (state.status === 'success' && state.player_state) {
                const currentVolume = state.player_state.volume || 50;
                const newVolume = Math.max(0, Math.min(100, currentVolume + delta));
                return await this.setVolume(newVolume);
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error al ajustar volumen', error);
            throw error;
        }
    }

    async seekRelative(seconds) {
        try {
            const state = await this.getPlayerState();
            
            if (state.status === 'success' && state.player_state) {
                const currentPosition = state.player_state.position || 0;
                const duration = state.player_state.duration || 0;
                const newPosition = Math.max(0, Math.min(duration, currentPosition + seconds));
                
                return await this.seek(newPosition);
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error al navegar relativamente', error);
            throw error;
        }
    }

    // ============================
    // 📋 BATCH OPERATIONS
    // ============================

    async batchRequest(requests) {
        const promises = requests.map(request => {
            const { method, endpoint, data } = request;
            
            if (method === 'POST') {
                return this.makePostRequest(endpoint, data);
            } else {
                return this.makeRequest(endpoint);
            }
        });

        try {
            const results = await Promise.allSettled(promises);
            
            return results.map((result, index) => ({
                request: requests[index],
                success: result.status === 'fulfilled',
                data: result.status === 'fulfilled' ? result.value : null,
                error: result.status === 'rejected' ? result.reason : null
            }));
            
        } catch (error) {
            this.config.Utils.log('error', 'Error en batch request', error);
            throw error;
        }
    }

    // ============================
    // 🔄 RETRY LOGIC
    // ============================

    async makeRequestWithRetry(endpoint, options = {}, maxRetries = 3) {
        let lastError;

        for (let attempt = 1; attempt <= maxRetries; attempt++) {
            try {
                return await this.makeRequest(endpoint, options);
            } catch (error) {
                lastError = error;
                
                if (attempt < maxRetries) {
                    const delay = Math.pow(2, attempt) * 1000; // Exponential backoff
                    this.config.Utils.log('warn', `Reintentando en ${delay}ms (intento ${attempt}/${maxRetries})`);
                    await new Promise(resolve => setTimeout(resolve, delay));
                } else {
                    this.config.Utils.log('error', `Falló después de ${maxRetries} intentos`);
                }
            }
        }

        throw lastError;
    }

    // ============================
    // 🎵 FUNCIONES ADICIONALES
    // ============================

    async addToQueue(trackId) {
        if (!trackId) {
            throw new Error('ID de pista requerido');
        }
        return this.makeRequest(`/api/player/queue/add/${encodeURIComponent(trackId)}`, {
            method: 'POST'
        });
    }

    async addToFavorites(trackId) {
        if (!trackId) {
            throw new Error('ID de pista requerido');
        }
        return this.makeRequest(`/api/library/favorites/add/${encodeURIComponent(trackId)}`, {
            method: 'POST'
        });
    }

    async shufflePlay() {
        return this.makeRequest('/api/player/shuffle', {
            method: 'POST'
        });
    }

    async getSongs() {
        return this.makeRequest('/api/library/songs');
    }
}

// ============================
// 🌐 SINGLETON INSTANCE
// ============================

window.musicPlayerAPI = new MusicPlayerAPI();

// Exportar para módulos que lo necesiten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MusicPlayerAPI;
}
