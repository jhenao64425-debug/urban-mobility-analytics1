# 🚀 Sistema Activo - Guía de Uso Actual

## Estado Actual del Sistema

✅ **Recolector**: ACTIVO (PID: 20821)  
✅ **Dashboard**: ACTIVO en http://localhost:8501  
✅ **Base de Datos**: 311 registros  
✅ **Estado**: FUNCIONANDO PERFECTAMENTE

---

## 📊 Lo que está sucediendo AHORA

### Recolector de Datos
```
- Ejecutándose cada 120 segundos
- Recolectando tráfico de 6 rutas simultáneamente
- Guardando en CSV y SQLite
- Retries automáticos si falla una ruta
- Logs en: logs/collector_background.log
```

### Dashboard Streamlit
```
- URL: http://localhost:8501
- Actualización automática cada 120 segundos
- Selector dinámico de 6 rutas
- Filtros de fecha funcionando
- Gráficas en tiempo real
- Tabla histórica con 311 registros
```

### Base de Datos
```
- SQLite: data/mobility.db (311 registros)
- CSV: data/raw/route_weather_data.csv (312 líneas)
- Índices activos en timestamp, origin, destination
- Sincronización automática
```

---

## 🔍 Monitorear el Sistema

### Verificar Estado Rápido
```bash
bash monitor.sh
```

### Ver Logs en Tiempo Real
```bash
tail -f logs/collector_background.log
```

### Verificar Base de Datos
```bash
# Total de registros
sqlite3 data/mobility.db "SELECT COUNT(*) FROM route_measurements;"

# Últimas 5 mediciones
sqlite3 data/mobility.db "SELECT timestamp, origin, destination, travel_time_min FROM route_measurements ORDER BY timestamp DESC LIMIT 5;"

# Registros por ruta
sqlite3 data/mobility.db "SELECT origin, destination, COUNT(*) FROM route_measurements GROUP BY origin, destination;"
```

### Ver Procesos Activos
```bash
ps aux | grep -E "route_extraction|streamlit"
```

---

## 🛑 Detener el Sistema

### Detener Solo el Recolector
```bash
pkill -f "src.route_extraction --interval"
```

### Detener Solo el Dashboard
```bash
pkill -f "streamlit run streamlit_app/app.py"
```

### Detener Todo
```bash
pkill -f "route_extraction"
pkill -f "streamlit"
```

---

## ▶️ Reiniciar el Sistema

### Reiniciar Recolector
```bash
python -m src.route_extraction --interval 120 > logs/collector_background.log 2>&1 &
```

### Reiniciar Dashboard
```bash
python -m streamlit run streamlit_app/app.py --server.port 8501 &
```

### Reiniciar Todo (Script Automático)
```bash
#!/bin/bash
# Kill existing processes
pkill -f "route_extraction" || true
pkill -f "streamlit" || true
sleep 2

# Start collector
python -m src.route_extraction --interval 120 > logs/collector_background.log 2>&1 &

# Start dashboard
python -m streamlit run streamlit_app/app.py --server.port 8501 &

echo "✓ Sistema reiniciado"
```

---

## 📈 Análisis en Tiempo Real

### Ver Resumen de Datos
```bash
python -m src.analytics summary
```

### Analizar Tendencia de una Ruta
```bash
python -m src.analytics trend Msida Marsaskala
```

### Impacto del Clima
```bash
python -m src.analytics weather Msida Sliema
```

### Comparar Todas las Rutas
```bash
python -m src.analytics compare
```

---

## 🤖 Modelos Predictivos

### Estado de Modelos
```bash
python train_models.py
```

### Entrenar Modelos Nuevos
```bash
python train_models.py
# Requiere 50+ muestras por ruta
# Actualmente: Msida→Marsaskala ✅ (60 muestras)
# Otras rutas: 49 muestras (necesitan 1 más)
```

---

## 📊 Dashboard Web

### Acceder al Dashboard
```
Navegador: http://localhost:8501
```

### Características Disponibles
- ✅ Selector de rutas (6 opciones)
- ✅ Filtros de tiempo (24h, 7d, 30d, custom)
- ✅ 8 tarjetas de métricas en tiempo real
- ✅ Mapa interactivo
- ✅ 4 tabs de análisis (tiempo, tráfico, clima, rankings)
- ✅ Tabla histórica filtrable
- ✅ Exportación CSV/JSON
- ✅ Auto-refresh cada 120s

---

## 🔧 Problemas Comunes

### Dashboard no carga
```bash
# Reiniciar dashboard
pkill -f "streamlit"
python -m streamlit run streamlit_app/app.py --server.port 8501 &
```

### Recolector se detiene
```bash
# Ver error
tail -20 logs/collector_background.log

# Reiniciar si está muerto
ps aux | grep route_extraction | grep -v grep || \
  python -m src.route_extraction --interval 120 > logs/collector_background.log 2>&1 &
```

### Sin datos en dashboard
```bash
# Esperar a que se complete el ciclo (120 segundos)
# Luego recargar dashboard (F5)

# O verificar datos manuales
sqlite3 data/mobility.db "SELECT COUNT(*) FROM route_measurements;"
```

---

## 📋 Mantenimiento Periódico

### Cada Hora
```bash
bash monitor.sh
```

### Cada 24 Horas
```bash
# Verificar logs
wc -l logs/collector*.log

# Entrenar modelos
python train_models.py

# Análisis completo
python -m src.analytics summary
```

### Cada Semana
```bash
# Backup de base de datos
cp data/mobility.db data/mobility_$(date +%Y%m%d).db

# Limpiar logs viejos
gzip logs/collector_*.log 2>/dev/null || true
```

---

## 📞 Recursos de Ayuda

### Documentación
- **Guía Completa**: README_FINAL.md
- **Quick Start**: QUICKSTART.md
- **Este archivo**: RUNNING_NOW.md

### Comandos Frecuentes
```bash
# Monitoreo
bash monitor.sh

# Logs en tiempo real
tail -f logs/collector_background.log

# Análisis
python -m src.analytics summary

# Modelos
python train_models.py

# Tests
python test_dashboard.py
```

### Detención de Emergencia
```bash
pkill -f "route_extraction"
pkill -f "streamlit"
```

---

## ✅ Checklist de Verificación

- [x] Recolector iniciado
- [x] Dashboard en http://localhost:8501
- [x] Base de datos con 311 registros
- [x] Logs guardándose en tiempo real
- [x] Auto-refresh funcionando
- [x] Modelos listos para entrenar
- [x] Sistema estable y respondiendo

---

## 📊 Próximas Acciones Automáticas

- **Cada 120 segundos**: Nueva recolección de datos
- **Cada medición**: Guardar en CSV + SQLite
- **Cada actualización**: Dashboard refleja cambios
- **Después de 50+ muestras/ruta**: Entrenar modelos

---

**¡El sistema está ACTIVO y recolectando datos AHORA! 🚀**

Última actualización: 2026-07-19 01:01:50 UTC

Para parar, usar: `pkill -f route_extraction && pkill -f streamlit`
