"""
MonitoringAgent-moduuli (M10) — järjestelmänvalvonta ja metriikkajärjestelmä.

Sisältää kolme agenttia:
- MonitoringAgent: valvoo agenttien ja järjestelmän tilannetta.
- LoggingAgent: rekisteröi tapahtumat, virheet ja lokiputket.
- MetricsAgent: kerää ja analysoi suorituskyky-metriikat.
"""

from __future__ import annotations

import json
import statistics
import time
from collections import defaultdict, deque
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


class MonitoringInput(AgentInput):
    """MonitoringAgentin syöte."""

    metrics: dict[str, Any] = Field(default_factory=dict, description="Kerätyt metriikat.")
    events: Optional[list[dict[str, Any]]] = Field(default=None, description="Tapahtumat.")
    check_thresholds: bool = Field(default=True, description="Tarkistetaanko kynnysarvot.")
    alert_threshold: float = Field(default=0.8, description="Varoitus kynnys (0-1).")


class MonitoringOutput(AgentOutput):
    """MonitoringAgentin tuloste."""

    status: str = Field(default="healthy", description="Järjestelmän tila.")
    alerts: list[dict[str, Any]] = Field(default_factory=list, description="Tuotetut varoitukset.")
    metrics_analyzed: dict[str, Any] = Field(default_factory=dict, description="Analysoidut metriikat.")
    score: float = Field(default=100.0, description="Järjestelmän terveys (0-100).")


class LoggingInput(AgentInput):
    """LoggingAgentin syöte."""

    message: str = Field(..., min_length=1, description="Lokiviesti.")
    level: str = Field(default="info", description="Lokitaso (info/warning/error/critical).")
    source: str = Field(default="system", description="Lähteen nimi.")
    log_file: str = Field(default="logs/aide.log", description="Lokitiedoston polku.")
    structured: bool = Field(default=True, description="Rakenteellinen loki (JSON).")


class LoggingOutput(AgentOutput):
    """LoggingAgentin tuloste."""

    logged: bool = Field(default=False, description="Onko viesti kirjoitettu.")
    log_entry: str = Field(default="", description="Kirjoitettu lokimerkintä.")
    log_file_path: str = Field(default="", description="Käytetty lokitiedosto.")
    entry_count: int = Field(default=0, description="Lokimerkintöjen lukumäärä tiedostossa.")


class MetricsInput(AgentInput):
    """MetricsAgentin syöte."""

    data: dict[str, Any] = Field(default_factory=dict, description="Mittadatat.")
    metric_type: str = Field(default="latency", description="Metriikan tyyppi.")
    window_size: int = Field(default=100, description="Ikkunan koko (viimeisimmät näytteet).")


class MetricsOutput(AgentOutput):
    """MetricsAgentin tuloste."""

    metric_name: str = Field(default="", description="Metriikan nimi.")
    values: list[float] = Field(default_factory=list, description="Mittausarvot.")
    stats: dict[str, float] = Field(default_factory=dict, description="Statistiikka (avg, min, max, p95, std).")
    anomalies: list[dict[str, Any]] = Field(default_factory=list, description="Havaitut poikkeamaa.")
    total_samples: int = Field(default=0, description="Näytteiden kokonaismäärä.")


class MonitoringAgent(BaseAgent):
    """
    MonitoringAgent valvoo järjestelmän tilannetta ja tuottaa varoitukset.

    Usage:
        agent = MonitoringAgent()
        result = agent.run("Tarkista terveys", metrics={"cpu": 0.85, "memory": 0.6})
    """

    agent_type: str = "monitoring"
    input_schema = MonitoringInput
    output_schema = MonitoringOutput

    # Kynnysarvot eri metriikoille
    THRESHOLDS: dict[str, float] = {
        "cpu": 0.85,
        "memory": 0.80,
        "disk": 0.90,
        "error_rate": 0.05,
        "latency_ms": 1000,
        "queue_size": 100,
    }

    def _analyze_metrics(self, metrics: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
        """Analysoi metriikat ja tuottaa varoitukset."""
        analyzed: dict[str, Any] = {}
        alerts: list[dict[str, Any]] = []

        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                analyzed[key] = {"value": value, "status": "healthy"}
                threshold = self.THRESHOLDS.get(key, 1.0)
                if value >= threshold:
                    analyzed[key]["status"] = "warning"
                    alerts.append({
                        "metric": key,
                        "value": value,
                        "threshold": threshold,
                        "severity": "warning",
                        "message": f"{key} ylittää kynnysarvon: {value:.4f} >= {threshold:.4f}",
                    })
                    if value >= threshold * 1.2:
                        analyzed[key]["status"] = "critical"
                        alerts[-1]["severity"] = "critical"
            elif isinstance(value, str):
                analyzed[key] = {"value": value, "status": "info"}
            elif isinstance(value, dict):
                analyzed[key] = {"value": value, "status": "info"}

        return analyzed, alerts

    def _calculate_score(self, analyzed: dict[str, Any], alerts: list[dict[str, Any]]) -> float:
        """Laske järjestelmän terveys-pisteet."""
        if not analyzed:
            return 100.0
        critical = sum(1 for a in alerts if a["severity"] == "critical")
        warnings = sum(1 for a in alerts if a["severity"] == "warning")
        score = 100.0 - (critical * 15) - (warnings * 5)
        return max(0.0, score)

    def _determine_status(self, alerts: list[dict[str, Any]]) -> str:
        """Määritä järjestelmän tila."""
        severities = {a["severity"] for a in alerts}
        if "critical" in severities:
            return "critical"
        elif "warning" in severities:
            return "degraded"
        return "healthy"

    def _run(self, input_data: MonitoringInput) -> MonitoringOutput:
        """MonitoringAgentin päälogiika."""
        metrics = input_data.metrics
        events = input_data.events or []

        # 1. Analysoi metriikat
        analyzed, alerts = self._analyze_metrics(metrics) if metrics else ({}, [])

        # 2. Analysoi tapahtumat (merkitse virheet)
        for event in events:
            if isinstance(event, dict):
                level = event.get("level", "info")
                if level in ("error", "critical"):
                    alerts.append({
                        "metric": "events",
                        "value": event.get("message", ""),
                        "threshold": 0,
                        "severity": level,
                        "message": f"Tapahtuma: {event.get('source', 'tuntematon')} - {event.get('message', '')}",
                    })

        # 3. Laske pisteet ja tila
        score = self._calculate_score(analyzed, alerts)
        status = self._determine_status(alerts)

        return MonitoringOutput(
            success=True,
            result={"status": status, "alerts": len(alerts), "score": score},
            message=f"Monitorointi valmis: tila={status}, {len(alerts)} varoitusta, pisteet {score}/100.",
            agent_type=self.agent_type,
            status=status,
            alerts=alerts,
            metrics_analyzed=analyzed,
            score=score,
        )


class LoggingAgent(BaseAgent):
    """
    LoggingAgent rekisteröi tapahtumat ja virheet lokitiedostoon.

    Usage:
        agent = LoggingAgent()
        result = agent.run("Kirjaa viesti", message="Projekti aloitettu", level="info")
    """

    agent_type: str = "logging"
    input_schema = LoggingInput
    output_schema = LoggingOutput

    def _format_entry(self, message: str, level: str, source: str, structured: bool) -> str:
        """Muotoilee logimerkinnän."""
        timestamp = datetime.now().isoformat()
        if structured:
            entry = {
                "timestamp": timestamp,
                "level": level,
                "source": source,
                "message": message,
            }
            return json.dumps(entry)
        else:
            return f"[{timestamp}] [{level.upper()}] [{source}] {message}"

    def _count_entries(self, log_file: Path) -> int:
        """Laske merkintöjen määrä lokitiedostossa."""
        if not log_file.exists():
            return 0
        with open(log_file, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())

    def _run(self, input_data: LoggingInput) -> LoggingOutput:
        """LoggingAgentin päälogiika."""
        log_path = Path(input_data.log_file)
        entry = self._format_entry(
            input_data.message,
            input_data.level,
            input_data.source,
            input_data.structured,
        )

        # Varmista lokikansio
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # Kirjoita merkintä
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(entry + "\n")
            logged = True
        except OSError as e:
            return LoggingOutput(
                success=False,
                result=None,
                message=f"Lokirintä epäonnistui: {e}",
                agent_type=self.agent_type,
                logged=False,
            )

        entry_count = self._count_entries(log_path)

        return LoggingOutput(
            success=True,
            result={"logged": logged, "path": str(log_path)},
            message=f"Logiviesti tallennettu: {log_path}",
            agent_type=self.agent_type,
            logged=logged,
            log_entry=entry,
            log_file_path=str(log_path),
            entry_count=entry_count,
        )


class MetricsAgent(BaseAgent):
    """
    MetricsAgent kerää ja analysoi suorituskyky-metriikat.

    Usage:
        agent = MetricsAgent()
        result = agent.run("Analysoi latenssin", data={"latency_ms": [10, 20, 30]})
    """

    agent_type: str = "metrics"
    input_schema = MetricsInput
    output_schema = MetricsOutput

    def _extract_values(self, data: dict[str, Any], metric_type: str) -> list[float]:
        """Poimi numeeriset arvot datasta."""
        values: list[float] = []

        # Jos data on suora lista
        if metric_type in data and isinstance(data[metric_type], list):
            for v in data[metric_type]:
                if isinstance(v, (int, float)):
                    values.append(float(v))
        elif metric_type in data and isinstance(data[metric_type], (int, float)):
            values = [float(data[metric_type])]
        else:
            # Etsi kaikki numeeriset arvot
            for v in data.values():
                if isinstance(v, (int, float)):
                    values.append(float(v))
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, (int, float)):
                            values.append(float(item))

        return values

    def _calculate_stats(self, values: list[float]) -> dict[str, float]:
        """Laske tilastot numeerisille arvoille."""
        if not values:
            return {"avg": 0.0, "min": 0.0, "max": 0.0, "p95": 0.0, "std": 0.0}

        avg = statistics.mean(values)
        minimum = min(values)
        maximum = max(values)
        p95 = self._percentile(values, 95)
        std = statistics.stdev(values) if len(values) > 1 else 0.0

        return {
            "avg": round(avg, 6),
            "min": round(minimum, 6),
            "max": round(maximum, 6),
            "p95": round(p95, 6),
            "std": round(std, 6),
        }

    def _percentile(self, values: list[float], percentile: float) -> float:
        """Laske percentyiliaika."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        index = int(len(sorted_vals) * percentile / 100)
        index = min(index, len(sorted_vals) - 1)
        return sorted_vals[index]

    def _detect_anomalies(self, values: list[float], stats: dict[str, float]) -> list[dict[str, Any]]:
        """Havitse poikkeamat (arvot, jotka poikkeavat keskiarvosta 2 std)."""
        anomalies: list[dict[str, Any]] = []
        if len(values) < 3 or stats["std"] == 0:
            return anomalies

        mean = stats["avg"]
        std = stats["std"]
        threshold = mean + (2 * std)

        for i, v in enumerate(values):
            if v > threshold or v < mean - (2 * std):
                anomalies.append({
                    "index": i,
                    "value": v,
                    "expected_range": f"[{mean - 2*std:.4f}, {threshold:.4f}]",
                    "severity": "anomaly",
                })

        return anomalies[:10]  # rajoitus

    def _run(self, input_data: MetricsInput) -> MetricsOutput:
        """MetricsAgentin päälogiika."""
        metric_type = input_data.metric_type
        window_size = input_data.window_size

        # 1. Poimi arvot
        values = self._extract_values(input_data.data, metric_type)

        # 2. Sovita ikkuna
        if len(values) > window_size:
            values = values[-window_size:]

        # 3. Laske tilastot
        stats = self._calculate_stats(values)

        # 4. Havai poikkeammat
        anomalies = self._detect_anomalies(values, stats)

        return MetricsOutput(
            success=True,
            result={"metric": metric_type, "samples": len(values), "avg": stats["avg"]},
            message=f"Metriikka analysoitu: {len(values)} näytettä, keskiarvo {stats['avg']:.6f}s.",
            agent_type=self.agent_type,
            metric_name=metric_type,
            values=values,
            stats=stats,
            anomalies=anomalies,
            total_samples=len(values),
        )


__all__ = [
    "MonitoringAgent",
    "MonitoringInput",
    "MonitoringOutput",
    "LoggingAgent",
    "LoggingInput",
    "LoggingOutput",
    "MetricsAgent",
    "MetricsInput",
    "MetricsOutput",
]
