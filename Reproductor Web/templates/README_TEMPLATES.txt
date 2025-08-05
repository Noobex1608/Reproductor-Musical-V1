# 📄 TEMPLATES/ - PLANTILLAS HTML
# =============================================
# Directorio: templates/ - Interfaz Web HTML
# =============================================

## 📁 CONTENIDO DE TEMPLATES/

```
templates/
├── 📄 index.html              # Página principal del reproductor
├── 📄 index_backup.html       # Backup de versión anterior
└── 📄 library.html            # Página de biblioteca musical
```

## 📄 index.html - PÁGINA PRINCIPAL

### PROPÓSITO
**Plantilla principal**: Interfaz completa del reproductor musical web con todos los componentes integrados

### ESTRUCTURA HTML
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <!-- 🌐 Meta tags para responsividad y PWA -->
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Reproductor Musical Profesional">
    <title>🎵 Music Player Pro</title>
    
    <!-- 🎨 CSS Links -->
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/components.css">
    <link rel="stylesheet" href="/static/css/visualizer.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>

<body>
    <!-- 🏗️ Layout Principal -->
    <div class="main-container">
        
        <!-- 📋 Sidebar Navigation -->
        <aside class="sidebar">
            <div class="logo">
                <h1>🎵 Music Player Pro</h1>
            </div>
            
            <nav class="navigation">
                <ul>
                    <li><a href="#home" class="nav-link active">🏠 Inicio</a></li>
                    <li><a href="#library" class="nav-link">📚 Biblioteca</a></li>
                    <li><a href="#playlists" class="nav-link">📋 Playlists</a></li>
                    <li><a href="#settings" class="nav-link">⚙️ Configuración</a></li>
                </ul>
            </nav>
        </aside>

        <!-- 🌟 Contenido Principal -->
        <main class="main-content">
            <!-- 🎨 Visualizador de Espectro -->
            <section class="visualizer-section">
                <canvas id="visualizer-canvas"></canvas>
                <div class="visualizer-controls">
                    <button id="visualizer-toggle">🎨 Efectos</button>
                </div>
            </section>

            <!-- 🎵 Información de Canción Actual -->
            <section class="now-playing">
                <div class="song-info">
                    <img id="current-cover" src="/static/images/default-cover.png" alt="Portada">
                    <div class="song-details">
                        <h2 id="current-title">Sin reproducir</h2>
                        <p id="current-artist">Selecciona una canción</p>
                        <p id="current-album"></p>
                    </div>
                </div>
            </section>

            <!-- 📚 Biblioteca Musical -->
            <section class="library-section">
                <div class="library-header">
                    <h3>📚 Tu Biblioteca Musical</h3>
                    <div class="library-actions">
                        <input type="text" id="search-input" placeholder="🔍 Buscar música...">
                        <button id="scan-library">🔄 Escanear</button>
                    </div>
                </div>
                
                <div class="library-content">
                    <div id="songs-grid" class="songs-grid">
                        <!-- Songs se cargan dinámicamente via JavaScript -->
                    </div>
                </div>
            </section>
        </main>

        <!-- 🎮 Barra de Control del Reproductor -->
        <footer class="player-bar">
            <div class="player-controls">
                <!-- 🎵 Controles principales -->
                <div class="main-controls">
                    <button id="shuffle-btn" title="Aleatorio">🔀</button>
                    <button id="previous-btn" title="Anterior">⏮️</button>
                    <button id="play-pause-btn" title="Reproducir">▶️</button>
                    <button id="next-btn" title="Siguiente">⏭️</button>
                    <button id="repeat-btn" title="Repetir">🔁</button>
                </div>

                <!-- ⏱️ Barra de Progreso -->
                <div class="progress-section">
                    <span id="current-time">0:00</span>
                    <input type="range" id="progress-slider" min="0" max="100" value="0">
                    <span id="total-time">0:00</span>
                </div>

                <!-- 🔊 Control de Volumen -->
                <div class="volume-section">
                    <button id="mute-btn">🔊</button>
                    <input type="range" id="volume-slider" min="0" max="100" value="50">
                </div>
            </div>
        </footer>
    </div>

    <!-- 📜 JavaScript Scripts -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <script src="/static/js/config.js"></script>
    <script src="/static/js/api.js"></script>
    <script src="/static/js/websocket.js"></script>
    <script src="/static/js/player-controls.js"></script>
    <script src="/static/js/visualizer.js"></script>
    <script src="/static/js/library.js"></script>
    <script src="/static/js/ui.js"></script>
    <script src="/static/js/app.js"></script>
</body>
</html>
```

### COMPONENTES PRINCIPALES

#### 🏗️ LAYOUT RESPONSIVO
```html
<!-- Grid Layout Principal -->
<div class="main-container">
    <aside class="sidebar">      <!-- Navegación lateral -->
    <main class="main-content">  <!-- Contenido principal -->
    <footer class="player-bar">  <!-- Controles del reproductor -->
</div>

<!-- Responsive: En móvil se convierte en layout vertical -->
```

#### 🎵 REPRODUCTOR INTEGRADO
```html
<!-- Información de canción actual -->
<section class="now-playing">
    <img id="current-cover">        <!-- Portada dinámica -->
    <h2 id="current-title">         <!-- Título de la canción -->
    <p id="current-artist">         <!-- Artista -->
    <p id="current-album">          <!-- Álbum -->
</section>

<!-- Controles del reproductor -->
<div class="player-controls">
    <button id="shuffle-btn">🔀      <!-- Modo aleatorio -->
    <button id="previous-btn">⏮️     <!-- Canción anterior -->
    <button id="play-pause-btn">▶️   <!-- Play/Pause -->
    <button id="next-btn">⏭️        <!-- Siguiente canción -->
    <button id="repeat-btn">🔁       <!-- Modo repeat -->
</div>
```

#### 🎨 VISUALIZADOR DE ESPECTRO
```html
<section class="visualizer-section">
    <canvas id="visualizer-canvas"></canvas>  <!-- Canvas para efectos -->
    <div class="visualizer-controls">
        <button id="visualizer-toggle">🎨 Efectos</button>
    </div>
</section>
```

#### 📚 BIBLIOTECA MUSICAL
```html
<section class="library-section">
    <div class="library-header">
        <input type="text" id="search-input" placeholder="🔍 Buscar...">
        <button id="scan-library">🔄 Escanear</button>
    </div>
    
    <div id="songs-grid" class="songs-grid">
        <!-- Canciones se cargan dinámicamente -->
    </div>
</section>
```

### CARACTERÍSTICAS TÉCNICAS

#### 📱 RESPONSIVIDAD
```html
<!-- Meta viewport para móvil -->
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<!-- CSS Media Queries aplicadas automáticamente -->
<!-- JavaScript detecta tamaño de pantalla y adapta UI -->
```

#### 🌐 PWA READY
```html
<!-- Meta tags para Progressive Web App -->
<meta name="theme-color" content="#6C5CE7">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">

<!-- Icons para instalación como app -->
<link rel="icon" href="/static/images/favicon.png">
<link rel="apple-touch-icon" href="/static/images/favicon.png">
```

#### ⚡ OPTIMIZACIÓN DE CARGA
```html
<!-- CSS crítico inline (futuro) -->
<!-- Preload de recursos importantes -->
<link rel="preload" href="/static/css/main.css" as="style">
<link rel="preload" href="/static/js/app.js" as="script">

<!-- Scripts al final del body para no bloquear renderizado -->
```

## 📄 library.html - PÁGINA DE BIBLIOTECA

### PROPÓSITO
**Página dedicada**: Vista completa de la biblioteca musical con funcionalidades avanzadas

### ESTRUCTURA ESPECÍFICA
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📚 Biblioteca Musical - Music Player Pro</title>
    
    <!-- CSS específico para biblioteca -->
    <link rel="stylesheet" href="/static/css/main.css">
    <link rel="stylesheet" href="/static/css/library.css">
</head>

<body>
    <div class="library-container">
        <!-- 🔍 Panel de Búsqueda y Filtros -->
        <header class="library-header">
            <h1>📚 Biblioteca Musical</h1>
            
            <div class="search-section">
                <input type="text" id="search-input" placeholder="🔍 Buscar por título, artista o álbum...">
                <button id="advanced-search">🔧 Búsqueda Avanzada</button>
            </div>
            
            <div class="filter-section">
                <select id="genre-filter">
                    <option value="">Todos los géneros</option>
                    <!-- Géneros se cargan dinámicamente -->
                </select>
                
                <select id="artist-filter">
                    <option value="">Todos los artistas</option>
                    <!-- Artistas se cargan dinámicamente -->
                </select>
                
                <select id="sort-by">
                    <option value="title">Ordenar por Título</option>
                    <option value="artist">Ordenar por Artista</option>
                    <option value="album">Ordenar por Álbum</option>
                    <option value="date">Ordenar por Fecha</option>
                </select>
            </div>
            
            <div class="view-controls">
                <button id="grid-view" class="active">📱 Grid</button>
                <button id="list-view">📋 Lista</button>
                <button id="scan-library">🔄 Escanear Nueva Música</button>
            </div>
        </header>

        <!-- 📊 Estadísticas de Biblioteca -->
        <section class="library-stats">
            <div class="stat-card">
                <h3 id="total-songs">0</h3>
                <p>Canciones</p>
            </div>
            <div class="stat-card">
                <h3 id="total-artists">0</h3>
                <p>Artistas</p>
            </div>
            <div class="stat-card">
                <h3 id="total-albums">0</h3>
                <p>Álbumes</p>
            </div>
            <div class="stat-card">
                <h3 id="total-duration">0h 0m</h3>
                <p>Duración Total</p>
            </div>
        </section>

        <!-- 🎵 Grid/Lista de Canciones -->
        <main class="library-content">
            <div id="songs-container" class="songs-grid-view">
                <!-- Canciones se cargan dinámicamente -->
                <!-- Soporte para virtual scrolling en listas grandes -->
            </div>
            
            <!-- 📄 Paginación -->
            <div class="pagination">
                <button id="prev-page">◀️ Anterior</button>
                <span id="page-info">Página 1 de 1</span>
                <button id="next-page">Siguiente ▶️</button>
            </div>
        </main>

        <!-- 🎮 Mini Player (sticky) -->
        <footer class="mini-player">
            <div class="current-song-mini">
                <img id="mini-cover" src="/static/images/default-cover.png">
                <div class="song-info-mini">
                    <span id="mini-title">Sin reproducir</span>
                    <span id="mini-artist">-</span>
                </div>
            </div>
            
            <div class="mini-controls">
                <button id="mini-play-pause">▶️</button>
                <button id="mini-next">⏭️</button>
            </div>
            
            <div class="mini-progress">
                <input type="range" id="mini-progress-slider" min="0" max="100" value="0">
            </div>
        </footer>
    </div>

    <!-- JavaScript específico -->
    <script src="/static/js/config.js"></script>
    <script src="/static/js/api.js"></script>
    <script src="/static/js/library-page.js"></script>
</body>
</html>
```

### FUNCIONALIDADES AVANZADAS

#### 🔍 BÚSQUEDA Y FILTRADO
```html
<!-- Búsqueda en tiempo real -->
<input type="text" id="search-input" placeholder="🔍 Buscar...">

<!-- Filtros por categoría -->
<select id="genre-filter">    <!-- Por género -->
<select id="artist-filter">   <!-- Por artista -->
<select id="album-filter">    <!-- Por álbum -->

<!-- Ordenamiento -->
<select id="sort-by">         <!-- Múltiples criterios -->
```

#### 📱 VISTAS INTERCAMBIABLES
```html
<!-- Toggle entre vista grid y lista -->
<button id="grid-view">📱 Grid</button>    <!-- Cards con portadas -->
<button id="list-view">📋 Lista</button>    <!-- Lista compacta -->

<!-- CSS classes dinámicas -->
<div id="songs-container" class="songs-grid-view">  <!-- o songs-list-view -->
```

#### 📊 ESTADÍSTICAS EN TIEMPO REAL
```html
<section class="library-stats">
    <div class="stat-card">
        <h3 id="total-songs">0</h3>        <!-- Contador de canciones -->
        <p>Canciones</p>
    </div>
    <!-- Más estadísticas... -->
</section>
```

## 📄 index_backup.html - RESPALDO

### PROPÓSITO
**Backup seguro**: Versión anterior de index.html preservada para rollback

**Características**:
- Contiene versión funcional anterior
- Respaldo de features que funcionaban
- Punto de restauración en caso de problemas
- Referencia para comparar cambios

## 🔗 INTERCONEXIONES DE TEMPLATES

### 🌐 CON STATIC RESOURCES
```html
<!-- CSS Stylesheets -->
<link rel="stylesheet" href="/static/css/main.css">
<link rel="stylesheet" href="/static/css/components.css">
<link rel="stylesheet" href="/static/css/library.css">
<link rel="stylesheet" href="/static/css/visualizer.css">

<!-- JavaScript Modules -->
<script src="/static/js/config.js"></script>
<script src="/static/js/api.js"></script>
<script src="/static/js/app.js"></script>
<!-- etc... -->

<!-- Images -->
<img src="/static/images/default-cover.png">
<link rel="icon" href="/static/images/favicon.png">
```

### 🧠 CON BACKEND FLASK
```python
# Flask sirve estas plantillas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/library')
def library():
    return render_template('library.html')

# SPA Fallback - todas las rutas van a index.html
@app.errorhandler(404)
def not_found(error):
    return render_template('index.html')
```

### 📱 CON API REST
```javascript
// JavaScript en templates llama APIs
fetch('/api/player/status')          // Estado del reproductor
fetch('/api/library')                // Biblioteca musical
fetch('/api/player/play')            // Control de reproducción
```

### 🔄 CON WEBSOCKETS
```javascript
// Socket.IO client en templates
const socket = io();                 // Conexión WebSocket
socket.on('player_status_update');   // Eventos en tiempo real
socket.on('song_changed');           // Cambios de canción
```

## 🎨 DESIGN SYSTEM

### 🏗️ ESTRUCTURA CONSISTENTE
```html
<!-- Patrón de estructura común -->
<div class="container">
    <header class="section-header">
        <h2>Título de Sección</h2>
        <div class="section-actions">
            <!-- Botones de acción -->
        </div>
    </header>
    
    <main class="section-content">
        <!-- Contenido principal -->
    </main>
    
    <footer class="section-footer">
        <!-- Controles o paginación -->
    </footer>
</div>
```

### 🎨 COMPONENTES REUTILIZABLES
```html
<!-- Song Card Component -->
<div class="song-card" data-song-id="123">
    <img class="song-cover" src="cover.jpg">
    <div class="song-info">
        <h3 class="song-title">Título</h3>
        <p class="song-artist">Artista</p>
    </div>
    <div class="song-actions">
        <button class="play-btn">▶️</button>
        <button class="add-playlist-btn">➕</button>
    </div>
</div>

<!-- Button Component -->
<button class="btn btn-primary btn-icon" data-action="play">
    <i class="fas fa-play"></i>
    <span>Reproducir</span>
</button>
```

## ⚡ OPTIMIZACIONES

### 🚀 PERFORMANCE
```html
<!-- Lazy loading de imágenes -->
<img class="song-cover" data-src="cover.jpg" loading="lazy">

<!-- Preload de recursos críticos -->
<link rel="preload" href="/static/css/main.css" as="style">

<!-- DNS prefetch para recursos externos -->
<link rel="dns-prefetch" href="//cdnjs.cloudflare.com">
```

### 📱 MOBILE OPTIMIZATION
```html
<!-- Viewport optimizado -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">

<!-- Touch-friendly buttons -->
<button class="btn btn-touch">Botón</button>  <!-- min-height: 44px -->

<!-- Prevent zoom on inputs -->
<input type="text" style="font-size: 16px;">
```

### 🔍 SEO Y ACCESIBILIDAD
```html
<!-- Meta tags para SEO -->
<meta name="description" content="Reproductor Musical Profesional">
<meta name="keywords" content="música, reproductor, audio, playlist">

<!-- Accesibilidad -->
<button aria-label="Reproducir canción" title="Reproducir">▶️</button>
<img alt="Portada del álbum" src="cover.jpg">

<!-- Semantic HTML -->
<main role="main">
<nav role="navigation">
<section aria-labelledby="library-heading">
```

## 🔌 PUNTOS DE EXTENSIÓN

1. **Nuevas Páginas**: Crear templates adicionales
2. **Componentes**: Agregar nuevos elementos reutilizables
3. **Temas**: Sistema de themes con CSS variables
4. **PWA**: Manifest.json y service worker
5. **i18n**: Internacionalización de textos
6. **Accessibility**: Mejoras para lectores de pantalla

## ⚠️ CONSIDERACIONES

### 🔒 SEGURIDAD
- Sanitización de inputs del usuario
- CSP headers para prevenir XSS
- HTTPS en producción

### 📊 ANALYTICS
- Google Analytics o similar
- Tracking de uso de funcionalidades
- Métricas de performance

### 🌐 COMPATIBILIDAD
- Graceful degradation para navegadores antiguos
- Polyfills para features modernas
- Testing en múltiples navegadores
