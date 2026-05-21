# 🏛️ Sistema de Monitoreo SICOES (Infosiscon)

Este proyecto es un sistema automatizado en Python diseñado para el raspado (scraping) de convocatorias de licitaciones públicas de municipios en Bolivia (Riberalta y Cobija) desde la plataforma Infosiscon. Cuenta con alertas en tiempo real y un Bot interactivo de Telegram con soporte para múltiples administradores.

## 🚀 Características

* **Extracción Automática:** Escaneo programado de licitaciones dos veces al día.
* **Alertas Multi-Usuario:** Notificaciones automáticas e instantáneas de nuevos procesos enviadas a múltiples IDs de Telegram en paralelo.
* **Bot Interactivo:** Comandos manuales para consultar el historial de la base de datos local (`SQLite3`).
* **Zona Horaria Local:** Sincronizado nativamente con la hora oficial de Bolivia (GMT-4).

---

## 🛠️ Requisitos e Instalación

### 1. Clonar el repositorio
```bash
git clone [https://github.com/tu-usuario/tu-repositorio.git](https://github.com/tu-usuario/tu-repositorio.git)
cd tu-repositorio
