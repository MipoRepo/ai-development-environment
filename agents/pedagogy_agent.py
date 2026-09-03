"""
PedagogyAgent-moduuli (M11) — oppiminen ja käyttäjän ohjaus ohjelmistokehityksessä.

Sisältää neljää agenttia:
- MentorAgent: opettaja-agentti, joka opettaa käyttäjälle ohjelmistokehitystä.
- ExplainerAgent: selittää koodin ja konseptit ymmärrettävästi.
- PedagogyAgent: suunnittelee oppimisalan suunnitelmat.
- ContentDesignerAgent: luo oppimismateriaalia (harjoitukset, selitykset).
"""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Oppimistasot ja niiden kuvaukset
LEARNING_LEVELS: dict[str, dict[str, Any]] = {
    "beginner": {
        "name": "ALOITTAJA",
        "description": "Tunteedukeneet perusasiat (muuttujat, funktiot, luokat).",
        "teaching_style": "askel askeleelta, runsa esimerkkejä, välttää monimutkainen syntaksi",
        "assumed_knowledge": "Perus-tietokoneen käyttö, tiedostojärjestelmä",
    },
    "intermediate": {
        "name": "KOKEILEVA",
        "description": "Ymmärtää moduulit, paketit ja frameworkit. Etsii parannuksia.",
        "teaching_style": "projektien läpi, paransiksista, koodin refaktoroinnissa",
        "assumed_knowledge": "Funktiot, luokat, moduulit, perus-OOP",
    },
    "advanced": {
        "name": "EDISTYNYT",
        "description": "Käsittelee suuria järjestelmiä, suunnittelumalleja ja suorituskykyä.",
        "teaching_style": "suunnittelumallit, korkean suorituskyvyn, jakaminen osiin",
        "assumed_knowledge": "Kaikki perus- ja keskiverto-taidot, frameworkit",
    },
}

# Oppimisalan aihepiirit
LEARNING_TOPICS: dict[str, list[str]] = {
    "python": [
        "Perusmuoto ja syntaksi",
        "Tietotyypit ja muuttujat",
        "Funktiot ja moduulit",
        "Luokat ja olio-ohjelmointi",
        "Poissaltuminen ja virheenkäsittely",
        "Tiedostojen lukeminen ja kirjoittaminen",
        "Kirjastot ja pip",
        "Testaus (pytest)",
        "Type-huomautukset (type hints)",
        "Async-ohjelmointi",
        "Suunnittelumallit",
    ],
    "javascript": [
        "Perusmuoto ja muuttujat",
        "Funktiot ja nolla-arvoisuus",
        "DOM-manipulaatio",
        "Promiseit ja async/await",
        "Moduulit ja npm",
        "Frontend-kehitys (React/Vue/Angular)",
        "Backend (Node.js)",
        "Testaus (Jest/Vitest)",
    ],
    "devops": [
        "Docker-perusteet",
        "Docker-komposit",
        "CI/CD-periaatteet",
        "GitHub Actions",
        "Kubernetes-perusteet",
        "Infra-koodi (IaC)",
        "Monitoring ja lokiointi",
        "Cloud (AWS/GCP/Azure)",
    ],
    "security": [
        "Syötevahvistus",
        "Salaus perusteet",
        "OAuth ja JWT",
        "SAST ja DAST",
        "Container-turvallisuus",
        "Zero Trust -malli",
    ],
}

# Selostusgilit eri tasolle
EXPLANATION_PROMPTS: dict[str, str] = {
    "beginner": "Selitä tämä koodi aloittelijalle. Käytä yksinkertaisia sanoja, selitä jokainen rivi, ja anna esimerkki miten koodi voitaisiin käyttää.",
    "intermediate": "Selitä tämä koodi keskiverto-taitotasolle. Keskustele suunnittelusta, vaihtoehdoista ja mahdollisista parannuksista.",
    "advanced": "Analysoi tämä koodi edistyneenä. Poimi suunnittelumallit, suorituksen aikarajat ja mahdolliset pullonkaulat.",
}

# Oppimisharjoitukset projektin perusteella
EXERCISE_TYPES: dict[str, list[str]] = {
    "debugging": ["Etsi virhe tästä koodista", " Korjaa syntaksivirhe", " Paranna virheenkäsittelyä"],
    "refactoring": ["Tiivistä tämä funktio", " Poista käytämättomat importit", " Jakaa tämä luokka osiin"],
    "extension": ["Lisää uusi ominaisuus", " Laajenna tätä funktiota", " Lisää testit"],
    "security": [" Lisää syötevahvistus", " Salaa arkiset tiedot", " Varmista oikeudet"],
    "documentation": [" Kirjoita docstringi", " Lisää tyyppihuomautukset", " Päivitä README"],
}

# Oppimisasuunnitelman vaiheet
CURRICULUM_PHASES = [
    "Tavoite asetelma",
    "Resurssit ja aikataulu",
    "Moduulit ja alix",
    "Harjoitukset ja testaus",
    "Arviointi ja palaute",
]


class MentorAgentInput(AgentInput):
    """MentorAgentin syöte."""

    skill_level: str = Field(
        default="beginner",
        description="Käyttäjän taitotaso (beginner, intermediate, advanced).",
    )
    topic: str = Field(default="python", description="Oppiminen aihe (python, javascript, devops, security).")
    learning_speed: str = Field(
        default="moderate",
        description="Oppimisnopeus (slow, moderate, fast).",
    )
    user_goals: list[str] = Field(default_factory=list, description="Käyttäjän oppimis-tavoitteet.")


class MentorAgentOutput(AgentOutput):
    """MentorAgentin tuloste."""

    lesson_plan: dict[str, Any] = Field(default_factory=dict, description="Oppimissuunnitelma.")
    resources: list[str] = Field(default_factory=list, description="Suositellut resurssit.")
    estimated_weeks: int = Field(default=4, description="Arvioitu oppimisaika viikoissa.")
    next_steps: list[str] = Field(default_factory=list, description="Seuraavat askeleet.")


class ExplainerAgentInput(AgentInput):
    """ExplainerAgentin syöte."""

    code: str = Field(default="", description="Selitettävä koodi suoraan.")
    file_path: Optional[str] = Field(default=None, description=" Tiedosto selitettäväksi.")
    skill_level: str = Field(default="beginner", description="Taso selitykselle (beginner, intermediate, advanced).")
    concept: Optional[str] = Field(default=None, description="Selitettävä käsittein (esim. 'recursion', 'decorator').")


class ExplainerAgentOutput(AgentOutput):
    """ExplainerAgentin tuloste."""

    explanation: str = Field(default="", description="Selostus käyttämättömälle tasolla.")
    code_breakdown: list[dict[str, Any]] = Field(default_factory=list, description="Koodin kohta analyysi.")
    key_concepts: list[str] = Field(default_factory=list, description="Tärkeimmät käsitteet.")
    analogies: list[str] = Field(default_factory=list, description="Selitysanalogiikat.")


class PedagogyAgentInput(AgentInput):
    """PedagogyAgentin syöte."""

    topic: str = Field(default="python", description="Oppimisalan aihe.")
    skill_level: str = Field(default="beginner", description="Käyttäjän taitotaso.")
    duration_weeks: int = Field(default=4, description="Toivottu kesto viikoissa.")
    include_exercises: bool = Field(default=True, description="Sisällytä harjoitukset suunnitelmaan.")
    user_background: str = Field(default="none", description="Käyttäjän taustaosaaminen (none, basic, some, strong).")


class PedagogyAgentOutput(AgentOutput):
    """PedagogyAgentin tuloste."""

    curriculum: dict[str, Any] = Field(default_factory=dict, description="Oppimissuunnitelma moduuleina.")
    phases: list[str] = Field(default_factory=list, description="Suunnitelman vaiheet.")
    total_exercises: int = Field(default=0, description="Harjoitusten kokonaismäärä.")


class ContentDesignerAgentInput(AgentInput):
    """ContentDesignerAgentin syöte."""

    content_type: str = Field(
        default="explanation",
        description="Tuotteen tyyppi (explanation, exercise, quiz, tutorial, cheat_sheet).",
    )
    topic: str = Field(default="python", description="Sisällön aihe.")
    skill_level: str = Field(default="beginner", description="Taso sisällölle.")
    context_text: str = Field(default="", description="Lisäkonteksti generoinnissa (esim. koodinpätkä tai kuvaus).")
    num_items: int = Field(default=5, description="Tuotettaiden määrä (esim. kysymysten määrä quizissä).")


class ContentDesignerAgentOutput(AgentOutput):
    """ContentDesignerAgentin tuloste."""

    content: list[dict[str, Any]] = Field(default_factory=list, description="Luotu sisältö.")
    content_type: str = Field(default="", description="Tuotteen tyyppi.")
    total_items: int = Field(default=0, description="Tuotettaiden kokonaismäärä.")


class MentorAgent(BaseAgent):
    """
    MentorAgent opettaa käyttäjälle ohjelmistokehitystä.

    Usage:
        agent = MentorAgent()
        result = agent.run("Opeta python-perusteet", skill_level="beginner", topic="python")
    """

    agent_type: str = "mentor"
    input_schema = MentorAgentInput
    output_schema = MentorAgentOutput

    def _calculate_estimated_weeks(self, skill_level: str, learning_speed: str, user_goals: list[str]) -> int:
        """Laskee arvioidun oppimisaian."""
        base = {"beginner": 8, "intermediate": 6, "advanced": 4}.get(skill_level, 6)
        speed_mult = {"slow": 1.5, "moderate": 1.0, "fast": 0.7}.get(learning_speed, 1.0)
        goal_bonus = len(user_goals) * 0.5
        return max(1, int((base + goal_bonus) * speed_mult))

    def _get_resources(self, topic: str) -> list[str]:
        """Palauttaa suositut resurssit aiheelle."""
        resources_map: dict[str, list[str]] = {
            "python": [
                "Python-virallinen dokusivu (python.org)",
                "Automate the Boring Stuff with Python",
                "Python Crash Course",
                "Real Python -opas",
            ],
            "javascript": [
                "MDN Web Docs",
                "JavaScript.info",
                "Eloquent JavaScript",
                "You Don't Know JS -kirja",
            ],
            "devops": [
                "Docker-dokumentaatio",
                "Kubernetes -opas",
                "GitHub Actions -dokumentaatio",
                "Terraform -opas",
            ],
            "security": [
                "OWASP Top 10",
                "PortSwigger Web Security Testaus",
                "HackTheBox -haasteet",
                "Security Journey",
            ],
        }
        return resources_map.get(topic, ["Dokumentaatio", "Esimerkit", "Harjoitukset"])

    def _build_lesson_plan(self, topic: str, skill_level: str, duration_weeks: int) -> dict[str, Any]:
        """Rakentaa oppimissuunnitelman."""
        topics = LEARNING_TOPICS.get(topic, LEARNING_TOPICS["python"])
        level_info = LEARNING_LEVELS.get(skill_level, LEARNING_LEVELS["beginner"])

        weeks_content = []
        topics_per_week = max(1, len(topics) // duration_weeks)

        for i in range(duration_weeks):
            start_idx = i * topics_per_week
            end_idx = min(start_idx + topics_per_week, len(topics))
            week_topics = topics[start_idx:end_idx] if start_idx < len(topics) else [topics[-1]]

            weeks_content.append({
                "week": i + 1,
                "topics": week_topics,
                "exercises": len(week_topics) * 2,
                "reading": f"{len(week_topics)} artikkelia/aihetta",
            })

        return {
            "topic": topic,
            "level": level_info["name"].strip(),
            "level_description": level_info["description"],
            "teaching_style": level_info["teaching_style"],
            "assumed_knowledge": level_info["assumed_knowledge"],
            "weeks": weeks_content,
        }

    def _run(self, input_data: MentorAgentInput) -> MentorAgentOutput:
        """MentorAgentin päälogiika."""
        skill_level = input_data.skill_level
        topic = input_data.topic
        learning_speed = input_data.learning_speed
        user_goals = input_data.user_goals

        # 1. Laske aika
        estimated_weeks = self._calculate_estimated_weeks(skill_level, learning_speed, user_goals)

        # 2. Hae resurssit
        resources = self._get_resources(topic)

        # 3. Rakenna suunnitelma
        lesson_plan = self._build_lesson_plan(topic, skill_level, estimated_weeks)

        # 4. Seuraavat askeleet
        next_steps = [
            f"Aloita viikko 1: {lesson_plan['weeks'][0]['topics'][0]}",
            "Valitse yksi suositellusta resurssista",
            "Aseta viikkotavoite (esim. 5h/viikko)",
            "Merkitse edmistymisen kirjanpitoon",
        ]

        return MentorAgentOutput(
            success=True,
            result={"estimated_weeks": estimated_weeks, "topic": topic, "level": skill_level},
            message=f"Oppimissuunnitelma luodaan aiheelle '{topic}' ({skill_level}-taso, {estimated_weeks} viikkoa).",
            agent_type=self.agent_type,
            lesson_plan=lesson_plan,
            resources=resources,
            estimated_weeks=estimated_weeks,
            next_steps=next_steps,
        )


class ExplainerAgent(BaseAgent):
    """
    ExplainerAgent selittää koodin ja käsitteet ymmärrettävästi.

    Usage:
        agent = ExplainerAgent()
        result = agent.run("Selitä tämä koodi", code="def fib(n): ...", skill_level="beginner")
    """

    agent_type: str = "explainer"
    input_schema = ExplainerAgentInput
    output_schema = ExplainerAgentOutput

    def _explain_code(self, code: str, skill_level: str) -> str:
        """Generoi selityksen koodille tietysti tasosta."""
        style = EXPLANATION_PROMPTS.get(skill_level, EXPLANATION_PROMPTS["beginner"])

        # Analysoi AST-koodin
        try:
            tree = ast.parse(code)
            functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        except SyntaxError:
            functions = []
            classes = []

        # Muodosta selitys
        if skill_level == "beginner":
            explanation = (
                f"Tämä koodi sisältää {len(functions)} funktion ja {len(classes)} luokan.\n\n"
                f"Funkiot: {', '.join(functions) if functions else 'ei yhtään'}\n"
                f"Luokat: {', '.join(classes) if classes else 'ei yhtään'}\n\n"
                f"Perusajatus: Koodi suorittaa annetut tehtävät yksitellen "
                f"kutsuen funktioita ja käyttämällä luokkia."
            )
        elif skill_level == "intermediate":
            explanation = (
                f"Koodin struktuuri: {len(functions)} funktiota, {len(classes)} luokkaa.\n\n"
                f"Suunnittelu: Koodi on jaettu pieniin, yksitoimiviin funkintoihin, "
                f"mikä seura  on hyvä ohjelmointikäytäntö (SRP).\n"
                f"Funktiot: {', '.join(functions) if functions else 'ei yhtäinkään'}\n"
                f"Luokat tarjoavat abstraktion ja koodin kääntäisyyttä."
            )
        else:  # advanced
            explanation = (
                f"Monimutkaisuus: {len(functions)} funktiota, {len(classes)} luokkaa.\n\n"
                f"Suunnittelukuvioita: Tämä on modulaarinen rakenne, jossa "
                f"funktiot ovat käännettävissä ja testattavissa erikseen.\n"
                f"Suoritusajan optimointi: Funktiokutsut ovat O(1) keskimäärin, "
                f"mutta suluissa saattaa olla korkeita monimutkaisia operaatioita."
            )

        return explanation

    def _break_down_code(self, code: str) -> list[dict[str, Any]]:
        """Purkaa koodin riveistä analyysiä varten."""
        # Jos koodissa on syntaksivirhe, palauta tyhjä lista
        try:
            ast.parse(code)
        except SyntaxError:
            return []

        breakdown: list[dict[str, Any]] = []
        for i, line in enumerate(code.splitlines(), 1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            breakdown.append({
                "line": i,
                "code": stripped[:80],
                "type": self._classify_line(stripped),
            })

        return breakdown[:30]  # Rajoita 30:ään

    def _classify_line(self, line: str) -> str:
        """Luokittelee koodirivin tyypin."""
        if line.startswith("def "):
            return "funktio"
        elif line.startswith("class "):
            return "luokka"
        elif line.startswith("if ") or line.startswith("elif ") or line.startswith("else:"):
            return "ehto"
        elif line.startswith("for ") or line.startswith("while "):
            return "silmukka"
        elif line.startswith("import ") or line.startswith("from "):
            return "importti"
        elif line.startswith("return"):
            return "paluuarvo"
        elif line.startswith("print(") or line.startswith("echo("):
            return "tulostus"
        elif "=" in line:
            return "sijoitus"
        else:
            return "muu"

    def _generate_analogies(self, code: str, skill_level: str) -> list[str]:
        """Luo analogioita koodin ymmärtämiseen."""
        analogies: list[str] = []

        # yritä löytyä yhteisiä kuvioita
        code_lower = code.lower()

        if "for" in code_lower or "while" in code_lower:
            analogies.append("Silmukka on kuin resepti — toistat samat askeleet kunnes ehje täyttyy.")
        if "if" in code_lower:
            analogies.append("Ehto on kuin valitsijavalo — jos ehto täyttyy, valitset tien A, muuten tien B.")
        if "def" in code_lower:
            analogies.append("Funktio on kuin reseptikortti — annat sille ainekset ja se palauttaa valmiin tuloksen.")
        if "class" in code_lower:
            analogies.append("Luokka on kuin pohjanaapikarii -malli — siitä voi tehdä lukuisia erilaisia esineitä.")
        if "list" in code_lower or "dict" in code_lower or "[" in code:
            analogies.append("Lista on kuin muistelijan kirja — järjestetyt tiedot indeksein.")
        if not analogies:
            if skill_level == "beginner":
                analogies.append("Ohjelmointi on kuin resepti — jokainen askel on täsmälleen määritelty, ja tulos on yhtä jokaisella kerralla.")
            else:
                analogies.append("Koodi on suunnitelma — sitä suoritetaan koneessa, joka ymmärtää vain konekieltä.")

        return analogies

    def _run(self, input_data: ExplainerAgentInput) -> ExplainerAgentOutput:
        """ExplainerAgentin päälogiika."""
        code = input_data.code
        file_path = input_data.file_path
        skill_level = input_data.skill_level
        concept = input_data.concept

        # 1. Hae koodi tiedostosta jos annettu
        if not code and file_path:
            path = Path(file_path)
            if path.exists():
                code = path.read_text(encoding="utf-8")
            else:
                return ExplainerAgentOutput(
                    success=False,
                    result=None,
                    message="Tiedostoa ei löydy.",
                    agent_type=self.agent_type,
                )

        if not code and not concept:
            return ExplainerAgentOutput(
                success=False,
                result=None,
                message="Anna joko koodi tai käsittein selitettäväksi.",
                agent_type=self.agent_type,
            )

        # 2. Generoi selitys
        explanation = self._explain_code(code or concept or "", skill_level)

        # 3. Koodin kohta analyysi
        code_breakdown = self._break_down_code(code) if code else []

        # 4. Tärkeimmät käsitteet
        key_concepts = []
        if concept:
            key_concepts = [concept]
        elif code:
            code_lower = code.lower()
            if "def" in code_lower:
                key_concepts.append("funktio")
            if "class" in code_lower:
                key_concepts.append("luokka")
            if "for" in code_lower or "while" in code_lower:
                key_concepts.append("silmukka")
            if "if" in code_lower:
                key_concepts.append("ehto")
            if not key_concepts:
                key_concepts = ["perusohjelmointi"]

        # 5. Analogiat
        analogies = self._generate_analogies(code or concept or "", skill_level)

        return ExplainerAgentOutput(
            success=True,
            result={"explanation_length": len(explanation), "breakdown_count": len(code_breakdown)},
            message=f"Selitys luodaan (taso: {skill_level}, koodirivit: {len(code_breakdown)}).",
            agent_type=self.agent_type,
            explanation=explanation,
            code_breakdown=code_breakdown,
            key_concepts=key_concepts,
            analogies=analogies,
        )


class PedagogyAgent(BaseAgent):
    """
    PedagogyAgent suunnittelee oppimisalan suunnitelmat moduuleihin.

    Usage:
        agent = PedagogyAgent()
        result = agent.run("Laadi kurssi", topic="python", skill_level="beginner", duration_weeks=4)
    """

    agent_type: str = "pedagogy"
    input_schema = PedagogyAgentInput
    output_schema = PedagogyAgentOutput

    def _get_user_level_index(self, user_background: str) -> int:
        """Palauttaa käyttäjän taustan indeksin opetussuunnitelman mukaan."""
        return {"none": 0, "basic": 1, "some": 2, "strong": 3}.get(user_background, 1)

    def _build_curriculum(
        self, topic: str, skill_level: str, duration_weeks: int, include_exercises: bool,
        user_background: str = "none",
    ) -> dict[str, Any]:
        """Rakentaa oppimissuunnitelman."""
        topic_list = LEARNING_TOPICS.get(topic, LEARNING_TOPICS["python"])
        bg_index = self._get_user_level_index(user_background)

        # Jaa aihepiirit viikoittain
        topics_per_week = max(1, len(topic_list) // duration_weeks)
        weeks: dict[str, list[str]] = {}

        for i in range(duration_weeks):
            start = i * topics_per_week
            end = min(start + topics_per_week, len(topic_list))
            week_topics = topic_list[start:end] if start < len(topic_list) else [topic_list[-1]]
            weeks[f"viikko_{i + 1}"] = week_topics

        # Lisää moduulit
        modules: dict[str, Any] = {}
        for wk_name, wk_topics in weeks.items():
            modules[wk_name] = {
                "aihepiirit": wk_topics,
                "tavoitteet": [f"Saa oikeus {t.lower()}" for t in wk_topics[:2]],
                "harjoitukset": len(wk_topics) * 2 if include_exercises else 0,
                "arviointi": f"Lopputesti: {wk_topics[-1]}",
            }

        return {
            "topic": topic,
            "skill_level": skill_level,
            "duration_weeks": duration_weeks,
            "modules": modules,
            "user_background": bg_index,
        }

    def _run(self, input_data: PedagogyAgentInput) -> PedagogyAgentOutput:
        """PedagogyAgentin päälogiika."""
        topic = input_data.topic
        skill_level = input_data.skill_level
        duration_weeks = input_data.duration_weeks
        include_exercises = input_data.include_exercises
        user_background = input_data.user_background

        # 1. Rakoa opiskun suunnitelma
        curriculum = self._build_curriculum(
            topic, skill_level, duration_weeks, include_exercises, user_background
        )

        # 2. Laske harjoitusten kokonaismäärä
        total_exercises = sum(m["harjoitukset"] for m in curriculum["modules"].values())

        # 3. Vaiheet
        phases = CURRICULUM_PHASES

        # 4. Lisää resurssit
        if "resources" not in curriculum:
            curriculum["resources"] = LEARNING_TOPICS.get(topic, [])

        return PedagogyAgentOutput(
            success=True,
            result={"topic": topic, "weeks": duration_weeks, "modules": len(curriculum["modules"])},
            message=f"Oppimissuunnitelma luodaan aiheelle '{topic}' ({duration_weeks} viikkoa, {total_exercises} harjoitusta).",
            agent_type=self.agent_type,
            curriculum=curriculum,
            phases=phases,
            total_exercises=total_exercises,
        )


class ContentDesignerAgent(BaseAgent):
    """
    ContentDesignerAgent luo oppimismateriaalia (selitykset, harjoitukset, kyselyt, tutoriaalit).

    Usage:
        agent = ContentDesignerAgent()
        result = agent.run("Luo kysely", content_type="quiz", topic="python", num_items=5)
    """

    agent_type: str = "content_designer"
    input_schema = ContentDesignerAgentInput
    output_schema = ContentDesignerAgentOutput

    def _generate_explanation(self, topic: str, skill_level: str, context: str, num_items: int) -> list[dict[str, str]]:
        """Generoi selityksiä."""
        items: list[dict[str, str]] = []
        topics = LEARNING_TOPICS.get(topic, ["Ohjelmointi"])

        if context:
            items.append({
                "title": "Koodin selostus",
                "content": f"Annettu konteksti:\n\n```\n{context[:500]}\n```\n\n"
                f"Tämä koodi on kirjoitettu {skill_level}-tasolle.",
            })

        for i in range(min(num_items, len(topics))):
            items.append({
                "title": topics[i],
                "content": f"Selitys {topics[i]}-aiheelta ({skill_level}-taso).",
            })

        return items if items else [{"title": topic, "content": f"Perusominaisuudet {topic}."}]

    def _generate_exercise(self, topic: str, skill_level: str, context: str, num_items: int) -> list[dict[str, str]]:
        """Generoi harjoituksia."""
        exercises: list[dict[str, str]] = []
        exercise_types = EXERCISE_TYPES.get("debugging", EXERCISE_TYPES["debugging"])

        for i in range(num_items):
            ex_type = exercise_types[i % len(exercise_types)]
            exercises.append({
                "title": f"Harjoitus {i + 1}: {ex_type.strip()}",
                "content": f"Tehtävä: {ex_type}. Aihe: {topic}, taso: {skill_level}.",
                "difficulty": skill_level,
            })

        return exercises

    def _generate_quiz(self, topic: str, skill_level: str, num_items: int) -> list[dict[str, str]]:
        """Generoi kysymyksiä."""
        questions = [
            {"title": "Perustava kysymys", "content": "Mikä seuraavista on oikein?", "options": ["A", "B", "C", "D"], "answer": "A"},
            {"title": "Keskiverto kysymys", "content": "Mitä koodi tekee?", "options": ["A", "B", "C", "D"], "answer": "B"},
            {"title": "Haastava kysymys", "content": "Mikä on suunnittelun vaikutus?", "options": ["A", "B", "C", "D"], "answer": "C"},
        ]

        items = []
        for i in range(min(num_items, len(questions))):
            q = questions[i].copy()
            q["title"] = f"Kysymys {i + 1}"
            items.append(q)

        return items if items else questions[:num_items]

    def _generate_tutorial(self, topic: str, skill_level: str, context: str, num_items: int) -> list[dict[str, str]]:
        """Generoi tutoriaalia."""
        steps = []
        topics = LEARNING_TOPICS.get(topic, ["Ohjelmointi"])

        if context:
            steps.append({
                "title": "Asennus ja ympäristö",
                "content": f"Aseta ympäristö kontekstin mukaan:\n\n```\n{context[:300]}\n```",
            })

        num_steps = num_items if num_items > 0 else 3
        for i in range(num_steps):
            if i < len(topics):
                steps.append({
                    "title": f"Vaihe {i + 1}: {topics[i]}",
                    "content": f"Täydennä tämä osa {topic}-projektissa ({skill_level}-taso).",
                })
            else:
                steps.append({
                    "title": f"Vaihe {i + 1}",
                    "content": f"Käytä saatuja tietoja edell bahkoissa jatkaaksesi.",
                })

        return steps if steps else [{"title": "Aloita", "content": f"Aloita {topic}-projekti."}]

    def _generate_cheat_sheet(self, topic: str, skill_level: str, num_items: int) -> list[dict[str, str]]:
        """Generoi cheat sheet -lomakkeen."""
        items = []
        topics = LEARNING_TOPICS.get(topic, ["Ohjelmointi"])

        for i in range(min(num_items, len(topics))):
            items.append({
                "title": topics[i],
                "content": f"```\n# Esimerkkikoodi\n{topic}_example()\n```",
            })

        return items

    def _run(self, input_data: ContentDesignerAgentInput) -> ContentDesignerAgentOutput:
        """ContentDesignerAgentin päälogiika."""
        content_type = input_data.content_type
        topic = input_data.topic
        skill_level = input_data.skill_level
        context_text = input_data.context_text
        num_items = input_data.num_items

        # 1. Generoi sisältö valitun tyypin perusteella
        if content_type == "explanation":
            content = self._generate_explanation(topic, skill_level, context_text, num_items)
        elif content_type == "exercise":
            content = self._generate_exercise(topic, skill_level, context_text, num_items)
        elif content_type == "quiz":
            content = self._generate_quiz(topic, skill_level, num_items)
        elif content_type == "tutorial":
            content = self._generate_tutorial(topic, skill_level, context_text, num_items)
        elif content_type == "cheat_sheet":
            content = self._generate_cheat_sheet(topic, skill_level, num_items)
        else:
            content = self._generate_explanation(topic, skill_level, context_text, num_items)

        return ContentDesignerAgentOutput(
            success=True,
            result={"content_type": content_type, "total_items": len(content)},
            message=f"Luodaan {len(content)} {content_type}-kohdetta aiheelta '{topic}'.",
            agent_type=self.agent_type,
            content=content,
            content_type=content_type,
            total_items=len(content),
        )


__all__ = [
    "MentorAgent",
    "MentorAgentInput",
    "MentorAgentOutput",
    "ExplainerAgent",
    "ExplainerAgentInput",
    "ExplainerAgentOutput",
    "PedagogyAgent",
    "PedagogyAgentInput",
    "PedagogyAgentOutput",
    "ContentDesignerAgent",
    "ContentDesignerAgentInput",
    "ContentDesignerAgentOutput",
    "LEARNING_LEVELS",
    "LEARNING_TOPICS",
    "EXPLANATION_PROMPTS",
    "EXERCISE_TYPES",
    "CURRICULUM_PHASES",
]
