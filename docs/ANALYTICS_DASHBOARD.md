# SmartCam Auditor v2.0 Pro - Dashboard de Analytics

## 📈 Nueva Funcionalidad: Visualización de Gráficos de Seguridad

### Descripción
El nuevo dashboard de analytics proporciona visualización avanzada de métricas de seguridad mediante gráficos interactivos, permitiendo a los profesionales de ciberseguridad analizar datos de auditorías de manera visual e intuitiva.

### 🎯 Acceso a la Funcionalidad

#### Desde el Dashboard Principal
```
Dashboard → Botón "📈 Ver Gráficos"
```

#### URL Directa
```
http://localhost:5000/graficos
```

### 📊 Tipos de Gráficos Implementados

#### 1. **Distribución de Vulnerabilidades por Severidad** 🎯
- **Tipo**: Gráfico de donut (doughnut)
- **Datos**: Críticas, Altas, Medias, Bajas
- **Colores**: 
  - 🔴 Críticas (#ef4444)
  - 🟠 Altas (#f97316)
  - 🟡 Medias (#eab308)
  - 🟢 Bajas (#22c55e)
- **Funcionalidad**: Tooltips con porcentajes

#### 2. **Métricas de Seguridad por Categoría** 🔒
- **Tipo**: Gráfico de barras
- **Categorías**:
  - Credenciales débiles
  - Dispositivos vulnerables
  - Puertos inseguros
  - Dispositivos seguros
- **Características**: Barras con bordes redondeados y colores diferenciados

#### 3. **Evolución Temporal de Amenazas** 📈
- **Tipo**: Gráfico de líneas múltiples
- **Datos**: Vulnerabilidades y dispositivos por período
- **Períodos**: Últimas 4 semanas
- **Características**: 
  - Líneas suaves con relleno
  - Puntos destacados
  - Doble eje Y

#### 4. **Distribución por Tipo de Dispositivo** 🔧
- **Tipo**: Gráfico circular (pie)
- **Categorías**:
  - 📹 Cámaras IP
  - 📼 DVR/NVR
  - 🌐 Routers
  - 🔌 Otros IoT
- **Vista complementaria**: Lista detallada con contadores

### 🎨 Características Visuales

#### **Resumen Ejecutivo**
```html
📋 Resumen Ejecutivo
├── 🔍 Dispositivos Analizados
├── ⚠️ Vulnerabilidades Totales  
├── 🔑 Credenciales Vulnerables
└── 🛡️ Nivel de Seguridad (%)
```

#### **Paleta de Colores**
```css
--critical: #ef4444    /* Rojo crítico */
--high: #f97316        /* Naranja alto */
--medium: #eab308      /* Amarillo medio */
--low: #22c55e         /* Verde bajo */
--primary: #3b82f6     /* Azul primario */
--success: #10b981     /* Verde éxito */
--warning: #f59e0b     /* Amarillo advertencia */
--info: #06b6d4        /* Cian información */
```

### 🔧 Implementación Técnica

#### **Backend (routes.py)**
```python
@web_bp.route("/graficos")
@require_auth
def graficos():
    # Cálculo de estadísticas reales de auditorías
    total_devices = len(audit_status.get("results", []))
    
    # Datos de demostración si no hay auditorías
    if total_devices == 0:
        vulnerability_severity_data = {
            "Críticas": 3, "Altas": 5, "Medias": 8, "Bajas": 4
        }
        # ... más datos de ejemplo
    
    return render_template("charts.html", **data)
```

#### **Frontend (charts.html)**
```html
<!-- Chart.js integration -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<canvas id="vulnerabilitySeverityChart"></canvas>

<script>
const vulnerabilitySeverityChart = new Chart(ctx, {
    type: 'doughnut',
    data: vulnerabilitySeverityData,
    options: { /* configuración */ }
});
</script>
```

#### **Estilos (style.css)**
```css
.chart-container {
    position: relative;
    height: 400px;
    background: var(--card-bg);
    border-radius: 12px;
}

.executive-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
}
```

### 📱 Funcionalidades Interactivas

#### **Acciones Rápidas**
- 📊 **Volver al Dashboard**: Navegación principal
- 🔄 **Actualizar Gráficos**: Recarga datos en tiempo real
- 📥 **Exportar Reporte Visual**: Funcionalidad en desarrollo
- ⚡ **Nueva Auditoría Rápida**: Lanzar nueva auditoría

#### **Controles de Usuario**
- 🌙 **Tema Oscuro**: Toggle entre claro/oscuro
- 👤 **Usuario**: Información de sesión actual
- 🚪 **Cerrar Sesión**: Logout seguro

### 🔄 Fuente de Datos

#### **Datos Reales de Auditorías**
```python
# Cálculo dinámico basado en audit_status
total_devices = len(audit_status.get("results", []))
critical_vulns = sum(1 for r in audit_status.get("results", []) 
                    for v in r.get("vulnerabilities", []) 
                    if v.get("severity") == "CRITICAL")
```

#### **Datos de Demostración**
```python
# Datos de ejemplo cuando no hay auditorías
if total_devices == 0:
    vulnerability_severity_data = {
        "Críticas": 3, "Altas": 5, "Medias": 8, "Bajas": 4
    }
```

### 🎯 Casos de Uso

#### **Análisis de Vulnerabilidades**
1. Identificar distribución de severidad
2. Priorizar remediación por criticidad
3. Tracking de mejoras temporales

#### **Gestión de Dispositivos**
1. Inventario visual por categorías
2. Identificación de tipos más vulnerables
3. Planificación de actualizaciones

#### **Reportes Ejecutivos**
1. Métricas de alto nivel para management
2. Tendencias de seguridad
3. ROI de inversiones en seguridad

### 🚀 Mejoras Futuras

#### **v2.1 Planned Features**
- [ ] **Exportación PDF**: Reportes ejecutivos automáticos
- [ ] **Gráficos Comparativos**: Auditorías históricas
- [ ] **Alertas Visuales**: Thresholds configurables
- [ ] **Drill-down**: Detalles por clic en gráficos
- [ ] **Filtros Temporales**: Rango de fechas personalizables
- [ ] **Métricas Personalizadas**: KPIs configurables

#### **Integraciones Futuras**
- [ ] **APIs de Threat Intelligence**: CVE scoring
- [ ] **SIEM Integration**: Correlación de eventos
- [ ] **Compliance Dashboards**: SOC, PCI DSS, ISO 27001
- [ ] **Mobile Analytics**: App nativa

### 🔒 Consideraciones de Seguridad

#### **Autenticación Requerida**
```python
@web_bp.route("/graficos")
@require_auth  # Protección obligatoria
def graficos():
    if "user" not in session:
        return redirect(url_for("web_panel.login"))
```

#### **Validación de Datos**
- Sanitización de inputs
- Validación de rangos numéricos
- Protección contra XSS en gráficos

### 📊 Métricas de Rendimiento

#### **Carga de Datos**
- **Tiempo inicial**: <2 segundos
- **Actualización**: <1 segundo
- **Rendering gráficos**: <500ms

#### **Compatibilidad**
- **Navegadores**: Chrome 80+, Firefox 75+, Safari 13+
- **Dispositivos**: Desktop, tablet, móvil
- **Resoluciones**: 320px - 4K

### 🎨 Responsive Design

#### **Desktop (>1024px)**
```css
.charts-grid {
    grid-template-columns: 1fr 1fr;
}
.chart-container {
    height: 400px;
}
```

#### **Tablet (768px-1024px)**
```css
.executive-summary {
    grid-template-columns: repeat(2, 1fr);
}
```

#### **Mobile (<768px)**
```css
.charts-grid {
    grid-template-columns: 1fr;
}
.chart-container {
    height: 300px;
}
```

### 🐛 Troubleshooting

#### **Gráficos No Cargan**
```bash
# Verificar Chart.js CDN
curl -I https://cdn.jsdelivr.net/npm/chart.js

# Revisar errores en consola
F12 > Console > Buscar errores JavaScript
```

#### **Datos Vacíos**
```python
# Verificar audit_status
print(audit_status.get("results", []))

# Forzar datos de ejemplo
total_devices = 0  # Activará datos demo
```

### 📞 API Endpoints

```bash
GET /graficos              # Dashboard de analytics
GET /api/status           # Estado para gráficos en tiempo real  
GET /api/results          # Datos para calcular estadísticas
```

---

**SmartCam Auditor v2.0 Pro Analytics Dashboard** - Visualización profesional de métricas de seguridad para cámaras inteligentes y dispositivos IoT.

*Desarrollado con Chart.js y tecnologías web modernas - 2025*
