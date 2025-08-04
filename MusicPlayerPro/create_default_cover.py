# -*- coding: utf-8 -*-
"""
Script para crear imagen de carátula por defecto
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Crear imagen de 200x200 con fondo gradiente
    size = (200, 200)
    image = Image.new('RGB', size, '#1a1a2e')
    draw = ImageDraw.Draw(image)
    
    # Crear gradiente simple
    for i in range(size[1]):
        r = int(26 + (57 - 26) * i / size[1])  # De #1a1a2e a #16213e
        g = int(26 + (33 - 26) * i / size[1])
        b = int(46 + (62 - 46) * i / size[1])
        color = (r, g, b)
        draw.line([(0, i), (size[0], i)], fill=color)
    
    # Dibujar icono musical simple
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # Nota musical grande
    draw.ellipse([center_x - 30, center_y - 10, center_x - 10, center_y + 10], 
                fill='#e94560', outline='#fff', width=2)
    draw.rectangle([center_x - 12, center_y - 40, center_x - 8, center_y - 10], 
                  fill='#e94560')
    draw.ellipse([center_x - 15, center_y - 45, center_x - 5, center_y - 35], 
                fill='#e94560')
    
    # Nota musical pequeña
    draw.ellipse([center_x + 10, center_y - 5, center_x + 25, center_y + 10], 
                fill='#0f4c75', outline='#fff', width=1)
    draw.rectangle([center_x + 23, center_y - 25, center_x + 26, center_y - 5], 
                  fill='#0f4c75')
    
    # Guardar imagen
    output_path = "static/images/default-cover.png"
    image.save(output_path)
    print(f"✅ Imagen por defecto creada: {output_path}")
    
except ImportError:
    print("⚠️ PIL no disponible, creando archivo placeholder...")
    # Crear archivo vacío como placeholder
    os.makedirs("static/images", exist_ok=True)
    with open("static/images/default-cover.png", "wb") as f:
        # Crear PNG mínimo válido (1x1 pixel transparente)
        png_data = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # Width & height = 1
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # Bit depth, color, CRC
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # Compressed data
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # 
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
            0x42, 0x60, 0x82
        ])
        f.write(png_data)
    print("✅ Archivo placeholder creado: static/images/default-cover.png")
except Exception as e:
    print(f"❌ Error creando imagen: {e}")
