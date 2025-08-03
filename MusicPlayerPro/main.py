# -*- coding: utf-8 -*-
"""
MUSIC PLAYER PRO - MAIN APPLICATION
===================================
Reproductor musical de próxima generación con:
- Motor de audio VLC profesional
- Visualizador de espectro en 3D
- IA para recomendaciones
- Efectos visuales avanzados
- Control gestual
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
from src.ui.main_window import MainWindow
from src.effects.visual_manager import VisualEffectsManager
from src.ai.music_ai import MusicAI

# Librerías estándar
import asyncio
import threading
from pathlib import Path
import logging

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
        'vlc', 'customtkinter', 'librosa', 'numpy', 
        'matplotlib', 'sqlalchemy', 'PIL'
    ]
    
    missing_deps = []
    
    for dep in critical_deps:
        try:
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
    """Función principal"""
    try:
        print("MUSIC PLAYER PRO - Iniciando...")
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
            
            # 6. Aplicación principal
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
        
        # 7. Ventana principal
        main_window = MainWindow(app)
        
        logger.info("Todos los componentes inicializados correctamente")
        print(">>> Music Player Pro listo!")
        print(">>> Disfruta de la experiencia musical del futuro")
        print(">>> Abriendo interfaz grafica...")
        
        # Ejecutar aplicación en thread separado
        import threading
        app_thread = threading.Thread(target=lambda: loop.run_until_complete(app.run()))
        app_thread.daemon = True
        app_thread.start()
        
        # Ejecutar UI en hilo principal (requerido por tkinter)
        main_window.run()
        
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
        # Limpieza
        try:
            pass
        except:
            pass

if __name__ == "__main__":
    run_app()
