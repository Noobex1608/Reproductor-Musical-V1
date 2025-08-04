# -*- coding: utf-8 -*-
"""
MUSIC PLAYER PRO - MAIN APPLICATION (WEB VERSION)
================================================
Reproductor musical web de próxima generación con:
- Motor de audio VLC profesional
- Interfaz web moderna (Flask + HTML5)
- WebSockets para tiempo real
- Visualizador de espectro avanzado
- IA para recomendaciones
- API REST completa
- Base de datos SQLite
"""

import sys
import os

# Configurar codificación para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importaciones principales
from src.core.app import MusicPlayerProApp
from src.core.config_manager import ConfigManager
from src.core.database import DatabaseManager
from src.audio.vlc_engine import VLCAudioEngine
from src.web.flask_app import MusicPlayerWebApp  # Cambiado: usar web app en lugar de UI
from src.effects.visual_manager import VisualEffectsManager
from src.ai.music_ai import MusicAI

# Librerías estándar
import asyncio
import threading
from pathlib import Path
import logging
import webbrowser
import time

# Configurar logging avanzado sin caracteres especiales
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('music_player_pro.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica e instala dependencias críticas automáticamente"""
    critical_deps = [
        'vlc', 'librosa', 'numpy', 'matplotlib', 'sqlalchemy', 
        'PIL', 'flask', 'flask_socketio', 'requests'  # Agregadas dependencias web
    ]
    
    missing_deps = []
    
    for dep in critical_deps:
        try:
            if dep == 'PIL':
                __import__('PIL.Image')
            elif dep == 'flask_socketio':
                __import__('flask_socketio')
            else:
                __import__(dep)
        except ImportError:
            missing_deps.append(dep)
    
    if missing_deps:
        logger.warning(f"Dependencias faltantes: {missing_deps}")
        print(">>> Instalando dependencias automaticamente...")
        
        import subprocess
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ])
            print(">>> Dependencias instaladas correctamente")
        except subprocess.CalledProcessError:
            print("ERROR instalando dependencias. Ejecuta manualmente:")
            print("pip install -r requirements.txt")
            return False
    
    return True

def initialize_directories():
    """Inicializa directorios necesarios"""
    directories = [
        'data', 'cache', 'logs', 'playlists', 
        'themes', 'plugins', 'covers'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

def main():
    """Función principal - Versión Web"""
    try:
        print("MUSIC PLAYER PRO - WEB VERSION")
        print("=" * 50)
        
        # Verificar dependencias
        if not check_dependencies():
            return
        
        # Inicializar directorios
        initialize_directories()
        
        # Función para inicializar componentes async
        async def init_components():
            logger.info("Inicializando componentes del sistema...")
            
            # 1. Gestor de configuración
            config_manager = ConfigManager()
            await config_manager.load_config()
            
            # 2. Base de datos
            db_manager = DatabaseManager()
            await db_manager.initialize()
            
            # 3. Motor de audio VLC
            audio_engine = VLCAudioEngine()
            await audio_engine.initialize()
            
            # 4. Gestor de efectos visuales
            visual_manager = VisualEffectsManager()
            await visual_manager.initialize()
            
            # 5. IA musical
            music_ai = MusicAI()
            await music_ai.initialize()
            
            # 6. Aplicación principal (versión web integrada)
            app = MusicPlayerProApp(
                config_manager=config_manager,
                db_manager=db_manager,
                audio_engine=audio_engine,
                visual_manager=visual_manager,
                music_ai=music_ai
            )
            
            return app
        
        # Inicializar componentes
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        app = loop.run_until_complete(init_components())
        
        # 7. Aplicación Web Flask
        web_app = MusicPlayerWebApp(app)
        
        logger.info("Todos los componentes inicializados correctamente")
        print(">>> Music Player Pro Web listo!")
        print(">>> Disfruta de la experiencia musical web del futuro")
        print(">>> Iniciando servidor web...")
        
        # Ejecutar aplicación backend en thread separado
        app_thread = threading.Thread(target=lambda: loop.run_until_complete(app.run()))
        app_thread.daemon = True
        app_thread.start()
        
        # Abrir navegador automáticamente
        def open_browser():
            time.sleep(2)
            webbrowser.open('http://localhost:5000')
        
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Ejecutar servidor Flask (bloqueante)
        web_app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        logger.error(f"Error critico en la aplicacion: {e}")
        print(f"ERROR CRITICO: {e}")
        raise

def run_app():
    """Ejecuta la aplicación con manejo de eventos"""
    try:
        # Ejecutar aplicación principal
        main()
        
    except KeyboardInterrupt:
        print("\n>>> Cerrando Music Player Pro...")
        logger.info("Aplicación cerrada por el usuario")
    except Exception as e:
        logger.error(f"Error en la ejecucion: {e}")
        print(f"ERROR: {e}")
    finally:
        # Limpieza de seguridad al cerrar (solo recursos, no biblioteca)
        try:
            print("🧹 Cerrando recursos...")
            print("✅ Aplicación cerrada correctamente")
            # NOTA: La biblioteca musical se mantiene para preservar metadatos
                
        except Exception as e:
            print(f"⚠️ Error en limpieza final: {e}")
            pass

if __name__ == "__main__":
    run_app()
