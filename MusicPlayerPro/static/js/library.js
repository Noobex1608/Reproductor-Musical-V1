// 🎵 MUSIC PLAYER PRO - LIBRARY MANAGEMENT
// =======================================
// Gestión de la biblioteca musical y lista de canciones

// Definir extensiones de biblioteca para cuando MusicPlayerApp esté disponible
window.LibraryExtensions = {
    
    // ============================
    // 📚 RENDERIZADO DE BIBLIOTECA
    // ============================

    renderSongsList(songs) {
        if (!this.elements.songsList) return;

        if (!songs || songs.length === 0) {
            this.showNoSongs();
            return;
        }

        this.hideSongsLoading();
        this.hideNoSongs();
        this.elements.songsList.style.display = 'block';

        // Limpiar lista actual
        this.elements.songsList.innerHTML = '';

        // Renderizar cada canción
        songs.forEach((song, index) => {
            const songElement = this.createSongElement(song, index);
            this.elements.songsList.appendChild(songElement);
        });

        this.config.Utils.log('debug', `Renderizadas ${songs.length} canciones`);
    },

    createSongElement(song, index) {
        const div = document.createElement('div');
        div.className = 'song-item';
        div.dataset.trackId = song.id;
        div.dataset.index = index;
        div.title = `🎵 Haz clic para reproducir "${song.title}"`;

        // Verificar si es la canción actual
        const isCurrentTrack = this.state.currentTrack && this.state.currentTrack.id === song.id;
        const isPlaying = isCurrentTrack && this.state.isPlaying;

        if (isCurrentTrack) {
            div.classList.add('active');
        }
        if (isPlaying) {
            div.classList.add('playing');
        }

        div.innerHTML = `
            <div class="song-number">${(index + 1).toString().padStart(2, '0')}</div>
            <div class="song-artwork">
                🎵
            </div>
            <div class="song-info">
                <div class="song-title">${this.escapeHtml(song.title || 'Sin título')}</div>
                <div class="song-meta">
                    <span class="song-artist">${this.escapeHtml(song.artist || 'Artista desconocido')}</span>
                    <span class="song-album">${this.escapeHtml(song.album || 'Álbum desconocido')}</span>
                </div>
            </div>
            <div class="song-duration">${this.config.Utils.formatTime(song.duration || 0)}</div>
            <div class="song-actions">
                <button class="song-action-btn" title="Agregar a favoritos" data-action="favorite">
                    <i class="far fa-heart"></i>
                </button>
                <button class="song-action-btn" title="Agregar a playlist" data-action="playlist">
                    <i class="fas fa-plus"></i>
                </button>
                <button class="song-action-btn play-hint" title="Haz clic para reproducir" data-action="play">
                    <i class="fas fa-play"></i>
                </button>
            </div>
        `;

        // Event listeners
        this.setupSongElementEvents(div, song);

        return div;
    },

    setupSongElementEvents(element, song) {
        // Click en la canción para reproducir
        element.addEventListener('click', (e) => {
            // Evitar que se active si se hizo click en un botón de acción
            if (!e.target.closest('.song-actions')) {
                this.playTrack(song.id);
            }
        });

        // Doble click para reproducir inmediatamente
        element.addEventListener('dblclick', (e) => {
            if (!e.target.closest('.song-actions')) {
                this.playTrack(song.id);
            }
        });

        // Botones de acción
        const actionButtons = element.querySelectorAll('.song-action-btn');
        actionButtons.forEach(button => {
            button.addEventListener('click', (e) => {
                e.stopPropagation();
                const action = button.dataset.action;
                this.handleSongAction(song, action, button);
            });
        });

        // Hover effects
        element.addEventListener('mouseenter', () => {
            element.style.transform = 'translateX(4px)';
        });

        element.addEventListener('mouseleave', () => {
            element.style.transform = 'translateX(0)';
        });
    },

    handleSongAction(song, action, button) {
        switch (action) {
            case 'play':
                this.playTrack(song.id);
                break;
            case 'favorite':
                this.toggleFavorite(song, button);
                break;
            case 'playlist':
                this.showAddToPlaylistModal(song);
                break;
            case 'menu':
                this.showSongContextMenu(song, button);
                break;
        }
    },

    toggleFavorite(song, button) {
        // TODO: Implementar sistema de favoritos
        const icon = button.querySelector('i');
        const isFavorite = icon.classList.contains('fas');
        
        if (isFavorite) {
            icon.className = 'far fa-heart';
            button.title = 'Agregar a favoritos';
            this.showToast('info', 'Favorito', 'Removido de favoritos');
        } else {
            icon.className = 'fas fa-heart';
            button.title = 'Remover de favoritos';
            this.showToast('success', 'Favorito', 'Agregado a favoritos');
        }
        
        this.config.Utils.log('info', `Toggle favorite: ${song.title} - ${!isFavorite}`);
    },

    // ============================
    // 🔍 BÚSQUEDA Y FILTRADO
    // ============================

    sortSongs(criteria) {
        if (!this.state.playlist || this.state.playlist.length === 0) return;

        const sortedSongs = [...this.state.playlist];

        switch (criteria) {
            case 'title':
                sortedSongs.sort((a, b) => (a.title || '').localeCompare(b.title || ''));
                break;
            case 'artist':
                sortedSongs.sort((a, b) => (a.artist || '').localeCompare(b.artist || ''));
                break;
            case 'album':
                sortedSongs.sort((a, b) => (a.album || '').localeCompare(b.album || ''));
                break;
            case 'year':
                sortedSongs.sort((a, b) => (b.year || 0) - (a.year || 0));
                break;
            case 'duration':
                sortedSongs.sort((a, b) => (b.duration || 0) - (a.duration || 0));
                break;
            default:
                return; // No cambiar orden
        }

        this.renderSongsList(sortedSongs);
        this.showToast('info', 'Ordenado', `Canciones ordenadas por ${criteria}`);
    },

    // ============================
    // 📊 ESTADÍSTICAS
    // ============================

    updateLibraryStats(songs) {
        if (!songs) return;

        // Actualizar contador
        if (this.elements.libraryCount) {
            this.elements.libraryCount.textContent = songs.length;
        }

        // Calcular duración total
        const totalDuration = songs.reduce((total, song) => total + (song.duration || 0), 0);
        const totalDurationElement = document.getElementById('total-duration');
        if (totalDurationElement) {
            totalDurationElement.textContent = this.config.Utils.formatTime(totalDuration);
        }

        // Calcular tamaño estimado (aproximado)
        const estimatedSize = songs.length * 4; // ~4MB promedio por canción
        const librarySizeElement = document.getElementById('library-size');
        if (librarySizeElement) {
            librarySizeElement.textContent = estimatedSize > 1024 
                ? `${(estimatedSize / 1024).toFixed(1)} GB` 
                : `${estimatedSize} MB`;
        }

        this.config.Utils.log('debug', 'Estadísticas actualizadas:', {
            count: songs.length,
            totalDuration,
            estimatedSize
        });
    },

    // ============================
    // 🎨 ESTADOS DE UI
    // ============================

    showLibraryLoading() {
        if (this.elements.songsLoading) {
            this.elements.songsLoading.style.display = 'flex';
        }
        if (this.elements.songsList) {
            this.elements.songsList.style.display = 'none';
        }
        if (this.elements.noSongs) {
            this.elements.noSongs.style.display = 'none';
        }
    },

    hideSongsLoading() {
        if (this.elements.songsLoading) {
            this.elements.songsLoading.style.display = 'none';
        }
    },

    showNoSongs() {
        if (this.elements.noSongs) {
            this.elements.noSongs.style.display = 'flex';
        }
        if (this.elements.songsList) {
            this.elements.songsList.style.display = 'none';
        }
        if (this.elements.songsLoading) {
            this.elements.songsLoading.style.display = 'none';
        }
    },

    hideNoSongs() {
        if (this.elements.noSongs) {
            this.elements.noSongs.style.display = 'none';
        }
    },

    showLibraryError(message = 'Error al cargar la biblioteca musical') {
        this.hideNoSongs();
        this.hideSongsLoading();
        
        if (this.elements.songsList) {
            this.elements.songsList.style.display = 'block';
            this.elements.songsList.innerHTML = `
                <div class="library-error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>Error de carga</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="musicPlayerApp.loadLibrary()">
                        <i class="fas fa-sync"></i>
                        Reintentar
                    </button>
                </div>
            `;
        }
        
        this.showToast('error', 'Error', message);
    },

    // ============================
    // 🔧 UTILIDADES
    // ============================

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // ============================
    // 🎵 PLAYLIST MANAGEMENT
    // ============================

    toggleShuffle() {
        this.state.isShuffled = !this.state.isShuffled;
        
        if (this.elements.shuffleBtn) {
            if (this.state.isShuffled) {
                this.elements.shuffleBtn.classList.add('active');
                this.showToast('info', 'Aleatorio', 'Reproducción aleatoria activada');
            } else {
                this.elements.shuffleBtn.classList.remove('active');
                this.showToast('info', 'Aleatorio', 'Reproducción aleatoria desactivada');
            }
        }
        
        // Guardar preferencia
        this.config.Utils.setStoredSetting('SHUFFLE', this.state.isShuffled);
    },

    toggleRepeat() {
        this.state.isRepeating = !this.state.isRepeating;
        
        if (this.elements.repeatBtn) {
            if (this.state.isRepeating) {
                this.elements.repeatBtn.classList.add('active');
                this.showToast('info', 'Repetir', 'Repetición activada');
            } else {
                this.elements.repeatBtn.classList.remove('active');
                this.showToast('info', 'Repetir', 'Repetición desactivada');
            }
        }
        
        // Guardar preferencia
        this.config.Utils.setStoredSetting('REPEAT', this.state.isRepeating);
    },

    // ============================
    // 📋 MODALS
    // ============================

    showAddToPlaylistModal(song) {
        // TODO: Implementar sistema de playlists
        this.showModal('Agregar a Playlist', `
            <div class="modal-playlist-content">
                <h4>Agregar "${song.title}" a:</h4>
                <div class="playlist-list">
                    <div class="playlist-item">
                        <i class="fas fa-music"></i>
                        <span>Mis Favoritas</span>
                    </div>
                    <div class="playlist-item">
                        <i class="fas fa-plus"></i>
                        <span>Crear nueva playlist</span>
                    </div>
                </div>
            </div>
        `);
    },

    showSongContextMenu(song, button) {
        // TODO: Implementar menú contextual
        this.showToast('info', 'Menú', 'Menú contextual próximamente disponible');
    },

    showModal(title, content) {
        if (this.elements.modalTitle) {
            this.elements.modalTitle.textContent = title;
        }
        
        if (this.elements.modalBody) {
            this.elements.modalBody.innerHTML = content;
        }
        
        if (this.elements.modalOverlay) {
            this.elements.modalOverlay.style.display = 'flex';
        }
    },

    hideModal() {
        if (this.elements.modalOverlay) {
            this.elements.modalOverlay.style.display = 'none';
        }
    }
};

// CSS adicional para estilos de biblioteca (inyectado dinámicamente)
const libraryStyles = `
    .library-error {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 3rem;
        text-align: center;
        color: var(--text-secondary);
    }
    
    .library-error i {
        font-size: 3rem;
        color: var(--error);
        margin-bottom: 1rem;
    }
    
    .library-error h3 {
        color: var(--text-primary);
        margin-bottom: 0.5rem;
    }
    
    .library-error p {
        margin-bottom: 1.5rem;
        max-width: 300px;
        line-height: 1.6;
    }
    
    .modal-playlist-content h4 {
        color: var(--text-primary);
        margin-bottom: 1rem;
    }
    
    .playlist-list {
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    
    .playlist-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1rem;
        background: var(--bg-tertiary);
        border: 1px solid var(--border-color);
        border-radius: var(--border-radius-md);
        cursor: pointer;
        transition: all var(--transition-fast);
    }
    
    .playlist-item:hover {
        background: var(--bg-accent);
        border-color: var(--accent-primary);
    }
    
    .playlist-item i {
        color: var(--accent-primary);
        width: 20px;
        text-align: center;
    }
`;

// Inyectar estilos
if (!document.getElementById('library-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'library-styles';
    styleSheet.textContent = libraryStyles;
    document.head.appendChild(styleSheet);
}
