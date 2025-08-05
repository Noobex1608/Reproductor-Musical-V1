// 🔧 FIX DEFINITIVO PARA SHUFFLE & REPEAT
// =======================================
// Este script se ejecuta después de que la página principal carga

console.log('🔧 === INICIANDO FIX DE SHUFFLE & REPEAT ===');

// Esperar a que todo esté cargado
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ DOM Content Loaded - Iniciando fix...');
    
    // Esperar un poco más para asegurar que todo esté inicializado
    setTimeout(function() {
        setupShuffleRepeatFix();
    }, 2000);
});

function setupShuffleRepeatFix() {
    console.log('🔧 Configurando fix de shuffle y repeat...');
    
    // Buscar los botones
    const shuffleBtn = document.getElementById('shuffle-btn');
    const repeatBtn = document.getElementById('repeat-btn');
    
    console.log('🔀 Botón shuffle encontrado:', shuffleBtn ? '✅' : '❌');
    console.log('🔁 Botón repeat encontrado:', repeatBtn ? '✅' : '❌');
    
    if (!shuffleBtn || !repeatBtn) {
        console.error('❌ No se encontraron los botones. Reintentando en 2 segundos...');
        setTimeout(setupShuffleRepeatFix, 2000);
        return;
    }
    
    // REMOVER todos los event listeners existentes clonando los elementos
    const newShuffleBtn = shuffleBtn.cloneNode(true);
    const newRepeatBtn = repeatBtn.cloneNode(true);
    shuffleBtn.parentNode.replaceChild(newShuffleBtn, shuffleBtn);
    repeatBtn.parentNode.replaceChild(newRepeatBtn, repeatBtn);
    
    console.log('🔄 Botones clonados para limpiar event listeners...');
    
    // AGREGAR nuevos event listeners
    newShuffleBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔀 ¡CLICK EN SHUFFLE DETECTADO!');
        handleShuffleClick();
    });
    
    newRepeatBtn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('🔁 ¡CLICK EN REPEAT DETECTADO!');
        handleRepeatClick();
    });
    
    console.log('✅ Event listeners agregados correctamente');
    
    // Sincronizar estado inicial
    syncInitialState();
}

async function handleShuffleClick() {
    console.log('🔀 === EJECUTANDO SHUFFLE ===');
    
    try {
        console.log('🔀 Enviando request a /api/player/shuffle...');
        
        const response = await fetch('/api/player/shuffle', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('🔀 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('🔀 Response data:', data);
        
        if (data.success) {
            updateShuffleButton(data.shuffle_enabled || data.shuffle);
            showNotification('🔀 ' + data.message, 'success');
        } else {
            showNotification('❌ Error: ' + (data.message || 'Error al cambiar shuffle'), 'error');
        }
        
    } catch (error) {
        console.error('🔀 ERROR:', error);
        showNotification('❌ Error de conexión: ' + error.message, 'error');
    }
}

async function handleRepeatClick() {
    console.log('🔁 === EJECUTANDO REPEAT ===');
    
    try {
        console.log('🔁 Enviando request a /api/player/repeat...');
        
        const response = await fetch('/api/player/repeat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        console.log('🔁 Response status:', response.status);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('🔁 Response data:', data);
        
        if (data.status === 'success' || data.success) {
            updateRepeatButton(data.repeat_mode || data.repeat);
            showNotification('🔁 ' + data.message, 'success');
        } else {
            showNotification('❌ Error: ' + (data.message || 'Error al cambiar repeat'), 'error');
        }
        
    } catch (error) {
        console.error('🔁 ERROR:', error);
        showNotification('❌ Error de conexión: ' + error.message, 'error');
    }
}

function updateShuffleButton(isEnabled) {
    const shuffleBtn = document.getElementById('shuffle-btn');
    if (!shuffleBtn) return;
    
    console.log('🎨 Actualizando botón shuffle:', isEnabled);
    
    if (isEnabled) {
        shuffleBtn.classList.add('active');
        shuffleBtn.style.color = '#ff6b6b';
        shuffleBtn.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
    } else {
        shuffleBtn.classList.remove('active');
        shuffleBtn.style.color = '';
        shuffleBtn.style.backgroundColor = '';
    }
}

function updateRepeatButton(mode) {
    const repeatBtn = document.getElementById('repeat-btn');
    if (!repeatBtn) return;
    
    console.log('🎨 Actualizando botón repeat:', mode);
    
    repeatBtn.classList.remove('active');
    
    const icon = repeatBtn.querySelector('i');
    if (!icon) return;
    
    switch (mode) {
        case 'one':
            repeatBtn.classList.add('active');
            repeatBtn.style.color = '#ff6b6b';
            repeatBtn.style.backgroundColor = 'rgba(255, 107, 107, 0.1)';
            icon.className = 'fas fa-redo';
            break;
        case 'all':
            repeatBtn.classList.add('active');
            repeatBtn.style.color = '#4FC3F7';
            repeatBtn.style.backgroundColor = 'rgba(79, 195, 247, 0.1)';
            icon.className = 'fas fa-redo';
            break;
        default:
            repeatBtn.style.color = '';
            repeatBtn.style.backgroundColor = '';
            icon.className = 'fas fa-redo';
            break;
    }
}

async function syncInitialState() {
    console.log('🔄 Sincronizando estado inicial...');
    
    try {
        const response = await fetch('/api/player/state');
        const data = await response.json();
        
        if (data.success) {
            console.log('📊 Estado inicial obtenido:', data);
            updateShuffleButton(data.shuffle);
            updateRepeatButton(data.repeat);
        }
    } catch (error) {
        console.error('❌ Error obteniendo estado inicial:', error);
    }
}

function showNotification(message, type = 'info') {
    console.log('📢 Notification:', message);
    
    // Crear notificación simple
    const notification = document.createElement('div');
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        border-radius: 4px;
        z-index: 10000;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        font-family: Arial, sans-serif;
        font-size: 14px;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remover después de 3 segundos
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Funciones globales para testing manual
window.testShuffleFix = function() {
    console.log('🧪 Test manual de shuffle...');
    handleShuffleClick();
};

window.testRepeatFix = function() {
    console.log('🧪 Test manual de repeat...');
    handleRepeatClick();
};

console.log('✅ Fix de shuffle y repeat cargado. Usa testShuffleFix() y testRepeatFix() para probar manualmente.');
