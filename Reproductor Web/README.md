# 🎵 Music Player Pro - Versión Web

## 🌐 Interfaz Web Moderna

Music Player Pro ahora incluye una **interfaz web completamente nueva** desarrollada con Flask + HTML5 + WebSockets para una experiencia moderna y responsive.

## 🚀 Características Web

### ✨ Interfaz Moderna
- **Diseño Responsive**: Compatible con desktop, tablet y móvil
- **Tema Dark Cyberpunk**: Colores neón y efectos visuales modernos
- **Animaciones Smooth**: Transiciones suaves y efectos hover
- **Accesibilidad**: Soporte completo para lectores de pantalla

### 🎛️ Funcionalidades
- **Control en Tiempo Real**: WebSockets para actualizaciones instantáneas
- **Visualizador de Espectro**: Análisis visual en tiempo real del audio
- **Gestión de Biblioteca**: Explorar, buscar y organizar música
- **Listas de Reproducción**: Crear y gestionar playlists
- **Efectos Visuales**: Visualizaciones avanzadas del espectro de audio

### 📡 API REST
- **Endpoints Completos**: Control total vía HTTP API
- **WebSocket Events**: Comunicación bidireccional en tiempo real
- **CORS Habilitado**: Acceso desde diferentes dominios

## 🛠️ Instalación y Uso

### 1. Instalar Dependencias Web
```bash
pip install flask flask-socketio flask-cors python-socketio requests
```

O instalar todas las dependencias:
```bash
pip install -r requirements.txt
```

### 2. Ejecutar Versión Web

#### Opción A: Lanzador Web Dedicado (Recomendado)
```bash
python web_launcher.py
```

#### Opción B: Main.py (Migrado a Web)
```bash
python main.py
```

### 3. Acceder a la Interfaz
- **URL**: http://localhost:5000
- **Móvil**: Usar la misma URL desde tu dispositivo móvil
- **Navegador**: Se abre automáticamente

## 📱 Compatibilidad

### 🌐 Navegadores Soportados
- ✅ Chrome/Chromium (Recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Edge
- ✅ Navegadores móviles

### 📊 Dispositivos
- 🖥️ **Desktop**: Experiencia completa
- 📱 **Móvil**: Interfaz táctil optimizada
- 📟 **Tablet**: Layout adaptativo

## 🎯 Arquitectura Web

```
src/web/
├── flask_app.py          # Servidor Flask principal
├── templates/
│   └── index.html        # Interfaz HTML5
└── static/
    ├── css/
    │   ├── main.css      # Estilos principales
    │   ├── components.css # Componentes UI
    │   └── visualizer.css # Visualizador
    └── js/
        ├── app.js        # Aplicación principal
        ├── api.js        # Cliente API REST
        ├── websocket.js  # Comunicación WebSocket
        ├── visualizer.js # Espectro visual
        ├── library.js    # Gestión biblioteca
        ├── player-controls.js # Controles
        ├── ui.js         # Utilidades UI
        └── config.js     # Configuración
```

## 🔧 API Endpoints

### 🎵 Control de Reproducción
- `GET /api/player/status` - Estado actual
- `POST /api/player/play` - Reproducir
- `POST /api/player/pause` - Pausar
- `POST /api/player/stop` - Detener
- `POST /api/player/volume` - Ajustar volumen

### 📚 Biblioteca Musical
- `GET /api/library/songs` - Obtener canciones
- `POST /api/library/scan` - Escanear biblioteca
- `GET /api/library/search` - Buscar música

### 📡 WebSocket Events
- `player_state` - Estado del reproductor
- `spectrum_data` - Datos del espectro
- `library_updated` - Biblioteca actualizada

## 🎨 Personalización

### Temas
Los estilos CSS están organizados con variables CSS para fácil personalización:

```css
:root {
  --primary-color: #00ff41;
  --secondary-color: #ff0080;
  --bg-color: #0a0a0a;
  --text-color: #ffffff;
}
```

### Componentes
La interfaz está dividida en componentes modulares:
- **Sidebar**: Navegación principal
- **Library**: Explorador de música
- **Player**: Controles de reproducción
- **Visualizer**: Efectos visuales
- **Settings**: Configuración

## 🔄 Migración desde CustomTkinter

La versión web **reemplaza completamente** la interfaz CustomTkinter manteniendo toda la funcionalidad:

### ✅ Migrado
- ✅ Reproductor de audio VLC
- ✅ Gestión de biblioteca
- ✅ Visualizador de espectro
- ✅ Base de datos SQLite
- ✅ Sistema de configuración
- ✅ Efectos visuales
- ✅ IA musical

### 🆕 Mejorado
- 🆕 Interfaz responsive moderna
- 🆕 Acceso desde móviles
- 🆕 WebSocket tiempo real
- 🆕 API REST completa
- 🆕 Mejor rendimiento
- 🆕 Tema cyberpunk

## 🚨 Troubleshooting

### Puerto en Uso
Si el puerto 5000 está ocupado:
```bash
python web_launcher.py --port 8080
```

### VLC No Encontrado
Asegúrate de tener VLC Media Player instalado:
- Windows: https://www.videolan.org/vlc/
- Linux: `sudo apt install vlc`
- macOS: `brew install --cask vlc`

### Problemas de CORS
Si accedes desde otro dominio, el CORS está habilitado por defecto.

## 📞 Soporte

- 📧 **Issues**: Reportar problemas en GitHub
- 📖 **Docs**: Documentación completa en `/docs`
- 💬 **Community**: Únete a nuestro Discord

---

🎵 **Music Player Pro Web** - La evolución del reproductor musical hacia la web moderna.
