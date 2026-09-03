"""
LearningPathAgent-moduuli (M12) — yksilaudettujen oppimispolut ja edistymisen seurinta.

Sisältää kolme agenttia:
- LearningPathAgent: suunnittelee henkilökohtaisen oppimispolun käyttäjän taustan, tavoitteiden ja edistymisen perusteella.
- AssessmentAgent: luo ja arvioi testit, kokeet ja palautekysymykset.
- FeedbackAgent: antaa reaaliaikaisen palautteen koodaukseen ja oppimiseen.
"""

from __future__ import annotations

import ast
import re
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent
from agents.pedagogy_agent import EXPLANATION_PROMPTS, LEARNING_LEVELS, LEARNING_TOPICS


# Oppimustyyplit ja niiden ominaisuudet
PATH_STRATEGIES: dict[str, dict[str, Any]] = {
    "hands_on": {
        "name": "Käytännönlähteä",
        "description": "Opiskelee tekemällä — paljon harjoitusta ja projekteja.",
        "weight_code_reading": 0.3,
        "weight_exercises": 0.7,
        "weight_theory": 0.0,
    },
    "theoretical": {
        "name": "Teoreettinen",
        "description": "Opiskelee konsepteista ja teoreetasta ennen käytäntöä.",
        "weight_code_reading": 0.4,
        "weight_exercises": 0.2,
        "weight_theory": 0.4,
    },
    "balanced": {
        "name": "Tasapainainen",
        "description": " Tasapaineinen yhdistelmä teoreiasta ja käytännöstä.",
        "weight_code_reading": 0.3,
        "weight_exercises": 0.4,
        "weight_theory": 0.3,
    },
}

# Arviointikriteerit
ASSESSMENT_CRITERIA: dict[str, dict[str, float]] = {
    "beginner": {
        "comprehension": 0.4,
        "accuracy": 0.4,
        "completion": 0.2,
    },
    "intermediate": {
        "comprehension": 0.5,
        "accuracy": 0.3,
        "completion": 0.2,
    },
    "advanced": {
        "comprehension": 0.6,
        "accuracy": 0.2,
        "completion": 0.2,
    },
}


class LearningPathAgentInput(AgentInput):
    """LearningPathAgentin syöte."""
    user_id: str = Field(default="default_user", description="Käyttäjän tunniste.")
    current_skill_level: str = Field(default="beginner", description="Nykyinen taitotaso.")
    target_skill_level: str = Field(default="intermediate", description="Tavoite-taitotaso.")
    preferred_strategy: str = Field(default="balanced", description="Oppimustyyppi (hands_on, theoretical, balanced).")
    current_progress: dict[str, Any] = Field(default_factory=dict, description="Nykyinen edistyminen (esim. suoritetut moduulit).")
    interests: list[str] = Field(default_factory=list, description="Käyttäjän kiinnostuksen kohteet (esim. web-dev, security).")


class LearningPathAgentOutput(AgentOutput):
    """LearningPathAgentin tuloste."""
    path_id: str = Field(default="", description="Oppimispolan yksilöivä tunniste.")
    modules: list[dict[str, Any]] = Field(default_factory=list, description="Suunnitellut oppimismoduulit.")
    estimated_duration_hours: float = Field(default=0, description="Arvioitu kokonaisaika tunneissa.")
    progress_percentage: float = Field(default=0, description="Nykyinen edistymisprosentti.")
    next_recommendation: str = Field(default="", description="Seuraava suositeltu toiminta.")


class AssessmentInput(AgentInput):
    """AssessmentAgentin syöte."""
    assessment_type: str = Field(default="quiz", description="Arviirtypukuoma (quiz, coding_challenge, project_review, peer_review).")
    skill_level: str = Field(default="beginner", description="Taitotaso arvioille.")
    topic: str = Field(default="python", description="Aihe arvioille.")
    num_items: int = Field(default=5, description="Arviointitekojen määrä.")
    context_text: str = Field(default="", description="Lisäkonteksti (esim. arvioitu koodi tai projekti).")
    previous_scores: list[float] = Field(default_factory=list, description="Aiemmat pisteet prosentteina.")


class AssessmentOutput(AgentOutput):
    """AssessmentAgentin tuloste."""
    assessments: list[dict[str, Any]] = Field(default_factory=list, description="Luodut arviointitehtävät.")
    criteria: dict[str, float] = Field(default_factory=dict, description="Käytetyt arviointikriteerit.")
    average_difficulty: float = Field(default=0, description="Keskiarvoinen vaikeusaste.")
    total_items: int = Field(default=0, description="Arviointitekojen yhteismäärä.")


class FeedbackInput(AgentInput):
    """FeedbackAgentin syöte."""
    code: str = Field(default="", description="Analysoitava koodi.")
    feedback_type: str = Field(default="code_review", description="Palaute-tyyppi (code_review, learning, style, performance).")
    skill_level: str = Field(default="beginner", description="Käyttäjän taitotaso.")
    focus_areas: list[str] = Field(default_factory=list, description="Keskittymisalueet (esim. readability, efficiency, security).")


class FeedbackOutput(AgentOutput):
    """FeedbackAgentin tuloste."""
    feedback_items: list[dict[str, str]] = Field(default_factory=list, description="Palautteiden lista.")
    severity: str = Field(default="info", description="Palautteen voimakkuus (info, warning, error, critical).")
    suggestions: list[str] = Field(default_factory=list, description="Konkreettiset parannusehdotukset.")
    score: float = Field(default=0, description="Koodin arvosana 0-100.")


class LearningPathAgent(BaseAgent):
    """
    LearningPathAgent suunnittelee henkilökohtaiset oppimispolut.

    Käyttää käyttäjän taustaa, tavoitteita, kiinnostuksia ja edistymistä
    luodakseen dynaamisen oppimissuunnitelman.

    Usage:
        agent = LearningPathAgent()
        result = agent.run("Luon oppimispolan", current_skill_level="beginner", target_skill_level="intermediate")
    """

    agent_type: str = "learning_path"
    input_schema = LearningPathAgentInput
    output_schema = LearningPathAgentOutput

    def _calculate_path_id(self, user_id: str, topic: str) -> str:
        """Luo yksilöllisen oppimispolan tunnuksen."""
        import hashlib
        base = f"{user_id}:{topic}"
        return hashlib.md5(base.encode()).hexdigest()[:8]

    def _select_strategy(self, preferred_strategy: str, user_background: str) -> str:
        """Valitsee oppimustyypin käyttäjän taustan ja mielipiteen perusteella."""
        # Käytä määriteltyä strategiaa jos se on tunnettu
        if preferred_strategy in PATH_STRATEGIES:
            return preferred_strategy
        # Oletus: tasapainainen, mutta aloittelijat saavat käytännön
        if user_background == "beginner":
            return "hands_on"
        return "balanced"

    def _estimate_module_duration(self, module: dict[str, Any], strategy: str) -> float:
        """Arvioi moduulin kesto tunneissa."""
        base_hours = len(module.get("topics", [])) * 1.5
        strategy_weights = PATH_STRATEGIES.get(strategy, PATH_STRATEGIES["balanced"])
        adjustment = (
            strategy_weights["weight_code_reading"] * 0.5
            + strategy_weights["weight_exercises"] * 1.2
            + strategy_weights["weight_theory"] * 0.8
        )
        return round(base_hours * adjustment, 1)

    def _build_modules(
        self,
        topic: str,
        current_level: str,
        target_level: str,
        strategy: str,
        interests: list[str],
    ) -> list[dict[str, Any]]:
        """Rakentaa oppimismoduulit stratheegian ja kiinnostusten mukaan."""
        topic_list = LEARNING_TOPICS.get(topic, LEARNING_TOPICS["python"])

        # Jaa moduulit taitotasojen mukaan
        topics_split: dict[str, list[str]] = {}
        topics_per_level = max(1, len(topic_list) // 3)

        topics_split["beginner"] = topic_list[:topics_per_level]
        topics_split["intermediate"] = topic_list[topics_per_level:2 * topics_per_level]
        topics_split["advanced"] = topic_list[2 * topics_per_level:]

        # Aseta järjestys
        level_order = ["beginner", "intermediate", "advanced"]
        start_idx = level_order.index(current_level) if current_level in level_order else 0
        end_idx = level_order.index(target_level) if target_level in level_order else 2

        modules = []
        for i in range(start_idx, end_idx + 1):
            level = level_order[i]
            level_topics = topics_split.get(level, [])

            # Suodata kiinnostusten mukaan
            filtered_topics = level_topics
            if interests:
                # Lisää kiinnostukselliset aiheet prioriteetit
                for interest in interests:
                    if interest in topic:
                        filtered_topics = level_topics[:max(2, len(level_topics) // 2)]
                        break

            module = {
                "id": f"module_{i + 1}",
                "level": level,
                "topics": filtered_topics,
                "strategy": strategy,
                "exercises": len(filtered_topics) * 3 if strategy != "theoretical" else len(filtered_topics) * 2,
                "duration_hours": self._estimate_module_duration({"topics": filtered_topics}, strategy),
                "prerequisites": [f"module_{i}"] if i > 0 else [],
            }
            modules.append(module)

        return modules

    def _calculate_progress(self, current_progress: dict[str, Any], total_modules: int) -> float:
        """Laskee edistymisprosentin."""
        completed = current_progress.get("completed_modules", [])
        in_progress = current_progress.get("in_progress_module", None)

        percentage = (len(completed) / total_modules * 100) if total_modules > 0 else 0

        if in_progress is not None:
            # Lisää puolikas prosessi meneessä olevasta moduulista
            percentage += (100 / total_modules * 0.5) if total_modules > 0 else 0

        return min(round(percentage, 1), 100)

    def _generate_next_recommendation(
        self,
        current_progress: dict[str, Any],
        modules: list[dict[str, Any]],
        strategy: str,
    ) -> str:
        """Luo seuraavan suosituksen."""
        completed = current_progress.get("completed_modules", [])
        in_progress = current_progress.get("in_progress_module")

        if in_progress is not None:
            module = next((m for m in modules if m["id"] == in_progress), None)
            if module:
                if strategy == "hands_on":
                    return f"Jatka moduulia '{in_progress}' tekemällä koodiharjoituksia aihepiirteistä {', '.join(module['topics'][:2])}."
                return f"Jatka moduulia '{in_progress}' ja keskitty harjoitteluun."

        next_module = next((m for m in modules if m["id"] not in completed), None)
        if next_module:
            level_name = LEARNING_LEVELS.get(next_module["level"], {}).get("name", next_module["level"])
            if strategy == "hands_on":
                return f"Aloita moduuli '{next_module['id']}' ({level_name}): koodaa harjoituksia aihepiiristä {', '.join(next_module['topics'][:3])}."
            return f"Aloita moduuli '{next_module['id']}' ({level_name}): {', '.join(next_module['topics'][:3])}."

        return "Onneksi olkoo edistyneet! Kaikki moduulit suoritettu."

    def _run(self, input_data: LearningPathAgentInput) -> LearningPathAgentOutput:
        """LearningPathAgentin päälogiikka."""
        topic = input_data.context.get("topic", "python")
        current_level = input_data.current_skill_level
        target_level = input_data.target_skill_level
        strategy = self._select_strategy(input_data.preferred_strategy, input_data.metadata.get("user_background", "none"))

        # Rakoa moduulit
        modules = self._build_modules(topic, current_level, target_level, strategy, input_data.interests)

        # Laske kokonaisaika
        total_duration = sum(m["duration_hours"] for m in modules)

        # Laske edistyminen
        progress = self._calculate_progress(input_data.current_progress, len(modules))

        # Luo suositukset
        next_recommendation = self._generate_next_recommendation(input_data.current_progress, modules, strategy)

        # Luo polkutunniste
        path_id = self._calculate_path_id(input_data.user_id, topic)

        return LearningPathAgentOutput(
            success=True,
            result={"path_id": path_id, "modules_count": len(modules)},
            message=f"Oppimispola luodaan aiheelle '{topic}' (strategia: {PATH_STRATEGIES[strategy]['name']}).",
            agent_type=self.agent_type,
            path_id=path_id,
            modules=modules,
            estimated_duration_hours=round(total_duration, 1),
            progress_percentage=progress,
            next_recommendation=next_recommendation,
        )


class AssessmentAgent(BaseAgent):
    """
    AssessmentAgent luo ja arvioi kyselyjä, koodihaasteita ja projektiarviointeja.

    Usage:
        agent = AssessmentAgent()
        result = agent.run("Luo kysely", assessment_type="quiz", topic="python", skill_level="beginner")
    """

    agent_type: str = "assessment"
    input_schema = AssessmentInput
    output_schema = AssessmentOutput

    def _get_difficulty_level(self, skill_level: str) -> str:
        """Kartoittaa taitotason vaikeustason."""
        return LEARNING_LEVELS.get(skill_level, LEARNING_LEVELS["beginner"])["name"]

    def _generate_quiz_assessment(self, topic: str, skill_level: str, num_items: int) -> list[dict[str, Any]]:
        """Generoi kyselytestin."""
        level_name = self._get_difficulty_level(skill_level)
        questions = []

        # Perus kysymykset
        q_templates = [
            {
                "type": "multiple_choice",
                "question": f"Mikä seuraavista on oikein {topic}-kontekstissa?",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "difficulty": level_name,
            },
            {
                "type": "true_false",
                "question": f"Tosiksi vai väärin: {topic} on keskeinen ohjelmistokehityksen ala?",
                "options": ["Tos sitä", "Väärin"],
                "correct_answer": "A",
                "difficulty": level_name,
            },
            {
                "type": "short_answer",
                "question": f" Miksi on tärkeää ymmärtää {topic[:1].upper() + topic[1:]}-periaatteet?",
                "options": [],
                "correct_answer": "avoin",
                "difficulty": level_name,
            },
        ]

        # Täydennä kysymykset tarvittavalla määrällä
        for i in range(num_items):
            q = q_templates[i % len(q_templates)].copy()
            q["id"] = f"q_{i + 1}"
            q["question"] = q["question"].replace("A", str(i + 1))
            questions.append(q)

        return questions

    def _generate_coding_challenge(self, topic: str, skill_level: str, num_items: int) -> list[dict[str, Any]]:
        """Generoi koodaushaasteen."""
        level_name = self._get_difficulty_level(skill_level)
        challenges = []

        challenge_templates = [
            {
                "type": "code_writing",
                "title": f"Kirjoita {topic}-funktio",
                "description": f"Totea funktio joka ottaa syötteenä listan ja palauttaa sen käänteisessä järjestyksessä.",
                "starter_code": "def reverse_list(lst):\n    pass",
                "difficulty": level_name,
                "test_cases": ["assert reverse_list([1,2,3]) == [3,2,1]", "assert reverse_list([]) == []"],
            },
            {
                "type": "debugging",
                "title": "Etsi virhe",
                "description": "Koodissa on syntaksivirhe. Korjaa se.",
                "starter_code": "def buggy():\n    if True\n        return True",
                "difficulty": level_name,
                "test_cases": ["Koodin tulee suoritua ilman virheitä"],
            },
            {
                "type": "refactoring",
                "title": "Paranna koodia",
                "description": "Refaktoi koodi käyttämään parempaa nimitystapaa.",
                "starter_code": "x = 1\ndef f(a):\n    return a + x",
                "difficulty": level_name,
                "test_cases": ["Funktion nimen tulee olla selkeä", "Muuttujan nimen tulee olla kuvaava"],
            },
        ]

        for i in range(num_items):
            c = challenge_templates[i % len(challenge_templates)].copy()
            c["id"] = f"c_{i + 1}"
            challenges.append(c)

        return challenges

    def _generate_project_review(self, topic: str, skill_level: str, context_text: str, num_items: int) -> list[dict[str, Any]]:
        """Generoi projektin arvioinnin."""
        level_name = self._get_difficulty_level(skill_level)
        reviews = []

        # Analysoi konteksti jos saatavilla
        code_analysis = ""
        if context_text:
            try:
                tree = ast.parse(context_text)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                code_analysis = f"Koodissa on {len(functions)} funktiota ja {len(classes)} luokkaa."
            except SyntaxError:
                code_analysis = "Koodissa on mahdollinen syntaksivirhe."

        review_templates = [
            {
                "type": "code_quality",
                "title": "Koodin laatu",
                "criteria": ["Lukukelpailisuus", "Komplikaasisuus", "Modularisuus"],
                "max_score": 10,
                "context_analysis": code_analysis,
            },
            {
                "type": "functionality",
                "title": "Toiminnallisuus",
                "criteria": ["Odotukset täyttyneet", "Rajatilanteet käsitelty", "API-mukainen"],
                "max_score": 10,
                "context_analysis": code_analysis,
            },
            {
                "type": "documentation",
                "title": "Dokumentaatio",
                "criteria": ["Docstringit", "Typen tarkennus", "Esimerkit"],
                "max_score": 10,
                "context_analysis": code_analysis,
            },
        ]

        for i in range(min(num_items, len(review_templates))):
            r = review_templates[i].copy()
            r["id"] = f"r_{i + 1}"
            r["difficulty"] = level_name
            reviews.append(r)

        return reviews

    def _calculate_average_difficulty(self, items: list[dict[str, Any]]) -> float:
        """Laskee keskiarvosmuutavan vaikeuden 1-5 asteemllä."""
        difficulty_map = {"ALOITTAJA": 1, "KOKEILEVA": 3, "EDISTYNYT": 5}
        if not items:
            return 0
        total = sum(difficulty_map.get(item.get("difficulty", "beginner"), 1) for item in items)
        return round(total / len(items), 1)

    def _adjust_for_previous_scores(self, items: list[dict[str, Any]], previous_scores: list[float]) -> list[dict[str, Any]]:
        """Säätää vaikeutta edellisistä pisteistä."""
        if not previous_scores:
            return items

        avg_score = sum(previous_scores) / len(previous_scores)

        # Jos käyttäjä saa hyvät pisteet, nosta vaikeus
        if avg_score > 80:
            for item in items:
                item["difficulty_adjustment"] = "harder"
        elif avg_score < 50:
            for item in items:
                item["difficulty_adjustment"] = "easier"
        else:
            for item in items:
                item["difficulty_adjustment"] = "same"

        return items

    def _run(self, input_data: AssessmentInput) -> AssessmentOutput:
        """AssessmentAgentin päälogiikka."""
        assessment_type = input_data.assessment_type
        skill_level = input_data.skill_level
        topic = input_data.topic
        num_items = input_data.num_items
        context_text = input_data.context_text

        # Generoi arviointi oikeaan tyyliin
        if assessment_type == "quiz":
            items = self._generate_quiz_assessment(topic, skill_level, num_items)
        elif assessment_type == "coding_challenge":
            items = self._generate_coding_challenge(topic, skill_level, num_items)
        elif assessment_type == "project_review":
            items = self._generate_project_review(topic, skill_level, context_text, num_items)
        elif assessment_type == "peer_review":
            items = self._generate_quiz_assessment(topic, skill_level, num_items)
            for item in items:
                item["type"] = "peer_review"
        else:
            items = self._generate_quiz_assessment(topic, skill_level, num_items)

        # Säädä aiempien pisteidemmek
        items = self._adjust_for_previous_scores(items, input_data.previous_scores)

        # Hae arviointikriteerit
        criteria = ASSESSMENT_CRITERIA.get(skill_level, ASSESSMENT_CRITERIA["beginner"])

        # Laske keskivaikeus
        avg_difficulty = self._calculate_average_difficulty(items)

        return AssessmentOutput(
            success=True,
            result={"assessment_type": assessment_type, "items_count": len(items)},
            message=f"Luodaan {len(items)} {assessment_type}-arvioitusta kysymyksestä aiheelta '{topic}'.",
            agent_type=self.agent_type,
            assessments=items,
            criteria=criteria,
            average_difficulty=avg_difficulty,
            total_items=len(items),
        )


class FeedbackAgent(BaseAgent):
    """
    FeedbackAgent antaa reaaliaikaista palautetta koodaukseen.

    Usage:
        agent = FeedbackAgent()
        result = agent.run("Arvostele koodia", code="def foo(): pass", feedback_type="code_review")
    """

    agent_type: str = "feedback"
    input_schema = FeedbackInput
    output_schema = FeedbackOutput

    # Palaute-kategorioit
    FEEDBACK_CATEGORIES: dict[str, list[str]] = {
        "code_review": ["lukukelpailisuus", "virheet", "suunnittelu"],
        "learning": ["ymmärrys", "parannus", "seuraavat_askeleet"],
        "style": ["nimeistö", "muotoilu", "yhtenäisyys"],
        "performance": [" tehokkuus", "optimointi", " resurssit"],
    }

    def _analyze_code_structure(self, code: str) -> dict[str, Any]:
        """Analysoi koodin rakenteen AST-parsimuksen avulla."""
        result = {
            "functions": [],
            "classes": [],
            "imports": [],
            "complexity": 0,
            "syntax_valid": True,
            "issues": [],
        }

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            result["syntax_valid"] = False
            result["issues"].append(f"Syntaksivirhe: {e}")
            return result

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                result["functions"].append(node.name)
                # Laske kompleksisuus yksinkertaisesti
                result["complexity"] += sum(1 for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler)))
            elif isinstance(node, ast.ClassDef):
                result["classes"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                result["imports"].append(node.names[0].name if hasattr(node, 'names') and node.names else "unknown")

        return result

    def _generate_code_feedback(self, structure: dict[str, Any], skill_level: str) -> list[dict[str, str]]:
        """Luo palaute koodin rakenteen perusteella."""
        feedback = []
        level_desc = LEARNING_LEVELS.get(skill_level, LEARNING_LEVELS["beginner"])

        # Syntaksivirheet
        if not structure["syntax_valid"]:
            for issue in structure["issues"]:
                feedback.append({
                    "category": "virhe",
                    "message": issue,
                    "severity": "error",
                    "explanation": "Korjaa syntaksivirhe ennen jatkoa." if skill_level == "beginner" else issue,
                })

        # Funktioanalyysi
        if structure["functions"]:
            feedback.append({
                "category": "rakenne",
                "message": f"Koodi sisältää {len(structure['functions'])} funktiota: {', '.join(structure['functions'])}.",
                "severity": "info",
                "explanation": "Funktiot tekevät koodista Modulaarisen ja testoitujan.",
            })

        # Luokat
        if structure["classes"]:
            feedback.append({
                "category": "rakenne",
                "message": f"Koodi sisältää {len(structure['classes'])} luokkaa: {', '.join(structure['classes'])}.",
                "severity": "info",
                "explanation": "Luokat ovat hyvässä muodissa OOP-periaatteen mukaisesti.",
            })

        # Kompleksisuus
        if structure["complexity"] > 0:
            if structure["complexity"] > 10 and skill_level == "beginner":
                feedback.append({
                    "category": "lukukelpailisuus",
                    "message": f" Funktiot ovat melko monimutkaisia (kompleksisuus: {structure['complexity']}).",
                    "severity": "warning",
                    "explanation": "Harkitse funktioiden pilkomista pienempiin osiin.",
                })
            elif structure["complexity"] > 5:
                feedback.append({
                    "category": "lukukelpailisuus",
                    "message": f" Tämä on OK mutta voit harkita refaktorointia kompleksisuuden hallinnoinnin vuoksi.",
                    "severity": "info",
                    "explanation": f"Kompleksisuus on {structure['complexity']}.",
                })

        # Tyhjät rivit
        if not structure["functions"] and not structure["classes"] and structure["syntax_valid"]:
            feedback.append({
                "category": "sisältö",
                "message": "Koodi on syntaksin kelpo mutta ei sisällä mitään määritelmiä.",
                "severity": "info",
                "explanation": "Lisää funktioita tai luokkia.",
            })

        return feedback

    def _generate_learning_feedback(self, structure: dict[str, Any], skill_level: str) -> list[dict[str, str]]:
        """Luo oppimisprofiilin mukaan palautetta."""
        feedback = []
        explanation_prompt = EXPLANATION_PROMPTS.get(skill_level, EXPLANATION_PROMPTS["beginner"])

        if structure["syntax_valid"]:
            if skill_level == "beginner":
                feedback.append({
                    "category": "edistys",
                    "message": "Hyvä aloitus! Koodisi on syntaktisesti kelvollinen.",
                    "severity": "info",
                    "explanation": "Käytä askel askeleelta -lähestymistapaa ja tarkista jokainen rivi.",
                })
            else:
                feedback.append({
                    "category": "edistys",
                    "message": "Koodin rakenteesi on solid.",
                    "severity": "info",
                    "explanation": "Jatka samalla tiellä ja lisää monipuolisia testejä.",
                })

            if structure["functions"]:
                feedback.append({
                    "category": "seuraavat_askeleet",
                    "message": f" Harkitse lisäämään dokumentaatiota funktioille: {', '.join(structure['functions'])}.",
                    "severity": "info",
                    "explanation": "Hyvällä dokumentaatiolla on selkeä enneminen ja ylläpidettävyys.",
                })

            if structure["imports"]:
                feedback.append({
                    "category": "ymmärrys",
                    "message": f" Käytit kirjastoja: {', '.join(structure['imports'])}.",
                    "severity": "info",
                    "explanation": "Tämä on edelläkäteen edistynyt ominaisuus.",
                })
        else:
            for issue in structure["issues"]:
                feedback.append({
                    "category": "parannus",
                    "message": issue,
                    "severity": "warning",
                    "explanation": f"Virheitä korjattaessa: {explanation_prompt}",
                })

        return feedback

    def _check_style(self, code: str, focus_areas: list[str]) -> list[dict[str, str]]:
        """Tarkistaa tyyliin liittyvät ongelmat."""
        feedback = []

        # Tarkista rivinvaihto
        long_lines = [(i + 1, len(line)) for i, line in enumerate(code.splitlines()) if len(line) > 88]
        if long_lines:
            feedback.append({
                "category": "tyyli",
                "message": f" {len(long_lines)} riviä yli 88 merkkiä.",
                "severity": "warning",
                "explanation": "PEP 8 suosittelee enintään 79–88 merkkiä per rivi.",
            })

        # Tarkista tyhjät rivit
        if "\n\n\n" in code:
            feedback.append({
                "category": "tyyli",
                "message": " Liian montä tyhjää riviä peräkkäin.",
                "severity": "warning",
                "explanation": "Käytä enintään yhtä tyhjää rivia erott BuCSien välein.",
            })

        return feedback

    def _calculate_score(self, structure: dict[str, Any], feedback_items: list[dict[str, str]]) -> float:
        """Laskee koodin pisteet 0-100."""
        score = 100

        # Vahenna pisteitä virheistä
        error_count = sum(1 for f in feedback_items if f.get("severity") == "error")
        warning_count = sum(1 for f in feedback_items if f.get("severity") == "warning")

        score -= error_count * 20
        score -= warning_count * 5

        # Lisää pisteitä hyvistä asioista
        if structure["functions"]:
            score += 5
        if structure["classes"]:
            score += 3
        if structure["imports"]:
            score += 2
        if structure["syntax_valid"]:
            score += 10

        return max(0, min(100, round(score, 1)))

    def _determine_severity(self, feedback_items: list[dict[str, str]]) -> str:
        """Määrittää palautteen voimakkuuden."""
        if any(f.get("severity") == "error" for f in feedback_items):
            return "error"
        if any(f.get("severity") == "critical" for f in feedback_items):
            return "critical"
        if any(f.get("severity") == "warning" for f in feedback_items):
            return "warning"
        return "info"

    def _generate_suggestions(self, feedback_items: list[dict[str, str]], focus_areas: list[str]) -> list[str]:
        """Luo konkreettiset parannusehdotukset."""
        suggestions = []

        for item in feedback_items:
            if item.get("category") == "virhe":
                suggestions.append("Korjaa virhe ensiksi.")
            elif item.get("category") == "lukukelpailisuus":
                suggestions.append("Harkitse selkeämpää muotoilua ja kommentteja.")
            elif item.get("category") == "rakenne":
                suggestions.append("Jatka toimintojen jakamista erillosiin.")

        if not suggestions:
            suggestions.append("Koodisi näyttää hyvältä. Jatka niin pitkään!")

        # Täydennä keskityskohteiden perusteella
        for area in focus_areas:
            if area == "readability" and not any("luku" in s.lower() for s in suggestions):
                suggestions.append("Lisää kommentteja parantaaksesi lukukelpoisuutta.")
            elif area == "efficiency" and not any("tehokkuus" in s.lower() in s for s in suggestions if "tehokkuus" in s.lower()):
                suggestions.append("Harkitse algoritmin optimointia suorituskyvyn parantamiseksi.")
            elif area == "security" and not any("turva" in s.lower() for s in suggestions):
                suggestions.append("Tarkista syötevahvistus ja mahdolliset turvallisuusongelmat.")

        return suggestions

    def _run(self, input_data: FeedbackInput) -> FeedbackOutput:
        """FeedbackAgentin päälogiikka."""
        code = input_data.code
        feedback_type = input_data.feedback_type
        skill_level = input_data.skill_level
        focus_areas = input_data.focus_areas

        # Analysoi koodi
        structure = self._analyze_code_structure(code)

        # Generoi palaute oikeaan tyyliin
        if feedback_type == "code_review":
            feedback_items = self._generate_code_feedback(structure, skill_level)
        elif feedback_type == "learning":
            feedback_items = self._generate_learning_feedback(structure, skill_level)
        elif feedback_type == "style":
            feedback_items = self._check_style(code, focus_areas)
        elif feedback_type == "performance":
            feedback_items = self._generate_code_feedback(structure, skill_level)
            feedback_items.append({
                "category": "tehokkuus",
                "message": "Suorituskyvyn tarkistus edellyttää profilausta.",
                "severity": "info",
                "explanation": "Käytä timeit-kirjastoa tai cProfile-työkalua.",
            })
        else:
            feedback_items = self._generate_code_feedback(structure, skill_level)

        # Muuta dict-listaksi oikeaan muotoon
        formatted_feedback = []
        for item in feedback_items:
            formatted_feedback.append({
                "category": item.get("category", "general"),
                "message": item.get("message", ""),
                "severity": item.get("severity", "info"),
                "explanation": item.get("explanation", ""),
            })

        # Laske pisteet ja voimakkuus
        score = self._calculate_score(structure, formatted_feedback)
        severity = self._determine_severity(formatted_feedback)
        suggestions = self._generate_suggestions(formatted_feedback, focus_areas)

        return FeedbackOutput(
            success=True,
            result={"score": score, "feedback_count": len(formatted_feedback)},
            message=f"Palaute luodaan tyypin '{feedback_type}' mukaan (pisteet: {score}/100).",
            agent_type=self.agent_type,
            feedback_items=formatted_feedback,
            severity=severity,
            suggestions=suggestions,
            score=score,
        )
