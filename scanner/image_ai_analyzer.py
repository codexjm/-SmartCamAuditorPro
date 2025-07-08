#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo de análisis de imágenes con IA para SmartCam Auditor

Proporciona funciones para analizar streams RTSP y detectar objetos usando YOLO.
Módulo independiente que puede ser importado desde otros componentes.
"""

import os
import time
import datetime
from typing import Dict, List, Optional, Union

# Importaciones para análisis de video con IA
try:
    import cv2
    from ultralytics import YOLO
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

def analizar_rtsp(rtsp_url: str, output_dir: str = "scanner/detecciones", 
                  config: Optional[Dict] = None) -> Optional[str]:
    """
    Analiza un stream RTSP usando YOLO para detección de objetos
    
    Args:
        rtsp_url (str): URL del stream RTSP (ej: rtsp://admin:admin@192.168.1.10:554)
        output_dir (str): Directorio donde guardar las detecciones
        config (dict, optional): Configuración adicional para el análisis
    
    Returns:
        str: Ruta del archivo de imagen guardado si es exitoso, None si falla
    
    Example:
        imagen = analizar_rtsp("rtsp://admin:admin@192.168.1.10:554")
        if imagen:
            print(f"Análisis completado: {imagen}")
    """
    if not AI_AVAILABLE:
        print("❌ OpenCV y/o ultralytics no están disponibles")
        print("💡 Instalar con: pip install opencv-python ultralytics")
        return None
    
    # Configuración por defecto
    default_config = {
        'confidence_threshold': 0.5,
        'yolo_model': 'yolov8n.pt',
        'timeout': 10,
        'max_attempts': 3,
        'enable_logging': True
    }
    
    if config:
        default_config.update(config)
    
    config = default_config
    
    # Crear directorio de salida
    os.makedirs(output_dir, exist_ok=True)
    
    if config['enable_logging']:
        print(f"🎥 [IA] Conectando a {rtsp_url}")
    
    try:
        # Intentos múltiples para conexión más robusta
        cap = None
        for attempt in range(config['max_attempts']):
            if config['enable_logging'] and attempt > 0:
                print(f"🔄 [IA] Intento {attempt + 1}/{config['max_attempts']}")
            
            # Configurar captura de video con timeout
            cap = cv2.VideoCapture(rtsp_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reducir buffer para menor latencia
            
            # Configurar timeout si está disponible en esta versión de OpenCV
            try:
                cap.set(cv2.CAP_PROP_TIMEOUT, config['timeout'] * 1000)  # Timeout en ms
            except AttributeError:
                # CAP_PROP_TIMEOUT no disponible en esta versión de OpenCV
                pass
            
            # Verificar conexión
            if cap.isOpened():
                # Intentar capturar frame
                ret, frame = cap.read()
                if ret and frame is not None:
                    break
                else:
                    cap.release()
                    if attempt < config['max_attempts'] - 1:
                        time.sleep(1)  # Esperar antes del siguiente intento
            else:
                if attempt < config['max_attempts'] - 1:
                    time.sleep(1)
        
        if not cap or not cap.isOpened():
            if config['enable_logging']:
                print(f"❌ [IA] No se pudo acceder a la cámara: {rtsp_url}")
            return None
        
        # Capturar frame final
        ret, frame = cap.read()
        cap.release()
        
        if not ret or frame is None:
            if config['enable_logging']:
                print(f"❌ [IA] No se pudo capturar imagen del stream")
            return None
        
        if config['enable_logging']:
            print(f"✅ [IA] Frame capturado exitosamente ({frame.shape[1]}x{frame.shape[0]})")
        
        # Cargar modelo YOLO
        if config['enable_logging']:
            print(f"🧠 [IA] Cargando modelo YOLO ({config['yolo_model']})...")
        
        try:
            modelo = YOLO(config['yolo_model'])
        except Exception as e:
            if config['enable_logging']:
                print(f"📥 [IA] Descargando modelo YOLO por primera vez...")
            modelo = YOLO(config['yolo_model'])
        
        # Realizar detección
        if config['enable_logging']:
            print(f"🔍 [IA] Analizando imagen con IA...")
        
        start_time = time.time()
        resultados = modelo.predict(frame, conf=config['confidence_threshold'], verbose=False)
        analysis_time = time.time() - start_time
        
        # Extraer información de detecciones
        detecciones = []
        if len(resultados) > 0:
            boxes = resultados[0].boxes
            if boxes is not None:
                for box in boxes:
                    # Obtener datos de la detección
                    xyxy = box.xyxy[0].tolist()  # Coordenadas
                    conf = float(box.conf[0])    # Confianza
                    cls = int(box.cls[0])        # Clase
                    
                    # Nombre de la clase
                    class_name = modelo.names[cls]
                    
                    detecciones.append({
                        'objeto': class_name,
                        'confianza': round(conf, 2),
                        'coordenadas': {
                            'x1': int(xyxy[0]),
                            'y1': int(xyxy[1]),
                            'x2': int(xyxy[2]),
                            'y2': int(xyxy[3])
                        }
                    })
        
        # Generar nombre de archivo único
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ip_clean = rtsp_url.replace('rtsp://', '').replace(':', '_').replace('/', '_').replace('@', '_at_')
        nombre_archivo = os.path.join(output_dir, f"ia_deteccion_{ip_clean}_{timestamp}.jpg")
        
        # Guardar imagen con detecciones
        if len(resultados) > 0 and detecciones:
            # Guardar con bounding boxes
            resultados[0].save(filename=nombre_archivo)
        else:
            # Guardar frame original si no hay detecciones
            cv2.imwrite(nombre_archivo, frame)
        
        # Log de resultados
        if config['enable_logging']:
            print(f"✅ [IA] Análisis completado en {analysis_time:.2f}s:")
            print(f"   📸 Imagen guardada: {nombre_archivo}")
            print(f"   🎯 Objetos detectados: {len(detecciones)}")
            
            if detecciones:
                objetos_unicos = list(set([d['objeto'] for d in detecciones]))
                print(f"   📋 Tipos de objetos: {', '.join(objetos_unicos)}")
                
                # Detalles de detecciones importantes
                personas = [d for d in detecciones if d['objeto'] == 'person']
                vehiculos = [d for d in detecciones if d['objeto'] in ['car', 'truck', 'bus', 'motorcycle']]
                
                if personas:
                    print(f"   👥 Personas detectadas: {len(personas)}")
                if vehiculos:
                    print(f"   🚗 Vehículos detectados: {len(vehiculos)}")
        
        return nombre_archivo
        
    except Exception as e:
        if config['enable_logging']:
            print(f"❌ [IA] Error durante el análisis: {str(e)}")
        return None

def analizar_rtsp_detallado(rtsp_url: str, output_dir: str = "scanner/detecciones", 
                           config: Optional[Dict] = None) -> Dict:
    """
    Versión detallada del análisis RTSP que retorna información completa
    
    Args:
        rtsp_url (str): URL del stream RTSP
        output_dir (str): Directorio donde guardar las detecciones
        config (dict, optional): Configuración adicional
    
    Returns:
        dict: Información detallada del análisis
    """
    if not AI_AVAILABLE:
        return {
            'success': False,
            'error': 'Módulos de IA no disponibles',
            'detalle': 'Instalar con: pip install opencv-python ultralytics'
        }
    
    # Configuración por defecto
    default_config = {
        'confidence_threshold': 0.5,
        'yolo_model': 'yolov8n.pt',
        'timeout': 10,
        'max_attempts': 3,
        'enable_logging': True,
        'save_image': True
    }
    
    if config:
        default_config.update(config)
    
    config = default_config
    
    start_time = time.time()
    
    try:
        # Usar la función principal para obtener la imagen
        imagen_path = analizar_rtsp(rtsp_url, output_dir, config)
        
        if not imagen_path:
            return {
                'success': False,
                'error': 'No se pudo analizar el stream RTSP',
                'rtsp_url': rtsp_url
            }
        
        # Cargar imagen para análisis adicional
        image = cv2.imread(imagen_path)
        if image is None:
            return {
                'success': False,
                'error': 'No se pudo cargar la imagen guardada',
                'imagen_path': imagen_path
            }
        
        # Realizar análisis detallado
        modelo = YOLO(config['yolo_model'])
        resultados = modelo.predict(image, conf=config['confidence_threshold'], verbose=False)
        
        # Extraer información detallada
        detecciones = []
        if len(resultados) > 0:
            boxes = resultados[0].boxes
            if boxes is not None:
                for box in boxes:
                    xyxy = box.xyxy[0].tolist()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = modelo.names[cls]
                    
                    detecciones.append({
                        'objeto': class_name,
                        'confianza': round(conf, 2),
                        'coordenadas': {
                            'x1': int(xyxy[0]),
                            'y1': int(xyxy[1]),
                            'x2': int(xyxy[2]),
                            'y2': int(xyxy[3])
                        },
                        'area': (int(xyxy[2]) - int(xyxy[0])) * (int(xyxy[3]) - int(xyxy[1]))
                    })
        
        # Análisis de seguridad
        personas = [d for d in detecciones if d['objeto'] == 'person']
        vehiculos = [d for d in detecciones if d['objeto'] in ['car', 'truck', 'bus', 'motorcycle']]
        objetos_sospechosos = [d for d in detecciones if d['objeto'] in ['knife', 'gun']]
        
        analysis_time = time.time() - start_time
        
        return {
            'success': True,
            'rtsp_url': rtsp_url,
            'imagen_guardada': imagen_path,
            'detecciones': detecciones,
            'total_objetos': len(detecciones),
            'objetos_unicos': list(set([d['objeto'] for d in detecciones])),
            'personas_detectadas': len(personas),
            'vehiculos_detectados': len(vehiculos),
            'objetos_sospechosos': len(objetos_sospechosos),
            'alerta_seguridad': len(personas) > 0 or len(objetos_sospechosos) > 0,
            'resolucion': f"{image.shape[1]}x{image.shape[0]}",
            'tiempo_analisis': round(analysis_time, 2),
            'timestamp': datetime.datetime.now().isoformat(),
            'modelo_usado': config['yolo_model'],
            'umbral_confianza': config['confidence_threshold']
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Error en análisis detallado: {str(e)}',
            'rtsp_url': rtsp_url,
            'tiempo_analisis': time.time() - start_time
        }

def analizar_multiples_rtsp(urls_rtsp: List[str], output_dir: str = "scanner/detecciones",
                           config: Optional[Dict] = None) -> List[Dict]:
    """
    Analiza múltiples streams RTSP
    
    Args:
        urls_rtsp (list): Lista de URLs RTSP a analizar
        output_dir (str): Directorio donde guardar las detecciones
        config (dict, optional): Configuración adicional
    
    Returns:
        list: Lista de resultados de análisis
    """
    if not AI_AVAILABLE:
        return [{
            'success': False,
            'error': 'Módulos de IA no disponibles',
            'url': url
        } for url in urls_rtsp]
    
    resultados = []
    
    default_config = {
        'enable_logging': True,
        'delay_between_analysis': 1.0  # Pausa entre análisis
    }
    
    if config:
        default_config.update(config)
    
    config = default_config
    
    if config['enable_logging']:
        print(f"🎬 [IA] Analizando {len(urls_rtsp)} streams RTSP...")
    
    for i, url in enumerate(urls_rtsp, 1):
        if config['enable_logging']:
            print(f"\n🎯 [IA] Analizando stream {i}/{len(urls_rtsp)}: {url}")
        
        resultado = analizar_rtsp_detallado(url, output_dir, config)
        resultado['orden_analisis'] = i
        resultados.append(resultado)
        
        # Pausa entre análisis para evitar sobrecargar el sistema
        if i < len(urls_rtsp) and config['delay_between_analysis'] > 0:
            time.sleep(config['delay_between_analysis'])
    
    # Resumen final
    if config['enable_logging']:
        exitosos = len([r for r in resultados if r['success']])
        total_detecciones = sum([r.get('total_objetos', 0) for r in resultados if r['success']])
        
        print(f"\n📊 [IA] RESUMEN DEL ANÁLISIS MASIVO:")
        print(f"   🎯 Streams analizados: {len(urls_rtsp)}")
        print(f"   ✅ Análisis exitosos: {exitosos}")
        print(f"   ❌ Fallos: {len(urls_rtsp) - exitosos}")
        print(f"   🎯 Total objetos detectados: {total_detecciones}")
        
        # Alertas de seguridad
        alertas = len([r for r in resultados if r.get('alerta_seguridad')])
        if alertas > 0:
            print(f"   🚨 Streams con alertas de seguridad: {alertas}")
    
    return resultados

def verificar_disponibilidad_ia() -> Dict:
    """
    Verifica la disponibilidad de los módulos de IA
    
    Returns:
        dict: Estado de disponibilidad de los módulos
    """
    estado = {
        'ai_disponible': AI_AVAILABLE,
        'opencv_disponible': False,
        'ultralytics_disponible': False,
        'version_opencv': None,
        'modelos_yolo_disponibles': []
    }
    
    try:
        import cv2
        estado['opencv_disponible'] = True
        estado['version_opencv'] = cv2.__version__
    except ImportError:
        pass
    
    try:
        from ultralytics import YOLO
        estado['ultralytics_disponible'] = True
        
        # Verificar modelos YOLO comunes
        modelos_comunes = ['yolov8n.pt', 'yolov8s.pt', 'yolov8m.pt', 'yolov8l.pt']
        for modelo in modelos_comunes:
            try:
                YOLO(modelo)
                estado['modelos_yolo_disponibles'].append(modelo)
            except:
                pass
                
    except ImportError:
        pass
    
    return estado

# Función de compatibilidad con el código anterior
def analizar_stream_rtsp(rtsp_url: str, output_dir: str = "scanner/detecciones") -> Optional[str]:
    """
    Función de compatibilidad - alias para analizar_rtsp
    """
    return analizar_rtsp(rtsp_url, output_dir)
