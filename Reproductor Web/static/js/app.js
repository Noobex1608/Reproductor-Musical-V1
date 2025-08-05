// 🎵 MUSIC PLAYER PRO - MAIN APPLICATION
// ======================================
// Aplicación principal JavaScript

class MusicPlayerApp {
    constructor() {
        this.config = window.MusicPlayerConfig;
        this.api = window.musicPlayerAPI;
        this.websocket = null;
        
        // Estado de la aplicación
        this.state = {
            isInitialized: false,
            currentTrack: null,
            isPlaying: false,
            isPaused: false,
            volume: 70,
            position: 0,
            duration: 0,
            playlist: [],
            currentPlaylistIndex: -1,
            shuffleEnabled: false,
            repeatMode: 'none'  // none, one, all
        };
        
        // Referencias DOM
        this.elements = {};
        
        this.config.Utils.log('info', 'Aplicación Music Player Pro inicializada');
    }

    // ============================
    // 🚀 INICIALIZACIÓN
    // ============================

    async init() {
        try {
            this.showLoadingScreen();
            
            // 1. Verificar conexión con servidor
            await this.checkServerConnection();
            
            // 2. Obtener referencias DOM
            this.setupDOMReferences();
            
            // 3. Configurar WebSocket
            this.setupWebSocket();
            
            // 4. Configurar event listeners
            this.setupEventListeners();
            
            // 5. Configurar layout responsivo
            this.setupResponsiveLayout();
            
            // 6. Cargar estado inicial
            await this.loadInitialState();
            
            // 7. Cargar biblioteca musical
            await this.loadLibrary();
            
            // 8. Configurar visualizador
            this.setupVisualizer();
            
            // 9. Mostrar aplicación
            this.hideLoadingScreen();
            
            this.state.isInitialized = true;
            
            // 9. Cargar extensiones
            this.loadExtensions();
            
            this.config.Utils.log('info', 'Aplicación inicializada correctamente');
            
            this.showToast('success', '¡Bienvenido!', 'Music Player Pro está listo');
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al inicializar aplicación:', error);
            this.showError('Error de inicialización', error.message);
        }
    }

    async checkServerConnection() {
        const isHealthy = await this.api.checkHealth();
        
        if (!isHealthy) {
            throw new Error('No se puede conectar con el servidor. Verifica que esté ejecutándose.');
        }
        
        this.config.Utils.log('info', 'Conexión con servidor establecida');
    }

    setupDOMReferences() {
        const selectors = {
            // Loading
            loadingScreen: '#loading-screen',
            mainApp: '#main-app',
            
            // Player controls
            playPauseBtn: '#play-pause-btn',
            prevBtn: '#prev-btn',
            nextBtn: '#next-btn',
            stopBtn: '#stop-btn',
            shuffleBtn: '#shuffle-btn',
            repeatBtn: '#repeat-btn',
            
            // Volume
            volumeSlider: '#volume-slider',
            volumeIcon: '#volume-icon',
            volumeDisplay: '#volume-display',
            
            // Progress
            progressContainer: '.progress-container',
            progressBar: '.progress-bar',
            progressFill: '#progress-fill',
            progressHandle: '#progress-handle',
            currentTime: '#current-time',
            totalTime: '#total-time',
            
            // Track info
            currentTitle: '#current-title',
            currentArtist: '#current-artist',
            currentAlbum: '#current-album',
            trackArtwork: '#track-artwork',
            
            // Library
            songsList: '#songs-list',
            songsLoading: '#songs-loading',
            noSongs: '#no-songs',
            searchInput: '#search-input',
            searchClear: '#search-clear',
            libraryCount: '#library-count',
            
            // Current Song Display
            currentSongContainer: '#current-song-container',
            currentSongItem: '#current-song-item',
            currentSongNumber: '#current-song-number',
            totalSongsCount: '#total-songs-count',
            prevSongBtn: '#prev-song-btn',
            nextSongBtn: '#next-song-btn',
            
            // Controls
            refreshLibrary: '#refresh-library',
            sortSelect: '#sort-select',
            playAllBtn: '#play-all-btn',
            addMusicBtn: '#add-music-btn',
            
            // Modals
            modalOverlay: '#modal-overlay',
            modalTitle: '#modal-title',
            modalBody: '#modal-body',
            modalClose: '#modal-close',
            
            // Toast
            toastContainer: '#toast-container'
        };

        this.elements = {};
        for (const [key, selector] of Object.entries(selectors)) {
            this.elements[key] = document.querySelector(selector);
            if (!this.elements[key] && ['shuffleBtn', 'repeatBtn', 'addMusicBtn'].includes(key)) {
                this.config.Utils.log('error', `❌ Elemento no encontrado: ${key} (selector: ${selector})`);
            } else if (['shuffleBtn', 'repeatBtn', 'addMusicBtn'].includes(key)) {
                this.config.Utils.log('info', `✅ Elemento encontrado: ${key}`);
            }
        }

        this.config.Utils.log('debug', 'Referencias DOM configuradas');
    }

    setupWebSocket() {
        if (window.musicPlayerWebSocket) {
            this.websocket = window.musicPlayerWebSocket;
            
            // Escuchar actualizaciones de estado
            this.websocket.on('stateUpdate', (data) => {
                this.handleStateUpdate(data);
            });
            
            // Escuchar datos del espectro
            this.websocket.on('spectrumUpdate', (data) => {
                if (window.visualizer) {
                    window.visualizer.updateSpectrum(data.spectrum);
                }
            });
            
            this.config.Utils.log('info', 'WebSocket configurado');
        }
    }

    setupEventListeners() {
        // Controles de reproducción
        if (this.elements.playPauseBtn) {
            this.elements.playPauseBtn.addEventListener('click', () => this.togglePlayPause());
        }
        
        if (this.elements.prevBtn) {
            this.elements.prevBtn.addEventListener('click', () => this.previousTrack());
        }
        
        if (this.elements.nextBtn) {
            this.elements.nextBtn.addEventListener('click', () => this.nextTrack());
        }
        
        if (this.elements.shuffleBtn) {
            this.config.Utils.log('info', 'Configurando evento click para botón Shuffle');
            this.elements.shuffleBtn.addEventListener('click', async () => {
                console.log('🖱️ CLICK SHUFFLE DETECTADO - Llamando toggleShuffle()'); // Log directo
                this.config.Utils.log('info', 'Click en botón Shuffle detectado');
                try {
                    console.log('🔄 ANTES de llamar toggleShuffle()');
                    await this.toggleShuffle();
                    console.log('✅ DESPUÉS de llamar toggleShuffle()');
                } catch (error) {
                    console.error('❌ Error llamando toggleShuffle:', error);
                    this.config.Utils.log('error', 'Error llamando toggleShuffle:', error);
                }
            });
        } else {
            this.config.Utils.log('error', 'Elemento shuffleBtn no encontrado');
        }
        
        if (this.elements.repeatBtn) {
            this.config.Utils.log('info', 'Configurando evento click para botón Repeat');
            this.elements.repeatBtn.addEventListener('click', async () => {
                console.log('🖱️ CLICK REPEAT DETECTADO - Llamando toggleRepeat()'); // Log directo
                this.config.Utils.log('info', 'Click en botón Repeat detectado');
                try {
                    console.log('🔄 ANTES de llamar toggleRepeat()');
                    await this.toggleRepeat();
                    console.log('✅ DESPUÉS de llamar toggleRepeat()');
                } catch (error) {
                    console.error('❌ Error llamando toggleRepeat:', error);
                    this.config.Utils.log('error', 'Error llamando toggleRepeat:', error);
                }
            });
        } else {
            this.config.Utils.log('error', 'Elemento repeatBtn no encontrado');
        }

        // Control de volumen
        if (this.elements.volumeSlider) {
            this.elements.volumeSlider.addEventListener('input', (e) => {
                this.setVolume(parseInt(e.target.value));
            });
        }

        // Barra de progreso
        if (this.elements.progressContainer) {
            this.elements.progressContainer.addEventListener('click', (e) => {
                this.handleProgressClick(e);
            });
        }

        // Búsqueda
        if (this.elements.searchInput) {
            let searchTimeout;
            this.elements.searchInput.addEventListener('input', (e) => {
                clearTimeout(searchTimeout);
                searchTimeout = setTimeout(() => {
                    this.searchSongs(e.target.value);
                }, this.config.UI.SEARCH_DEBOUNCE);
            });
        }
        
        if (this.elements.searchClear) {
            this.elements.searchClear.addEventListener('click', () => {
                this.elements.searchInput.value = '';
                this.searchSongs('');
                this.elements.searchClear.style.display = 'none';
            });
        }

        // Controles de biblioteca
        if (this.elements.refreshLibrary) {
            this.elements.refreshLibrary.addEventListener('click', () => this.loadLibrary());
        }
        
        if (this.elements.sortSelect) {
            this.elements.sortSelect.addEventListener('change', (e) => {
                this.sortSongs(e.target.value);
            });
        }

        // Navegación de canciones en la biblioteca
        if (this.elements.prevSongBtn) {
            this.elements.prevSongBtn.addEventListener('click', () => this.previousTrack());
        }
        
        if (this.elements.nextSongBtn) {
            this.elements.nextSongBtn.addEventListener('click', () => this.nextTrack());
        }
        
        // Botón Reproducir todo
        if (this.elements.playAllBtn) {
            this.elements.playAllBtn.addEventListener('click', () => this.playAllSongs());
        }

        // Cargar música desde carpeta
        if (this.elements.addMusicBtn) {
            this.config.Utils.log('info', 'Configurando evento click para botón Cargar música');
            this.elements.addMusicBtn.addEventListener('click', () => {
                this.config.Utils.log('info', 'Click en botón Cargar música detectado');
                this.showAddMusicDialog();
            });
        } else {
            this.config.Utils.log('error', 'Elemento addMusicBtn no encontrado');
        }

        // Modal
        if (this.elements.modalClose) {
            this.elements.modalClose.addEventListener('click', () => this.hideModal());
        }
        
        if (this.elements.modalOverlay) {
            this.elements.modalOverlay.addEventListener('click', (e) => {
                if (e.target === this.elements.modalOverlay) {
                    this.hideModal();
                }
            });
        }

        // Atajos de teclado
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));

        this.config.Utils.log('debug', 'Event listeners configurados');
    }

    // ============================
    // 📱 DISEÑO RESPONSIVO
    // ============================

    setupResponsiveLayout() {
        try {
            // Configurar breakpoints para diseño responsivo
            const handleResize = () => {
                const width = window.innerWidth;
                const height = window.innerHeight;
                
                // Aplicar clases CSS basadas en el tamaño de pantalla
                document.body.classList.toggle('mobile', width <= 768);
                document.body.classList.toggle('tablet', width > 768 && width <= 1024);
                document.body.classList.toggle('desktop', width > 1024);
                
                // Ajustar visualizador
                if (window.visualizer) {
                    window.visualizer.resize();
                }
            };

            // Configurar listener de resize
            window.addEventListener('resize', handleResize);
            
            // Ejecutar al cargar
            handleResize();
            
            this.config.Utils.log('info', 'Layout responsivo configurado');
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al configurar layout responsivo:', error);
        }
    }

    setupAdvancedSearch() {
        try {
            this.config.Utils.log('info', 'Configurando búsqueda avanzada...');
            
            // Configurar filtros de búsqueda
            const searchInput = document.getElementById('search-input');
            const searchFilters = document.getElementById('search-filters');
            
            if (searchInput) {
                // Búsqueda en tiempo real
                let searchTimeout;
                searchInput.addEventListener('input', (e) => {
                    clearTimeout(searchTimeout);
                    searchTimeout = setTimeout(() => {
                        this.performSearch(e.target.value);
                    }, 300);
                });
            }
            
            if (searchFilters) {
                // Configurar filtros
                searchFilters.addEventListener('change', (e) => {
                    this.applySearchFilters();
                });
            }
            
            this.config.Utils.log('info', 'Búsqueda avanzada configurada');
        } catch (error) {
            this.config.Utils.log('error', 'Error configurando búsqueda avanzada:', error);
        }
    }

    showLibraryLoading() {
        try {
            if (this.elements.songsLoading) {
                this.elements.songsLoading.style.display = 'flex';
            }
            if (this.elements.currentSongContainer) {
                this.elements.currentSongContainer.style.display = 'none';
            }
            if (this.elements.noSongs) {
                this.elements.noSongs.style.display = 'none';
            }
            this.config.Utils.log('info', 'Mostrando indicador de carga de biblioteca');
        } catch (error) {
            this.config.Utils.log('error', 'Error mostrando carga de biblioteca:', error);
        }
    }

    hideLibraryLoading() {
        try {
            if (this.elements.songsLoading) {
                this.elements.songsLoading.style.display = 'none';
            }
            this.config.Utils.log('info', 'Indicador de carga de biblioteca ocultado');
        } catch (error) {
            this.config.Utils.log('error', 'Error ocultando carga de biblioteca:', error);
        }
    }

    showNoSongs() {
        try {
            if (this.elements.songsLoading) {
                this.elements.songsLoading.style.display = 'none';
            }
            if (this.elements.currentSongContainer) {
                this.elements.currentSongContainer.style.display = 'none';
            }
            if (this.elements.noSongs) {
                this.elements.noSongs.style.display = 'flex';
            }
            this.config.Utils.log('info', 'Mostrando mensaje sin canciones');
        } catch (error) {
            this.config.Utils.log('error', 'Error mostrando sin canciones:', error);
        }
    }

    showLibraryError(error) {
        try {
            // Ocultar loading
            if (this.elements.songsLoading) {
                this.elements.songsLoading.style.display = 'none';
            }
            
            // Ocultar current song container
            if (this.elements.currentSongContainer) {
                this.elements.currentSongContainer.style.display = 'none';
            }
            
            // Mostrar mensaje de no canciones como fallback
            if (this.elements.noSongs) {
                this.elements.noSongs.style.display = 'flex';
                
                // Personalizar el mensaje para error
                const noSongsContainer = this.elements.noSongs;
                noSongsContainer.innerHTML = `
                    <i class="fas fa-exclamation-triangle" style="color: #ff6b6b;"></i>
                    <h3>Error cargando biblioteca</h3>
                    <p>${error || 'No se pudo conectar con el servidor'}</p>
                    <button id="retry-library" class="btn btn-primary">
                        <i class="fas fa-sync"></i>
                        Reintentar
                    </button>
                `;
                
                // Agregar event listener al botón de reintentar
                const retryBtn = document.getElementById('retry-library');
                if (retryBtn) {
                    retryBtn.addEventListener('click', () => this.loadLibrary());
                }
            }
            
            this.config.Utils.log('error', 'Error en biblioteca:', error);
        } catch (err) {
            this.config.Utils.log('error', 'Error mostrando error de biblioteca:', err);
        }
    }

    performSearch(query) {
        try {
            if (!query || query.trim() === '') {
                this.showAllTracks();
                return;
            }

            const searchTerm = query.toLowerCase().trim();
            const tracks = document.querySelectorAll('.track-item');
            
            tracks.forEach(track => {
                const title = track.querySelector('.track-title')?.textContent?.toLowerCase() || '';
                const artist = track.querySelector('.track-artist')?.textContent?.toLowerCase() || '';
                const album = track.querySelector('.track-album')?.textContent?.toLowerCase() || '';
                
                const matches = title.includes(searchTerm) || 
                               artist.includes(searchTerm) || 
                               album.includes(searchTerm);
                
                track.style.display = matches ? 'block' : 'none';
            });
            
            this.config.Utils.log('info', `Búsqueda realizada: "${query}"`);
        } catch (error) {
            this.config.Utils.log('error', 'Error en búsqueda:', error);
        }
    }

    applySearchFilters() {
        try {
            const filters = {
                genre: document.getElementById('genre-filter')?.value || '',
                year: document.getElementById('year-filter')?.value || '',
                duration: document.getElementById('duration-filter')?.value || ''
            };

            const tracks = document.querySelectorAll('.track-item');
            
            tracks.forEach(track => {
                let visible = true;
                
                // Aplicar filtros
                if (filters.genre && filters.genre !== 'all') {
                    const trackGenre = track.dataset.genre || '';
                    visible = visible && trackGenre.toLowerCase() === filters.genre.toLowerCase();
                }
                
                if (filters.year && filters.year !== 'all') {
                    const trackYear = track.dataset.year || '';
                    visible = visible && trackYear === filters.year;
                }
                
                track.style.display = visible ? 'block' : 'none';
            });
            
            this.config.Utils.log('info', 'Filtros aplicados');
        } catch (error) {
            this.config.Utils.log('error', 'Error aplicando filtros:', error);
        }
    }

    showAllTracks() {
        try {
            const tracks = document.querySelectorAll('.track-item');
            tracks.forEach(track => {
                track.style.display = 'block';
            });
        } catch (error) {
            this.config.Utils.log('error', 'Error mostrando todas las pistas:', error);
        }
    }

    // ============================
    // 🎵 CONTROL DE REPRODUCCIÓN
    // ============================

    async togglePlayPause() {
        try {
            // Si no hay una canción actual seleccionada, reproducir la primera canción
            if (!this.state.currentTrack && this.songs && this.songs.length > 0) {
                this.config.Utils.log('info', 'No hay canción seleccionada, reproduciendo la primera');
                await this.playTrack(this.songs[0].id);
                return;
            }
            
            const response = await this.api.togglePlayPause();
            
            if (response.status === 'success') {
                // El estado se actualizará vía WebSocket
                this.config.Utils.log('info', `Acción: ${response.action}`);
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al alternar reproducción:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar el estado de reproducción');
        }
    }

    async playTrack(trackId) {
        try {
            const response = await this.api.playTrack(trackId);
            
            if (response.status === 'success') {
                this.config.Utils.log('info', 'Reproduciendo pista:', response.track);
                this.showToast('success', 'Reproduciendo', response.track.title);
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al reproducir pista:', error);
            this.showToast('error', 'Error', 'No se pudo reproducir la pista');
        }
    }

    async playAllSongs() {
        try {
            // Verificar si hay canciones cargadas
            const songs = this.state.playlist;
            if (!songs || songs.length === 0) {
                this.showToast('warning', 'Biblioteca vacía', 'No hay canciones para reproducir');
                return;
            }

            // Reproducir la primera canción de la biblioteca
            const firstSong = songs[0];
            if (firstSong && firstSong.id) {
                await this.playTrack(firstSong.id);
                this.showToast('success', '🎵 Reproduciendo todo', `Iniciando con "${firstSong.title}"`);
                this.config.Utils.log('info', `Reproduciendo toda la biblioteca (${songs.length} canciones)`);
            } else {
                this.showToast('error', 'Error', 'No se pudo reproducir la biblioteca');
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al reproducir toda la biblioteca:', error);
            this.showToast('error', 'Error', 'No se pudo reproducir la biblioteca');
        }
    }

    async previousTrack() {
        try {
            this.config.Utils.log('info', '⏮️ Navegando a pista anterior (usando API backend)...');
            
            // Llamar al endpoint del backend en lugar de lógica local
            const response = await fetch('/api/player/previous', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            this.config.Utils.log('info', '⏮️ Respuesta del backend previous:', result);
            
            if (result.success) {
                this.config.Utils.log('info', '⏮️ Navegación a pista anterior exitosa');
                
                // El backend maneja shuffle/repeat automáticamente
                // Solo necesitamos actualizar el estado local si el backend devuelve info
                if (result.track) {
                    // Actualizar inmediatamente con la información recibida
                    this.state.currentTrack = result.track;
                    this.displayCurrentSong(result.track, result.track_index || 1);
                    this.config.Utils.log('info', `⏮️ Interfaz actualizada con: ${result.track.title || 'Sin título'}`);
                    
                    // Dar tiempo al backend para procesar el cambio y luego hacer actualización completa
                    setTimeout(async () => {
                        await this.updatePlayerState();
                    }, 500);
                } else {
                    this.config.Utils.log('info', '⏮️ No hay pista anterior disponible');
                }
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al ir a pista anterior:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar a la pista anterior');
        }
    }

    async nextTrack() {
        try {
            this.config.Utils.log('info', '⏭️ Navegando a siguiente pista (usando API backend)...');
            
            // Llamar al endpoint del backend en lugar de lógica local
            const response = await fetch('/api/player/next', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const result = await response.json();
            
            this.config.Utils.log('info', '⏭️ Respuesta del backend next:', result);
            
            if (result.success) {
                this.config.Utils.log('info', '⏭️ Navegación a siguiente pista exitosa');
                
                // El backend maneja shuffle/repeat automáticamente
                // Solo necesitamos actualizar el estado local si el backend devuelve info
                if (result.track) {
                    // Actualizar inmediatamente con la información recibida
                    this.state.currentTrack = result.track;
                    this.displayCurrentSong(result.track, result.track_index || 1);
                    this.config.Utils.log('info', `⏭️ Interfaz actualizada con: ${result.track.title || 'Sin título'}`);
                    
                    // Dar tiempo al backend para procesar el cambio y luego hacer actualización completa
                    setTimeout(async () => {
                        await this.updatePlayerState();
                    }, 500);
                } else {
                    this.config.Utils.log('info', '⏭️ No hay siguiente pista disponible');
                }
            } else {
                throw new Error(result.error || 'Error desconocido');
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al ir a siguiente pista:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar a la siguiente pista');
        }
    }

    // Método para reproducir la canción actual mostrada
    async playCurrentSong() {
        if (this.state.playlist && this.state.currentPlaylistIndex >= 0) {
            const currentSong = this.state.playlist[this.state.currentPlaylistIndex];
            if (currentSong) {
                await this.playTrack(currentSong.id);
            }
        }
    }

    // Alternar modo aleatorio
    async toggleShuffle() {
        console.log('INICIANDO toggleShuffle()'); // Log directo a la consola
        
        try {
            console.log('Punto 2 - antes del fetch');
            if (this.config && this.config.Utils) {
                this.config.Utils.log('info', '🔀 Iniciando toggleShuffle()');
            }
            
            console.log('� LÍNEA 3 - Haciendo fetch');
            const response = await fetch('/api/player/shuffle', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('� LÍNEA 4 - Respuesta recibida:', response.status);
            
            const data = await response.json();
            console.log('� LÍNEA 5 - Datos parseados:', data);
            
            if (data.success === true) {
                console.log('🔀 LÍNEA 6 - Éxito, actualizando estado');
                this.state.shuffleEnabled = data.shuffle_enabled;
                console.log('🔀 LÍNEA 7 - Estado actualizado, llamando updateShuffleButton');
                this.updateShuffleButton();
                console.log('🔀 LÍNEA 8 - Mostrando toast');
                this.showToast('success', 'Shuffle', data.message);
            } else {
                console.error('🔀 LÍNEA 9 - Error en respuesta:', data);
                this.showToast('error', 'Error', data.message || 'Error al cambiar modo aleatorio');
            }
        } catch (error) {
            console.error('🔀 LÍNEA 10 - Error en toggleShuffle:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar el modo aleatorio');
        }
        
        console.log('🔀 LÍNEA 11 - FINALIZANDO toggleShuffle()');
    }

    // Cambiar modo de repetición
    async toggleRepeat() {
        console.log('🔁 INICIANDO toggleRepeat() - LÍNEA 1'); // Log directo
        
        try {
            console.log('🔁 LÍNEA 2 - Verificando config.Utils');
            if (this.config && this.config.Utils) {
                this.config.Utils.log('info', '🔁 Alternando modo repeat');
            }
            
            console.log('� LÍNEA 3 - Haciendo fetch');
            const response = await fetch('/api/player/repeat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            console.log('� LÍNEA 4 - Respuesta recibida repeat:', response.status);
            const data = await response.json();
            console.log('� LÍNEA 5 - Datos repeat parseados:', data);
            
            if (data.status === 'success') {
                console.log('🔁 LÍNEA 6 - Éxito repeat, actualizando estado');
                this.state.repeatMode = data.repeat_mode;
                console.log('🔁 LÍNEA 7 - Estado actualizado, llamando updateRepeatButton');
                this.updateRepeatButton();
                console.log('🔁 LÍNEA 8 - Mostrando toast');
                this.showToast('success', 'Repetir', data.message);
            } else {
                console.error('🔁 LÍNEA 9 - Error en respuesta repeat:', data);
                this.showToast('error', 'Error', data.message || 'Error al cambiar modo de repetición');
            }
        } catch (error) {
            console.error('🔁 LÍNEA 10 - Error en toggleRepeat:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar el modo de repetición');
        }
        
        console.log('🔁 LÍNEA 11 - FINALIZANDO toggleRepeat()');
    }

    // Actualizar apariencia del botón shuffle
    updateShuffleButton() {
        console.log('🎨 INICIANDO updateShuffleButton(), estado:', this.state.shuffleEnabled);
        
        try {
            if (this.config && this.config.Utils) {
                this.config.Utils.log('info', '🎨 Actualizando botón shuffle, estado:', this.state.shuffleEnabled);
            }
            
            if (this.elements.shuffleBtn) {
                console.log('🎨 Elemento shuffleBtn encontrado');
                if (this.config && this.config.Utils) {
                    this.config.Utils.log('info', '🎨 Elemento shuffleBtn encontrado');
                }
                
                if (this.state.shuffleEnabled) {
                    console.log('🎨 Activando botón shuffle');
                    this.elements.shuffleBtn.classList.add('active');
                    this.elements.shuffleBtn.style.color = 'var(--accent-primary)';
                    
                    if (this.config && this.config.Utils) {
                        this.config.Utils.log('info', '🎨 Activando botón shuffle');
                    }
                } else {
                    console.log('🎨 Desactivando botón shuffle');
                    this.elements.shuffleBtn.classList.remove('active');
                    this.elements.shuffleBtn.style.color = '';
                    
                    if (this.config && this.config.Utils) {
                        this.config.Utils.log('info', '🎨 Desactivando botón shuffle');
                    }
                }
            } else {
                console.error('❌ Elemento shuffleBtn no encontrado');
                if (this.config && this.config.Utils) {
                    this.config.Utils.log('error', '❌ Elemento shuffleBtn no encontrado');
                }
            }
        } catch (error) {
            console.error('❌ Error en updateShuffleButton:', error);
        }
        
        console.log('🎨 FINALIZANDO updateShuffleButton()');
    }

    // Actualizar apariencia del botón repeat
    updateRepeatButton() {
        if (this.elements.repeatBtn) {
            this.elements.repeatBtn.classList.remove('active', 'repeat-one', 'repeat-all');
            
            const icon = this.elements.repeatBtn.querySelector('i');
            if (icon) {
                switch (this.state.repeatMode) {
                    case 'one':
                        this.elements.repeatBtn.classList.add('active', 'repeat-one');
                        this.elements.repeatBtn.style.color = 'var(--accent-primary)';
                        icon.className = 'fas fa-redo';
                        break;
                    case 'all':
                        this.elements.repeatBtn.classList.add('active', 'repeat-all');
                        this.elements.repeatBtn.style.color = 'var(--accent-secondary)';
                        icon.className = 'fas fa-redo';
                        break;
                    default:
                        this.elements.repeatBtn.style.color = '';
                        icon.className = 'fas fa-redo';
                        break;
                }
            }
        }
    }

    // Actualizar estado de botones de navegación
    updateNavigationButtons() {
        if (this.elements.prevSongBtn && this.elements.nextSongBtn) {
            const hasPrevious = this.state.playlist && this.state.playlist.length > 1;
            const hasNext = this.state.playlist && this.state.playlist.length > 1;
            
            this.elements.prevSongBtn.disabled = !hasPrevious;
            this.elements.nextSongBtn.disabled = !hasNext;
        }
    }

    // Formatear duración en mm:ss
    formatDuration(seconds) {
        if (!seconds || isNaN(seconds)) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    async setVolume(volume) {
        try {
            await this.api.setVolume(volume);
            this.state.volume = volume;
            
            // Actualizar UI inmediatamente
            this.updateVolumeDisplay(volume);
            
            // Guardar en localStorage
            this.config.Utils.setStoredSetting('VOLUME', volume);
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al establecer volumen:', error);
        }
    }

    async seekTo(position) {
        try {
            await this.api.seek(position);
        } catch (error) {
            this.config.Utils.log('error', 'Error al navegar:', error);
        }
    }

    // ============================
    // 📚 BIBLIOTECA MUSICAL
    // ============================

    async loadLibrary() {
        try {
            this.showLibraryLoading();
            
            this.config.Utils.log('info', 'Iniciando carga de biblioteca...');
            
            const response = await this.api.getSongs();
            
            this.config.Utils.log('info', 'Respuesta de API recibida:', response);
            
            if (response && response.success && response.songs) {
                this.state.playlist = response.songs;
                this.initializeCurrentSongDisplay(response.songs);
                this.updateLibraryStats(response.songs);
                
                this.config.Utils.log('info', `✅ Biblioteca cargada: ${response.songs.length} canciones`);
            } else {
                this.config.Utils.log('error', 'Respuesta inválida de API:', response);
                throw new Error('No se recibieron canciones válidas del servidor');
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al cargar biblioteca:', error);
            this.showLibraryError(error.message || error);
        }
    }

    initializeCurrentSongDisplay(songs) {
        // Forzar la ocultación del loading
        this.hideLibraryLoading();
        
        if (!songs || songs.length === 0) {
            this.showNoSongs();
            return;
        }

        // Mostrar contenedor de canción actual
        if (this.elements.currentSongContainer) {
            this.elements.currentSongContainer.style.display = 'flex';
        }

        // Actualizar contador total
        if (this.elements.totalSongsCount) {
            this.elements.totalSongsCount.textContent = songs.length;
        }

        // Si no hay canción actual, mostrar la primera
        if (!this.state.currentTrack && songs.length > 0) {
            this.state.currentPlaylistIndex = 0;
            this.displayCurrentSong(songs[0], 1);
        } else if (this.state.currentTrack) {
            // Buscar la canción actual en la lista
            const currentIndex = songs.findIndex(song => song.id === this.state.currentTrack.id);
            if (currentIndex !== -1) {
                this.state.currentPlaylistIndex = currentIndex;
                this.displayCurrentSong(songs[currentIndex], currentIndex + 1);
            } else {
                // Canción actual no encontrada, mostrar la primera
                this.state.currentPlaylistIndex = 0;
                this.displayCurrentSong(songs[0], 1);
            }
        }
    }

    displayCurrentSong(song, position) {
        if (!song || !this.elements.currentSongItem) return;

        this.elements.currentSongItem.innerHTML = `
            <div class="current-song-content">
                <div class="current-song-artwork">
                    <div class="artwork-display">
                        <i class="fas fa-music"></i>
                    </div>
                </div>
                <div class="current-song-details">
                    <h3 class="current-song-title">${song.title || 'Sin título'}</h3>
                    <p class="current-song-artist">${song.artist || 'Artista desconocido'}</p>
                    <p class="current-song-album">${song.album || 'Álbum desconocido'}</p>
                    <div class="current-song-meta">
                        <span class="song-duration">
                            <i class="fas fa-clock"></i>
                            ${this.formatDuration(song.duration || 0)}
                        </span>
                        <span class="song-bitrate">
                            <i class="fas fa-signal"></i>
                            ${song.bitrate || 'Unknown'} kbps
                        </span>
                    </div>
                </div>
                <div class="current-song-actions">
                    <button class="action-btn play-current-btn" onclick="window.musicPlayerApp.playCurrentSong()">
                        <i class="fas fa-play"></i>
                        <span>Reproducir</span>
                    </button>
                </div>
            </div>
        `;

        // Actualizar número de canción actual
        if (this.elements.currentSongNumber) {
            this.elements.currentSongNumber.textContent = position;
        }

        // Actualizar estado de botones de navegación
        this.updateNavigationButtons();
    }

    renderSongsList(songs) {
        try {
            // Debug: Listar todos los elementos disponibles
            const allElements = document.querySelectorAll('[id]');
            this.config.Utils.log('info', `Elementos disponibles: ${Array.from(allElements).map(el => el.id).join(', ')}`);
            
            const libraryContainer = document.getElementById('library-container');
            this.config.Utils.log('info', `Buscando library-container: ${libraryContainer ? 'ENCONTRADO' : 'NO ENCONTRADO'}`);
            
            if (!libraryContainer) {
                // Intentar con selector alternativo
                const songsContainer = document.querySelector('.songs-container');
                const songsListContainer = document.getElementById('songs-list');
                
                this.config.Utils.log('info', `Contenedor alternativo songs-container: ${songsContainer ? 'ENCONTRADO' : 'NO ENCONTRADO'}`);
                this.config.Utils.log('info', `Contenedor alternativo songs-list: ${songsListContainer ? 'ENCONTRADO' : 'NO ENCONTRADO'}`);
                
                if (songsListContainer) {
                    // Usar songs-list como alternativa
                    this.renderInContainer(songsListContainer, songs);
                    return;
                } else if (songsContainer) {
                    // Crear el elemento library-container dinámicamente
                    const newLibraryContainer = document.createElement('div');
                    newLibraryContainer.id = 'library-container';
                    newLibraryContainer.className = 'library-container';
                    songsContainer.appendChild(newLibraryContainer);
                    this.renderInContainer(newLibraryContainer, songs);
                    return;
                }
                
                this.config.Utils.log('error', 'No se pudo encontrar ningún contenedor de biblioteca');
                return;
            }

            this.renderInContainer(libraryContainer, songs);
        } catch (error) {
            this.config.Utils.log('error', 'Error renderizando lista de canciones:', error);
        }
    }

    renderInContainer(container, songs) {
        try {
            if (!songs || songs.length === 0) {
                container.innerHTML = `
                    <div class="empty-library">
                        <div class="empty-icon">🎵</div>
                        <h3>No hay canciones disponibles</h3>
                        <p>Agrega música a tu biblioteca para comenzar</p>
                    </div>
                `;
                return;
            }

            const songsHTML = songs.map((song, index) => `
                <div class="track-item" data-track-id="${song.id || index}" 
                     data-genre="${song.genre || ''}" data-year="${song.year || ''}">
                    <div class="track-cover">
                        <img src="${song.cover || '/static/images/default-cover.png'}" 
                             alt="${song.title}" onerror="this.src='/static/images/default-cover.png'">
                        <div class="play-overlay" onclick="window.musicPlayerApp.playTrack(${song.id || index})">
                            <i class="fas fa-play"></i>
                        </div>
                    </div>
                    <div class="track-info">
                        <div class="track-title">${song.title || 'Título desconocido'}</div>
                        <div class="track-artist">${song.artist || 'Artista desconocido'}</div>
                        <div class="track-album">${song.album || 'Álbum desconocido'}</div>
                        <div class="track-duration">${this.formatDuration(song.duration || 0)}</div>
                    </div>
                    <div class="track-actions">
                        <button onclick="window.musicPlayerApp.addToQueue(${song.id || index})" 
                                class="action-btn" title="Agregar a cola">
                            <i class="fas fa-plus"></i>
                        </button>
                        <button onclick="window.musicPlayerApp.addToFavorites(${song.id || index})" 
                                class="action-btn" title="Agregar a favoritos">
                            <i class="fas fa-heart"></i>
                        </button>
                    </div>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="library-header">
                    <h2>Mi Biblioteca (${songs.length} canciones)</h2>
                    <div class="library-controls">
                        <button onclick="window.musicPlayerApp.shuffleAll()" class="control-btn">
                            <i class="fas fa-random"></i> Reproducir todo
                        </button>
                    </div>
                </div>
                <div class="tracks-list">
                    ${songsHTML}
                </div>
            `;

            // Hacer visible el contenedor
            container.style.display = 'block';

            this.config.Utils.log('info', `Lista de canciones renderizada: ${songs.length} elementos en ${container.id || container.className}`);
        } catch (error) {
            this.config.Utils.log('error', 'Error renderizando en contenedor:', error);
        }
    }

    updateLibraryStats(songs) {
        try {
            const statsContainer = document.getElementById('library-stats');
            if (statsContainer && songs) {
                const totalDuration = songs.reduce((total, song) => total + (song.duration || 0), 0);
                const artists = new Set(songs.map(song => song.artist)).size;
                const albums = new Set(songs.map(song => song.album)).size;

                statsContainer.innerHTML = `
                    <div class="stat-item">
                        <span class="stat-number">${songs.length}</span>
                        <span class="stat-label">Canciones</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${artists}</span>
                        <span class="stat-label">Artistas</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${albums}</span>
                        <span class="stat-label">Álbumes</span>
                    </div>
                    <div class="stat-item">
                        <span class="stat-number">${this.formatDuration(totalDuration)}</span>
                        <span class="stat-label">Duración</span>
                    </div>
                `;
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error actualizando estadísticas:', error);
        }
    }

    formatDuration(seconds) {
        if (!seconds || seconds === 0) return '0:00';
        
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    }

    setupVisualizer() {
        try {
            this.config.Utils.log('info', 'Configurando visualizador...');
            
            // El visualizador ya está configurado en el módulo visualizer.js
            // Solo necesitamos verificar que esté disponible
            if (window.musicVisualizer) {
                window.musicVisualizer.initVisualizer();
                this.config.Utils.log('info', 'Visualizador configurado correctamente');
            } else {
                this.config.Utils.log('warning', 'Módulo de visualizador no disponible');
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error configurando visualizador:', error);
        }
    }

    async playTrack(trackId) {
        try {
            this.config.Utils.log('info', `Reproduciendo pista: ${trackId}`);
            const response = await this.api.playTrack(trackId);
            
            if (response.status === 'success') {
                this.config.Utils.log('info', 'Pista iniciada correctamente');
            } else {
                throw new Error('Error al reproducir pista');
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error reproduciendo pista:', error);
        }
    }

    async addToQueue(trackId) {
        try {
            this.config.Utils.log('info', `Agregando a cola: ${trackId}`);
            const response = await this.api.addToQueue(trackId);
            
            if (response.status === 'success') {
                this.config.Utils.log('info', 'Pista agregada a la cola');
                this.showNotification('Agregado a la cola', 'success');
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error agregando a cola:', error);
            this.showNotification('Error agregando a cola', 'error');
        }
    }

    async addToFavorites(trackId) {
        try {
            this.config.Utils.log('info', `Agregando a favoritos: ${trackId}`);
            const response = await this.api.addToFavorites(trackId);
            
            if (response.status === 'success') {
                this.config.Utils.log('info', 'Pista agregada a favoritos');
                this.showNotification('Agregado a favoritos', 'success');
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error agregando a favoritos:', error);
            this.showNotification('Error agregando a favoritos', 'error');
        }
    }

    async shuffleAll() {
        try {
            this.config.Utils.log('info', 'Reproduciendo toda la biblioteca en modo aleatorio');
            const response = await this.api.shufflePlay();
            
            if (response.status === 'success') {
                this.config.Utils.log('info', 'Reproducción aleatoria iniciada');
                this.showNotification('Reproducción aleatoria activada', 'success');
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error en reproducción aleatoria:', error);
            this.showNotification('Error en reproducción aleatoria', 'error');
        }
    }

    showNotification(message, type = 'info') {
        try {
            // Crear elemento de notificación si no existe
            let notificationContainer = document.getElementById('notification-container');
            if (!notificationContainer) {
                notificationContainer = document.createElement('div');
                notificationContainer.id = 'notification-container';
                notificationContainer.className = 'notification-container';
                document.body.appendChild(notificationContainer);
            }

            const notification = document.createElement('div');
            notification.className = `notification notification-${type}`;
            notification.innerHTML = `
                <span>${message}</span>
                <button onclick="this.parentElement.remove()" class="notification-close">×</button>
            `;

            notificationContainer.appendChild(notification);

            // Auto-eliminar después de 3 segundos
            setTimeout(() => {
                if (notification.parentElement) {
                    notification.remove();
                }
            }, 3000);

        } catch (error) {
            this.config.Utils.log('error', 'Error mostrando notificación:', error);
        }
    }

    async updatePlayerState() {
        try {
            this.config.Utils.log('info', '🔄 Actualizando estado del reproductor...');
            
            // Consultar el estado actual del backend
            const response = await fetch('/api/player/state');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const state = await response.json();
            
            if (state.success && state.current_track) {
                this.config.Utils.log('info', '🎵 Actualizando información de la canción actual');
                
                // Buscar la canción en la playlist local para obtener toda la información
                let currentSong = null;
                if (this.state.playlist && Array.isArray(this.state.playlist)) {
                    currentSong = this.state.playlist.find(song => song.id === state.current_track.id);
                }
                
                // Si no se encuentra en la playlist local, usar la información del backend
                if (!currentSong) {
                    currentSong = state.current_track;
                }
                
                // Actualizar índice actual en el estado local
                if (state.current_track_index !== undefined) {
                    this.state.currentPlaylistIndex = state.current_track_index - 1; // API devuelve 1-indexed, convertir a 0-indexed
                }
                
                // Actualizar la interfaz con la nueva canción
                this.displayCurrentSong(currentSong, state.current_track_index || 1);
                
                this.config.Utils.log('info', `🎵 Interfaz actualizada con: ${currentSong.title || 'Sin título'}`);
            } else {
                this.config.Utils.log('info', '⏹️ No hay canción reproduciéndose actualmente');
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error actualizando estado del reproductor:', error);
        }
    }

    async searchSongs(query) {
        try {
            const response = await this.api.searchSongs(query);
            
            if (response.status === 'success') {
                this.renderSongsList(response.songs);
                
                // Mostrar/ocultar botón de limpiar búsqueda
                if (this.elements.searchClear) {
                    this.elements.searchClear.style.display = query ? 'flex' : 'none';
                }
            }
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al buscar canciones:', error);
        }
    }

    // ============================
    // 🎨 ACTUALIZACIÓN DE UI
    // ============================

    handleStateUpdate(data) {
        if (!data) return;
        
        // Log para debugging
        this.config.Utils.log('info', '🔄 WebSocket recibió actualización de estado:', data);
        
        // Actualizar estado interno
        this.state.isPlaying = data.state === 'playing';
        this.state.isPaused = data.state === 'paused';
        this.state.volume = data.volume || this.state.volume;
        this.state.position = data.position || 0;
        this.state.duration = data.duration || 0;
        this.state.currentTrack = data.current_track || this.state.currentTrack;
        
        // Actualizar shuffle y repeat si están presentes
        if (data.shuffle_enabled !== undefined) {
            this.state.shuffleEnabled = data.shuffle_enabled;
            this.updateShuffleButton();
        }
        if (data.shuffle !== undefined) {
            this.state.shuffleEnabled = data.shuffle;
            this.updateShuffleButton();
        }
        if (data.repeat_mode !== undefined) {
            this.state.repeatMode = data.repeat_mode;
            this.updateRepeatButton();
        }
        if (data.repeat !== undefined) {
            this.state.repeatMode = data.repeat;
            this.updateRepeatButton();
        }
        
        // Actualizar UI
        this.updatePlayPauseButton();
        this.updateVolumeDisplay(this.state.volume);
        this.updateProgressBar();
        this.updateTrackInfo();
        
        // Actualizar el contenedor de "reproduciendo ahora" si cambió la canción
        if (data.current_track && this.state.currentTrack) {
            this.config.Utils.log('info', '🎵 Actualizando contenedor de reproduciendo ahora desde WebSocket');
            
            // Buscar información completa de la canción en la playlist local
            let fullTrackInfo = this.state.currentTrack;
            if (this.state.playlist && Array.isArray(this.state.playlist)) {
                const foundTrack = this.state.playlist.find(song => song.id === this.state.currentTrack.id);
                if (foundTrack) {
                    fullTrackInfo = foundTrack;
                }
            }
            
            // Actualizar índice si está disponible
            const trackIndex = data.current_track_index || (this.state.currentPlaylistIndex + 1);
            
            // Actualizar contenedor completo
            this.displayCurrentSong(fullTrackInfo, trackIndex);
        }
        
        this.config.Utils.log('debug', 'Estado actualizado:', data);
    }

    updatePlayPauseButton() {
        if (!this.elements.playPauseBtn) return;
        
        const icon = this.elements.playPauseBtn.querySelector('i');
        if (icon) {
            if (this.state.isPlaying) {
                icon.className = 'fas fa-pause';
                this.elements.playPauseBtn.title = 'Pausar';
                this.elements.playPauseBtn.classList.add('paused');
            } else {
                icon.className = 'fas fa-play';
                this.elements.playPauseBtn.title = 'Reproducir';
                this.elements.playPauseBtn.classList.remove('paused');
            }
        }
    }

    updateVolumeDisplay(volume) {
        if (this.elements.volumeSlider) {
            this.elements.volumeSlider.value = volume;
        }
        
        if (this.elements.volumeDisplay) {
            this.elements.volumeDisplay.textContent = `${volume}%`;
        }
        
        if (this.elements.volumeIcon) {
            const icon = this.elements.volumeIcon;
            if (volume === 0) {
                icon.className = 'fas fa-volume-mute';
            } else if (volume < 30) {
                icon.className = 'fas fa-volume-down';
            } else {
                icon.className = 'fas fa-volume-up';
            }
        }
    }

    updateProgressBar() {
        if (!this.elements.progressFill || !this.elements.progressHandle) return;
        
        const percentage = this.state.duration > 0 ? (this.state.position / this.state.duration) * 100 : 0;
        
        this.elements.progressFill.style.width = `${percentage}%`;
        this.elements.progressHandle.style.left = `${percentage}%`;
        
        if (this.elements.currentTime) {
            this.elements.currentTime.textContent = this.config.Utils.formatTime(this.state.position);
        }
        
        if (this.elements.totalTime) {
            this.elements.totalTime.textContent = this.config.Utils.formatTime(this.state.duration);
        }
    }

    updateTrackInfo() {
        const track = this.state.currentTrack;
        
        if (this.elements.currentTitle) {
            this.elements.currentTitle.textContent = track?.title || 'Selecciona una canción';
        }
        
        if (this.elements.currentArtist) {
            this.elements.currentArtist.textContent = track?.artist || 'Music Player Pro';
        }
        
        if (this.elements.currentAlbum) {
            this.elements.currentAlbum.textContent = track?.album || 'Listo para reproducir';
        }
    }

    updateCurrentSongDisplay() {
        const track = this.state.currentTrack;
        const currentSongContainer = document.getElementById('current-song-container');
        
        if (!track || !currentSongContainer) return;
        
        // Mostrar contenedor de canción actual
        currentSongContainer.style.display = 'block';
        
        // Actualizar contador de canción
        const currentSongNumber = document.getElementById('current-song-number');
        if (currentSongNumber && this.state.currentPlaylistIndex >= 0) {
            currentSongNumber.textContent = this.state.currentPlaylistIndex + 1;
        }
        
        // Actualizar total de canciones
        const totalSongsCount = document.getElementById('total-songs-count');
        if (totalSongsCount) {
            totalSongsCount.textContent = this.state.playlist.length || 0;
        }
        
        // Actualizar información del item actual
        const currentSongItem = document.getElementById('current-song-item');
        if (currentSongItem) {
            currentSongItem.innerHTML = `
                <div class="song-item playing">
                    <div class="song-info">
                        <div class="song-title">${track.title || 'Título desconocido'}</div>
                        <div class="song-meta">${track.artist || 'Artista desconocido'} • ${track.album || 'Álbum desconocido'}</div>
                    </div>
                    <div class="song-duration">${this.config.Utils.formatTime(track.duration || 0)}</div>
                </div>
            `;
        }
    }

    highlightCurrentTrack() {
        // Remover resaltado anterior
        const previousHighlighted = document.querySelectorAll('.song-item.playing');
        previousHighlighted.forEach(item => {
            item.classList.remove('playing');
        });
        
        // Resaltar canción actual en la biblioteca
        if (this.state.currentTrack && this.state.currentTrack.id) {
            const currentTrackElement = document.querySelector(`[data-track-id="${this.state.currentTrack.id}"]`);
            if (currentTrackElement) {
                currentTrackElement.classList.add('playing');
                
                // Hacer scroll para mostrar la canción actual
                currentTrackElement.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'center' 
                });
            }
        }
    }

    // ============================
    // 🔧 MÉTODOS AUXILIARES
    // ============================

    showLoadingScreen() {
        if (this.elements.loadingScreen) {
            this.elements.loadingScreen.style.display = 'flex';
        }
        if (this.elements.mainApp) {
            this.elements.mainApp.style.display = 'none';
        }
    }

    hideLoadingScreen() {
        console.log('🔄 EJECUTANDO hideLoadingScreen()');
        if (this.elements.loadingScreen) {
            this.elements.loadingScreen.style.display = 'none';
            console.log('✅ Loading screen ocultado');
        }
        if (this.elements.mainApp) {
            this.elements.mainApp.style.display = 'flex';
            this.elements.mainApp.style.visibility = 'visible';
            console.log('✅ Main app mostrado con display: flex');
        }
    }

    showToast(type, title, message, duration = 5000) {
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
            </div>
            <button class="toast-close">
                <i class="fas fa-times"></i>
            </button>
            <div class="toast-progress ${type}"></div>
        `;
        
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            toast.remove();
        });
        
        this.elements.toastContainer.appendChild(toast);
        
        // Auto remover después del tiempo especificado
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, duration);
    }

    async loadInitialState() {
        try {
            const response = await this.api.getPlayerState();
            
            if (response.success && response) {
                // Manejar el estado del reproductor
                this.state.isPlaying = response.state === 'playing';
                this.state.isPaused = response.state === 'paused';
                this.state.volume = response.volume || this.state.volume;
                this.state.position = response.position || 0;
                this.state.duration = response.duration || 0;
                
                // ¡IMPORTANTE! Manejar información del track actual
                if (response.current_track && response.has_current_track) {
                    this.state.currentTrack = response.current_track;
                    this.state.currentPlaylistIndex = (response.current_track_index || 1) - 1; // Convertir a índice base 0
                    
                    this.config.Utils.log('info', `Track actual restaurado: ${response.current_track.title} por ${response.current_track.artist}`);
                    
                    // Actualizar UI con información del track
                    this.updateTrackInfo();
                    this.updateCurrentSongDisplay();
                    
                    // Si hay biblioteca cargada, resaltar la canción actual
                    setTimeout(() => {
                        this.highlightCurrentTrack();
                    }, 1000);
                } else {
                    this.config.Utils.log('info', 'No hay track actualmente en reproducción');
                }
                
                // Actualizar controles UI
                this.updatePlayPauseButton();
                this.updateVolumeDisplay(this.state.volume);
                this.updateProgressBar();
                
                // ¡IMPORTANTE! Sincronizar shuffle y repeat desde el backend
                if (response.shuffle !== undefined) {
                    this.state.shuffleEnabled = response.shuffle;
                    this.updateShuffleButton();
                    this.config.Utils.log('info', `Shuffle sincronizado: ${response.shuffle}`);
                }
                
                if (response.repeat !== undefined) {
                    this.state.repeatMode = response.repeat;
                    this.updateRepeatButton();
                    this.config.Utils.log('info', `Repeat sincronizado: ${response.repeat}`);
                }
                
                this.config.Utils.log('info', 'Estado inicial cargado:', response);
            }
            
        } catch (error) {
            this.config.Utils.log('warn', 'No se pudo cargar estado inicial:', error);
        }
    }

    handleProgressClick(e) {
        if (!this.elements.progressBar || this.state.duration === 0) return;
        
        const rect = this.elements.progressBar.getBoundingClientRect();
        const percentage = (e.clientX - rect.left) / rect.width;
        const newPosition = percentage * this.state.duration;
        
        this.seekTo(newPosition);
    }

    handleKeyDown(e) {
        // Atajos de teclado
        switch (e.code) {
            case 'Space':
                if (e.target.tagName !== 'INPUT') {
                    e.preventDefault();
                    this.togglePlayPause();
                }
                break;
            case 'ArrowLeft':
                if (e.ctrlKey) {
                    this.previousTrack();
                }
                break;
            case 'ArrowRight':
                if (e.ctrlKey) {
                    this.nextTrack();
                }
                break;
            case 'ArrowUp':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.api.adjustVolume(this.config.PLAYER.VOLUME_STEP);
                }
                break;
            case 'ArrowDown':
                if (e.ctrlKey) {
                    e.preventDefault();
                    this.api.adjustVolume(-this.config.PLAYER.VOLUME_STEP);
                }
                break;
        }
    }

    showError(title, message) {
        this.showToast('error', title, message);
        this.config.Utils.log('error', `${title}: ${message}`);
    }

    // ============================
    // 🔧 CARGA DE EXTENSIONES
    // ============================

    loadExtensions() {
        try {
            // Cargar extensiones de controles del reproductor
            if (window.PlayerControlsExtensions) {
                Object.assign(this, window.PlayerControlsExtensions);
                this.config.Utils.log('info', 'Extensiones de controles del reproductor cargadas');
            }
            
            // Cargar extensiones de biblioteca
            if (window.LibraryExtensions) {
                Object.assign(this, window.LibraryExtensions);
                this.config.Utils.log('info', 'Extensiones de biblioteca cargadas');
            }
            
            // Cargar extensiones de UI
            if (window.UIExtensions) {
                Object.assign(this, window.UIExtensions);
                this.config.Utils.log('info', 'Extensiones de UI cargadas');
            }
            
            // Inicializar extensiones si tienen métodos de init
            if (this.initPlayerControlsExtension) {
                this.initPlayerControlsExtension();
            }
            
            this.config.Utils.log('info', 'Todas las extensiones cargadas correctamente');
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al cargar extensiones:', error);
        }
    }

    // ============================
    // 📁 GESTIÓN DE ARCHIVOS
    // ============================

    showAddMusicDialog() {
        this.config.Utils.log('info', '📁 Abriendo diálogo de selección de carpeta');
        
        // Si estamos en Electron, usar el API nativo para seleccionar carpetas
        if (window.electronAPI && window.electronAPI.selectFolder) {
            this.config.Utils.log('info', '🖥️ Usando Electron API para selección de carpeta');
            window.electronAPI.selectFolder().then(folderPath => {
                if (folderPath) {
                    this.config.Utils.log('info', `📁 Carpeta seleccionada: ${folderPath}`);
                    this.addMusicFolder(folderPath, []);
                }
            });
            return;
        }
        
        // Fallback: Pedir al usuario que ingrese la ruta manualmente
        const folderPath = prompt('Por favor, ingresa la ruta completa de la carpeta con música:\n(Ejemplo: C:\\Users\\TuUsuario\\Music\\rock)');
        
        if (folderPath && folderPath.trim()) {
            this.config.Utils.log('info', `📁 Ruta ingresada manualmente: ${folderPath.trim()}`);
            this.addMusicFolder(folderPath.trim(), []);
        } else {
            this.config.Utils.log('info', '❌ Operación cancelada por el usuario');
        }
    }
    
    async addMusicFolder(folderPath, files) {
        try {
            this.config.Utils.log('info', `🔄 Iniciando procesamiento de carpeta: ${folderPath}`);
            
            // Mostrar indicador de carga
            const addButton = document.getElementById('add-music-btn');
            const originalText = addButton.innerHTML;
            addButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Cargando...';
            addButton.disabled = true;
            
            if (!folderPath || !folderPath.trim()) {
                this.config.Utils.log('error', '❌ No se proporcionó ruta de carpeta');
                this.showNotification('Error: No se proporcionó ruta de carpeta', 'error');
                return;
            }
            
            this.config.Utils.log('info', `📂 Enviando carpeta al servidor: ${folderPath}`);
            
            // Enviar petición al servidor
            const response = await fetch('/api/library/add-folder', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    folderPath: folderPath.trim()
                })
            });
            
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
            const result = await response.json();
            this.config.Utils.log('info', `📥 Respuesta del servidor:`, result);
            
            if (result.success) {
                const message = result.message || `Se agregaron ${result.added || 0} nuevas canciones`;
                this.showNotification(message, 'success');
                this.config.Utils.log('info', `✅ ${message}`);
                
                // Recargar biblioteca después de un breve delay
                this.config.Utils.log('info', '🔄 Recargando biblioteca...');
                setTimeout(() => {
                    this.loadLibrary();
                }, 1000);
            } else {
                const errorMsg = result.message || result.error || 'Error desconocido';
                this.showNotification(`Error: ${errorMsg}`, 'error');
                this.config.Utils.log('error', `❌ Error del servidor: ${errorMsg}`);
            }
            
        } catch (error) {
            this.config.Utils.log('error', '❌ Error al agregar música:', error);
            this.showNotification('Error al conectar con el servidor', 'error');
        } finally {
            // Restaurar botón
            const addButton = document.getElementById('add-music-btn');
            addButton.innerHTML = '<i class="fas fa-folder-plus"></i> Cargar música';
            addButton.disabled = false;
        }
    }
    
    showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 
                           type === 'warning' ? 'fa-exclamation-triangle' : 
                           type === 'error' ? 'fa-times-circle' : 'fa-info-circle'}"></i>
            ${message}
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => notification.classList.add('show'), 100);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
}

// ============================
// 🌐 INICIALIZACIÓN GLOBAL
// ============================

let musicPlayerApp = null;

document.addEventListener('DOMContentLoaded', async function() {
    try {
        // Esperar un poco para asegurar que todos los recursos estén cargados
        await new Promise(resolve => setTimeout(resolve, 100));
        
        musicPlayerApp = new MusicPlayerApp();
        window.musicPlayerApp = musicPlayerApp;
        
        await musicPlayerApp.init();
        
    } catch (error) {
        console.error('Error al inicializar Music Player Pro:', error);
        
        // Mostrar error en la UI si es posible
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.innerHTML = `
                <div class="loading-content">
                    <div style="font-size: 3rem; margin-bottom: 1rem; color: #ff6b6b;">⚠️</div>
                    <h2 style="color: #ff6b6b;">Error de Inicialización</h2>
                    <p style="color: #b3b3b3; max-width: 400px; text-align: center; line-height: 1.6;">
                        ${error.message || 'No se pudo inicializar la aplicación'}
                    </p>
                    <button onclick="location.reload()" style="
                        margin-top: 1rem; 
                        padding: 0.5rem 1rem; 
                        background: #ff6b6b; 
                        color: white; 
                        border: none; 
                        border-radius: 0.5rem; 
                        cursor: pointer;
                        font-size: 0.9rem;
                    ">
                        Recargar Página
                    </button>
                </div>
            `;
        }
    }
});

// Exportar para módulos que lo necesiten
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MusicPlayerApp;
}
