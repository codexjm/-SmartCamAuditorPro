#!/usr/bin/env python3
"""
Módulo shodan_local - Base de datos local para almacenar información de dispositivos IoT
Simula funcionalidad de Shodan pero con datos locales almacenados en SQLite
"""

import sqlite3
import json
import datetime
import os
from typing import List, Dict, Optional

class ShodanLocal:
    """
    Clase para gestionar una base de datos local de dispositivos IoT
    Similar a Shodan pero con datos recopilados localmente
    """
    
    def __init__(self, db_path="scanner/shodan_local.db"):
        """
        Inicializa la base de datos local
        
        Args:
            db_path (str): Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.crear_base_datos()
    
    def crear_base_datos(self):
        """
        Crea las tablas necesarias para la base de datos local
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Tabla principal de dispositivos
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS dispositivos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        ip TEXT UNIQUE NOT NULL,
                        puerto INTEGER,
                        protocolo TEXT,
                        servicio TEXT,
                        banner TEXT,
                        version TEXT,
                        fabricante TEXT,
                        modelo TEXT,
                        device_type TEXT,
                        vulnerabilidades TEXT,  -- JSON string
                        fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        activo BOOLEAN DEFAULT 1,
                        confianza INTEGER DEFAULT 0,
                        puertos_abiertos TEXT,  -- JSON string
                        coordenadas TEXT,  -- JSON string para lat/lng si está disponible
                        asn TEXT,
                        organizacion TEXT,
                        pais TEXT,
                        ciudad TEXT,
                        notas TEXT
                    )
                ''')
                
                # Tabla de servicios por dispositivo
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS servicios (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dispositivo_id INTEGER,
                        puerto INTEGER,
                        protocolo TEXT,
                        servicio TEXT,
                        version TEXT,
                        banner TEXT,
                        ssl_info TEXT,  -- JSON string
                        fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (dispositivo_id) REFERENCES dispositivos (id)
                    )
                ''')
                
                # Tabla de vulnerabilidades
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS vulnerabilidades (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        dispositivo_id INTEGER,
                        cve_id TEXT,
                        descripcion TEXT,
                        severidad TEXT,
                        cvss_score REAL,
                        exploit_disponible BOOLEAN DEFAULT 0,
                        fecha_deteccion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        verificado BOOLEAN DEFAULT 0,
                        FOREIGN KEY (dispositivo_id) REFERENCES dispositivos (id)
                    )
                ''')
                
                # Tabla de escaneos históricos
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS escaneos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha_inicio TIMESTAMP,
                        fecha_fin TIMESTAMP,
                        rango_red TEXT,
                        dispositivos_encontrados INTEGER,
                        vulnerabilidades_encontradas INTEGER,
                        tipo_escaneo TEXT,
                        notas TEXT
                    )
                ''')
                
                # Índices para mejorar rendimiento
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_dispositivos_ip ON dispositivos(ip)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_dispositivos_activo ON dispositivos(activo)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_servicios_puerto ON servicios(puerto)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_vulnerabilidades_cve ON vulnerabilidades(cve_id)')
                
                conn.commit()
                print("✅ Base de datos local creada exitosamente")
                print(f"📁 Ubicación: {self.db_path}")
                
        except Exception as e:
            print(f"❌ Error creando base de datos: {e}")
            raise
    
    def agregar_dispositivo(self, ip: str, device_data: Dict) -> int:
        """
        Agrega o actualiza un dispositivo en la base de datos
        
        Args:
            ip (str): Dirección IP del dispositivo
            device_data (dict): Datos del dispositivo
        
        Returns:
            int: ID del dispositivo en la base de datos
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Verificar si el dispositivo ya existe
                cursor.execute('SELECT id FROM dispositivos WHERE ip = ?', (ip,))
                existing = cursor.fetchone()
                
                # Preparar datos para inserción/actualización
                puertos_json = json.dumps(device_data.get('open_ports', []))
                vulnerabilidades_json = json.dumps(device_data.get('cves_found', []))
                
                if existing:
                    # Actualizar dispositivo existente
                    device_id = existing[0]
                    cursor.execute('''
                        UPDATE dispositivos SET
                            device_type = ?, fabricante = ?, modelo = ?,
                            puertos_abiertos = ?, vulnerabilidades = ?,
                            ultima_actualizacion = CURRENT_TIMESTAMP,
                            confianza = ?, activo = 1
                        WHERE id = ?
                    ''', (
                        device_data.get('device_type', ''),
                        device_data.get('fabricante', ''),
                        device_data.get('modelo', ''),
                        puertos_json,
                        vulnerabilidades_json,
                        device_data.get('confidence', 0),
                        device_id
                    ))
                    print(f"📝 Dispositivo {ip} actualizado en base de datos")
                else:
                    # Insertar nuevo dispositivo
                    cursor.execute('''
                        INSERT INTO dispositivos (
                            ip, device_type, fabricante, modelo,
                            puertos_abiertos, vulnerabilidades, confianza
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        ip,
                        device_data.get('device_type', ''),
                        device_data.get('fabricante', ''),
                        device_data.get('modelo', ''),
                        puertos_json,
                        vulnerabilidades_json,
                        device_data.get('confidence', 0)
                    ))
                    device_id = cursor.lastrowid
                    print(f"➕ Dispositivo {ip} agregado a base de datos (ID: {device_id})")
                
                conn.commit()
                return device_id
                
        except Exception as e:
            print(f"❌ Error agregando dispositivo {ip}: {e}")
            return -1
    
    def buscar_dispositivos(self, filtros: Optional[Dict] = None) -> List[Dict]:
        """
        Busca dispositivos en la base de datos con filtros opcionales
        
        Args:
            filtros (dict, opcional): Filtros de búsqueda
                - ip: Dirección IP específica
                - device_type: Tipo de dispositivo
                - puerto: Puerto específico
                - fabricante: Fabricante del dispositivo
                - activo: Solo dispositivos activos (True/False)
        
        Returns:
            list: Lista de dispositivos encontrados
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row  # Para acceso por nombre de columna
                cursor = conn.cursor()
                
                # Construir consulta SQL dinámicamente
                query = 'SELECT * FROM dispositivos WHERE 1=1'
                params = []
                
                if filtros:
                    if 'ip' in filtros:
                        query += ' AND ip LIKE ?'
                        params.append(f"%{filtros['ip']}%")
                    
                    if 'device_type' in filtros:
                        query += ' AND device_type LIKE ?'
                        params.append(f"%{filtros['device_type']}%")
                    
                    if 'fabricante' in filtros:
                        query += ' AND fabricante LIKE ?'
                        params.append(f"%{filtros['fabricante']}%")
                    
                    if 'activo' in filtros:
                        query += ' AND activo = ?'
                        params.append(1 if filtros['activo'] else 0)
                    
                    if 'puerto' in filtros:
                        query += ' AND puertos_abiertos LIKE ?'
                        params.append(f'%{filtros["puerto"]}%')
                
                query += ' ORDER BY ultima_actualizacion DESC'
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convertir a lista de diccionarios
                dispositivos = []
                for row in rows:
                    dispositivo = dict(row)
                    
                    # Deserializar campos JSON
                    try:
                        dispositivo['puertos_abiertos'] = json.loads(dispositivo['puertos_abiertos'] or '[]')
                        dispositivo['vulnerabilidades'] = json.loads(dispositivo['vulnerabilidades'] or '[]')
                    except:
                        dispositivo['puertos_abiertos'] = []
                        dispositivo['vulnerabilidades'] = []
                    
                    dispositivos.append(dispositivo)
                
                return dispositivos
                
        except Exception as e:
            print(f"❌ Error buscando dispositivos: {e}")
            return []
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas de la base de datos local
        
        Returns:
            dict: Estadísticas de dispositivos y vulnerabilidades
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                stats = {}
                
                # Total de dispositivos
                cursor.execute('SELECT COUNT(*) FROM dispositivos')
                stats['total_dispositivos'] = cursor.fetchone()[0]
                
                # Dispositivos activos
                cursor.execute('SELECT COUNT(*) FROM dispositivos WHERE activo = 1')
                stats['dispositivos_activos'] = cursor.fetchone()[0]
                
                # Dispositivos por tipo
                cursor.execute('''
                    SELECT device_type, COUNT(*) as count 
                    FROM dispositivos 
                    WHERE activo = 1 
                    GROUP BY device_type 
                    ORDER BY count DESC
                ''')
                stats['por_tipo'] = dict(cursor.fetchall())
                
                # Total de vulnerabilidades
                cursor.execute('SELECT COUNT(*) FROM vulnerabilidades')
                stats['total_vulnerabilidades'] = cursor.fetchone()[0]
                
                # Vulnerabilidades críticas
                cursor.execute('SELECT COUNT(*) FROM vulnerabilidades WHERE severidad = "CRITICAL"')
                stats['vulnerabilidades_criticas'] = cursor.fetchone()[0]
                
                # Último escaneo
                cursor.execute('SELECT MAX(fecha_fin) FROM escaneos')
                ultimo_escaneo = cursor.fetchone()[0]
                stats['ultimo_escaneo'] = ultimo_escaneo
                
                return stats
                
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def exportar_datos(self, formato='json', archivo_salida=None) -> str:
        """
        Exporta todos los datos de la base de datos
        
        Args:
            formato (str): Formato de exportación ('json', 'csv')
            archivo_salida (str, opcional): Archivo donde guardar los datos
        
        Returns:
            str: Ruta del archivo generado o datos en string
        """
        try:
            dispositivos = self.buscar_dispositivos()
            
            if formato.lower() == 'json':
                datos_exportacion = {
                    'timestamp': datetime.datetime.now().isoformat(),
                    'total_dispositivos': len(dispositivos),
                    'dispositivos': dispositivos,
                    'estadisticas': self.obtener_estadisticas()
                }
                
                if archivo_salida:
                    with open(archivo_salida, 'w', encoding='utf-8') as f:
                        json.dump(datos_exportacion, f, indent=2, ensure_ascii=False, default=str)
                    print(f"📄 Datos exportados a: {archivo_salida}")
                    return archivo_salida
                else:
                    return json.dumps(datos_exportacion, indent=2, ensure_ascii=False, default=str)
            
            elif formato.lower() == 'csv':
                import csv
                import io
                
                output = io.StringIO()
                fieldnames = ['ip', 'device_type', 'fabricante', 'modelo', 'puertos_abiertos', 
                             'vulnerabilidades_count', 'confianza', 'ultima_actualizacion']
                
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                
                for device in dispositivos:
                    row = {
                        'ip': device['ip'],
                        'device_type': device['device_type'],
                        'fabricante': device['fabricante'],
                        'modelo': device['modelo'],
                        'puertos_abiertos': ','.join(map(str, device['puertos_abiertos'])),
                        'vulnerabilidades_count': len(device['vulnerabilidades']),
                        'confianza': device['confianza'],
                        'ultima_actualizacion': device['ultima_actualizacion']
                    }
                    writer.writerow(row)
                
                csv_data = output.getvalue()
                output.close()
                
                if archivo_salida:
                    with open(archivo_salida, 'w', encoding='utf-8') as f:
                        f.write(csv_data)
                    print(f"📄 Datos exportados a: {archivo_salida}")
                    return archivo_salida
                else:
                    return csv_data
            
            else:
                raise ValueError(f"Formato no soportado: {formato}")
                
        except Exception as e:
            print(f"❌ Error exportando datos: {e}")
            return ""
    
    def limpiar_dispositivos_inactivos(self, dias_inactividad=30):
        """
        Marca como inactivos los dispositivos que no han sido actualizados recientemente
        
        Args:
            dias_inactividad (int): Días de inactividad para marcar como inactivo
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                fecha_limite = datetime.datetime.now() - datetime.timedelta(days=dias_inactividad)
                
                cursor.execute('''
                    UPDATE dispositivos 
                    SET activo = 0 
                    WHERE ultima_actualizacion < ? AND activo = 1
                ''', (fecha_limite,))
                
                dispositivos_inactivos = cursor.rowcount
                conn.commit()
                
                print(f"🔄 {dispositivos_inactivos} dispositivos marcados como inactivos")
                
        except Exception as e:
            print(f"❌ Error limpiando dispositivos inactivos: {e}")

# Funciones de conveniencia para uso directo
def crear_base_datos(db_path="scanner/shodan_local.db"):
    """
    Función de conveniencia para crear la base de datos
    
    Args:
        db_path (str): Ruta al archivo de base de datos
    """
    print("🗄️  Creando base de datos local tipo Shodan...")
    shodan_local = ShodanLocal(db_path)
    
    # Mostrar estadísticas iniciales
    stats = shodan_local.obtener_estadisticas()
    print(f"📊 Estadísticas de la base de datos:")
    print(f"   • Total dispositivos: {stats.get('total_dispositivos', 0)}")
    print(f"   • Dispositivos activos: {stats.get('dispositivos_activos', 0)}")
    print(f"   • Vulnerabilidades: {stats.get('total_vulnerabilidades', 0)}")
    
    return shodan_local

def integrar_con_scanner(dispositivos_detectados, db_path="scanner/shodan_local.db"):
    """
    Integra los resultados del scanner con la base de datos local
    
    Args:
        dispositivos_detectados (list): Lista de dispositivos detectados por el scanner
        db_path (str): Ruta a la base de datos
    
    Returns:
        ShodanLocal: Instancia de la base de datos local
    """
    print("🔗 Integrando resultados del scanner con base de datos local...")
    
    shodan_local = ShodanLocal(db_path)
    
    dispositivos_agregados = 0
    dispositivos_actualizados = 0
    
    for device in dispositivos_detectados:
        device_id = shodan_local.agregar_dispositivo(device['ip'], device)
        if device_id > 0:
            if device_id == len(dispositivos_detectados):  # Nuevo dispositivo
                dispositivos_agregados += 1
            else:  # Dispositivo actualizado
                dispositivos_actualizados += 1
    
    print(f"✅ Integración completada:")
    print(f"   • Dispositivos nuevos: {dispositivos_agregados}")
    print(f"   • Dispositivos actualizados: {dispositivos_actualizados}")
    
    return shodan_local

def buscar_en_base_local(termino_busqueda, db_path="scanner/shodan_local.db"):
    """
    Busca dispositivos en la base de datos local
    
    Args:
        termino_busqueda (str): Término a buscar (IP, tipo de dispositivo, etc.)
        db_path (str): Ruta a la base de datos
    
    Returns:
        list: Lista de dispositivos encontrados
    """
    shodan_local = ShodanLocal(db_path)
    
    # Intentar diferentes tipos de búsqueda
    filtros = {}
    
    # Si parece una IP
    if '.' in termino_busqueda and all(part.isdigit() for part in termino_busqueda.split('.') if part):
        filtros['ip'] = termino_busqueda
    # Si es un número (puerto)
    elif termino_busqueda.isdigit():
        filtros['puerto'] = int(termino_busqueda)
    # Búsqueda por tipo de dispositivo o fabricante
    else:
        filtros['device_type'] = termino_busqueda
        # Si no encuentra por tipo, buscar por fabricante
        resultados = shodan_local.buscar_dispositivos(filtros)
        if not resultados:
            filtros = {'fabricante': termino_busqueda}
    
    resultados = shodan_local.buscar_dispositivos(filtros)
    
    print(f"🔍 Búsqueda de '{termino_busqueda}': {len(resultados)} resultados encontrados")
    
    return resultados

if __name__ == "__main__":
    # Demo de la funcionalidad
    print("🔍 DEMO: Shodan Local Database")
    print("=" * 50)
    
    # Crear base de datos
    shodan_local = crear_base_datos()
    
    # Mostrar estadísticas
    stats = shodan_local.obtener_estadisticas()
    print(f"\n📊 Estadísticas actuales:")
    for key, value in stats.items():
        print(f"   • {key}: {value}")
