// 🎵 MUSIC PLAYER PRO - PLAYER CONTROLS
// ====================================
// Controles específicos del reproductor

// Definir extensiones del reproductor para cuando MusicPlayerApp esté disponible
window.PlayerControlsExtensions = {
    
    // ============================
    // 🎛️ CONTROLES AVANZADOS
    // ============================

    setupPlayerControls() {
        this.setupProgressBarInteraction();
        this.setupVolumeControls();
        this.setupKeyboardShortcuts();
        this.startProgressUpdater();
    },

    setupProgressBarInteraction() {
        if (!this.elements.progressContainer) return;

        let isDragging = false;
        let dragStartX = 0;

        // Mouse events
        this.elements.progressContainer.addEventListener('mousedown', (e) => {
            isDragging = true;
            dragStartX = e.clientX;
            this.handleProgressInteraction(e);
            document.addEventListener('mousemove', handleMouseMove);
            document.addEventListener('mouseup', handleMouseUp);
        });

        const handleMouseMove = (e) => {
            if (isDragging) {
                e.preventDefault();
                this.handleProgressInteraction(e);
            }
        };

        const handleMouseUp = () => {
            isDragging = false;
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
        };

        // Touch events para móvil
        this.elements.progressContainer.addEventListener('touchstart', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            this.handleProgressInteraction(touch);
        });

        this.elements.progressContainer.addEventListener('touchmove', (e) => {
            e.preventDefault();
            const touch = e.touches[0];
            this.handleProgressInteraction(touch);
        });

        // Hover effects
        this.elements.progressContainer.addEventListener('mouseenter', () => {
            if (this.elements.progressHandle) {
                this.elements.progressHandle.style.opacity = '1';
            }
        });

        this.elements.progressContainer.addEventListener('mouseleave', () => {
            if (this.elements.progressHandle && !isDragging) {
                this.elements.progressHandle.style.opacity = '0';
            }
        });
    },

    handleProgressInteraction(event) {
        if (!this.elements.progressBar || this.state.duration === 0) return;

        const rect = this.elements.progressBar.getBoundingClientRect();
        const percentage = Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width));
        const newPosition = percentage * this.state.duration;

        // Actualizar UI inmediatamente para respuesta rápida
        this.updateProgressBarUI(percentage);

        // Enviar al servidor
        this.seekTo(newPosition);
    },

    updateProgressBarUI(percentage) {
        if (this.elements.progressFill) {
            this.elements.progressFill.style.width = `${percentage * 100}%`;
        }
        
        if (this.elements.progressHandle) {
            this.elements.progressHandle.style.left = `${percentage * 100}%`;
        }
        
        if (this.elements.currentTime) {
            const timeValue = percentage * this.state.duration;
            this.elements.currentTime.textContent = this.config.Utils.formatTime(timeValue);
        }
    },

    setupVolumeControls() {
        if (!this.elements.volumeSlider) return;

        // Mouse wheel sobre el slider de volumen
        this.elements.volumeSlider.addEventListener('wheel', (e) => {
            e.preventDefault();
            const delta = e.deltaY > 0 ? -this.config.PLAYER.VOLUME_STEP : this.config.PLAYER.VOLUME_STEP;
            const newVolume = Math.max(0, Math.min(100, parseInt(this.elements.volumeSlider.value) + delta));
            this.elements.volumeSlider.value = newVolume;
            this.setVolume(newVolume);
        });

        // Click en el icono de volumen para mutear/desmutear
        if (this.elements.volumeIcon) {
            this.elements.volumeIcon.addEventListener('click', () => {
                this.toggleMute();
            });
        }

        // Doble click en el slider para volumen rápido (50%)
        this.elements.volumeSlider.addEventListener('dblclick', () => {
            this.setVolume(50);
        });
    },

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Solo procesar si no estamos en un input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                return;
            }

            switch (e.code) {
                case 'Space':
                    e.preventDefault();
                    this.togglePlayPause();
                    break;

                case 'ArrowLeft':
                    if (e.shiftKey) {
                        e.preventDefault();
                        this.api.seekRelative(-30); // 30 segundos atrás
                    } else if (e.ctrlKey) {
                        e.preventDefault();
                        this.previousTrack();
                    } else {
                        e.preventDefault();
                        this.api.seekRelative(-this.config.PLAYER.SEEK_STEP);
                    }
                    break;

                case 'ArrowRight':
                    if (e.shiftKey) {
                        e.preventDefault();
                        this.api.seekRelative(30); // 30 segundos adelante
                    } else if (e.ctrlKey) {
                        e.preventDefault();
                        this.nextTrack();
                    } else {
                        e.preventDefault();
                        this.api.seekRelative(this.config.PLAYER.SEEK_STEP);
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

                case 'KeyM':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.toggleMute();
                    }
                    break;

                case 'KeyS':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.toggleShuffle();
                    }
                    break;

                case 'KeyR':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.toggleRepeat();
                    }
                    break;

                case 'KeyF':
                    if (e.ctrlKey) {
                        e.preventDefault();
                        this.focusSearch();
                    }
                    break;

                case 'Escape':
                    this.hideModal();
                    break;
            }
        });
    },

    startProgressUpdater() {
        // Actualizar progreso cada segundo cuando está reproduciéndose
        setInterval(() => {
            if (this.state.isPlaying && this.state.duration > 0) {
                // WebSocket debería manejar esto, pero como backup...
                this.state.position += 1;
                if (this.state.position > this.state.duration) {
                    this.state.position = this.state.duration;
                }
                this.updateProgressBar();
            }
        }, 1000);
    },

    // ============================
    // 🔊 CONTROLES DE VOLUMEN
    // ============================

    toggleMute() {
        if (this.state.volume > 0) {
            this.previousVolume = this.state.volume;
            this.setVolume(0);
        } else {
            this.setVolume(this.previousVolume || 50);
        }
    },

    setVolumePreset(preset) {
        const presets = {
            low: 25,
            medium: 50,
            high: 75,
            max: 100
        };
        
        if (presets[preset] !== undefined) {
            this.setVolume(presets[preset]);
            this.showToast('info', 'Volumen', `Ajustado a ${preset}: ${presets[preset]}%`);
        }
    },

    // ============================
    // ⏯️ CONTROLES DE REPRODUCCIÓN
    // ============================

    async stop() {
        try {
            await this.api.stop();
            this.showToast('info', 'Detenido', 'Reproducción detenida');
        } catch (error) {
            this.config.Utils.log('error', 'Error al detener:', error);
            this.showToast('error', 'Error', 'No se pudo detener la reproducción');
        }
    },

    async playPause() {
        try {
            if (this.state.isPlaying) {
                await this.api.pause();
            } else {
                await this.api.play();
            }
        } catch (error) {
            this.config.Utils.log('error', 'Error en play/pause:', error);
            this.showToast('error', 'Error', 'No se pudo cambiar el estado de reproducción');
        }
    },

    // ============================
    // 📋 GESTIÓN DE LISTAS
    // ============================

    async playPlaylist(playlist, startIndex = 0) {
        if (!playlist || playlist.length === 0) {
            this.showToast('warning', 'Lista vacía', 'No hay canciones para reproducir');
            return;
        }

        try {
            this.state.playlist = playlist;
            this.state.currentPlaylistIndex = startIndex;
            
            const track = playlist[startIndex];
            await this.playTrack(track.id);
            
            this.showToast('success', 'Lista reproduciendo', `${playlist.length} canciones en cola`);
            
        } catch (error) {
            this.config.Utils.log('error', 'Error al reproducir playlist:', error);
            this.showToast('error', 'Error', 'No se pudo reproducir la lista');
        }
    },

    getNextTrackIndex() {
        if (this.state.playlist.length === 0) return -1;
        
        if (this.state.isShuffled) {
            // Modo aleatorio
            let nextIndex;
            do {
                nextIndex = Math.floor(Math.random() * this.state.playlist.length);
            } while (nextIndex === this.state.currentPlaylistIndex && this.state.playlist.length > 1);
            return nextIndex;
        } else {
            // Modo secuencial
            const nextIndex = this.state.currentPlaylistIndex + 1;
            if (nextIndex >= this.state.playlist.length) {
                return this.state.isRepeating ? 0 : -1;
            }
            return nextIndex;
        }
    },

    getPreviousTrackIndex() {
        if (this.state.playlist.length === 0) return -1;
        
        if (this.state.isShuffled && this.playHistory && this.playHistory.length > 1) {
            // En modo aleatorio, usar historial
            return this.playHistory[this.playHistory.length - 2];
        } else {
            // Modo secuencial
            const prevIndex = this.state.currentPlaylistIndex - 1;
            if (prevIndex < 0) {
                return this.state.isRepeating ? this.state.playlist.length - 1 : -1;
            }
            return prevIndex;
        }
    },

    // ============================
    // 🎨 EFECTOS VISUALES
    // ============================

    addVisualizationToBeatDrop() {
        // Detectar "beat drops" en la música para efectos visuales
        if (this.state.isPlaying && window.visualizer) {
            const avgLevel = window.visualizer.smoothedData.reduce((a, b) => a + b, 0) / window.visualizer.smoothedData.length;
            
            if (avgLevel > 80) {
                // Beat drop detectado
                this.triggerBeatDropEffect();
            }
        }
    },

    triggerBeatDropEffect() {
        // Efecto visual para beat drops
        const container = document.querySelector('.visualizer-container');
        if (container) {
            container.classList.add('beat-drop');
            setTimeout(() => {
                container.classList.remove('beat-drop');
            }, 200);
        }
        
        // Efecto en los controles
        if (this.elements.playPauseBtn) {
            this.elements.playPauseBtn.style.transform = 'scale(1.1)';
            setTimeout(() => {
                this.elements.playPauseBtn.style.transform = 'scale(1)';
            }, 150);
        }
    },

    // ============================
    // 🔧 UTILIDADES
    // ============================

    focusSearch() {
        if (this.elements.searchInput) {
            this.elements.searchInput.focus();
            this.elements.searchInput.select();
        }
    },

    savePlayerSettings() {
        const settings = {
            volume: this.state.volume,
            isShuffled: this.state.isShuffled,
            isRepeating: this.state.isRepeating,
            lastTrack: this.state.currentTrack?.id || null
        };
        
        this.config.Utils.setStoredSetting('SETTINGS', settings);
    },

    loadPlayerSettings() {
        const settings = this.config.Utils.getStoredSetting('SETTINGS', {});
        
        if (settings.volume !== undefined) {
            this.setVolume(settings.volume);
        }
        
        if (settings.isShuffled !== undefined) {
            this.state.isShuffled = settings.isShuffled;
            if (this.elements.shuffleBtn) {
                this.elements.shuffleBtn.classList.toggle('active', settings.isShuffled);
            }
        }
        
        if (settings.isRepeating !== undefined) {
            this.state.isRepeating = settings.isRepeating;
            if (this.elements.repeatBtn) {
                this.elements.repeatBtn.classList.toggle('active', settings.isRepeating);
            }
        }
    },

    // Inicializar controles del reproductor cuando la app esté lista
    initPlayerControlsExtension() {
        this.setupPlayerControls();
        this.loadPlayerSettings();
        
        // Guardar configuración cada 30 segundos
        setInterval(() => {
            if (this.config.PLAYER.AUTO_SAVE_SETTINGS) {
                this.savePlayerSettings();
            }
        }, 30000);
        
        // Detectar beat drops cada 100ms
        setInterval(() => {
            this.addVisualizationToBeatDrop();
        }, 100);
        
        this.config.Utils.log('info', 'Controles del reproductor extendidos inicializados');
    }
};

// CSS adicional para efectos
const playerControlsStyles = `
    .beat-drop {
        animation: beatDropGlow 0.2s ease-out;
    }
    
    @keyframes beatDropGlow {
        0% { box-shadow: inset 0 0 20px rgba(255, 107, 107, 0.3); }
        100% { box-shadow: inset 0 0 40px rgba(255, 107, 107, 0.6); }
    }
    
    .control-btn-main {
        transition: transform 0.15s ease;
    }
    
    .progress-handle {
        transition: opacity 0.3s ease, transform 0.1s ease;
    }
    
    .progress-handle:active {
        transform: translate(-50%, -50%) scale(1.3) !important;
    }
    
    .volume-slider::-webkit-slider-thumb {
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
`;

// Inyectar estilos si no existen
if (!document.getElementById('player-controls-styles')) {
    const styleSheet = document.createElement('style');
    styleSheet.id = 'player-controls-styles';
    styleSheet.textContent = playerControlsStyles;
    document.head.appendChild(styleSheet);
}

// Inicializar extensión cuando la app esté lista
document.addEventListener('DOMContentLoaded', function() {
    // Esperar a que MusicPlayerApp esté disponible
    const initExtension = () => {
        if (window.musicPlayerApp && window.musicPlayerApp.state.isInitialized) {
            window.musicPlayerApp.initPlayerControlsExtension();
        } else {
            setTimeout(initExtension, 100);
        }
    };
    
    setTimeout(initExtension, 1000);
});
