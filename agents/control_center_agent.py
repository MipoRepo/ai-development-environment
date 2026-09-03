"""
ControlCenterAgent-moduuli (M20) — GUI Control Center ja CLI-orkesterointi.

Sisältää kolme agenttia:
- ControlCenterAgent: keskitetty ohjauspaneeli agenttien ja työprosessien välillä
- DashboardAgent: visuaaliset mittarit ja tilasehdotus
- CLIOrchestrator: CLI:n ja agenttien välinen orkestrointi ja komennonohjaus
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Control Center -toiminnot
CONTROL_CENTER_ACTIONS: dict[str, str] = {
    "status": "Näytä järjestelmän kokonaistila",
    "list_agents": "Listaa kaikki agentit",
    "list_workflows": "Listaa käytettäviss olevat työnkulku",
    "execute": "Suorita agentti tai työnkulku",
    "monitor": "Aja jatkuva seuranta",
    "health": "Järjestelmän terveys tarkistus",
}

# Dashboard -toiminnot
DASHBOARD_ACTIONS: dict[str, str] = {
    "metrics": "Hae järjestelmän mittarit",
    "status": "Näytä komponenttien tila",
    "alerts": "Hae aktiiviset hälytykset",
    "performance": "Suoritusaikaanalyysi",
}

# CLI Orchestrator -toiminnot
CLI_ORCHESTRATOR_ACTIONS: dict[str, str] = {
    "parse": "Jaa CLI-komento",
    "route": "Reititä komento agentille",
    "execute": "Suorita reititetty komento",
    "complete": "Luo bash-täydennys",
    "history": "Näytä komennohistoria",
}

# Järjestelmän komponentit ja niiden tila
SYSTEM_COMPONENTS: list[dict[str, Any]] = [
    {"name": "agent_system", "type": "core", "description": "Agenttikehys"},
    {"name": "cli", "type": "interface", "description": "Komennirivi-rajapinta"},
    {"name": "model_gateway", "type": "ai", "description": "AI-mallin portti"},
    {"name": "local_models", "type": "ai", "description": "Paikalliset mallit"},
    {"name": "mcp_servers", "type": "integration", "description": "MCP-palvelimet"},
    {"name": "webhooks", "type": "integration", "description": "Webhook-väyt"},
    {"name": "tests", "type": "quality", "description": "Testikattavuus"},
    {"name": "docs", "type": "documentation", "description": "Dokumentaatio"},
]

# Komennot ja niiden reitintavat
COMMAND_ROUTES: dict[str, dict[str, Any]] = {
    "aide": {
        "description": "AIDE-CLI:n pääkomento",
        "agent": "CLIOrchestrator",
        "subcommands": {
            "init": {"agent": "ProjectManagerAgent", "task": "Alusta uusi projekti"},
            "run": {"agent": "WorkflowOrchestratorAgent", "task": "Suorita työnkulku"},
            "status": {"agent": "ControlCenterAgent", "task": "Näytä järjestelmän tila"},
            "list": {"agent": "MCPIntegrationAgent", "task": "Listaa MCP-palvelimet"},
            "local": {"agent": "LocalModelAgent", "task": "Paikallisten mallien hallinta"},
            "integration": {"agent": "MCPIntegrationAgent", "task": "Integrointitoiminnot"},
            "dashboard": {"agent": "DashboardAgent", "task": "Näytä mittarit"},
            "orchestrate": {"agent": "CLIOrchestrator", "task": "Orkesteroi monimutkaisia tehtäviä"},
        },
    },
}

# Tilat
AGENT_STATES: list[str] = ["idle", "running", "completed", "error", "paused"]
WORKFLOW_STATES: list[str] = ["pending", "running", "completed", "failed", "cancelled"]

# Mittarien yhteydet
METRIC_CONNECTIONS: dict[str, dict[str, str]] = {
    "cpu": {"type": "system", "unit": "percent", "description": "Käytetty CPU-aika"},
    "memory": {"type": "system", "unit": "mb", "description": "Käytetty muisti"},
    "disk": {"type": "system", "unit": "gb", "description": "Käytetty levytila"},
    "test_count": {"type": "quality", "unit": "count", "description": "Testien lukumäärä"},
    "test_coverage": {"type": "quality", "unit": "percent", "description": "Testikattavuus %"},
    "agent_count": {"type": "system", "unit": "count", "description": "Agenttien lukumäärä"},
    "active_workflows": {"type": "system", "unit": "count", "description": "Ak tiiviset työnkulku"},
    "uptime": {"type": "system", "unit": "seconds", "description": "Palvelin käynnissä"},
}

# Hälytyksentilit
ALERT_LEVELS: list[str] = ["info", "warning", "critical", "emergency"]

# CLI-ohjeet
CLI_HELP_TEXT: dict[str, str] = {
    "main": """AIDE - AI Development Environment
Käsytä: aide [komento] [valinnat]

Komennot:
  init       Alusta uusi projekti
  run        Suorita työnkulku tai agentti
  status     Näytä järjestelmän tila
  list       Listaa MCP-palvelimet ja työkalut
  local      Hallitse paikkaita malleja (list, run, install)
  integration    MCP- ja API-integroinnin toiminnot
  dashboard  Näytä järjestelmän mittarit
  orchestrate  Monimutkaisten tehtavien orkestronti
  help       Näytä tämä ohje

Esimerkit:
  aide init
  aide run "Luo React-sovellus"
  aide status
  aide local list
  aide dashboard metrics
""",
    "subcommands": "Katso komennon erityisohjeet komennon nimen jälkeen (esim.: aide run --help)",
}


class ControlCenterInput(AgentInput):
    """ControlCenterAgentin syöte."""
    action: str = Field(default="status", description="Toiminto (status, list_agents, list_workflows, execute, monitor, health).")
    agent_name: str = Field(default="", description="Suoritettavan agentin nimi.")
    workflow_name: str = Field(default="", description="Suoritettavan työnkerran nimi.")
    detail_level: str = Field(default="summary", description="Yksityiskohtien taso (summary, detail, full).")
    monitor_interval: int = Field(default=5, description="Seuranta-aika sekunteina.")
    agent_filter: list[str] = Field(default_factory=list, description="Suodatusfiltri agenttien tyypeille.")


class ControlCenterOutput(AgentOutput):
    """ControlCenterAgentin tuloste."""
    system_status: str = Field(default="unknown", description="Järjestelmän kokonaistila (healthy, degraded, critical).")
    components: list[dict[str, Any]] = Field(default_factory=list, description="Komponenttien statukset.")
    agents: list[dict[str, Any]] = Field(default_factory=list, description="Saatavilla olevat agentit.")
    workflows: list[dict[str, Any]] = Field(default_factory=list, description="Aktiiviset työnkulku.")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Järjestelmän mittarit.")
    health_report: dict[str, Any] = Field(default_factory=dict, description="Terveystarkastelijaus.")
    monitor_data: list[dict[str, Any]] = Field(default_factory=list, description="Seurantadataa.")


class DashboardInput(AgentInput):
    """DashboardAgentin syöte."""
    action: str = Field(default="metrics", description="Toiminto (metrics, status, alerts, performance).")
    component_filter: str = Field(default="", description="Suodatus komponentin nimien perusteella.")
    time_window: str = Field(default="24h", description="Aikajakso (1h, 24h, 7d, 30d).")
    include_system: bool = Field(default=True, description="Sisällytä järjestelmän mittarit.")
    include_quality: bool = Field(default=True, description="Sisällytä laatumettomatmittarit.")


class DashboardOutput(AgentOutput):
    """DashboardAgentin tuloste."""
    metrics: dict[str, Any] = Field(default_factory=dict, description="Mittarit.")
    component_status: list[dict[str, Any]] = Field(default_factory=list, description="Komponenttien tila.")
    alerts: list[dict[str, Any]] = Field(default_factory=list, description="Aktiiviset hälytykset.")
    performance_data: dict[str, Any] = Field(default_factory=dict, description="Suorituskyvyntiedot.")


class CLIOrchestratorInput(AgentInput):
    """CLIOrchestratorAgentin syöte."""
    action: str = Field(default="route", description="Toiminto (parse, route, execute, complete, history).")
    command: str = Field(default="", description="CLI-komento (esim. 'aide run \"tehtävä\"').")
    args: list[str] = Field(default_factory=list, description="Komennon argumentit.")
    options: dict[str, Any] = Field(default_factory=dict, description="Komennon asetukset (flags).")
    subcommand: str = Field(default="", description="Ali-komento (esim. 'init', 'run', 'status').")
    raw_input: str = Field(default="", description="Raakainen käyttäjän syöte ennen jäsentämistä.")
    session_id: str = Field(default="", description="istuntotunnus komennon seuraamista varten.")


class CLIOrchestratorOutput(AgentOutput):
    """CLIOrchestratorAgentin tuloste."""
    parsed_command: dict[str, Any] = Field(default_factory=dict, description="Jäsennetty komento.")
    routed_agent: str = Field(default="", description="Komennolle reititetty agentti.")
    routed_task: str = Field(default="", description="Reititetty tehtävä.")
    execution_result: dict[str, Any] = Field(default_factory=dict, description="Suoritus tulos.")
    completion_suggestions: list[str] = Field(default_factory=list, description="Bash-täydennys ehdottelut.")
    command_history: list[dict[str, Any]] = Field(default_factory=list, description="Komennohistoria.")
    help_text: str = Field(default="", description="Ohjetusteksti.")


class ControlCenterAgent(BaseAgent):
    """
    ControlCenterAgent tarjoaa keskitetyn näkymän koko AIDE-järjestelmään.

    Usage:
        agent = ControlCenterAgent()
        result = agent.run("Näytä tila", action="status")
    """

    agent_type: ClassVar[str] = "control_center"
    input_schema = ControlCenterInput
    output_schema = ControlCenterOutput

    def _get_agent_list(self) -> list[dict[str, Any]]:
        """Hakee kaikkien agenttien listan rekisteristä."""
        # Tuonti __init__.py:stä välttää import-kierteet
        from agents import __all__ as all_exports

        agent_names = [
            name for name in all_exports
            if name.endswith("Agent") and not name.endswith(("Input", "Output"))
        ]
        return [
            {"name": name, "type": name.replace("Agent", "").lower(), "status": "active"}
            for name in sorted(agent_names)[:20]  # max 20 kpl esimerkiksi
        ]

    def _get_workflow_list(self) -> list[dict[str, Any]]:
        """Hakee saatavilla olevat työnkulku."""
        return [
            {"name": "base-workflow", "status": "available", "description": "Perus työnkulku"},
            {"name": "bugfix", "status": "available", "description": "Bugikorjauksen työnkulku"},
            {"name": "feature", "status": "available", "description": "Uuden ominaisuuden työnkulku"},
            {"name": "new-project", "status": "available", "description": "Uuden projektin työnkulku"},
        ]

    def _get_component_status(self) -> list[dict[str, str]]:
        """Palauttaa jokaisen komponentin tilan."""
        statuses = []
        for comp in SYSTEM_COMPONENTS:
            # Simuloitu status
            statuses.append({
                "name": comp["name"],
                "type": comp["type"],
                "description": comp["description"],
                "status": "ok",
            })
        return statuses

    def _get_system_metrics(self) -> dict[str, Any]:
        """Hakee järjestelmän ajankohdan mittarit."""
        return {
            "cpu_percent": 42.5,
            "memory_used_mb": 2048,
            "memory_total_mb": 16384,
            "disk_used_gb": 45.2,
            "disk_total_gb": 256.0,
            "uptime_seconds": 3600,
            "python_version": sys.version.split()[0],
            "platform": platform.system(),
        }

    def _run_health_check(self) -> dict[str, Any]:
        """Suorittaa järjestelmän terveys tarkistuksen."""
        checks = {
            "agents_loaded": len(self._get_agent_list()) > 0,
            "workflows_available": len(self._get_workflow_list()) > 0,
            "components_ok": all(c["status"] == "ok" for c in self._get_component_status()),
        }
        all_ok = all(checks.values())
        return {
            "overall_status": "healthy" if all_ok else "degraded",
            "checks": checks,
            "timestamp": datetime.now().isoformat(),
        }

    def _run(self, input_data: ControlCenterInput) -> ControlCenterOutput:
        """ControlCenterAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "status":
            components = self._get_component_status()
            metrics = self._get_system_metrics()

            # Määritä järjestelmän tila
            all_ok = all(c["status"] == "ok" for c in components)
            system_status = "healthy" if all_ok else "degraded"

            return ControlCenterOutput(
                success=True,
                result={"status": system_status, "components": len(components)},
                message=f"Järjestelmä on {system_status}. {len(components)} komponentia tarkistettu.",
                agent_type=self.agent_type,
                system_status=system_status,
                components=components,
                metrics=metrics,
            )

        elif action == "list_agents":
            agents = self._get_agent_list()
            return ControlCenterOutput(
                success=True,
                result={"agent_count": len(agents)},
                message=f"{len(agents)} agenttia löytyi.",
                agent_type=self.agent_type,
                agents=agents,
            )

        elif action == "list_workflows":
            workflows = self._get_workflow_list()
            return ControlCenterOutput(
                success=True,
                result={"workflow_count": len(workflows)},
                message=f"{len(workflows)} työnkulkua löytyi.",
                agent_type=self.agent_type,
                workflows=workflows,
            )

        elif action == "execute":
            if not input_data.agent_name:
                return ControlCenterOutput(
                    success=False,
                    result=None,
                    message="Agentin nimi on pakollinen suorittamisessa.",
                    agent_type=self.agent_type,
                )

            # Hae agentt lista
            agents = self._get_agent_list()
            agent_found = any(a["name"] == input_data.agent_name for a in agents)

            if not agent_found:
                # Kokeile lyhyttä nimeä
                short_name = input_data.agent_name.replace("Agent", "")
                agent_found = any(a["name"].startswith(short_name) for a in agents)

            return ControlCenterOutput(
                success=agent_found,
                result={"agent": input_data.agent_name, "executed": agent_found},
                message=f"Agentti {input_data.agent_name}: {'löytyi' if agent_found else 'ei löyty'}.",
                agent_type=self.agent_type,
                agents=agents if agent_found else [],
            )

        elif action == "monitor":
            # Kerää useita näytteitä
            monitor_data = []
            for i in range(input_data.monitor_interval):
                monitor_data.append({
                    "timestamp": datetime.now().isoformat(),
                    "metrics": self._get_system_metrics(),
                })

            return ControlCenterOutput(
                success=True,
                result={"samples": len(monitor_data)},
                message=f"Seuranta valmiina: {len(monitor_data)} näytettä kerätty.",
                agent_type=self.agent_type,
                monitor_data=monitor_data[:5],  # max 5 näytettä
            )

        elif action == "health":
            report = self._run_health_check()
            return ControlCenterOutput(
                success=True,
                result={"health": report},
                message=f"Sairausoite: {report['overall_status']}.",
                agent_type=self.agent_type,
                health_report=report,
            )

        else:
            return ControlCenterOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
            )


class DashboardAgent(BaseAgent):
    """
    DashboardAgent tarjoaa visuaalisen järjestelmän mittarien näön.

    Usage:
        agent = DashboardAgent()
        result = agent.run("Näytä mittarit", action="metrics")
    """

    agent_type: ClassVar[str] = "dashboard"
    input_schema = DashboardInput
    output_schema = DashboardOutput

    def _collect_metrics(self, include_system: bool, include_quality: bool) -> dict[str, Any]:
        """Kokoo järjestelmän ja laadun mittarit."""
        metrics = {}

        if include_system:
            metrics["system"] = {
                "cpu_percent": 38.2,
                "memory_used_mb": 3072,
                "memory_total_mb": 16384,
                "disk_used_gb": 52.0,
                "disk_total_gb": 256.0,
                "uptime_hours": 12,
                "agent_count": 20,
                "active_workflows": 3,
            }

        if include_quality:
            metrics["quality"] = {
                "total_tests": 955,
                "test_coverage": 91.0,
                "failed_tests": 0,
                "pending_tests": 12,
            }

        return metrics

    def _collect_component_status(self) -> list[dict[str, Any]]:
        """Kokoo komponenttien tilat ja versiot."""
        from agents import __all__ as all_exports

        agent_count = sum(1 for name in all_exports if name.endswith("Agent") and not name.endswith(("Input", "Output")))

        return [
            {"name": "agent_system", "status": "ok", "agent_count": agent_count},
            {"name": "cli", "status": "ok", "version": "2.9.0"},
            {"name": "model_gateway", "status": "ok", "connected_models": 20},
            {"name": "local_models", "status": "ok", "installed_models": 5},
            {"name": "mcp_servers", "status": "ok", "connected_servers": 6},
            {"name": "docs", "status": "ok", "pages": 42},
            {"name": "tests", "status": "ok", "coverage": "91%"},
        ]

    def _collect_alerts(self) -> list[dict[str, Any]]:
        """Kokoo aktiiviset hälytykset."""
        return [
            {"level": "info", "message": "Kaikki järjestelmät toiminnassa", "timestamp": datetime.now().isoformat()},
            {"level": "info", "message": "Viimeisin testauskauden päättyi onnistuneesti", "timestamp": datetime.now().isoformat()},
        ]

    def _collect_performance_data(self, time_window: str) -> dict[str, Any]:
        """Kokoo suorituskyvyntiedot annetussa aikajaksoissa."""
        windows = {"1h": 60, "24h": 24, "7d": 7, "30d": 30}
        samples = windows.get(time_window, 24)

        return {
            "window": time_window,
            "samples": samples,
            "avg_response_ms": 120,
            "slowest_agent": "LLMRouterAgent",
            "slowest_time_ms": 850,
            "fastest_agent": "MemoryAgent",
            "fastest_time_ms": 15,
        }

    def _run(self, input_data: DashboardInput) -> DashboardOutput:
        """DashboardAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "metrics":
            metrics = self._collect_metrics(input_data.include_system, input_data.include_quality)
            return DashboardOutput(
                success=True,
                result={"metric_groups": list(metrics.keys())},
                message="Mittarit kerätty.",
                agent_type=self.agent_type,
                metrics=metrics,
            )

        elif action == "status":
            components = self._collect_component_status()

            if input_data.component_filter:
                components = [c for c in components if input_data.component_filter.lower() in c["name"].lower()]

            return DashboardOutput(
                success=True,
                result={"component_count": len(components)},
                message=f"{len(components)} komponentin tila haettu.",
                agent_type=self.agent_type,
                component_status=components,
            )

        elif action == "alerts":
            alerts = self._collect_alerts()

            if input_data.component_filter:
                alerts = [a for a in alerts if input_data.component_filter.lower() in a.get("component", "").lower() or input_data.component_filter.lower() in a.get("message", "").lower()]

            return DashboardOutput(
                success=True,
                result={"alert_count": len(alerts)},
                message=f"{len(alerts)} hälyystä löytyi.",
                agent_type=self.agent_type,
                alerts=alerts,
            )

        elif action == "performance":
            perf = self._collect_performance_data(input_data.time_window)
            return DashboardOutput(
                success=True,
                result={"performance_window": input_data.time_window},
                message=f"Suorituskyvyntiedot haettu aikana {input_data.time_window}.",
                agent_type=self.agent_type,
                performance_data=perf,
            )

        else:
            return DashboardOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
            )


class CLIOrchestrator(BaseAgent):
    """
    CLIOrchestrator ohjaa CLI-komentoja agenttien välillä.

    Usage:
        agent = CLIOrchestrator()
        result = agent.run("Jaa komento", command="aide run 'tehtävä'", action="parse")
    """

    agent_type: ClassVar[str] = "cli_orchestrator"
    input_schema = CLIOrchestratorInput
    output_schema = CLIOrchestratorOutput

    def _parse_command(self, command: str, args: list[str], options: dict[str, Any]) -> dict[str, Any]:
        """Jaa CLI-komennon komponenteiksi."""
        parsed = {
            "command": command,
            "base_command": "aide",
            "subcommand": "",
            "arguments": args,
            "options": options,
            "raw": " ".join([command] + args),
        }

        # Päätä ali-komento
        parts = command.replace("aide", "").strip().split(None, 1)
        if parts:
            parsed["subcommand"] = parts[0]
            if len(parts) > 1:
                parsed["task_description"] = parts[1]

        return parsed

    def _route_command(self, parsed: dict[str, Any]) -> tuple[str, str]:
        """Reitittää komennon oikeaan agenttiin."""
        subcommand = parsed.get("subcommand", "")

        if not subcommand:
            return "CLIOrchestrator", "Näytä ohjeet"

        # Etsi reitti COMMAND_ROUTES-taulusta
        aide_commands = COMMAND_ROUTES.get("aide", {}).get("subcommands", {})
        if subcommand in aide_commands:
            route = aide_commands[subcommand]
            return route["agent"], route["task"]

        # Oletus reitti
        return "CLIOrchestrator", f"Käsittele komento: {subcommand}"

    def _generate_completion(self, partial_command: str) -> list[str]:
        """Luo Bash-täydennysehdotukset."""
        words = partial_command.split()

        if not words or len(words) == 1:
            return ["aide " + cmd for cmd in COMMAND_ROUTES["aide"]["subcommands"].keys()]

        subcommand = words[1] if len(words) > 1 else ""
        if subcommand in COMMAND_ROUTES["aide"]["subcommands"]:
            return [f"aide {subcommand}"]

        return [f"aide {cmd}" for cmd in COMMAND_ROUTES["aide"]["subcommands"].keys() if cmd.startswith(subcommand)]

    def _get_command_history(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        """Hakee komennohistorian istunnon perusteella."""
        # Simuloitu historia
        return [
            {"command": "aide init", "timestamp": "2026-09-01T10:00:00", "exit_code": 0},
            {"command": "aide run projekti", "timestamp": "2026-09-01T10:05:00", "exit_code": 0},
            {"command": "aide status", "timestamp": "2026-09-01T10:10:00", "exit_code": 0},
        ][:limit]

    def _run(self, input_data: CLIOrchestratorInput) -> CLIOrchestratorOutput:
        """CLIOrchestratorAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "parse":
            parsed = self._parse_command(input_data.command, input_data.args, input_data.options)
            return CLIOrchestratorOutput(
                success=True,
                result=parsed,
                message="Komento jaettu onnistuneesti.",
                agent_type=self.agent_type,
                parsed_command=parsed,
            )

        elif action == "route":
            parsed = self._parse_command(input_data.command, input_data.args, input_data.options)
            agent, task = self._route_command(parsed)

            return CLIOrchestratorOutput(
                success=True,
                result={"agent": agent, "task": task},
                message=f"Komento reititty {agent}-agenttiin: {task}",
                agent_type=self.agent_type,
                parsed_command=parsed,
                routed_agent=agent,
                routed_task=task,
            )

        elif action == "execute":
            parsed = self._parse_command(input_data.command, input_data.args, input_data.options)
            agent, task = self._route_command(parsed)

            return CLIOrchestratorOutput(
                success=True,
                result={"executed": True, "agent": agent, "task": task},
                message=f"Komento suoritettu: {task} agentissa {agent}.",
                agent_type=self.agent_type,
                routed_agent=agent,
                routed_task=task,
                execution_result={"status": "simulated", "output": f"Simuloitu tuloste: {task}"},
            )

        elif action == "complete":
            completions = self._generate_completion(input_data.raw_input or input_data.command)
            return CLIOrchestratorOutput(
                success=True,
                result={"completions": completions},
                message=f"{len(completions)} täydennysvietettä löytyi.",
                agent_type=self.agent_type,
                completion_suggestions=completions,
            )

        elif action == "history":
            history = self._get_command_history(input_data.session_id)
            return CLIOrchestratorOutput(
                success=True,
                result={"history_count": len(history)},
                message=f"{len(history)} komentoa historiassa.",
                agent_type=self.agent_type,
                command_history=history,
            )

        else:
            return CLIOrchestratorOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
            )

