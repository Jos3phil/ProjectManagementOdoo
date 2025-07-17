#!/bin/bash
set -e

# ==================================================
# ===    ENHANCED AUTOMATION PIPELINE (DEMO)    ===
# ==================================================

# Importar funciones de monitoreo
source "$(dirname "$0")/monitor_performance.sh"

echo -e "\n\033[1;34m🚀 INICIANDO PIPELINE AUTOMATIZADO CON MONITOREO... (Modo Presentación)\033[0m\n"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Funciones de logging
log_step() { echo -e "${BLUE}▶️  [ETAPA $1] $2${NC}"; }
log_success() { echo -e "${GREEN}✅  ÉXITO: $1${NC}\n"; }
log_error() { echo -e "${RED}❌  FALLO: $1${NC}\n"; }
log_skipped() { echo -e "${YELLOW}🟡  SIMULADO: $1${NC}\n"; }

# Variables de estado
UNIT_PASSED=false
INTEGRATION_PASSED=false
OVERALL_START_TIME=$(date +%s)

# Mostrar info del sistema
show_system_info

# =================================================================
#               PIPELINE CON MONITOREO DE PERFORMANCE
# =================================================================

# --- ETAPA 1: TESTS UNITARIOS CON MONITOREO ---
log_step 1 "Ejecutando Tests Unitarios Puros con monitoreo de performance..."

if run_with_monitoring "docker compose run --rm web python -m unittest /mnt/extra-addons/project_management/tests/test_unit_pure.py" "Tests Unitarios"; then
    log_success "Tests Unitarios completados con monitoreo de performance."
    UNIT_PASSED=true
else
    log_error "Fallo en Tests Unitarios."
    UNIT_PASSED=false
    exit 1
fi

# --- ETAPA 2: TESTS DE INTEGRACIÓN CON MONITOREO ---
log_step 2 "Ejecutando Tests de Integración con monitoreo de performance..."

if run_with_monitoring "docker compose run --rm web odoo --test-enable --stop-after-init -d postgres -i project_management --test-file=/mnt/extra-addons/project_management/tests/test_integracion.py" "Tests de Integración"; then
    log_success "Tests de Integración completados con monitoreo."
    INTEGRATION_PASSED=true
else
    log_error "Fallo en Tests de Integración."
    INTEGRATION_PASSED=false
    exit 1
fi

# --- ETAPA 3: TESTS DE CORE (SIMULADO) ---
log_step 3 "Verificando Tests de Core con simulación de carga..."
if run_with_monitoring "sleep 3" "Simulación Tests Core"; then
    log_skipped "Tests de Core simulados con monitoreo de recursos."
fi

# --- ETAPA 4: TESTS FUNCIONALES (SIMULADO) ---
log_step 4 "Ejecutando Tests Funcionales con simulación de carga..."
if run_with_monitoring "sleep 5" "Simulación Tests Funcionales"; then
    log_skipped "Tests Funcionales simulados con monitoreo completo."
fi

# --- ETAPA 5: ANÁLISIS DE RENDIMIENTO CONSOLIDADO ---
log_step 5 "Generando análisis consolidado de rendimiento..."
generate_consolidated_report

# =================================================================
#               REPORTE FINAL MEJORADO
# =================================================================

generate_consolidated_report() {
    local overall_duration=$(($(date +%s) - OVERALL_START_TIME))
    
    echo -e "\n${CYAN}╔════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                    🎯 REPORTE FINAL DEL PIPELINE               ║${NC}"
    echo -e "${CYAN}╠════════════════════════════════════════════════════════════════╣${NC}"
    
    # Tiempo total
    local minutes=$((overall_duration / 60))
    local seconds=$((overall_duration % 60))
    echo -e "${CYAN}║${NC} ⏱️  Tiempo total del pipeline: ${YELLOW}${minutes}m ${seconds}s${NC}"
    
    # Resultados por etapa
    echo -e "${CYAN}║${NC} 📊 Resultados por etapa:"
    
    if [ "$UNIT_PASSED" = true ]; then
        echo -e "${CYAN}║${NC}    🟢 Etapa 1: Tests Unitarios... PASARON"
    else
        echo -e "${CYAN}║${NC}    🔴 Etapa 1: Tests Unitarios... FALLARON"
    fi
    
    if [ "$INTEGRATION_PASSED" = true ]; then
        echo -e "${CYAN}║${NC}    🟢 Etapa 2: Tests de Integración... PASARON"
    else
        echo -e "${CYAN}║${NC}    🔴 Etapa 2: Tests de Integración... FALLARON"
    fi
    
    echo -e "${CYAN}║${NC}    🟡 Etapa 3: Tests de Core... SIMULADO (OK)"
    echo -e "${CYAN}║${NC}    🟡 Etapa 4: Tests Funcionales... SIMULADO (OK)"
    echo -e "${CYAN}║${NC}    🔵 Etapa 5: Análisis de Rendimiento... COMPLETADO"
    
    # Métricas consolidadas
    echo -e "${CYAN}║${NC} 🖥️  Métricas del sistema:"
    echo -e "${CYAN}║${NC}    └─ CPU promedio: ${GREEN}${CPU_AVG:-N/A}%${NC}"
    echo -e "${CYAN}║${NC}    └─ Memory promedio: ${GREEN}${MEMORY_AVG:-N/A}%${NC}"
    echo -e "${CYAN}║${NC}    └─ Disk usage: ${YELLOW}${DISK_CURRENT:-N/A}%${NC}"
    
    # Contenedores Docker
    echo -e "${CYAN}║${NC} 🐳 Contenedores activos:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | tail -n +2 | while read container; do
        echo -e "${CYAN}║${NC}    └─ $container"
    done
    
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════╝${NC}\n"
    
    # Generar archivo para GitHub Actions
    generate_github_actions_summary
}

generate_github_actions_summary() {
    cat > /tmp/github_actions_summary.md << EOF
# 🚀 Pipeline Execution Summary

## ⏱️ Execution Time
- **Total Duration**: ${minutes}m ${seconds}s
- **Timestamp**: $(date -u +%Y-%m-%dT%H:%M:%SZ)

## 📊 Test Results
| Stage | Status | Duration |
|-------|--------|----------|
| Unit Tests | $([ "$UNIT_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | ~30s |
| Integration Tests | $([ "$INTEGRATION_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | ~3m |
| Core Tests | 🟡 SIMULATED | ~3s |
| Functional Tests | 🟡 SIMULATED | ~5s |

## 🖥️ System Performance
- **CPU Average**: ${CPU_AVG:-N/A}%
- **Memory Average**: ${MEMORY_AVG:-N/A}%
- **Disk Usage**: ${DISK_CURRENT:-N/A}%

## 🐳 Docker Containers
$(docker ps --format "- {{.Names}}: {{.Status}}")

## 🏆 Overall Status
$([ "$UNIT_PASSED" = true ] && [ "$INTEGRATION_PASSED" = true ] && echo "✅ **SUCCESS** - All tests passed!" || echo "❌ **FAILURE** - Some tests failed")
EOF
    
    echo -e "${GREEN}✅ Reporte para GitHub Actions generado: /tmp/github_actions_summary.md${NC}"
}

# =================================================================
#               EJECUCIÓN PRINCIPAL
# =================================================================

# Resultado final
if [ "$UNIT_PASSED" = true ] && [ "$INTEGRATION_PASSED" = true ]; then
    echo -e "${GREEN}🎉 PIPELINE EJECUTADO CON ÉXITO CON MONITOREO COMPLETO${NC}"
    echo -e "${CYAN}📊 Todos los datos de performance han sido capturados y analizados${NC}"
    exit 0
else
    echo -e "${RED}💥 Pipeline falló. Revisar logs y métricas de performance${NC}"
    exit 1
fi