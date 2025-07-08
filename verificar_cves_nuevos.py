#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script simple para verificar CVEs específicos integrados
Prueba CVE-2021-36260 y CVE-2020-13847
"""

import json
import os
import sys

def main():
    print("🔍 VERIFICACIÓN DE CVEs ESPECÍFICOS")
    print("="*50)
    
    # Cambiar al directorio correcto
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # CVEs objetivo
    cves_objetivo = ["CVE-2021-36260", "CVE-2020-13847"]
    
    try:
        # Cargar archivo CVE directamente
        with open("scanner/data/cves.json", "r", encoding="utf-8") as f:
            cves_data = json.load(f)
        
        print(f"✅ Base de datos CVE cargada: {len(cves_data)} vulnerabilidades")
        
        # Buscar CVEs específicos
        encontrados = {}
        for cve in cves_data:
            cve_id = cve.get("cve")
            if cve_id in cves_objetivo:
                encontrados[cve_id] = cve
                print(f"\n🎯 ENCONTRADO: {cve_id}")
                print(f"   Producto: {cve.get('producto', 'N/A')}")
                print(f"   Descripción: {cve.get('descripcion', 'N/A')}")
                print(f"   Severidad: {cve.get('severidad', 'N/A')} (Score: {cve.get('cvss_score', 'N/A')})")
                print(f"   Fecha: {cve.get('fecha', 'N/A')}")
                print(f"   Crítico: {'Sí' if cve.get('critico', False) else 'No'}")
        
        # Verificar que se encontraron todos
        print(f"\n📊 RESUMEN:")
        print(f"CVEs buscados: {len(cves_objetivo)}")
        print(f"CVEs encontrados: {len(encontrados)}")
        
        for cve_id in cves_objetivo:
            estado = "✅ INTEGRADO" if cve_id in encontrados else "❌ FALTA"
            print(f"  • {cve_id}: {estado}")
        
        if len(encontrados) == len(cves_objetivo):
            print(f"\n✅ ÉXITO: Todos los CVEs están correctamente integrados")
            
            # Probar el módulo CVEChecker
            print(f"\n🧪 Probando módulo CVEChecker...")
            try:
                sys.path.append(os.getcwd())
                from scanner.cve_checker import CVEChecker
                
                checker = CVEChecker()
                print(f"✅ CVEChecker inicializado")
                print(f"📊 CVEs en cache: {len(checker.cve_cache)}")
                
                # Probar búsqueda
                for cve_id in cves_objetivo:
                    encontrado = False
                    for cve in checker.cve_cache:
                        if cve.get('cve') == cve_id:
                            encontrado = True
                            break
                    print(f"  • {cve_id}: {'✅ Detectado' if encontrado else '❌ No detectado'}")
                
            except Exception as e:
                print(f"❌ Error probando CVEChecker: {e}")
        else:
            print(f"\n❌ FALLO: Faltan algunos CVEs")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
