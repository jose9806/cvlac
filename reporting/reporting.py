#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo de reporting para generar informes mejorados de las extracciones de CvLAC.

Este módulo proporciona funcionalidades para generar informes en diferentes formatos
(HTML, JSON, CSV) con estadísticas y análisis detallados de las extracciones realizadas.
"""

import os
import json
import csv
import datetime
import logging
from pathlib import Path
import shutil
from collections import Counter, defaultdict

# Configurar el logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("reporting")


class EnhancedReporting:
    """
    Clase para generar reportes mejorados con análisis de datos de extracción.
    """

    def __init__(self, base_dir="reports/enhanced"):
        """
        Inicializa el generador de reportes mejorados.

        Args:
            base_dir (str): Directorio base para almacenar los reportes.
        """
        self.base_dir = base_dir
        self._ensure_dirs_exist()

        # Plantillas y recursos para HTML
        self.template_dir = os.path.join(os.path.dirname(__file__), "templates")

        # Si el directorio de plantillas no existe, crear uno con plantillas predeterminadas
        if not os.path.exists(self.template_dir):
            self._create_default_templates()

    def _ensure_dirs_exist(self):
        """Asegura que los directorios necesarios existan."""
        os.makedirs(self.base_dir, exist_ok=True)

        # Crear subdirectorios para cada tipo de reporte
        for subdir in ["html", "json", "csv"]:
            os.makedirs(os.path.join(self.base_dir, subdir), exist_ok=True)

    def _create_default_templates(self):
        """Crea plantillas HTML predeterminadas."""
        os.makedirs(self.template_dir, exist_ok=True)

        # Plantilla HTML principal
        with open(
            os.path.join(self.template_dir, "main_template.html"), "w", encoding="utf-8"
        ) as f:
            f.write(self._get_default_html_template())

        # CSS para plantilla
        with open(
            os.path.join(self.template_dir, "style.css"), "w", encoding="utf-8"
        ) as f:
            f.write(self._get_default_css())

    def analyze_session_data(self, session_data):
        """
        Analiza los datos de sesión para generar estadísticas y métricas.

        Args:
            session_data (dict): Datos de sesión de extracción.

        Returns:
            dict: Análisis y estadísticas de los datos.
        """
        analysis = {
            "summary": {
                "total_cvlacs": session_data.get("cvlacs_processed", 0),
                "success_count": session_data.get("success_count", 0),
                "error_count": session_data.get("error_count", 0),
                "success_rate": 0,
                "started_at": session_data.get("started_at", ""),
                "ended_at": session_data.get(
                    "ended_at", datetime.datetime.now().isoformat()
                ),
                "duration": 0,
            },
            "tables": {
                "most_extracted": [],
                "most_errors": [],
                "table_stats": {},
            },
            "errors": {
                "common_errors": [],
                "error_by_table": {},
            },
            "processing": {
                "cvlacs_by_hour": {},
                "success_by_hour": {},
                "error_by_hour": {},
            },
        }

        # Calcular tasa de éxito
        total = analysis["summary"]["total_cvlacs"]
        if total > 0:
            analysis["summary"]["success_rate"] = (
                analysis["summary"]["success_count"] / total
            ) * 100

        # Calcular duración
        try:
            start_time = datetime.datetime.fromisoformat(
                analysis["summary"]["started_at"]
            )
            end_time = datetime.datetime.fromisoformat(analysis["summary"]["ended_at"])
            analysis["summary"]["duration"] = (
                end_time - start_time
            ).total_seconds() / 60.0  # en minutos
        except (ValueError, TypeError):
            logger.warning("No se pudo calcular la duración del proceso")

        # Analizar estadísticas de tablas
        table_stats = session_data.get("table_stats", {})
        analysis["tables"]["table_stats"] = table_stats

        # Tablas con más extracciones exitosas
        table_inserts = [
            (table, stats.get("inserts", 0) + stats.get("updates", 0))
            for table, stats in table_stats.items()
        ]
        table_inserts.sort(key=lambda x: x[1], reverse=True)
        analysis["tables"]["most_extracted"] = table_inserts[:10]  # Top 10

        # Tablas con más errores
        table_errors = [
            (table, stats.get("errors", 0)) for table, stats in table_stats.items()
        ]
        table_errors.sort(key=lambda x: x[1], reverse=True)
        analysis["tables"]["most_errors"] = table_errors[:10]  # Top 10

        # Analizar errores
        errors = session_data.get("errors", [])
        error_messages = [error.get("error", "") for error in errors]
        error_counter = Counter(error_messages)
        analysis["errors"]["common_errors"] = error_counter.most_common(10)  # Top 10

        # Errores por tabla
        error_by_table = defaultdict(list)
        for error in errors:
            table = error.get("table", "unknown")
            error_by_table[table].append(error.get("error", ""))

        analysis["errors"]["error_by_table"] = {
            table: Counter(error_list).most_common(5)  # Top 5 por tabla
            for table, error_list in error_by_table.items()
        }

        # Análisis temporal
        processing_history = session_data.get("processing_history", [])
        hour_counter = defaultdict(lambda: {"total": 0, "success": 0, "error": 0})

        for entry in processing_history:
            try:
                timestamp = datetime.datetime.fromisoformat(
                    entry.get("processed_at", "")
                )
                hour = timestamp.strftime("%Y-%m-%d %H:00")

                hour_counter[hour]["total"] += 1
                if entry.get("success", False):
                    hour_counter[hour]["success"] += 1
                else:
                    hour_counter[hour]["error"] += 1
            except (ValueError, TypeError):
                continue

        # Ordenar por hora
        sorted_hours = sorted(hour_counter.keys())
        analysis["processing"]["cvlacs_by_hour"] = {
            hour: hour_counter[hour]["total"] for hour in sorted_hours
        }
        analysis["processing"]["success_by_hour"] = {
            hour: hour_counter[hour]["success"] for hour in sorted_hours
        }
        analysis["processing"]["error_by_hour"] = {
            hour: hour_counter[hour]["error"] for hour in sorted_hours
        }

        return analysis

    def generate_html_report(self, session_data, enhanced_data=None):
        """
        Genera un reporte HTML con visualizaciones.

        Args:
            session_data (dict): Datos de sesión de extracción.
            enhanced_data (dict, optional): Datos de análisis pre-calculados.

        Returns:
            str: Ruta al archivo HTML generado.
        """
        if enhanced_data is None:
            enhanced_data = self.analyze_session_data(session_data)

        # Crear directorio de salida
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = session_data.get("session_id", f"session_{timestamp}")
        output_dir = os.path.join(self.base_dir, "html", session_id)
        os.makedirs(output_dir, exist_ok=True)

        # Copiar archivos de estilo
        css_file = os.path.join(self.template_dir, "style.css")
        if os.path.exists(css_file):
            shutil.copy(css_file, os.path.join(output_dir, "style.css"))

        # Generar HTML
        html_content = self._generate_html_content(session_data, enhanced_data)
        html_file = os.path.join(output_dir, "report.html")

        with open(html_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"Reporte HTML generado: {html_file}")
        return html_file

    def generate_json_report(self, session_data, enhanced_data=None):
        """
        Genera un reporte JSON con estadísticas adicionales.

        Args:
            session_data (dict): Datos de sesión de extracción.
            enhanced_data (dict, optional): Datos de análisis pre-calculados.

        Returns:
            str: Ruta al archivo JSON generado.
        """
        if enhanced_data is None:
            enhanced_data = self.analyze_session_data(session_data)

        # Crear directorio de salida
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = session_data.get("session_id", f"session_{timestamp}")
        output_dir = os.path.join(self.base_dir, "json", session_id)
        os.makedirs(output_dir, exist_ok=True)

        # Crear reporte JSON completo
        full_report = {"session_data": session_data, "analysis": enhanced_data}

        # Guardar archivo JSON
        json_file = os.path.join(output_dir, "report.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)

        # Generar también archivos JSON separados para análisis y resumen
        summary_file = os.path.join(output_dir, "summary.json")
        with open(summary_file, "w", encoding="utf-8") as f:
            json.dump(enhanced_data["summary"], f, indent=2, ensure_ascii=False)

        logger.info(f"Reporte JSON generado: {json_file}")
        return json_file

    def generate_csv_report(self, session_data, enhanced_data=None):
        """
        Genera reportes CSV para análisis en hojas de cálculo.

        Args:
            session_data (dict): Datos de sesión de extracción.
            enhanced_data (dict, optional): Datos de análisis pre-calculados.

        Returns:
            dict: Rutas a los archivos CSV generados.
        """
        if enhanced_data is None:
            enhanced_data = self.analyze_session_data(session_data)

        # Crear directorio de salida
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        session_id = session_data.get("session_id", f"session_{timestamp}")
        output_dir = os.path.join(self.base_dir, "csv", session_id)
        os.makedirs(output_dir, exist_ok=True)

        csv_files = {}

        # CSV de resumen
        summary_file = os.path.join(output_dir, "summary.csv")
        with open(summary_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Metric", "Value"])
            for key, value in enhanced_data["summary"].items():
                writer.writerow([key, value])
        csv_files["summary"] = summary_file

        # CSV de estadísticas de tablas
        tables_file = os.path.join(output_dir, "tables.csv")
        with open(tables_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Table", "Inserts", "Updates", "Skips", "Errors"])
            for table, stats in enhanced_data["tables"]["table_stats"].items():
                writer.writerow(
                    [
                        table,
                        stats.get("inserts", 0),
                        stats.get("updates", 0),
                        stats.get("skips", 0),
                        stats.get("errors", 0),
                    ]
                )
        csv_files["tables"] = tables_file

        # CSV de historial de procesamiento
        history_file = os.path.join(output_dir, "history.csv")
        with open(history_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["CvLAC ID", "Processed At", "Success", "Processing Time"])
            for entry in session_data.get("processing_history", []):
                writer.writerow(
                    [
                        entry.get("cvlac_id", ""),
                        entry.get("processed_at", ""),
                        entry.get("success", False),
                        entry.get("processing_time", 0),
                    ]
                )
        csv_files["history"] = history_file

        # CSV de análisis temporal
        time_file = os.path.join(output_dir, "time_analysis.csv")
        with open(time_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Hour", "Total", "Success", "Error"])
            for hour in enhanced_data["processing"]["cvlacs_by_hour"].keys():
                writer.writerow(
                    [
                        hour,
                        enhanced_data["processing"]["cvlacs_by_hour"].get(hour, 0),
                        enhanced_data["processing"]["success_by_hour"].get(hour, 0),
                        enhanced_data["processing"]["error_by_hour"].get(hour, 0),
                    ]
                )
        csv_files["time_analysis"] = time_file

        logger.info(f"Reportes CSV generados en: {output_dir}")
        return csv_files

    def _generate_html_content(self, session_data, enhanced_data):
        """
        Genera el contenido HTML del reporte.

        Args:
            session_data (dict): Datos de sesión de extracción.
            enhanced_data (dict): Datos de análisis.

        Returns:
            str: Contenido HTML.
        """
        # Cargar plantilla HTML
        template_path = os.path.join(self.template_dir, "main_template.html")
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
        else:
            template = self._get_default_html_template()

        # Extraer datos del resumen
        summary = enhanced_data["summary"]

        # Generar HTML para tablas más extraídas
        most_extracted_html = "<table><tr><th>Tabla</th><th>Registros</th></tr>"
        for table, count in enhanced_data["tables"]["most_extracted"]:
            most_extracted_html += f"<tr><td>{table}</td><td>{count}</td></tr>"
        most_extracted_html += "</table>"

        # Generar HTML para tablas con más errores
        most_errors_html = "<table><tr><th>Tabla</th><th>Errores</th></tr>"
        for table, count in enhanced_data["tables"]["most_errors"]:
            most_errors_html += f"<tr><td>{table}</td><td>{count}</td></tr>"
        most_errors_html += "</table>"

        # Generar HTML para estadísticas completas de tablas
        table_stats_html = "<table><tr><th>Tabla</th><th>Insertados</th><th>Actualizados</th><th>Omitidos</th><th>Errores</th></tr>"
        for table, stats in enhanced_data["tables"]["table_stats"].items():
            table_stats_html += f"<tr><td>{table}</td><td>{stats.get('inserts', 0)}</td><td>{stats.get('updates', 0)}</td><td>{stats.get('skips', 0)}</td><td>{stats.get('errors', 0)}</td></tr>"
        table_stats_html += "</table>"

        # Generar HTML para errores comunes
        common_errors_html = "<table><tr><th>Error</th><th>Ocurrencias</th></tr>"
        for error, count in enhanced_data["errors"]["common_errors"]:
            common_errors_html += f"<tr><td>{error}</td><td>{count}</td></tr>"
        common_errors_html += "</table>"

        # Generar datos para gráficos
        time_labels = list(enhanced_data["processing"]["cvlacs_by_hour"].keys())
        time_data_total = list(enhanced_data["processing"]["cvlacs_by_hour"].values())
        time_data_success = list(
            enhanced_data["processing"]["success_by_hour"].values()
        )
        time_data_error = list(enhanced_data["processing"]["error_by_hour"].values())

        table_names = [table for table, _ in enhanced_data["tables"]["most_extracted"]]
        table_counts = [count for _, count in enhanced_data["tables"]["most_extracted"]]

        # Reemplazar valores en la plantilla
        html_content = template.replace(
            "{{SESSION_ID}}", session_data.get("session_id", "Unknown")
        )
        html_content = html_content.replace(
            "{{TOTAL_CVLACS}}", str(summary["total_cvlacs"])
        )
        html_content = html_content.replace(
            "{{SUCCESS_COUNT}}", str(summary["success_count"])
        )
        html_content = html_content.replace(
            "{{ERROR_COUNT}}", str(summary["error_count"])
        )
        html_content = html_content.replace(
            "{{SUCCESS_RATE}}", f"{summary['success_rate']:.2f}%"
        )
        html_content = html_content.replace(
            "{{STARTED_AT}}", str(summary["started_at"])
        )
        html_content = html_content.replace("{{ENDED_AT}}", str(summary["ended_at"]))
        html_content = html_content.replace(
            "{{DURATION}}", f"{summary['duration']:.2f} minutos"
        )

        html_content = html_content.replace(
            "{{MOST_EXTRACTED_TABLES}}", most_extracted_html
        )
        html_content = html_content.replace("{{MOST_ERROR_TABLES}}", most_errors_html)
        html_content = html_content.replace("{{TABLE_STATS}}", table_stats_html)
        html_content = html_content.replace("{{COMMON_ERRORS}}", common_errors_html)

        # Datos para gráficos
        html_content = html_content.replace("{{TIME_LABELS}}", json.dumps(time_labels))
        html_content = html_content.replace(
            "{{TIME_DATA_TOTAL}}", json.dumps(time_data_total)
        )
        html_content = html_content.replace(
            "{{TIME_DATA_SUCCESS}}", json.dumps(time_data_success)
        )
        html_content = html_content.replace(
            "{{TIME_DATA_ERROR}}", json.dumps(time_data_error)
        )

        html_content = html_content.replace("{{TABLE_NAMES}}", json.dumps(table_names))
        html_content = html_content.replace(
            "{{TABLE_COUNTS}}", json.dumps(table_counts)
        )

        return html_content

    def _get_default_html_template(self):
        """
        Obtiene una plantilla HTML predeterminada para los reportes.

        Returns:
            str: Plantilla HTML.
        """
        return """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Extracción CvLAC</title>
    <link rel="stylesheet" href="style.css">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <header>
        <h1>Reporte de Extracción CvLAC</h1>
        <p>Sesión: {{SESSION_ID}}</p>
    </header>
    
    <section class="summary">
        <h2>Resumen</h2>
        <div class="cards">
            <div class="card">
                <h3>Total CvLACs</h3>
                <p class="big-number">{{TOTAL_CVLACS}}</p>
            </div>
            <div class="card success">
                <h3>Exitosos</h3>
                <p class="big-number">{{SUCCESS_COUNT}}</p>
            </div>
            <div class="card error">
                <h3>Errores</h3>
                <p class="big-number">{{ERROR_COUNT}}</p>
            </div>
            <div class="card">
                <h3>Tasa de Éxito</h3>
                <p class="big-number">{{SUCCESS_RATE}}</p>
            </div>
        </div>
        
        <div class="time-info">
            <p><strong>Inicio:</strong> {{STARTED_AT}}</p>
            <p><strong>Fin:</strong> {{ENDED_AT}}</p>
            <p><strong>Duración:</strong> {{DURATION}}</p>
        </div>
    </section>
    
    <section class="charts">
        <h2>Análisis Temporal</h2>
        <div class="chart-container">
            <canvas id="timeChart"></canvas>
        </div>
        
        <h2>Tablas con más extracciones</h2>
        <div class="chart-container">
            <canvas id="tablesChart"></canvas>
        </div>
    </section>
    
    <section class="tables">
        <div class="table-section">
            <h2>Tablas con más extracciones</h2>
            {{MOST_EXTRACTED_TABLES}}
        </div>
        
        <div class="table-section">
            <h2>Tablas con más errores</h2>
            {{MOST_ERROR_TABLES}}
        </div>
    </section>
    
    <section class="errors">
        <h2>Errores más comunes</h2>
        {{COMMON_ERRORS}}
    </section>
    
    <section class="all-tables">
        <h2>Estadísticas de todas las tablas</h2>
        {{TABLE_STATS}}
    </section>
    
    <footer>
        <p>Generado por CvLAC Scraper Enhanced Reporting</p>
        <p>Fecha de generación: <span id="genDate"></span></p>
    </footer>
    
    <script>
        // Establecer fecha de generación
        document.getElementById('genDate').textContent = new Date().toLocaleString();
        
        // Gráfico temporal
        const timeLabels = {{TIME_LABELS}};
        const timeDataTotal = {{TIME_DATA_TOTAL}};
        const timeDataSuccess = {{TIME_DATA_SUCCESS}};
        const timeDataError = {{TIME_DATA_ERROR}};
        
        const timeCtx = document.getElementById('timeChart').getContext('2d');
        new Chart(timeCtx, {
            type: 'line',
            data: {
                labels: timeLabels,
                datasets: [
                    {
                        label: 'Total',
                        data: timeDataTotal,
                        borderColor: 'rgba(75, 192, 192, 1)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Exitosos',
                        data: timeDataSuccess,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        tension: 0.1,
                        fill: false
                    },
                    {
                        label: 'Errores',
                        data: timeDataError,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        tension: 0.1,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Procesamiento por hora'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
        
        // Gráfico de tablas
        const tableNames = {{TABLE_NAMES}};
        const tableCounts = {{TABLE_COUNTS}};
        
        const tablesCtx = document.getElementById('tablesChart').getContext('2d');
        new Chart(tablesCtx, {
            type: 'bar',
            data: {
                labels: tableNames,
                datasets: [{
                    label: 'Registros',
                    data: tableCounts,
                    backgroundColor: 'rgba(54, 162, 235, 0.5)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'Top 10 tablas con más extracciones'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    </script>
</body>
</html>
"""

    def _get_default_css(self):
        """
        Obtiene un CSS predeterminado para los reportes.

        Returns:
            str: CSS para los reportes.
        """
        return """/* Estilos generales */
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    margin: 0;
    padding: 0;
    background-color: #f8f9fa;
}

header, section, footer {
    padding: 20px;
    margin: 0 auto;
    max-width: 1200px;
}

header {
    background-color: #343a40;
    color: white;
    padding: 30px 20px;
    text-align: center;
}

h1, h2, h3 {
    margin-top: 0;
}

h2 {
    color: #343a40;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 10px;
    margin-top: 30px;
}

/* Estilos para tarjetas de resumen */
.cards {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
    margin: 20px 0;
}

.card {
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 20px;
    flex: 1;
    min-width: 200px;
    text-align: center;
}

.card.success {
    background-color: #d4edda;
    color: #155724;
}

.card.error {
    background-color: #f8d7da;
    color: #721c24;
}

.big-number {
    font-size: 2.5em;
    font-weight: bold;
    margin: 10px 0;
}

/* Estilos para gráficos */
.chart-container {
    background-color: white;
    border-radius: 5px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    padding: 20px;
    margin: 20px 0;
    height: 400px;
}

/* Estilos para tablas */
.tables {
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    justify-content: space-between;
}

.table-section {
    flex: 1;
    min-width: 300px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: white;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

th, td {
    padding: 12px 15px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

th {
    background-color: #343a40;
    color: white;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

/* Estilos para el pie de página */
footer {
    text-align: center;
    padding: 20px;
    margin-top: 30px;
    background-color: #343a40;
    color: white;
}

/* Responsive */
@media (max-width: 768px) {
    .cards, .tables {
        flex-direction: column;
    }
    
    .card, .table-section {
        width: 100%;
    }
    
    .chart-container {
        height: 300px;
    }
}
"""
