"""
RequirementsAgent (M2) — analysoi käyttäjän kuvauksen ja luo vaatimukset.

Toiminnot:
1. Ottaa vastaan projektikuvauksen luonnollisessa kielessä.
2. Generoi rakenteelliset vaatimukset (Requirement-oliot).
3. Tuottaa .env-, architecture- ja testing-strategiat.
"""

from __future__ import annotations

import re
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent
from schemas.project import Priority, ProjectType, Requirement, RequirementList


# Sanat, jotka auttavat tunnistama kehitystyypin
TYPE_KEYWORDS: dict[ProjectType, list[str]] = {
    ProjectType.PYTHON_API: ["api", "fastapi", "flask", "django", "rest", "endpoint", "backend"],
    ProjectType.WEB_APP: ["web", "react", "next", "vue", "angular", "frontend", "sivu"],
    ProjectType.CLI: ["cli", "command line", "terminal", "cmd", "skripti", "skripti"],
    ProjectType.LIBRARY: ["kirjasto", "library", "moduuli", "package"],
    ProjectType.SCRIPT: ["skripti", "script", "automatiso"],
}

# Prioriteetin tunnistus
PRIORITY_KEYWORDS: dict[Priority, list[str]] = {
    Priority.LOW: ["pieni", "optimointi", "lisä", "bonus"],
    Priority.HIGH: ["tärkeä", "kriittinen", "pakollista", "välttämätön", "kaatuu", "virhe"],
    Priority.CRITICAL: ["kaatuu", "turvallisuus", "tietoturva", "auth", "kirjautumis", "kritiikki"],
}


class RequirementsInput(AgentInput):
    """RequirementsAgentin syöte."""

    project_type_hint: Optional[str] = Field(default=None, description="Vihje projektitavasta (esim. 'python-api').")
    existing_context: dict[str, Any] = Field(default_factory=dict, description="Olemassa oleva projekti-konteksti.")


class RequirementsOutput(AgentOutput):
    """RequirementsAgentin tuloste."""

    detected_type: str = Field(default="", description="Havaittu projekti-tyyppi.")
    requirements: list[dict[str, Any]] = Field(default_factory=list, description="Generoidut vaatimukset (dict-muodossa).")
    requirement_summary: str = Field(default="", description="Tiivistelmä vaatimuksista.")


class RequirementsAgent(BaseAgent):
    """
    RequirementsAgent analysoi käyttäjän kuvauksen ja luo vaatimukset.

    Usage:
        agent = RequirementsAgent()
        result = agent.run("Luo uusi FastAPI-sovellus, jossa käyttäjät voivat kirjautua.")
    """

    agent_type: str = "requirements"
    input_schema = RequirementsInput
    output_schema = RequirementsOutput

    def detect_project_type(self, task: str, hint: Optional[str] = None) -> ProjectType:
        """Havaitsee projektin tyypin tehtävätekstistä."""
        if hint:
            for pt in ProjectType:
                if hint.lower() in pt.value.lower():
                    return pt

        task_lower = task.lower()
        scored: dict[ProjectType, int] = {}
        for ptype, keywords in TYPE_KEYWORDS.items():
            matches = sum(1 for kw in keywords if kw in task_lower)
            if matches > 0:
                scored[ptype] = matches

        if scored:
            # Valitse eniten osumaa:
            best = max(scored, key=scored.get)
            return best

        return ProjectType.UNKNOWN

    def detect_priority(self, text: str) -> Priority:
        """Havaitsee prioriteetin vaatimustekstistä."""
        text_lower = text.lower()
        scores: dict[Priority, int] = {}
        for priority, keywords in PRIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[priority] = scores.get(priority, 0) + 1
        if scores:
            # CRITICAL > HIGH > NORMAL > LOW
            priority_order = {Priority.CRITICAL: 4, Priority.HIGH: 3, Priority.NORMAL: 2, Priority.LOW: 1}
            best = max(scores, key=lambda p: priority_order.get(p, 0) * scores[p])
            return best
        return Priority.NORMAL

    def parse_requirements(self, task: str) -> RequirementList:
        """
        Parsii vaatimukset käyttäjän kuvauksesta.

        Käytetään perusavainsanalistaa ja erottimia:
        - Eritetty toiminnot: verbit (lisää, toteuta, kirjautuma, testata, jne.)
        - Erillätyt toiminnot: pisteet / ja-toistot (;)
        """
        req_list = RequirementList()
        req_id = 1

        # Jako osiin rekisteröinti- ja erottimilla, jotka rikkoivat lauseet
        # Käytetään pistettä, puolipistettä ja "ja"-sanoja
        sentences = re.split(r"[.;]| ja | sekä |-,", task)
        sentences = [s.strip() for s in sentences if s.strip()]

        if not sentences:
            sentences = [task]

        for sentence in sentences:
            sentence_lower = sentence.lower()

            # Ohita liian yleiset lauseet
            if len(sentence) < 10 and "projekti" not in sentence_lower:
                continue

            title = self._extract_title(sentence)
            tags = self._extract_tags(sentence)
            priority = self.detect_priority(sentence)

            req = Requirement(
                id=f"REQ-{req_id:03d}",
                title=title,
                description=sentence if len(sentence) > 15 else "",
                priority=priority,
                tags=tags,
            )
            req_list.add(req)
            req_id += 1

        # Jos emme löytäneet mitään, luodaan yleinen vaatimus
        if not req_list.requirements:
            req_list.add(Requirement(
                id="REQ-001",
                title="Perustoiminnallisuus",
                description=task,
                priority=self.detect_priority(task),
                tags=["general"],
            ))

        return req_list

    def _extract_title(self, sentence: str) -> str:
        """
        Poimii otsikon lauseen ensimmäisestä osasta.

        Strategia:
        1. Poimi ensimmäinen 1-3 sanaa.
        2. Poista yleiset sanat (kuten, jossa, jotta).
        3. Muotoile Title Caseen ensimmäisen sanan jälkeen.
        """
        stop_words = {"kun", "joka", "jotta", "koska", "jos", "myös", "tai", "ei", "on", "ja", "sekä"}
        words = sentence.split()
        # Poimi ensimmäinen merkityksellinen osuus
        meaningful = []
        for w in words[:5]:
            w_clean = w.strip(".,;:!?\"'()")
            if w_clean and w_clean.lower() not in stop_words:
                meaningful.append(w_clean)
            if len(meaningful) >= 3:
                break

        if not meaningful:
            return "Vaatimus"

        title = " ".join(meaningful).capitalize()
        if len(title) > 60:
            title = title[:57] + "..."
        return title

    def _extract_tags(self, sentence: str) -> list[str]:
        """Pakkaa tunnistetut tagit lauseesta."""
        tags = []
        sentence_lower = sentence.lower()

        # Tagit avainsanojen perusteella
        tag_map = {
            "auth": ["kirjautumis", "login", "reigister", "auth", "token", "sessio"],
            "api": ["api", "endpoint", "rest", "http", "pyyntö"],
            "database": ["tietokanta", "tietokannan", "sqlite", "postgres", "mysql"],
            "ui": ["käyttöliittymä", "näytön", "komponentti", "näkymä", "sivu"],
            "test": ["testi", "testata", "testaus", "kattavuus"],
            "security": ["turvallisuus", "salaus", "salaus", "ssl", "oauth"],
            "performance": ["nopeus", "suorituskyky", "optimointi", "latkus"],
            "docs": ["dokumentaatio", "dokumentoida", "ohje"],
        }

        for tag, keywords in tag_map.items():
            if any(kw in sentence_lower for kw in keywords):
                tags.append(tag)

        if not tags:
            tags.append("general")

        return tags

    def _run(self, input_data: RequirementsInput) -> RequirementsOutput:
        """RequirementsAgentin päälogiikka."""
        task = input_data.task
        hint = input_data.project_type_hint

        # 1. Havaitse projekti-tyyppi
        detected_type = self.detect_project_type(task, hint)

        # 2. Parsi vaatimukset
        req_list = self.parse_requirements(task)

        # 3. Generoi tiivistelmä
        summary = req_list.to_markdown()

        # 4. Lisää projektipohja (jos projekti on tunnettu tyyppi)
        template = None
        type_str = detected_type.value

        if detected_type == ProjectType.PYTHON_API and "fastapi" in task.lower():
            template = "fastapi"
        elif detected_type == ProjectType.WEB_APP and "next" in task.lower():
            template = "nextjs"

        return RequirementsOutput(
            success=True,
            result={
                "detected_type": type_str,
                "requirement_count": len(req_list.requirements),
                "template": template,
            },
            message=summary,
            agent_type=self.agent_type,
            detected_type=type_str,
            requirements=[r.model_dump() for r in req_list.requirements],
            requirement_summary=summary,
        )


__all__ = ["RequirementsAgent", "RequirementsInput", "RequirementsOutput"]
