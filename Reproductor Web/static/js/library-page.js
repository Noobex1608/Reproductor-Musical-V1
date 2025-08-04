// 🎵 MUSIC PLAYER PRO - LIBRARY PAGE
// ==================================
// JavaScript para la página completa de biblioteca musical

class LibraryPage {
    constructor() {
        this.songs = [];
        this.filteredSongs = [];
        this.currentSort = 'title';
        this.sortOrder = 'asc';
        this.currentFilter = 'all';
        this.searchQuery = '';
        this.currentView = 'list';
        
        this.elements = {
            loading: document.getElementById('library-loading'),
            empty: document.getElementById('library-empty'),
            songs: document.getElementById('library-songs'),
            songsList: document.getElementById('songs-list'),
            search: document.getElementById('library-search'),
            clearSearch: document.getElementById('clear-search-btn'),
            sortSelect: document.getElementById('sort-select'),
            sortOrderBtn: document.getElementById('sort-order-btn'),
            shuffleAllBtn: document.getElementById('shuffle-all-btn'),
            totalSongs: document.getElementById('total-songs'),
            totalDuration: document.getElementById('total-duration'),
            totalSize: document.getElementById('total-size'),
            contextMenu: document.getElementById('context-menu'),
            miniPlayer: document.getElementById('mini-player')
        };
        
        this.contextMenuTarget = null;
        this.isConnected = false;
        
        this.init();
    }
    
    async init() {
        console.log('🎵 Inicializando página de biblioteca...');
        
        this.setupEventListeners();
        this.setupWebSocket();
        await this.loadLibrary();
        await this.loadPlayerState(); // ¡NUEVO! Cargar estado del reproductor
        this.updateMiniPlayer();
    }
    
    setupEventListeners() {
        // Search functionality
        this.elements.search.addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.updateClearSearchButton();
            this.filterAndRenderSongs();
        });
        
        this.elements.clearSearch.addEventListener('click', () => {
            this.elements.search.value = '';
            this.searchQuery = '';
            this.updateClearSearchButton();
            this.filterAndRenderSongs();
        });
        
        // Sort controls
        this.elements.sortSelect.addEventListener('change', (e) => {
            this.currentSort = e.target.value;
            this.filterAndRenderSongs();
        });
        
        this.elements.sortOrderBtn.addEventListener('click', () => {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
            this.updateSortOrderButton();
            this.filterAndRenderSongs();
        });
        
        // Filter buttons
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const filter = e.currentTarget.dataset.filter;
                this.setActiveFilter(filter);
                this.currentFilter = filter;
                this.filterAndRenderSongs();
            });
        });
        
        // View mode buttons
        document.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                this.setActiveViewMode(view);
                this.currentView = view;
                this.renderSongs();
            });
        });
        
        // Shuffle all button
        this.elements.shuffleAllBtn.addEventListener('click', () => {
            this.shuffleAndPlayAll();
        });
        
        // Context menu
        document.addEventListener('click', () => {
            this.hideContextMenu();
        });
        
        document.addEventListener('contextmenu', (e) => {
            const songItem = e.target.closest('.library-song-item');
            if (songItem) {
                e.preventDefault();
                this.showContextMenu(e, songItem);
            }
        });
        
        // Context menu actions
        document.querySelectorAll('.context-menu-item').forEach(item => {
            item.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleContextMenuAction(action);
            });
        });
    }
    
    setupWebSocket() {
        if (typeof io !== 'undefined') {
            this.socket = io();
            
            this.socket.on('connect', () => {
                this.isConnected = true;
                console.log('✅ WebSocket conectado');
            });
            
            this.socket.on('disconnect', () => {
                this.isConnected = false;
                console.log('❌ WebSocket desconectado');
            });
            
            this.socket.on('player_state_changed', (data) => {
                this.updateMiniPlayer(data);
                this.updateCurrentTrackHighlight(data);
            });
        }
    }
    
    async loadLibrary() {
        try {
            this.showLoading();
            
            console.log('📡 Cargando biblioteca musical...');
            const response = await fetch('/api/library/songs');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && Array.isArray(data.songs)) {
                this.songs = data.songs;
                this.filteredSongs = [...this.songs];
                
                console.log(`✅ ${this.songs.length} canciones cargadas`);
                
                this.updateLibraryStats();
                this.filterAndRenderSongs();
                this.hideLoading();
            } else {
                throw new Error(data.error || 'Error desconocido al cargar canciones');
            }
            
        } catch (error) {
            console.error('❌ Error cargando biblioteca:', error);
            this.showError('Error al cargar la biblioteca musical');
        }
    }

    async loadPlayerState() {
        try {
            console.log('📡 Cargando estado del reproductor...');
            const response = await fetch('/api/player/state');
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.current_track && data.has_current_track) {
                console.log('✅ Estado del reproductor cargado:', data.current_track);
                
                // Resaltar la canción que se está reproduciendo
                this.highlightCurrentTrack(data.current_track.id);
                
                // Actualizar mini player si existe
                this.updateMiniPlayerWithTrack(data);
            } else {
                console.log('ℹ️ No hay canción en reproducción actualmente');
            }
            
            // Actualizar estados de shuffle y repeat si están disponibles
            if (data.shuffle !== undefined) {
                console.log('🔀 Sincronizando estado shuffle:', data.shuffle);
                const shuffleBtn = document.getElementById('shuffle-btn');
                if (shuffleBtn) {
                    if (data.shuffle) {
                        shuffleBtn.classList.add('active');
                        shuffleBtn.style.color = 'var(--accent-primary)';
                    } else {
                        shuffleBtn.classList.remove('active');
                        shuffleBtn.style.color = '';
                    }
                }
            }
            
            if (data.repeat !== undefined) {
                console.log('🔁 Sincronizando estado repeat:', data.repeat);
                const repeatBtn = document.getElementById('repeat-btn');
                if (repeatBtn) {
                    repeatBtn.classList.remove('active', 'repeat-one', 'repeat-all');
                    const icon = repeatBtn.querySelector('i');
                    if (icon) {
                        switch (data.repeat) {
                            case 'one':
                                repeatBtn.classList.add('active', 'repeat-one');
                                repeatBtn.style.color = 'var(--accent-primary)';
                                icon.className = 'fas fa-redo';
                                break;
                            case 'all':
                                repeatBtn.classList.add('active', 'repeat-all');
                                repeatBtn.style.color = 'var(--accent-secondary)';
                                icon.className = 'fas fa-redo';
                                break;
                            default:
                                repeatBtn.style.color = '';
                                icon.className = 'fas fa-redo';
                        }
                    }
                }
            }
            
        } catch (error) {
            console.warn('⚠️ No se pudo cargar el estado del reproductor:', error);
        }
    }

    highlightCurrentTrack(trackId) {
        // Remover resaltado anterior
        const previousHighlighted = document.querySelectorAll('.song-item.playing');
        previousHighlighted.forEach(item => {
            item.classList.remove('playing');
        });
        
        // Resaltar canción actual
        if (trackId) {
            const currentTrackElement = document.querySelector(`[data-track-id="${trackId}"]`);
            if (currentTrackElement) {
                currentTrackElement.classList.add('playing');
                
                // Hacer scroll para mostrar la canción actual
                setTimeout(() => {
                    currentTrackElement.scrollIntoView({ 
                        behavior: 'smooth', 
                        block: 'center' 
                    });
                }, 500);
                
                console.log(`✅ Canción actual resaltada: ID ${trackId}`);
            }
        }
    }

    updateMiniPlayerWithTrack(playerData) {
        // Actualizar mini player con información del track actual
        const miniPlayer = document.getElementById('mini-player');
        if (!miniPlayer || !playerData.current_track) return;
        
        const track = playerData.current_track;
        const isPlaying = playerData.state === 'playing';
        
        miniPlayer.innerHTML = `
            <div class="mini-player-content">
                <div class="mini-track-info">
                    <div class="mini-track-title">${track.title || 'Título desconocido'}</div>
                    <div class="mini-track-artist">${track.artist || 'Artista desconocido'}</div>
                </div>
                <div class="mini-controls">
                    <button class="mini-btn" onclick="libraryPage.previousTrack()">
                        <i class="fas fa-step-backward"></i>
                    </button>
                    <button class="mini-btn play-pause" onclick="libraryPage.togglePlayPause()">
                        <i class="fas fa-${isPlaying ? 'pause' : 'play'}"></i>
                    </button>
                    <button class="mini-btn" onclick="libraryPage.nextTrack()">
                        <i class="fas fa-step-forward"></i>
                    </button>
                </div>
                <div class="mini-volume">
                    <i class="fas fa-volume-up"></i>
                    <span>${playerData.volume || 50}%</span>
                </div>
            </div>
        `;
        
        miniPlayer.style.display = 'block';
    }
    
    updateLibraryStats() {
        const totalSongs = this.songs.length;
        const totalDuration = this.songs.reduce((sum, song) => sum + (song.duration || 0), 0);
        const estimatedSize = Math.round(totalSongs * 4.5); // ~4.5MB promedio
        
        if (this.elements.totalSongs) {
            this.elements.totalSongs.textContent = `${totalSongs} canciones`;
        }
        
        if (this.elements.totalDuration) {
            this.elements.totalDuration.textContent = this.formatTime(totalDuration);
        }
        
        if (this.elements.totalSize) {
            const sizeText = estimatedSize > 1024 
                ? `${(estimatedSize / 1024).toFixed(1)} GB` 
                : `${estimatedSize} MB`;
            this.elements.totalSize.textContent = sizeText;
        }
    }
    
    filterAndRenderSongs() {
        let filtered = [...this.songs];
        
        // Apply search filter
        if (this.searchQuery) {
            filtered = filtered.filter(song => 
                ((song.title || '').toLowerCase().includes(this.searchQuery)) ||
                ((song.artist || '').toLowerCase().includes(this.searchQuery)) ||
                ((song.album || '').toLowerCase().includes(this.searchQuery))
            );
        }
        
        // Apply category filter
        switch (this.currentFilter) {
            case 'favorites':
                // TODO: Implement favorites system
                filtered = filtered.filter(song => song.is_favorite);
                break;
            case 'recent':
                // TODO: Implement recent plays tracking
                filtered = filtered.slice(0, 50); // Show last 50 as "recent"
                break;
            case 'all':
            default:
                // No additional filtering
                break;
        }
        
        // Apply sorting
        filtered = this.sortSongs(filtered);
        
        this.filteredSongs = filtered;
        this.renderSongs();
    }
    
    sortSongs(songs) {
        return songs.sort((a, b) => {
            let aVal, bVal;
            
            switch (this.currentSort) {
                case 'title':
                    aVal = (a.title || '').toLowerCase();
                    bVal = (b.title || '').toLowerCase();
                    break;
                case 'artist':
                    aVal = (a.artist || '').toLowerCase();
                    bVal = (b.artist || '').toLowerCase();
                    break;
                case 'album':
                    aVal = (a.album || '').toLowerCase();
                    bVal = (b.album || '').toLowerCase();
                    break;
                case 'year':
                    aVal = a.year || 0;
                    bVal = b.year || 0;
                    break;
                case 'duration':
                    aVal = a.duration || 0;
                    bVal = b.duration || 0;
                    break;
                case 'date-added':
                    aVal = new Date(a.date_added || 0);
                    bVal = new Date(b.date_added || 0);
                    break;
                default:
                    return 0;
            }
            
            let comparison = 0;
            if (aVal < bVal) comparison = -1;
            if (aVal > bVal) comparison = 1;
            
            return this.sortOrder === 'asc' ? comparison : -comparison;
        });
    }
    
    renderSongs() {
        if (!this.elements.songsList) return;
        
        if (this.filteredSongs.length === 0) {
            this.showEmpty();
            return;
        }
        
        this.showSongs();
        this.elements.songsList.innerHTML = '';
        
        this.filteredSongs.forEach((song, index) => {
            const songElement = this.createSongElement(song, index + 1);
            this.elements.songsList.appendChild(songElement);
        });
    }
    
    createSongElement(song, number) {
        const div = document.createElement('div');
        div.className = 'library-song-item';
        div.dataset.songId = song.id;
        div.dataset.index = number - 1;
        
        const duration = this.formatTime(song.duration || 0);
        
        div.innerHTML = `
            <div class="song-number">${number}</div>
            <div class="song-title" title="${song.title || 'Sin título'}">${song.title || 'Sin título'}</div>
            <div class="song-artist" title="${song.artist || 'Artista desconocido'}">${song.artist || 'Artista desconocido'}</div>
            <div class="song-album" title="${song.album || 'Álbum desconocido'}">${song.album || 'Álbum desconocido'}</div>
            <div class="song-duration">${duration}</div>
            <div class="song-actions">
                <button class="song-action-btn" data-action="play" title="Reproducir">
                    <i class="fas fa-play"></i>
                </button>
                <button class="song-action-btn" data-action="favorite" title="Favorito">
                    <i class="far fa-heart"></i>
                </button>
                <button class="song-action-btn" data-action="menu" title="Más opciones">
                    <i class="fas fa-ellipsis-v"></i>
                </button>
            </div>
        `;
        
        // Add event listeners
        div.addEventListener('click', (e) => {
            if (!e.target.closest('.song-actions')) {
                this.playTrack(song.id);
            }
        });
        
        div.addEventListener('dblclick', () => {
            this.playTrack(song.id);
        });
        
        // Action buttons
        div.querySelectorAll('.song-action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = btn.dataset.action;
                this.handleSongAction(song, action, btn);
            });
        });
        
        return div;
    }
    
    async playTrack(trackId) {
        try {
            console.log(`🎵 Reproduciendo canción ID: ${trackId}`);
            
            const response = await fetch(`/api/library/play/${trackId}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success) {
                console.log('✅ Reproducción iniciada');
                this.showToast('success', '🎵 Reproduciendo', data.message || 'Canción iniciada');
            } else {
                throw new Error(data.error || 'Error desconocido');
            }
            
        } catch (error) {
            console.error('❌ Error reproduciendo canción:', error);
            this.showToast('error', 'Error', 'No se pudo reproducir la canción');
        }
    }
    
    handleSongAction(song, action, button) {
        switch (action) {
            case 'play':
                this.playTrack(song.id);
                break;
            case 'favorite':
                this.toggleFavorite(song, button);
                break;
            case 'menu':
                this.showContextMenuForSong(song, button);
                break;
        }
    }
    
    toggleFavorite(song, button) {
        const icon = button.querySelector('i');
        const isFavorite = icon.classList.contains('fas');
        
        if (isFavorite) {
            icon.className = 'far fa-heart';
            button.title = 'Agregar a favoritos';
            this.showToast('info', '💔', 'Removido de favoritos');
        } else {
            icon.className = 'fas fa-heart';
            button.title = 'Remover de favoritos';
            this.showToast('success', '❤️', 'Agregado a favoritos');
        }
        
        // TODO: Implement actual favorites API call
    }
    
    async shuffleAndPlayAll() {
        if (this.filteredSongs.length === 0) {
            this.showToast('warning', '⚠️', 'No hay canciones para reproducir');
            return;
        }
        
        try {
            // Shuffle the array
            const shuffled = [...this.filteredSongs].sort(() => Math.random() - 0.5);
            const firstSong = shuffled[0];
            
            await this.playTrack(firstSong.id);
            this.showToast('success', '🔀', `Reproducción aleatoria iniciada con ${shuffled.length} canciones`);
            
        } catch (error) {
            console.error('❌ Error en reproducción aleatoria:', error);
            this.showToast('error', 'Error', 'No se pudo iniciar la reproducción aleatoria');
        }
    }
    
    showContextMenu(event, songElement) {
        const songId = songElement.dataset.songId;
        const song = this.songs.find(s => s.id == songId);
        
        if (!song) return;
        
        this.contextMenuTarget = song;
        
        if (this.elements.contextMenu) {
            this.elements.contextMenu.style.display = 'block';
            this.elements.contextMenu.style.left = event.pageX + 'px';
            this.elements.contextMenu.style.top = event.pageY + 'px';
        }
    }
    
    hideContextMenu() {
        if (this.elements.contextMenu) {
            this.elements.contextMenu.style.display = 'none';
        }
        this.contextMenuTarget = null;
    }
    
    handleContextMenuAction(action) {
        if (!this.contextMenuTarget) return;
        
        const song = this.contextMenuTarget;
        
        switch (action) {
            case 'play':
                this.playTrack(song.id);
                break;
            case 'play-next':
                this.showToast('info', '⏭️', 'Función "Reproducir siguiente" próximamente');
                break;
            case 'favorite':
                this.toggleFavorite(song);
                break;
            case 'playlist':
                this.showToast('info', '📝', 'Función "Agregar a playlist" próximamente');
                break;
            case 'info':
                this.showSongInfo(song);
                break;
        }
        
        this.hideContextMenu();
    }
    
    showSongInfo(song) {
        const info = `
            📀 Título: ${song.title || 'Desconocido'}
            🎤 Artista: ${song.artist || 'Desconocido'}
            💿 Álbum: ${song.album || 'Desconocido'}
            📅 Año: ${song.year || 'Desconocido'}
            ⏱️ Duración: ${this.formatTime(song.duration || 0)}
            📁 Ruta: ${song.path || 'Desconocida'}
        `;
        
        alert(info); // TODO: Replace with a proper modal
    }
    
    async updateMiniPlayer(playerState) {
        if (!playerState) {
            // Fetch current state
            try {
                const response = await fetch('/api/player/state');
                if (response.ok) {
                    const data = await response.json();
                    if (data.success) {
                        playerState = data.state;
                    }
                }
            } catch (error) {
                console.error('Error fetching player state:', error);
                return;
            }
        }
        
        if (!playerState || !playerState.current_track || !this.elements.miniPlayer) {
            if (this.elements.miniPlayer) {
                this.elements.miniPlayer.style.display = 'none';
            }
            return;
        }
        
        // Show mini player
        this.elements.miniPlayer.style.display = 'block';
        
        // Update track info
        const titleElement = document.getElementById('mini-track-title');
        const artistElement = document.getElementById('mini-track-artist');
        const coverElement = document.getElementById('mini-cover');
        const playButton = document.getElementById('mini-play-btn');
        
        if (titleElement) {
            titleElement.textContent = playerState.current_track.title || 'Sin título';
        }
        
        if (artistElement) {
            artistElement.textContent = playerState.current_track.artist || 'Artista desconocido';
        }
        
        if (coverElement) {
            // TODO: Use actual cover art when available
            coverElement.src = '/static/images/default-cover.png';
        }
        
        if (playButton) {
            const icon = playButton.querySelector('i');
            if (icon) {
                icon.className = playerState.is_playing ? 'fas fa-pause' : 'fas fa-play';
            }
        }
        
        // Setup mini player controls
        this.setupMiniPlayerControls();
    }
    
    setupMiniPlayerControls() {
        const playBtn = document.getElementById('mini-play-btn');
        const prevBtn = document.getElementById('mini-prev-btn');
        const nextBtn = document.getElementById('mini-next-btn');
        
        if (playBtn) {
            playBtn.onclick = () => this.togglePlayPause();
        }
        
        if (prevBtn) {
            prevBtn.onclick = () => this.previousTrack();
        }
        
        if (nextBtn) {
            nextBtn.onclick = () => this.nextTrack();
        }
    }
    
    async togglePlayPause() {
        try {
            // First get current state
            const stateResponse = await fetch('/api/player/state');
            const stateData = await stateResponse.json();
            
            if (!stateData.success) {
                throw new Error('No se pudo obtener el estado del reproductor');
            }
            
            const isPlaying = stateData.state.is_playing;
            const endpoint = isPlaying ? '/api/player/pause' : '/api/player/play';
            
            const response = await fetch(endpoint, { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                console.log(isPlaying ? '⏸️ Pausado' : '▶️ Reproduciendo');
            }
            
        } catch (error) {
            console.error('Error toggle play/pause:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar el estado de reproducción');
        }
    }
    
    async nextTrack() {
        try {
            const response = await fetch('/api/player/next', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                console.log('⏭️ Siguiente canción');
            }
            
        } catch (error) {
            console.error('Error next track:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar a la siguiente canción');
        }
    }
    
    async previousTrack() {
        try {
            const response = await fetch('/api/player/previous', { method: 'POST' });
            const data = await response.json();
            
            if (data.success) {
                console.log('⏮️ Canción anterior');
            }
            
        } catch (error) {
            console.error('Error previous track:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar a la canción anterior');
        }
    }
    
    updateCurrentTrackHighlight(playerState) {
        // Remove existing highlights
        document.querySelectorAll('.library-song-item.active, .library-song-item.playing').forEach(item => {
            item.classList.remove('active', 'playing');
        });
        
        if (!playerState || !playerState.current_track) return;
        
        // Find and highlight current track
        const currentTrackElement = document.querySelector(`[data-song-id="${playerState.current_track.id}"]`);
        if (currentTrackElement) {
            currentTrackElement.classList.add('active');
            if (playerState.is_playing) {
                currentTrackElement.classList.add('playing');
            }
        }
    }
    
    // UI State Management
    showLoading() {
        if (this.elements.loading) this.elements.loading.style.display = 'flex';
        if (this.elements.empty) this.elements.empty.style.display = 'none';
        if (this.elements.songs) this.elements.songs.style.display = 'none';
    }
    
    hideLoading() {
        if (this.elements.loading) this.elements.loading.style.display = 'none';
    }
    
    showEmpty() {
        this.hideLoading();
        if (this.elements.empty) this.elements.empty.style.display = 'flex';
        if (this.elements.songs) this.elements.songs.style.display = 'none';
    }
    
    showSongs() {
        this.hideLoading();
        if (this.elements.empty) this.elements.empty.style.display = 'none';
        if (this.elements.songs) this.elements.songs.style.display = 'block';
    }
    
    showError(message) {
        this.hideLoading();
        // TODO: Implement proper error display
        console.error('❌ Error:', message);
        this.showToast('error', 'Error', message);
    }
    
    // Helper methods
    updateClearSearchButton() {
        if (this.elements.clearSearch) {
            this.elements.clearSearch.style.display = this.searchQuery ? 'block' : 'none';
        }
    }
    
    updateSortOrderButton() {
        if (this.elements.sortOrderBtn) {
            const icon = this.elements.sortOrderBtn.querySelector('i');
            if (icon) {
                icon.className = this.sortOrder === 'asc' ? 'fas fa-sort-amount-up' : 'fas fa-sort-amount-down';
            }
        }
    }
    
    setActiveFilter(filter) {
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-filter="${filter}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
    
    setActiveViewMode(view) {
        document.querySelectorAll('.view-mode-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        
        const activeBtn = document.querySelector(`[data-view="${view}"]`);
        if (activeBtn) {
            activeBtn.classList.add('active');
        }
    }
    
    formatTime(seconds) {
        if (!seconds || seconds === 0) return '0:00';
        
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = Math.floor(seconds % 60);
        
        if (hours > 0) {
            return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        } else {
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        }
    }
    
    showToast(type, title, message) {
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <strong>${title}</strong>
                <span>${message}</span>
            </div>
        `;
        
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#ff4757' : type === 'success' ? '#2ed573' : '#3742fa'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 10px;
            z-index: 9999;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            animation: slideInRight 0.3s ease;
        `;
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.libraryPage = new LibraryPage();
});

// Add CSS animations for toasts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOutRight {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
