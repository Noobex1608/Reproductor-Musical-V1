// 🎵 MUSIC PLAYER PRO - UI UTILITIES
// ==================================
// Utilidades generales de interfaz de usuario

// Definir extensiones de UI para cuando MusicPlayerApp esté disponible
window.UIExtensions = {
    
    // ============================
    // 🎨 GESTIÓN DE TEMAS
    // ============================

    applyTheme(themeName) {
        const theme = this.config.THEMES[themeName];
        if (!theme) return;

        const root = document.documentElement;
        root.style.setProperty('--accent-primary', theme.primary);
        root.style.setProperty('--accent-secondary', theme.secondary);
        root.style.setProperty('--bg-primary', theme.background);
        root.style.setProperty('--bg-secondary', theme.surface);
        root.style.setProperty('--text-primary', theme.text);

        this.config.Utils.setStoredSetting('THEME', themeName);
        this.showToast('info', 'Tema', `Tema ${theme.name} aplicado`);
    },

    // ============================
    // 🔄 ANIMACIONES
    // ============================

    fadeIn(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.opacity = '0';
            element.style.display = 'block';
            element.style.transition = `opacity ${duration}ms ease`;

            requestAnimationFrame(() => {
                element.style.opacity = '1';
                setTimeout(resolve, duration);
            });
        });
    },

    fadeOut(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.transition = `opacity ${duration}ms ease`;
            element.style.opacity = '0';

            setTimeout(() => {
                element.style.display = 'none';
                resolve();
            }, duration);
        });
    },

    slideDown(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.height = '0px';
            element.style.overflow = 'hidden';
            element.style.display = 'block';
            element.style.transition = `height ${duration}ms ease`;

            const targetHeight = element.scrollHeight + 'px';
            
            requestAnimationFrame(() => {
                element.style.height = targetHeight;
                setTimeout(() => {
                    element.style.height = 'auto';
                    element.style.overflow = 'visible';
                    resolve();
                }, duration);
            });
        });
    },

    slideUp(element, duration = 300) {
        if (!element) return Promise.resolve();

        return new Promise(resolve => {
            element.style.height = element.scrollHeight + 'px';
            element.style.overflow = 'hidden';
            element.style.transition = `height ${duration}ms ease`;

            requestAnimationFrame(() => {
                element.style.height = '0px';
                setTimeout(() => {
                    element.style.display = 'none';
                    resolve();
                }, duration);
            });
        });
    },

    // ============================
    // 📱 RESPONSIVIDAD
    // ============================

    checkMobileLayout() {
        const isMobile = window.innerWidth <= 768;
        const isTablet = window.innerWidth <= 1024 && window.innerWidth > 768;

        document.body.classList.toggle('mobile-layout', isMobile);
        document.body.classList.toggle('tablet-layout', isTablet);
        document.body.classList.toggle('desktop-layout', !isMobile && !isTablet);

        // Ajustar visualizador en móvil
        if (isMobile && window.visualizer) {
            window.visualizer.setMode('spectrum'); // Modo más simple
        }

        return { isMobile, isTablet };
    },

    setupResponsiveLayout() {
        window.addEventListener('resize', () => {
            this.checkMobileLayout();
            
            // Redimensionar visualizador si es necesario
            if (window.visualizer) {
                setTimeout(() => window.visualizer.resize(), 100);
            }
        });

        // Check inicial
        this.checkMobileLayout();
    },

    // ============================
    // 🍞 GESTIÓN AVANZADA DE TOASTS
    // ============================

    showToastWithAction(type, title, message, actionText, actionCallback) {
        if (!this.elements.toastContainer) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;

        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };

        toast.innerHTML = `
            <i class="toast-icon ${iconMap[type] || iconMap.info}"></i>
            <div class="toast-content">
                <div class="toast-title">${title}</div>
                <div class="toast-message">${message}</div>
                ${actionText ? `<button class="toast-action">${actionText}</button>` : ''}
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Event listeners
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => toast.remove());

        const actionBtn = toast.querySelector('.toast-action');
        if (actionBtn && actionCallback) {
            actionBtn.addEventListener('click', () => {
                actionCallback();
                toast.remove();
            });
        }

        this.elements.toastContainer.appendChild(toast);

        // Auto remover después de 8 segundos (más tiempo por la acción)
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 8000);
    },

    clearAllToasts() {
        if (this.elements.toastContainer) {
            this.elements.toastContainer.innerHTML = '';
        }
    },

    // ============================
    // 🔍 BÚSQUEDA AVANZADA
    // ============================

    setupAdvancedSearch() {
        if (!this.elements.searchInput) return;

        let searchHistory = this.config.Utils.getStoredSetting('SEARCH_HISTORY', []);
        
        // Autocompletado basado en historial
        const suggestionsList = document.createElement('div');
        suggestionsList.className = 'search-suggestions';
        suggestionsList.style.display = 'none';
        this.elements.searchInput.parentNode.appendChild(suggestionsList);

        this.elements.searchInput.addEventListener('focus', () => {
            if (searchHistory.length > 0) {
                this.showSearchSuggestions(suggestionsList, searchHistory);
            }
        });

        this.elements.searchInput.addEventListener('blur', () => {
            setTimeout(() => {
                suggestionsList.style.display = 'none';
            }, 200);
        });

        this.elements.searchInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const query = this.elements.searchInput.value.trim();
                if (query) {
                    this.addToSearchHistory(query);
                    this.searchSongs(query);
                }
            }
        });
    },

    showSearchSuggestions(container, suggestions) {
        container.innerHTML = '';
        
        suggestions.slice(0, 5).forEach(suggestion => {
            const item = document.createElement('div');
            item.className = 'search-suggestion-item';
            item.textContent = suggestion;
            
            item.addEventListener('click', () => {
                this.elements.searchInput.value = suggestion;
                this.searchSongs(suggestion);
                container.style.display = 'none';
            });
            
            container.appendChild(item);
        });

        container.style.display = suggestions.length > 0 ? 'block' : 'none';
    },

    addToSearchHistory(query) {
        let history = this.config.Utils.getStoredSetting('SEARCH_HISTORY', []);
        
        // Remover si ya existe
        history = history.filter(item => item !== query);
        
        // Agregar al inicio
        history.unshift(query);
        
        // Limitar a 10 elementos
        history = history.slice(0, 10);
        
        this.config.Utils.setStoredSetting('SEARCH_HISTORY', history);
    },

    // ============================
    // ⌨️ ATAJOS DE TECLADO AVANZADOS
    // ============================

    showKeyboardShortcuts() {
        const shortcuts = [
            { keys: 'Espacio', action: 'Reproducir/Pausar' },
            { keys: 'Ctrl + ←/→', action: 'Pista Anterior/Siguiente' },
            { keys: '←/→', action: 'Navegar 10s' },
            { keys: 'Shift + ←/→', action: 'Navegar 30s' },
            { keys: 'Ctrl + ↑/↓', action: 'Subir/Bajar Volumen' },
            { keys: 'Ctrl + M', action: 'Mutear/Desmutear' },
            { keys: 'Ctrl + S', action: 'Aleatorio' },
            { keys: 'Ctrl + R', action: 'Repetir' },
            { keys: 'Ctrl + F', action: 'Buscar' },
            { keys: 'Escape', action: 'Cerrar Modal' }
        ];

        const content = `
            <div class="shortcuts-container">
                <h4>Atajos de Teclado</h4>
                <div class="shortcuts-list">
                    ${shortcuts.map(shortcut => `
                        <div class="shortcut-item">
                            <kbd class="shortcut-keys">${shortcut.keys}</kbd>
                            <span class="shortcut-action">${shortcut.action}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        this.showModal('Atajos de Teclado', content);
    },

    // ============================
    // 📊 INFORMACIÓN DEL SISTEMA
    // ============================

    async showSystemInfo() {
        const info = {
            version: '2.0.0',
            framework: 'Flask + HTML5',
            browser: navigator.userAgent,
            screen: `${screen.width}x${screen.height}`,
            viewport: `${window.innerWidth}x${window.innerHeight}`,
            connection: this.websocket ? this.websocket.getConnectionInfo() : null,
            performance: {
                memory: performance.memory ? {
                    used: Math.round(performance.memory.usedJSHeapSize / 1024 / 1024) + ' MB',
                    total: Math.round(performance.memory.totalJSHeapSize / 1024 / 1024) + ' MB',
                    limit: Math.round(performance.memory.jsHeapSizeLimit / 1024 / 1024) + ' MB'
                } : 'No disponible'
            }
        };

        // Verificar estado del servidor
        const serverHealthy = await this.api.checkHealth();

        const content = `
            <div class="system-info">
                <h4>Información del Sistema</h4>
                
                <div class="info-section">
                    <h5>Aplicación</h5>
                    <div class="info-item">
                        <span>Versión:</span>
                        <span>${info.version}</span>
                    </div>
                    <div class="info-item">
                        <span>Framework:</span>
                        <span>${info.framework}</span>
                    </div>
                    <div class="info-item">
                        <span>Servidor:</span>
                        <span class="${serverHealthy ? 'status-online' : 'status-offline'}">
                            ${serverHealthy ? 'En línea' : 'Desconectado'}
                        </span>
                    </div>
                </div>

                <div class="info-section">
                    <h5>Navegador</h5>
                    <div class="info-item">
                        <span>User Agent:</span>
                        <span class="user-agent">${info.browser}</span>
                    </div>
                    <div class="info-item">
                        <span>Pantalla:</span>
                        <span>${info.screen}</span>
                    </div>
                    <div class="info-item">
                        <span>Viewport:</span>
                        <span>${info.viewport}</span>
                    </div>
                </div>

                ${info.connection ? `
                <div class="info-section">
                    <h5>Conexión WebSocket</h5>
                    <div class="info-item">
                        <span>Estado:</span>
                        <span class="${info.connection.isConnected ? 'status-online' : 'status-offline'}">
                            ${info.connection.isConnected ? 'Conectado' : 'Desconectado'}
                        </span>
                    </div>
                    <div class="info-item">
                        <span>Reintentos:</span>
                        <span>${info.connection.reconnectAttempts}</span>
                    </div>
                    <div class="info-item">
                        <span>Socket ID:</span>
                        <span>${info.connection.socketId || 'N/A'}</span>
                    </div>
                </div>
                ` : ''}

                ${info.performance.memory !== 'No disponible' ? `
                <div class="info-section">
                    <h5>Rendimiento</h5>
                    <div class="info-item">
                        <span>Memoria Usada:</span>
                        <span>${info.performance.memory.used}</span>
                    </div>
                    <div class="info-item">
                        <span>Memoria Total:</span>
                        <span>${info.performance.memory.total}</span>
                    </div>
                    <div class="info-item">
                        <span>Límite:</span>
                        <span>${info.performance.memory.limit}</span>
                    </div>
                </div>
                ` : ''}

                <div class="info-actions">
                    <button class="btn btn-secondary" onclick="musicPlayerApp.copySystemInfo()">
                        <i class="fas fa-copy"></i>
                        Copiar Info
                    </button>
                    <button class="btn btn-secondary" onclick="musicPlayerApp.downloadLogs()">
                        <i class="fas fa-download"></i>
                        Descargar Logs
                    </button>
                </div>
            </div>
        `;

        this.showModal('Información del Sistema', content);
    },

    copySystemInfo() {
        // TODO: Implementar copia al portapapeles
        this.showToast('info', 'Copiado', 'Información copiada al portapapeles');
    },

    downloadLogs() {
        // TODO: Implementar descarga de logs
        this.showToast('info', 'Descarga', 'Funcionalidad próximamente disponible');
    },

    // ============================
    // 🎛️ CONFIGURACIÓN
    // ============================

    showSettings() {
        const settings = this.config.Utils.getStoredSetting('SETTINGS', {});
        
        const content = `
            <div class="settings-container">
                <h4>Configuración</h4>
                
                <div class="settings-section">
                    <h5>Reproducción</h5>
                    
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="auto-play" ${settings.autoPlay ? 'checked' : ''}>
                            Reproducción automática
                        </label>
                    </div>
                    
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="crossfade" ${settings.crossfade ? 'checked' : ''}>
                            Crossfade entre pistas
                        </label>
                    </div>
                    
                    <div class="setting-item">
                        <label for="seek-step">Paso de navegación (segundos):</label>
                        <input type="number" id="seek-step" min="5" max="60" value="${settings.seekStep || 10}">
                    </div>
                </div>

                <div class="settings-section">
                    <h5>Interfaz</h5>                    
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="show-tooltips" ${settings.showTooltips !== false ? 'checked' : ''}>
                            Mostrar tooltips
                        </label>
                    </div>
                    
                    <div class="setting-item">
                        <label>
                            <input type="checkbox" id="compact-mode" ${settings.compactMode ? 'checked' : ''}>
                            Modo compacto
                        </label>
                    </div>
                </div>

                <div class="settings-section">
                    <h5>Visualizador</h5>
                    
                    <div class="setting-item">
                        <label for="viz-mode">Modo por defecto:</label>
                        <select id="viz-mode">
                            <option value="spectrum">Espectro</option>
                            <option value="waveform">Ondas</option>
                            <option value="circular">Circular</option>
                        </select>
                    </div>
                    
                    <div class="setting-item">
                        <label for="viz-sensitivity">Sensibilidad:</label>
                        <input type="range" id="viz-sensitivity" min="0.1" max="2" step="0.1" value="${settings.vizSensitivity || 1}">
                    </div>
                </div>

                <div class="settings-actions">
                    <button class="btn btn-primary" onclick="musicPlayerApp.saveSettings()">
                        <i class="fas fa-save"></i>
                        Guardar
                    </button>
                    <button class="btn btn-secondary" onclick="musicPlayerApp.resetSettings()">
                        <i class="fas fa-undo"></i>
                        Restablecer
                    </button>
                </div>
            </div>
        `;

        this.showModal('Configuración', content);
    },

    saveSettings() {
        // TODO: Implementar guardado de configuración
        this.showToast('success', 'Guardado', 'Configuración guardada correctamente');
        this.hideModal();
    },

    resetSettings() {
        // TODO: Implementar restablecimiento
        this.showToast('info', 'Restablecido', 'Configuración restablecida a valores por defecto');
    }
};

// Estilos adicionales para las utilidades de UI
const uiUtilsStyles = `
    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-top: none;
        border-radius: 0 0 var(--border-radius-lg) var(--border-radius-lg);
        box-shadow: var(--shadow-md);
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    }
    
    .search-suggestion-item {
        padding: var(--spacing-sm) var(--spacing-md);
        cursor: pointer;
        transition: background var(--transition-fast);
        font-size: var(--font-size-sm);
        color: var(--text-secondary);
    }
    
    .search-suggestion-item:hover {
        background: var(--bg-accent);
        color: var(--text-primary);
    }
    
    .shortcuts-container,
    .system-info,
    .settings-container {
        max-width: 600px;
        margin: 0 auto;
    }
    
    .shortcuts-list {
        display: flex;
        flex-direction: column;
        gap: var(--spacing-sm);
        margin-top: var(--spacing-md);
    }
    
    .shortcut-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: var(--spacing-sm);
        background: var(--bg-tertiary);
        border-radius: var(--border-radius-sm);
    }
    
    .shortcut-keys {
        background: var(--bg-accent);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: var(--font-size-xs);
        font-family: monospace;
        border: 1px solid var(--border-color);
    }
    
    .info-section,
    .settings-section {
        margin-bottom: var(--spacing-lg);
        padding: var(--spacing-md);
        background: var(--bg-tertiary);
        border-radius: var(--border-radius-md);
    }
    
    .info-section h5,
    .settings-section h5 {
        margin-bottom: var(--spacing-md);
        color: var(--accent-primary);
        font-size: var(--font-size-sm);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .info-item,
    .setting-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: var(--spacing-xs) 0;
        border-bottom: 1px solid var(--border-color);
        font-size: var(--font-size-sm);
    }
    
    .info-item:last-child,
    .setting-item:last-child {
        border-bottom: none;
    }
    
    .user-agent {
        font-family: monospace;
        font-size: var(--font-size-xs);
        max-width: 300px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .status-online {
        color: var(--success);
        font-weight: 500;
    }
    
    .status-offline {
        color: var(--error);
        font-weight: 500;
    }
    
    .info-actions,
    .settings-actions {
        display: flex;
        gap: var(--spacing-md);
        justify-content: center;
        margin-top: var(--spacing-lg);
        padding-top: var(--spacing-lg);
        border-top: 1px solid var(--border-color);
    }
    
    .toast-action {
        background: var(--accent-primary);
        color: white;
        border: none;
        padding: var(--spacing-xs) var(--spacing-sm);
        border-radius: var(--border-radius-sm);
        font-size: var(--font-size-xs);
        cursor: pointer;
        margin-top: var(--spacing-xs);
        transition: all var(--transition-fast);
    }
    
    .toast-action:hover {
        background: #ff5252;
        transform: translateY(-1px);
    }
`;

// Inyectar estilos
if (!document.getElementById('ui-utils-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'ui-utils-styles';
    styleSheet.textContent = uiUtilsStyles;
    document.head.appendChild(styleSheet);
}

// Inicializar utilidades UI cuando la app esté lista
document.addEventListener('DOMContentLoaded', function() {
    const initUIUtils = () => {
        if (window.musicPlayerApp) {
            window.musicPlayerApp.setupResponsiveLayout();
            window.musicPlayerApp.setupAdvancedSearch();
            
            // Agregar botones de configuración a la UI
            const settingsBtn = document.getElementById('settings-btn');
            if (settingsBtn) {
                settingsBtn.addEventListener('click', () => {
                    window.musicPlayerApp.showSettings();
                });
            }
        } else {
            setTimeout(initUIUtils, 100);
        }
    };
    
    setTimeout(initUIUtils, 1000);
});


// Configura tu API Key de ChatGPT (guárdala de forma segura)
//QUITAR AL MOMENTO DE PROBAR
// const CHATGPT_API_KEY = 'AQUI VA LA API KEY';

// Renderizar las recomendaciones
function renderRecommendations(data) {
    const recommendationsList = document.getElementById('recommendations-list');
    
    if (!data || !data.recommendations || data.recommendations.length === 0) {
        recommendationsList.innerHTML = `
            <div class="recommendations-placeholder">
                <i class="fas fa-info-circle"></i>
                <p>No hay recomendaciones disponibles</p>
                <small>Intenta reproducir una canción primero</small>
            </div>
        `;
        return;
    }

    recommendationsList.innerHTML = data.recommendations.map(song => `
        <div class="recommendation-item">
            <div class="recommendation-artwork">
                <i class="fas fa-music"></i>
            </div>
            <div class="recommendation-info">
                <div class="recommendation-title">${song.title}</div>
                <div class="recommendation-artist">${song.artist}</div>
                <div class="recommendation-meta">
                    <span>${song.genre || 'Género desconocido'}</span>
                    ${song.year ? `• <span>${song.year}</span>` : ''}
                    <span class="recommendation-reason" title="${song.reason}">
                        <i class="fas fa-info-circle"></i>
                    </span>
                </div>
            </div>
            <button class="recommendation-play" onclick="searchAndPlay('${song.title}', '${song.artist}')">
                <i class="fas fa-play"></i>
            </button>
        </div>
    `).join('');
}

// Función para buscar y reproducir una canción recomendada
function searchAndPlay(title, artist) {
    // Implementar la búsqueda en tu biblioteca o servicios externos
    window.musicPlayerApp.showToast('info', 'Buscando', `Buscando "${title}"...`);
    
    // Aquí iría tu lógica para encontrar y reproducir la canción
    console.log(`Intentando reproducir: ${title} - ${artist}`);
}

// Mostrar errores
function showRecommendationsError(error) {
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = `
        <div class="recommendations-placeholder error">
            <i class="fas fa-exclamation-triangle"></i>
            <p>Error al cargar recomendaciones</p>
            <small>${error.message || 'Intenta de nuevo más tarde'}</small>
            <button onclick="loadDynamicRecommendations()" class="btn-retry">
                Reintentar
            </button>
        </div>
    `;
}

// Variable para llevar un conteo de recargas
let recommendationRefreshCount = 0;

// Función principal para cargar recomendaciones
async function loadDynamicRecommendations() {
    const recommendationsList = document.getElementById('recommendations-list');
    let currentSong = { title: 'Aleatorio', artist: 'Aleatorio' };
    if (window.musicPlayerApp && typeof window.musicPlayerApp.getCurrentSong === 'function') {
        const song = window.musicPlayerApp.getCurrentSong();
        if (song && song.title) {
            currentSong = song;
        }
    }

    // Aumentar el contador de recargas
    recommendationRefreshCount++;
    
    // Mostrar estado de carga
    recommendationsList.innerHTML = `
        <div class="recommendations-placeholder">
            <i class="fas fa-music"></i>
            <p>Buscando nuevas recomendaciones</p>
            <center><div class="loading-spinner-small"></div></center>
        </div>
    `;

    try {
        let recommendations;
        let prompt;
        const randomSeed = Math.floor(Math.random() * 1000);
        
        if (currentSong) {
            // Incluir el contador y semilla en el prompt para variar las respuestas
            prompt = `Como experto en música, recomienda 3 diferentes canciones populares a "${currentSong.title}" de ${currentSong.artist}. 
            Esta es la solicitud número ${recommendationRefreshCount}, por favor varía las recomendaciones.
            Varía completamente las recomendaciones.
            No repitas canciones que ya hayas recomendado anteriormente en esta sesión.
            
            Devuelve solo un JSON con este formato:
            {
                "recommendations": [
                    {
                        "title": "Nombre canción",
                        "artist": "Artista",
                        "genre": "Género",
                        "reason": "Por qué es similar"
                    }
                ]
            }`;
            
            recommendations = await getChatGPTRecommendations(prompt);
        } else {
            prompt = `Recomienda 3 diferentes canciones populares de diferentes géneros (solicitud #${recommendationRefreshCount}). 
            Varía las recomendaciones cada vez.
            Varía completamente las recomendaciones.
            No repitas canciones que ya hayas recomendado anteriormente en esta sesión.

            Devuelve solo un JSON con este formato:
            {
                "recommendations": [
                    {
                        "title": "Nombre canción",
                        "artist": "Artista",
                        "genre": "Género",
                        "reason": "Por qué es buena recomendación"
                    }
                ]
            }`;
            
            recommendations = await getChatGPTRecommendations(prompt);
        }
        
        renderRecommendations(recommendations);
        
    } catch (error) {
        console.error("Error al cargar recomendaciones:", error);
        showRecommendationsError(error);
    }
    console.log("🔄 Recomendaciones recibidas:", recommendationsList);
}

// Función modificada para aceptar prompt personalizado
async function getChatGPTRecommendations(prompt) {
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${CHATGPT_API_KEY}`
        },
        body: JSON.stringify({
            model: "gpt-3.5-turbo",
            messages: [{
                role: "user",
                content: prompt
            }],
            temperature: 0.8, // Aumentamos temperatura para más variedad
            max_tokens: 500
        })
    });
    
    if (!response.ok) {
        throw new Error(`Error de API: ${response.status}`);
    }
    
    const data = await response.json();
    try {
        return JSON.parse(data.choices[0].message.content);
    } catch (e) {
        console.error("Error parsing response:", e);
        throw new Error("Formato de respuesta inválido");
    }
}

// Inicializar al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    loadDynamicRecommendations();
    // Opcional: Actualizar cuando cambia la canción
    if (window.musicPlayerApp) {
        window.musicPlayerApp.on('songChanged', loadDynamicRecommendations);
    }
});

document.getElementById('refresh-recommendations').addEventListener('click', function(e) {
    e.preventDefault();
    loadDynamicRecommendations();
    
    // Efecto visual de rotación al hacer clic
    const icon = this.querySelector('i');
    icon.style.transform = 'rotate(360deg)';
    icon.style.transition = 'transform 0.5s ease';
    
    setTimeout(() => {
        icon.style.transform = 'rotate(0deg)';
    }, 500);
});