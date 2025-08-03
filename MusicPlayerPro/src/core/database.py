# -*- coding: utf-8 -*-
"""
📊 DATABASE MANAGER - GESTOR DE BASE DE DATOS MUSICAL
====================================================
Sistema de base de datos completo para gestión musical:
- SQLite optimizado para rendimiento
- Índices inteligentes
- Cache de metadatos
- Playlists avanzadas
- Historial y estadísticas
"""

import sqlite3
import asyncio
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de base de datos musical optimizado"""
    
    def __init__(self, db_path: str = "data/music_library.db"):
        self.db_path = Path(db_path)
        self.connection: Optional[sqlite3.Connection] = None
        
        # Cache en memoria para consultas frecuentes
        self._cache = {}
        self._cache_timeout = 300  # 5 minutos
        
        # Configuración de optimización
        self.pragma_settings = {
            'journal_mode': 'WAL',
            'synchronous': 'NORMAL',
            'cache_size': -64000,  # 64MB cache
            'temp_store': 'MEMORY',
            'mmap_size': 268435456,  # 256MB mmap
        }
    
    async def initialize(self):
        """Inicializa la base de datos y crea tablas"""
        try:
            logger.info("Inicializando base de datos musical...")
            
            # Crear directorio si no existe
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Conectar a la base de datos
            self.connection = sqlite3.connect(
                str(self.db_path),
                check_same_thread=False
            )
            self.connection.row_factory = sqlite3.Row  # Acceso por nombre de columna
            
            # Aplicar configuraciones de optimización
            await self._apply_pragma_settings()
            
            # Crear tablas
            await self._create_tables()
            
            # Crear índices
            await self._create_indexes()
            
            logger.info("✅ Base de datos inicializada correctamente")
            
        except Exception as e:
            logger.error(f"Error inicializando base de datos: {e}")
            raise
    
    async def _apply_pragma_settings(self):
        """Aplica configuraciones PRAGMA para optimización"""
        cursor = self.connection.cursor()
        
        for pragma, value in self.pragma_settings.items():
            cursor.execute(f"PRAGMA {pragma} = {value}")
        
        cursor.close()
        self.connection.commit()
    
    async def _create_tables(self):
        """Crea todas las tablas necesarias"""
        cursor = self.connection.cursor()
        
        # Tabla principal de canciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_hash TEXT UNIQUE NOT NULL,
                title TEXT NOT NULL,
                artist TEXT,
                album TEXT,
                genre TEXT,
                year INTEGER,
                duration REAL,
                bitrate INTEGER,
                sample_rate INTEGER,
                file_size INTEGER,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                date_modified DATETIME,
                play_count INTEGER DEFAULT 0,
                last_played DATETIME,
                rating INTEGER DEFAULT 0,
                bpm REAL,
                key_signature TEXT,
                mood TEXT,
                energy REAL,
                danceability REAL,
                valence REAL,
                acousticness REAL,
                instrumentalness REAL,
                liveness REAL,
                speechiness REAL,
                loudness REAL
            )
        """)
        
        # Tabla de playlists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                song_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                is_smart INTEGER DEFAULT 0,
                smart_criteria TEXT,
                cover_path TEXT
            )
        """)
        
        # Tabla de relación playlist-canción
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS playlist_songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER NOT NULL,
                song_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                date_added DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists (id) ON DELETE CASCADE,
                FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE,
                UNIQUE(playlist_id, song_id)
            )
        """)
        
        # Tabla de historial de reproducción
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id INTEGER NOT NULL,
                played_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                play_duration REAL,
                completion_percentage REAL,
                source TEXT,  -- playlist, search, random, etc.
                device_info TEXT,
                FOREIGN KEY (song_id) REFERENCES songs (id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de configuraciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT,
                category TEXT,
                modified_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Tabla de géneros
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                song_count INTEGER DEFAULT 0
            )
        """)
        
        # Tabla de artistas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS artists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                song_count INTEGER DEFAULT 0,
                album_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                bio TEXT,
                image_path TEXT
            )
        """)
        
        # Tabla de álbumes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS albums (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT,
                year INTEGER,
                song_count INTEGER DEFAULT 0,
                total_duration REAL DEFAULT 0,
                cover_path TEXT,
                UNIQUE(title, artist)
            )
        """)
        
        cursor.close()
        self.connection.commit()
    
    async def _create_indexes(self):
        """Crea índices para optimizar consultas"""
        cursor = self.connection.cursor()
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_songs_artist ON songs(artist)",
            "CREATE INDEX IF NOT EXISTS idx_songs_album ON songs(album)",
            "CREATE INDEX IF NOT EXISTS idx_songs_genre ON songs(genre)",
            "CREATE INDEX IF NOT EXISTS idx_songs_year ON songs(year)",
            "CREATE INDEX IF NOT EXISTS idx_songs_play_count ON songs(play_count)",
            "CREATE INDEX IF NOT EXISTS idx_songs_rating ON songs(rating)",
            "CREATE INDEX IF NOT EXISTS idx_songs_last_played ON songs(last_played)",
            "CREATE INDEX IF NOT EXISTS idx_songs_file_path ON songs(file_path)",
            "CREATE INDEX IF NOT EXISTS idx_songs_file_hash ON songs(file_hash)",
            
            "CREATE INDEX IF NOT EXISTS idx_playlist_songs_playlist ON playlist_songs(playlist_id)",
            "CREATE INDEX IF NOT EXISTS idx_playlist_songs_song ON playlist_songs(song_id)",
            "CREATE INDEX IF NOT EXISTS idx_playlist_songs_position ON playlist_songs(position)",
            
            "CREATE INDEX IF NOT EXISTS idx_play_history_song ON play_history(song_id)",
            "CREATE INDEX IF NOT EXISTS idx_play_history_date ON play_history(played_at)",
            
            "CREATE INDEX IF NOT EXISTS idx_settings_category ON settings(category)",
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
        
        cursor.close()
        self.connection.commit()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Genera hash único para archivo"""
        file_stat = Path(file_path).stat()
        content = f"{file_path}_{file_stat.st_size}_{file_stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()
    
    async def add_song(self, song_data: Dict[str, Any]) -> Optional[int]:
        """Añade una canción a la base de datos"""
        try:
            cursor = self.connection.cursor()
            
            # Generar hash del archivo
            file_hash = self._get_file_hash(song_data['file_path'])
            
            # Verificar si ya existe
            existing = await self.get_song_by_hash(file_hash)
            if existing:
                logger.info(f"Canción ya existe: {song_data['title']}")
                return existing['id']
            
            # Insertar canción
            cursor.execute("""
                INSERT INTO songs (
                    file_path, file_hash, title, artist, album, genre, year,
                    duration, bitrate, sample_rate, file_size, date_modified,
                    bpm, key_signature, mood, energy, danceability, valence,
                    acousticness, instrumentalness, liveness, speechiness, loudness
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                song_data['file_path'],
                file_hash,
                song_data.get('title', 'Unknown'),
                song_data.get('artist', 'Unknown Artist'),
                song_data.get('album', 'Unknown Album'),
                song_data.get('genre', 'Unknown'),
                song_data.get('year'),
                song_data.get('duration', 0.0),
                song_data.get('bitrate'),
                song_data.get('sample_rate'),
                song_data.get('file_size'),
                datetime.now(),
                song_data.get('bpm'),
                song_data.get('key_signature'),
                song_data.get('mood'),
                song_data.get('energy'),
                song_data.get('danceability'),
                song_data.get('valence'),
                song_data.get('acousticness'),
                song_data.get('instrumentalness'),
                song_data.get('liveness'),
                song_data.get('speechiness'),
                song_data.get('loudness')
            ))
            
            song_id = cursor.lastrowid
            cursor.close()
            self.connection.commit()
            
            # Actualizar contadores
            await self._update_counters(song_data)
            
            # Limpiar cache
            self._clear_cache()
            
            logger.info(f"✅ Canción añadida: {song_data['title']} (ID: {song_id})")
            return song_id
            
        except Exception as e:
            logger.error(f"Error añadiendo canción: {e}")
            return None
    
    async def get_song_by_hash(self, file_hash: str) -> Optional[Dict]:
        """Obtiene canción por hash de archivo"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM songs WHERE file_hash = ?", (file_hash,))
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error obteniendo canción por hash: {e}")
            return None
    
    async def get_song_by_id(self, song_id: int) -> Optional[Dict]:
        """Obtiene canción por ID"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM songs WHERE id = ?", (song_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            logger.error(f"Error obteniendo canción por ID: {e}")
            return None
    
    async def search_songs(self, query: str, limit: int = 100) -> List[Dict]:
        """Búsqueda de canciones con texto completo"""
        try:
            cache_key = f"search_{query}_{limit}"
            if cache_key in self._cache:
                return self._cache[cache_key]
            
            cursor = self.connection.cursor()
            
            # Búsqueda en múltiples campos
            search_query = f"%{query}%"
            cursor.execute("""
                SELECT * FROM songs 
                WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
                ORDER BY 
                    CASE 
                        WHEN title LIKE ? THEN 1
                        WHEN artist LIKE ? THEN 2
                        WHEN album LIKE ? THEN 3
                        ELSE 4
                    END,
                    play_count DESC,
                    title
                LIMIT ?
            """, (search_query, search_query, search_query, search_query,
                  search_query, search_query, search_query, limit))
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            # Cache por 5 minutos
            self._cache[cache_key] = results
            
            return results
            
        except Exception as e:
            logger.error(f"Error en búsqueda: {e}")
            return []
    
    async def get_all_songs(self, limit: Optional[int] = None, offset: int = 0) -> List[Dict]:
        """Obtiene todas las canciones con paginación opcional"""
        try:
            cursor = self.connection.cursor()
            
            if limit:
                cursor.execute("""
                    SELECT * FROM songs 
                    ORDER BY date_added DESC 
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            else:
                cursor.execute("SELECT * FROM songs ORDER BY date_added DESC")
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo canciones: {e}")
            return []
    
    async def get_songs_by_artist(self, artist: str) -> List[Dict]:
        """Obtiene canciones por artista"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM songs 
                WHERE artist = ? 
                ORDER BY album, title
            """, (artist,))
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo canciones por artista: {e}")
            return []
    
    async def get_songs_by_album(self, album: str, artist: Optional[str] = None) -> List[Dict]:
        """Obtiene canciones por álbum"""
        try:
            cursor = self.connection.cursor()
            
            if artist:
                cursor.execute("""
                    SELECT * FROM songs 
                    WHERE album = ? AND artist = ?
                    ORDER BY title
                """, (album, artist))
            else:
                cursor.execute("""
                    SELECT * FROM songs 
                    WHERE album = ?
                    ORDER BY artist, title
                """, (album,))
            
            results = [dict(row) for row in cursor.fetchall()]
            cursor.close()
            
            return results
            
        except Exception as e:
            logger.error(f"Error obteniendo canciones por álbum: {e}")
            return []
    
    async def update_play_count(self, song_id: int, play_duration: float = 0.0):
        """Actualiza contador de reproducciones"""
        try:
            cursor = self.connection.cursor()
            
            # Actualizar canción
            cursor.execute("""
                UPDATE songs 
                SET play_count = play_count + 1, last_played = ?
                WHERE id = ?
            """, (datetime.now(), song_id))
            
            # Añadir al historial
            completion = min(100.0, (play_duration / await self._get_song_duration(song_id)) * 100) if play_duration > 0 else 0.0
            
            cursor.execute("""
                INSERT INTO play_history (song_id, play_duration, completion_percentage, source)
                VALUES (?, ?, ?, ?)
            """, (song_id, play_duration, completion, 'player'))
            
            cursor.close()
            self.connection.commit()
            
            # Limpiar cache
            self._clear_cache()
            
        except Exception as e:
            logger.error(f"Error actualizando play count: {e}")
    
    async def _get_song_duration(self, song_id: int) -> float:
        """Obtiene duración de una canción"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT duration FROM songs WHERE id = ?", (song_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return result[0] if result else 0.0
            
        except Exception as e:
            logger.error(f"Error obteniendo duración: {e}")
            return 0.0
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de la biblioteca"""
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # Estadísticas básicas
            cursor.execute("SELECT COUNT(*) FROM songs")
            stats['total_songs'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT artist) FROM songs WHERE artist != 'Unknown Artist'")
            stats['total_artists'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT album) FROM songs WHERE album != 'Unknown Album'")
            stats['total_albums'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(duration) FROM songs")
            total_duration = cursor.fetchone()[0] or 0
            stats['total_duration'] = total_duration
            stats['total_hours'] = total_duration / 3600
            
            cursor.execute("SELECT SUM(play_count) FROM songs")
            stats['total_plays'] = cursor.fetchone()[0] or 0
            
            # Top artistas
            cursor.execute("""
                SELECT artist, COUNT(*) as song_count, SUM(play_count) as total_plays
                FROM songs 
                WHERE artist != 'Unknown Artist'
                GROUP BY artist 
                ORDER BY total_plays DESC 
                LIMIT 10
            """)
            stats['top_artists'] = [dict(row) for row in cursor.fetchall()]
            
            # Canciones más reproducidas
            cursor.execute("""
                SELECT title, artist, play_count 
                FROM songs 
                ORDER BY play_count DESC 
                LIMIT 10
            """)
            stats['most_played'] = [dict(row) for row in cursor.fetchall()]
            
            # Actividad reciente
            cursor.execute("""
                SELECT DATE(played_at) as date, COUNT(*) as plays
                FROM play_history 
                WHERE played_at > datetime('now', '-30 days')
                GROUP BY DATE(played_at)
                ORDER BY date DESC
            """)
            stats['recent_activity'] = [dict(row) for row in cursor.fetchall()]
            
            cursor.close()
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {}
    
    async def _update_counters(self, song_data: Dict[str, Any]):
        """Actualiza contadores de artistas, álbumes, géneros"""
        try:
            cursor = self.connection.cursor()
            
            # Actualizar contador de artista
            if song_data.get('artist') and song_data['artist'] != 'Unknown Artist':
                cursor.execute("""
                    INSERT OR IGNORE INTO artists (name, song_count) VALUES (?, 0)
                """, (song_data['artist'],))
                
                cursor.execute("""
                    UPDATE artists 
                    SET song_count = song_count + 1 
                    WHERE name = ?
                """, (song_data['artist'],))
            
            # Actualizar contador de género
            if song_data.get('genre') and song_data['genre'] != 'Unknown':
                cursor.execute("""
                    INSERT OR IGNORE INTO genres (name, song_count) VALUES (?, 0)
                """, (song_data['genre'],))
                
                cursor.execute("""
                    UPDATE genres 
                    SET song_count = song_count + 1 
                    WHERE name = ?
                """, (song_data['genre'],))
            
            cursor.close()
            self.connection.commit()
            
        except Exception as e:
            logger.error(f"Error actualizando contadores: {e}")
    
    def _clear_cache(self):
        """Limpia cache interno"""
        self._cache.clear()
    
    async def cleanup(self):
        """Limpieza de recursos"""
        try:
            if self.connection:
                self.connection.close()
            
            logger.info("🧹 Base de datos cerrada correctamente")
            
        except Exception as e:
            logger.error(f"Error en cleanup de base de datos: {e}")
    
    # MÉTODOS ADICIONALES PARA LA APLICACIÓN
    
    async def get_all_tracks(self) -> List[Dict[str, Any]]:
        """Obtiene todas las pistas de la base de datos"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT id, file_path, title, artist, album, genre, 
                       year, duration
                FROM songs 
                ORDER BY artist, album, id
            """)
            
            tracks = []
            for row in cursor.fetchall():
                tracks.append({
                    'id': str(row['id']),
                    'path': row['file_path'],
                    'title': row['title'] or 'Desconocido',
                    'artist': row['artist'] or 'Desconocido',
                    'album': row['album'] or 'Desconocido',
                    'genre': row['genre'] or '',
                    'year': row['year'] or 0,
                    'duration': row['duration'] or 0.0,
                    'track_number': 0  # Por defecto
                })
            
            cursor.close()
            return tracks
            
        except Exception as e:
            logger.error(f"Error obteniendo pistas: {e}")
            return []
    
    async def add_play_history(self, track_id: str):
        """Añade una pista al historial de reproducción"""
        try:
            cursor = self.connection.cursor()
            
            # Verificar si la columna device_info existe
            cursor.execute("PRAGMA table_info(play_history)")
            columns = [column[1] for column in cursor.fetchall()]
            
            if 'device_info' in columns:
                # Usar el formato completo si la columna existe
                cursor.execute("""
                    INSERT INTO play_history (song_id, played_at, device_info)
                    VALUES (?, datetime('now'), ?)
                """, (track_id, "Music Player Pro"))
            else:
                # Usar formato simplificado si no existe la columna
                cursor.execute("""
                    INSERT INTO play_history (song_id, played_at)
                    VALUES (?, datetime('now'))
                """, (track_id,))
            
            self.connection.commit()
            cursor.close()
            
        except Exception as e:
            logger.error(f"Error añadiendo a historial: {e}")
    
    async def get_recent_plays(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtiene las reproducciones recientes"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT s.id, s.title, s.artist, s.album, ph.played_at
                FROM play_history ph
                JOIN songs s ON ph.song_id = s.id
                ORDER BY ph.played_at DESC
                LIMIT ?
            """, (limit,))
            
            plays = []
            for row in cursor.fetchall():
                plays.append({
                    'id': str(row['id']),
                    'title': row['title'],
                    'artist': row['artist'],
                    'album': row['album'],
                    'played_at': row['played_at']
                })
            
            cursor.close()
            return plays
            
        except Exception as e:
            logger.error(f"Error obteniendo historial: {e}")
            return []

# Singleton para acceso global
_db_manager_instance = None

def get_database_manager() -> DatabaseManager:
    """Obtiene la instancia singleton del gestor de BD"""
    global _db_manager_instance
    if _db_manager_instance is None:
        _db_manager_instance = DatabaseManager()
    return _db_manager_instance
