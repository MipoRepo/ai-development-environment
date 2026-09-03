#!/usr/bin/env python3
"""
AIDE CLI — Agenttipohjainen kehitysympäristö

Usage:
    python cli.py init --name MyProject --type python-api
    python cli.py run "Lisää projektiin authentication."
    python cli.py status
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from typer import Typer, Option, Argument, echo
from typer import Exit as TyperExit

# Lisätään projekti polkuun
sys.path.insert(0, str(Path(__file__).parent))

from agents.director import DirectorAgent
from agents.project_manager import ProjectManagerAgent
from agents.requirements_agent import RequirementsAgent
from tools.ai_provider import AIProvider
from workflows.engine import WorkflowEngine, WorkflowState

app = Typer(
    help="AIDE — Agenttipohjainen kehitysympäristö.",
    no_args_is_help=True,
)


@app.command()
def init(
    name: str = Option(..., "--name", "-n", help="Projektin nimi."),
    project_type: str = Option(
        "python-api",
        "--type",
        "-t",
        help="Projektin tyyppi (python-api, web-app, cli).",
    ),
    target_dir: str = Option(
        ".",
        "--dir",
        "-d",
        help="Kohdehakemisto (oletus: nykyinen).",
    ),
    description: str = Option(
        None,
        "--description",
        "-D",
        help="Lyhyt kuvaus projektista.",
    ),
    version: str = Option("0.1.0", "--version", "-v", help="Projektin aloitusversio."),
    author: str = Option(None, "--author", "-a", help="Projektin omistajan nimi."),
):
    """Luo uuden AIDE-projektin rakenteen agenttien avulla."""
    base_path = Path(target_dir) / name
    echo(f"\n[ASETUKSET] Luodaan projekti: {base_path} (tyyppi: {project_type})")

    # 1. Käytä RequirementsAgentia projektiparametrien analysointiin
    req_agent = RequirementsAgent()
    task_desc = f"Luo uusi {project_type}-projekti nimeltä {name}"
    if description:
        task_desc += f", joka on {description}"

    req_result = req_agent.run(
        task=task_desc,
        project_type_hint=project_type,
    )
    echo(f"  [OK] RequirementsAgent havaitsi tyypin: {req_result.detected_type}")
    echo(f"  [OK] Vaatimuksia luodaan: {len(req_result.requirements)}")

    # 2. Muodista projektispeksi
    spec_dict = {
        "name": name,
        "type": project_type,
        "description": description or f"AIDE:lla luotu {project_type}-projekti.",
        "version": version,
        "author": author or "",
        "requirements": {"requirements": req_result.requirements},
        "file_structure": [],
    }

    # 3. Käytä ProjectManagerAgentia projektin luomiseen
    pm_agent = ProjectManagerAgent()
    pm_result = pm_agent.run(
        task=task_desc,
        project_spec=spec_dict,
        project_path=str(base_path),
        create_structure=True,
        generate_docs=True,
    )

    if not pm_result.success:
        echo(f"[VIRHE] Projektin luominen epäonnistui: {pm_result.message}")
        raise TyperExit(1)

    # Tulosta luodut tiedostot
    for f in pm_result.created_files:
        display = f if f.endswith("/") else f"  Luo: {f}"
        echo(f"  Luo: {f}")

    # Luo .env.example projektipuuhun
    env_example = base_path / ".env.example"
    env_example.write_text(
        "# OpenRouter API key (https://openrouter.ai/keys)\n"
        "OPENROUTER_API_KEY=sk-or-v1-placeholder\n"
        "# Default model\n"
        "DEFAULT_MODEL=openai/gpt-4o-mini\n",
        encoding="utf-8",
    )
    echo("  Luo: .env.example")

    echo(f"\n[OK] Projekti '{name}' luodaan onnistuneesti!")
    echo(f"  Siirry hakemistoon: cd {name}")
    echo(f"  Aseta API-avain: cp .env.example .env && edit .env")
    echo(f"  Aja CLI: python cli.py run \"Kuvaa projektin tavoitteet.\"")


@app.command()
def run(
    task: str = Argument(..., help="Tehtävä luonnollisessa kielessä."),
    workflow: str = Option(None, "--workflow", "-w", help="Pakotetaan tietty workflow."),
    dry_run: bool = Option(False, "--dry-run", help="Näytä workflow ilman todellista suoritusta."),
):
    """Aja tehtävä agenttien läpi koko workflow-ketjun."""
    try:
        # 1. Lataa ympäristömuuttujat
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass

        # 2. Alusta komponentit (dry-run ei tarvitse API-avainta)
        try:
            provider = AIProvider()
        except ValueError:
            if dry_run:
                provider = None
            else:
                echo(f"[!] OPENROUTER_API_KEY -ympäristömuuttuja on asetettava tai annettava api_key parametrina.")
                echo("Aseta OpenRouter-API-avain .env-tiedostoon (katso .env.example).")
                raise TyperExit(1)
        director = DirectorAgent(workflow_dir="workflows", ai_provider=provider)
        engine = WorkflowEngine(workflow_dir="workflows")

        echo(f"[ALOITUS] Tehtävä: {task}")

        # 3. Director valitsee workflowin
        director_result = director.run(
            task=task,
            preferred_workflow=workflow,
            priority="high" if "kiire" in task.lower() else "normal",
            max_steps=10,
        )

        if not director_result.success:
            echo(f"[VIRHE] Director-epäonnistui: {director_result.message}")
            raise TyperExit(1)

        echo(f"\n[WORKFLOW] Valittu workflow: {director_result.workflow}")
        echo(f"   Vaiheet: {', '.join(director_result.phases)}")

        # 4. Luo suorituksen
        execution = engine.create_execution(director_result.workflow)

        if dry_run:
            echo("\n[DRY-RUN] Workflowin esikatselu (ei toteuta itseään).")
            echo(director_result.task_breakdown)
            return

        # 5. Suorita workflowi
        echo("\n🔄 Aloitetaan workflow...\n")

        # Dummy handlerit (todellisissa agentit tässä kohdassa)
        def make_handler(phase: str):
            return lambda ctx: f"[placeholder] '{phase}' -vaihe suoritettu."

        handlers = {p: make_handler(p) for p in execution.phases}
        final_execution = engine.execute_all(execution, handlers=handlers)

        # 6. Tulosta tulokset
        echo("\n" + "=" * 60)
        for event in final_execution.events:
            echo(f"  {event}")
        echo("=" * 60)

        if final_execution.state == WorkflowState.COMPLETE:
            echo("\n[OK] Tehtävä valmis!")
        elif final_execution.state == WorkflowState.ERROR:
            echo("\n[VIRHE] Virheworkflowissa!")
            raise TyperExit(1)

    except ValueError as e:
        if "OPENROUTER_API_KEY" in str(e):
            echo(f"\n[!] {e}")
            echo("Aseta OpenRouter-API-avain .env-tiedostoon (katso .env.example).")
            raise TyperExit(1)
        else:
            echo(f"\n[VIRHE] {e}")
            raise TyperExit(1)
    except FileNotFoundError as e:
        echo(f"\n[VIRHE] Tiedostovirhe: {e}")
        raise TyperExit(1)


@app.command()
def status():
    """Näytä projektin tilanne."""
    echo("[TILA] AIDE-projektin tila\n")

    # Tarkista workflowt
    engine = WorkflowEngine(workflow_dir="workflows")
    workflows = engine.list_workflows()
    echo(f"  Saatavilla olevat workflowt: {workflows or 'ei mitään'}")

    # Tarkista .env
    if os.path.exists(".env"):
        echo("  [OK] .env -tiedosto löytyy")
    else:
        echo("  [!]  .env -tiedostoa ei löydy (luo: cp .env.example .env)")

    # Tarkista API-avain
    if os.getenv("OPENROUTER_API_KEY"):
        echo("  [OK] OPENROUTER_API_KEY on asetettu")
    else:
        echo("  [!]  OPENROUTER_API_KEY ei ole asetettu")

    echo(f"\n  Python: {sys.version.split()[0]}")

    # Agentit
    echo("\n  Agentit:")
    echo("    - DirectorAgent       (agents/director.py)")
    echo("    - ProjectManagerAgent (agents/project_manager.py)")
    echo("    - RequirementsAgent   (agents/requirements_agent.py)")
    echo("    - BaseAgent           (agents/base.py)")


@app.callback()
def main(
    version: bool = Option(
        False,
        "--version",
        "-V",
        help="Näytä versio ja poistu.",
    ),
):
    """AIDE CLI — Agenttipohjainen kehitysympäristö."""
    if version:
        echo("AIDE CLI v0.1.0 (alpha 1.2)")
        raise TyperExit(0)


if __name__ == "__main__":
    app()
