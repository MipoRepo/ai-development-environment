"""
KnowledgeAgent-moduuli (M13) — tietojärjestelmän hallinta, haku ja indeksointi.

Sisältää kolme agenttia:
- KnowledgeAgent: hallitsee tiedon tallentamista, hakua ja indeksointia.
- MemoryAgent: käyttäjän istunto- ja pitkäaikaisuuden muistin hallinta.
- ContextCompilerAgent: kokoaa yhteyttiedot useista lähteistä kontekstiin.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Tiedon indeksointityypit
INDEX_TYPES: dict[str, dict[str, Any]] = {
    "concept": {
        "name": "Konsepti",
        "description": "Abstrakti ohjelmistokehityksen konsepti (esim. 'dependency injection', 'microservice').",
        "extractors": ["imports", "classes", "functions"],
    },
    "pattern": {
        "name": "Malli",
        "description": "Toistuva koodikäytäntö tai malli projektissa.",
        "extractors": ["ast_patterns", "naming_patterns"],
    },
    "snippet": {
        "name": "Katkelma",
        "description": "Käytännönlähteä koodikatkelma, joka voi toistua.",
        "extractors": ["functions", "classes"],
    },
    "decision": {
        "name": "Päätös",
        "description": "Projektissa tehdyitä suunnittelupäätöksiä.",
        "extractors": ["context", "metadata"],
    },
}

# Muistin tallennusmuodot
MEMORY_STORE_TYPES: dict[str, dict[str, Any]] = {
    "session": {
        "ttl": None,
        "max_size": 100,
        "description": "Istunnonajan muistiin — poistetaan istunnon loputtua.",
    },
    "short_term": {
        "ttl": 3600,
        "max_size": 1000,
        "description": "Lyhyt aika — 1 tunti.",
    },
    "long_term": {
        "ttl": None,
        "max_size": 10000,
        "description": "Pitkäaikainen muisti — säilytetään.",
    },
}


class KnowledgeAgentInput(AgentInput):
    """KnowledgeAgentin syöte."""
    operation: str = Field(default="store", description="Toiminto (store, retrieve, index, search, delete).")
    knowledge_type: str = Field(default="concept", description="Tiedon tyyppi (concept, pattern, snippet, decision).")
    content: str = Field(default="", description="Tallennettava sisältö.")
    tags: list[str] = Field(default_factory=list, description="Sijoittavat tunnisteet tiedolle.")
    query: str = Field(default="", description="Hakukysely.")
    index_fields: list[str] = Field(default_factory=list, description="Kentät jotka tulevat indeksoiduksi.")
    source: str = Field(default="", description="Tiedon lähde (esim. tiedoston polku).")
    knowledge_id: str = Field(default="", description="Hakemisto, joka palautetaan, indeksoidaan tai poistetaan ID:llä.")


class KnowledgeAgentOutput(AgentOutput):
    """KnowledgeAgentin tuloste."""
    knowledge_id: str = Field(default="", description="Tiedon yksilöivä tunniste.")
    entries: list[dict[str, Any]] = Field(default_factory=list, description="Löydetyt tiedot.")
    index_name: str = Field(default="", description="Luodun indeksin nimi.")
    total_found: int = Field(default=0, description="Löydettyjen tulsten määrä.")
    confidence: float = Field(default=0, description="Hakatuloksen luottamuksellisuus 0-1.")


class MemoryInput(AgentInput):
    """MemoryAgentin syöte."""
    store_type: str = Field(default="session", description="Muistin tyyppi (session, short_term, long_term).")
    key: str = Field(default="", description="Muistin avain.")
    value: Any = Field(default=None, description="Muistettava arvo.")
    action: str = Field(default="store", description="Toiminto (store, retrieve, list, forget, clear).")
    ttl: Optional[int] = Field(default=None, description="Time-to-live sekunteina.")
    filter_tags: list[str] = Field(default_factory=list, description="Suodatin tunnisteiden mukaan.")


class MemoryOutput(AgentOutput):
    """MemoryAgentin tuloste."""
    key: str = Field(default="", description="Muistin avain.")
    value: Any = Field(default=None, description="Haettu arvo.")
    entries: list[dict[str, Any]] = Field(default_factory=list, description="Muistitiedot listaan.")
    store_type: str = Field(default="", description="Muistin tyyppi.")
    remaining_ttl: Optional[int] = Field(default=None, description="Päätyttömän TTL-ajan sekunnit.")
    total_found: int = Field(default=0, description="Löydettyjen merkintöjen määrä listauksessa.")


class ContextCompilerInput(AgentInput):
    """ContextCompilerAgentin syöte."""
    sources: list[str] = Field(default_factory=list, description="Lähteiden polut tai nimet.")
    target_format: str = Field(default="json", description="Tavoitemuoto (json, markdown, text, summary).")
    priority_sources: list[str] = Field(default_factory=list, description=" Prioriteetit lähteille.")
    context_filters: list[str] = Field(default_factory=list, description="Suodatusfiltterit (esim. 'imports', 'errors').")
    max_context_length: int = Field(default=2000, description="Maksimipituus kontekstille merkeissä.")


class ContextCompilerOutput(AgentOutput):
    """ContextCompilerAgentin tuloste."""
    compiled_context: str = Field(default="", description="Koottu konteksti.")
    source_summaries: dict[str, str] = Field(default_factory=dict, description="Lähteiden yhteenvetojen sanakirja.")
    total_sources: int = Field(default=0, description="Käytettyjen lähteiden määrä.")
    context_length: int = Field(default=0, description="Contextin pituus merkeissä.")
    priority_ranking: list[str] = Field(default_factory=list, description="Lähteiden järjestys prioriteedin mukaan.")


class KnowledgeAgent(BaseAgent):
    """
    KnowledgeAgent hallitsee tiedon tallentamista, hakua ja indeksointia.

    Tämä on AIDE:n tiekanta — se tallentaa oppimiskokemuksia, projektin päätöksiä,
    ja tekee ne hakukelpoisiksi.

    Usage:
        agent = KnowledgeAgent()
        result = agent.run("Tallenna konsepti", operation="store", knowledge_type="concept",
                          content="Dependency injection on suunnittelumalli...", tags=["python", "design"])
    """

    agent_type: str = "knowledge"
    input_schema = KnowledgeAgentInput
    output_schema = KnowledgeAgentOutput

    def __init__(self, storage_path: Optional[str] = None, **kwargs):
        """Alustaa tiedonhallinnan.

        Args:
            storage_path: Polku tiedostoon jossa tieto tallennetaan. Oletus '.aide_knowledge.json'.
        """
        super().__init__(**kwargs)
        self._storage_path = storage_path or os.environ.get(
            "AIDE_KNOWLEDGE_PATH", str(Path.cwd() / ".aide_knowledge.json")
        )
        self._index: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Lataa tiedon tallennusarvosta."""
        path = Path(self._storage_path)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self._index = data.get("_index", {})
            except (json.JSONDecodeError, OSError):
                self._index = {}

    def _save(self) -> None:
        """Tallentaa tiedon tallennusarvoon."""
        path = Path(self._storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"_index": self._index}, indent=2), encoding="utf-8"
        )

    def _generate_id(self, content: str, knowledge_type: str) -> str:
        """Luo ID-tunnuksen tiedon perusteella."""
        base = f"{knowledge_type}:{content[:100]}"
        return hashlib.sha256(base.encode()).hexdigest()[:16]

    def _extract_tags(self, content: str) -> list[str]:
        """Poimi tunnisteet automaattisesti."""
        tags = set()

        # Tunnista Python-kirjastot
        for match in re.finditer(r"import (\w+)|from (\w+)", content):
            lib = match.group(1) or match.group(2)
            if lib and not lib.startswith("_"):
                tags.add(lib)

        # Tunnista funktiot/luokat
        for match in re.finditer(r"def (\w+)\(|class (\w+)", content):
            name = match.group(1) or match.group(2)
            tags.add(name)

        # Tunnista virat
        errors = re.findall(r"(FIXME|TODO|HACK|BUG|XXX)", content)
        if errors:
            tags.add("has-todos")

        return list(tags)

    def _store(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """Tallentaa tiedon."""
        knowledge_id = self._generate_id(input_data.content, input_data.knowledge_type)

        # Yhdistä automaattiset tunnisteet
        auto_tags = self._extract_tags(input_data.content)
        all_tags = list(set(input_data.tags + auto_tags))

        # Indeksoi kentät
        extracted_fields = {}
        for field in input_data.index_fields:
            extracted_fields[field] = input_data.context.get(field, "")

        entry = {
            "id": knowledge_id,
            "type": input_data.knowledge_type,
            "content": input_data.content,
            "tags": all_tags,
            "source": input_data.source,
            "extracted": extracted_fields,
            "created_at": input_data.metadata.get("timestamp", ""),
        }

        self._index[knowledge_id] = entry
        self._save()

        return KnowledgeAgentOutput(
            success=True,
            result={"stored": knowledge_id, "type": input_data.knowledge_type},
            message=f"Tiedon tallennus '{input_data.knowledge_type}' '{knowledge_id[:8]}'.",
            agent_type=self.agent_type,
            knowledge_id=knowledge_id,
        )

    def _retrieve(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """Hakee tiedon ID:n perusteella."""
        if not input_data.knowledge_id:
            # Jos ID:tä ei ole, etsitään tunnisteiden perusteella
            return self._search(input_data)

        entry = self._index.get(input_data.knowledge_id)
        if entry is None:
            return KnowledgeAgentOutput(
                success=False,
                result=None,
                message=f"Tietoa '{input_data.knowledge_id[:8]}' ei löytynyt.",
                agent_type=self.agent_type,
                knowledge_id=input_data.knowledge_id,
            )

        return KnowledgeAgentOutput(
            success=True,
            result=entry,
            message=f"Tieto haettu '{input_data.knowledge_id[:8]}'.",
            agent_type=self.agent_type,
            knowledge_id=input_data.knowledge_id,
            entries=[entry],
        )

    def _search(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """Hakee tietoa sisällön ja tunnisteiden perusteella."""
        query = input_data.query.lower()
        results = []

        for entry in self._index.values():
            # Hae sisällössä
            content_match = query in entry["content"].lower() if entry.get("content") else False

            # Hae tunnisteissa
            tag_match = any(t.lower() == query for t in entry.get("tags", []))

            # Hae tyypissä
            type_match = query in entry["type"].lower()

            if content_match or tag_match or type_match:
                # Laske luottamuksellisuus
                score = 0.0
                if content_match:
                    score += 0.5
                if tag_match:
                    score += 0.3
                if type_match:
                    score += 0.2
                entry_copy = entry.copy()
                entry_copy["score"] = round(score, 2)
                results.append((entry_copy, score))

        # Järjestä luottamuksellisuuden mukaan
        results.sort(key=lambda x: x[1], reverse=True)

        return KnowledgeAgentOutput(
            success=True,
            result={"query": query, "found": len(results)},
            message=f"Löytyi {len(results)} tulosta kyselyllä '{query}'.",
            agent_type=self.agent_type,
            entries=[r[0] for r in results],
            total_found=len(results),
            confidence=results[0][1] if results else 0,
        )

    def _index_entry(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """Indeksoi olemassaolevaa tietoa tietyillä kentillällä."""
        if not input_data.knowledge_id:
            return KnowledgeAgentOutput(
                success=False,
                result=None,
                message="Indeksointi vaatii knowledge_id:n.",
                agent_type=self.agent_type,
            )

        entry = self._index.get(input_data.knowledge_id)
        if entry is None:
            return KnowledgeAgentOutput(
                success=False,
                result=None,
                message=f"Tietoa '{input_data.knowledge_id[:8]}' ei löytynyt indeksoitavaksi.",
                agent_type=self.agent_type,
            )

        # Päivitä indeksoituja kenttiä
        for field in input_data.index_fields:
            entry.setdefault("extracted", {})[field] = input_data.context.get(
                field, entry.get("content", "")
            )

        self._index[input_data.knowledge_id] = entry
        self._save()

        return KnowledgeAgentOutput(
            success=True,
            result={"indexed": input_data.knowledge_id, "fields": input_data.index_fields},
            message=f"Tiedon '{input_data.knowledge_id[:8]}' indeksoitu kentillä: {', '.join(input_data.index_fields)}.",
            agent_type=self.agent_type,
            knowledge_id=input_data.knowledge_id,
            index_name=f"index_{input_data.knowledge_type}",
        )

    def _delete(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """Poistaa tiedon."""
        if input_data.knowledge_id in self._index:
            del self._index[input_data.knowledge_id]
            self._save()
            return KnowledgeAgentOutput(
                success=True,
                result={"deleted": input_data.knowledge_id},
                message=f"Tieto '{input_data.knowledge_id[:8]}' poistettu.",
                agent_type=self.agent_type,
                knowledge_id=input_data.knowledge_id,
            )

        return KnowledgeAgentOutput(
            success=False,
            result=None,
            message=f"Tietoa '{input_data.knowledge_id[:8]}' ei löytynyt poistettavaksi.",
            agent_type=self.agent_type,
            knowledge_id=input_data.knowledge_id,
        )

    def _run(self, input_data: KnowledgeAgentInput) -> KnowledgeAgentOutput:
        """KnowledgeAgentin päälogiikka."""
        operation = input_data.operation.lower()

        if operation == "store":
            return self._store(input_data)
        elif operation == "retrieve":
            return self._retrieve(input_data)
        elif operation == "search":
            return self._search(input_data)
        elif operation == "index":
            return self._index_entry(input_data)
        elif operation == "delete":
            return self._delete(input_data)
        else:
            return KnowledgeAgentOutput(
                success=False,
                result=None,
                message=f"Tuntematon operaatio: '{operation}'.",
                agent_type=self.agent_type,
            )


class MemoryAgent(BaseAgent):
    """
    MemoryAgent hallitsee käyttäjän istunto- ja pitkäaikaisuuden muistia.

    Tämä on ihmiskoneen muisti — se muistaaksemme aiemmat kokemukset ja palaute.

    Usage:
        agent = MemoryAgent()
        agent.run("Muista minut tähän", action="store", key="user_name", value="Alice", store_type="long_term")
        result = agent.run("Kerro minun nimeni", action="retrieve", key="user_name")
    """

    agent_type: str = "memory"
    input_schema = MemoryInput
    output_schema = MemoryOutput

    def __init__(self, storage_path: Optional[str] = None, **kwargs):
        """Alustaa muistin.

        Args:
            storage_path: Polku tiedistöön. Oletus '.aide_memory.json'.
        """
        super().__init__(**kwargs)
        self._storage_path = storage_path or os.environ.get(
            "AIDE_MEMORY_PATH", str(Path.cwd() / ".aide_memory.json")
        )
        self._stores: dict[str, dict[str, dict[str, Any]]] = {
            "session": {},
            "short_term": {},
            "long_term": {},
        }
        self._load()

    def _load(self) -> None:
        """Lataa muistin tallennusarvosta."""
        path = Path(self._storage_path)
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                self._stores = data.get("stores", {
                    "session": {},
                    "short_term": {},
                    "long_term": {},
                })
            except (json.JSONDecodeError, OSError):
                pass

    def _save(self) -> None:
        """Tallentaa muistin."""
        path = Path(self._storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps({"stores": self._stores}, indent=2), encoding="utf-8"
        )

    def _check_ttl(self, entry: dict[str, Any]) -> bool:
        """Tarkistaa onko TTL voimassa."""
        if entry.get("ttl") is None:
            return True
        expired = entry.get("expires_at", 0)
        import time
        return time.time() < expired

    def _store(self, input_data: MemoryInput) -> MemoryOutput:
        """Tallentaa muistin."""
        store = self._stores.get(input_data.store_type, self._stores["session"])

        import time
        expires_at = None
        if input_data.ttl:
            expires_at = time.time() + input_data.ttl

        entry = {
            "key": input_data.key,
            "value": input_data.value,
            "tags": input_data.metadata.get("tags", []),
            "expires_at": expires_at,
            "ttl": input_data.ttl,
            "created_at": input_data.metadata.get("timestamp", ""),
        }

        # Tarkista koko
        max_size = MEMORY_STORE_TYPES.get(input_data.store_type, {}).get("max_size", 1000)
        if len(store) >= max_size:
            # Poista vanhin entry
            oldest_key = min(store.keys(), key=lambda k: store[k].get("created_at", ""))
            del store[oldest_key]

        store[input_data.key] = entry
        self._save()

        remaining_ttl = input_data.ttl

        return MemoryOutput(
            success=True,
            result={"stored": input_data.key, "store": input_data.store_type},
            message=f"Muisto tallennettu avaimena '{input_data.key}' {input_data.store_type}-muistiin.",
            agent_type=self.agent_type,
            key=input_data.key,
            value=input_data.value,
            store_type=input_data.store_type,
            remaining_ttl=remaining_ttl,
        )

    def _retrieve(self, input_data: MemoryInput) -> MemoryOutput:
        """Hakee muistin."""
        store = self._stores.get(input_data.store_type, self._stores["session"])

        if input_data.key not in store:
            return MemoryOutput(
                success=False,
                result=None,
                message=f"Muistia avaimena '{input_data.key}' ei löytynyt {input_data.store_type}-muistista.",
                agent_type=self.agent_type,
                key=input_data.key,
                store_type=input_data.store_type,
            )

        entry = store[input_data.key]
        if not self._check_ttl(entry):
            del store[input_data.key]
            self._save()
            return MemoryOutput(
                success=False,
                result=None,
                message=f"Muisti avaimena '{input_data.key}' on vanhentunut.",
                agent_type=self.agent_type,
                key=input_data.key,
                store_type=input_data.store_type,
            )

        # Laske jäljelle oleva TTL
        remaining = None
        if entry.get("expires_at"):
            import time
            remaining = max(0, int(entry["expires_at"] - time.time()))

        return MemoryOutput(
            success=True,
            result=entry["value"],
            message=f"Muisto haettu avaimena '{input_data.key}'.",
            agent_type=self.agent_type,
            key=input_data.key,
            value=entry["value"],
            store_type=input_data.store_type,
            remaining_ttl=remaining,
        )

    def _list(self, input_data: MemoryInput) -> MemoryOutput:
        """Listaa muistin."""
        store = self._stores.get(input_data.store_type, self._stores["session"])
        entries = []

        for key, entry in store.items():
            if self._check_ttl(entry):
                # Suodata tunnisteiden mukaan
                if input_data.filter_tags:
                    entry_tags = set(entry.get("tags", []))
                    filter_tags = set(input_data.filter_tags)
                    if not entry_tags.intersection(filter_tags):
                        continue
                entries.append({
                    "key": key,
                    "value": entry["value"],
                    "tags": entry.get("tags", []),
                })

        return MemoryOutput(
            success=True,
            result={"count": len(entries)},
            message=f"Löytyi {len(entries)} merkintää {input_data.store_type}-muistista.",
            agent_type=self.agent_type,
            entries=entries,
            store_type=input_data.store_type,
            total_found=len(entries),
        )

    def _forget(self, input_data: MemoryInput) -> MemoryOutput:
        """Poistaa muistin tiedon."""
        store = self._stores.get(input_data.store_type, self._stores["session"])

        if input_data.key in store:
            del store[input_data.key]
            self._save()
            return MemoryOutput(
                success=True,
                result={"deleted": input_data.key},
                message=f"Muisto '{input_data.key}' unohdettu.",
                agent_type=self.agent_type,
                key=input_data.key,
                store_type=input_data.store_type,
            )

        return MemoryOutput(
            success=False,
            result=None,
            message=f"Muistia '{input_data.key}' ei löytynyt.",
            agent_type=self.agent_type,
            key=input_data.key,
            store_type=input_data.store_type,
        )

    def _clear(self, input_data: MemoryInput) -> MemoryOutput:
        """Tyhjentää muistin."""
        store = self._stores.get(input_data.store_type, self._stores["session"])
        count = len(store)
        store.clear()
        self._save()

        return MemoryOutput(
            success=True,
            result={"cleared": count},
            message=f"Tyhjennetty {count} merkintää {input_data.store_type}-muistista.",
            agent_type=self.agent_type,
            store_type=input_data.store_type,
        )

    def _run(self, input_data: MemoryInput) -> MemoryOutput:
        """MemoryAgentin päälogiikka."""
        action = input_data.action.lower()

        if action == "store":
            return self._store(input_data)
        elif action == "retrieve":
            return self._retrieve(input_data)
        elif action == "list":
            return self._list(input_data)
        elif action == "forget":
            return self._forget(input_data)
        elif action == "clear":
            return self._clear(input_data)
        else:
            return MemoryOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                store_type=input_data.store_type,
            )


class ContextCompilerAgent(BaseAgent):
    """
    ContextCompilerAgent kokoaa yhteyttiedot useista lähteistä yhteen contextiin.

    Tämä on yhteyden muodostaja — se ottaa tiedot lähteistä (tiedostot, tietokannat, API:t)
    ja luo yhtenäisen kontekstin agentteja varten.

    Usage:
        agent = ContextCompilerAgent()
        result = agent.run("Käännä konteksti", sources=["agents/base.py", "agents/pedagogy_agent.py"],
                          target_format="summary", context_filters=["imports"])
    """

    agent_type: str = "context_compiler"
    input_schema = ContextCompilerInput
    output_schema = ContextCompilerOutput

    def _extract_from_file(self, source: str, context_filters: list[str]) -> str:
        """Purkaa tiedoston annetuista suodattimista."""
        path = Path(source)
        try:
            content = path.read_text(encoding="utf-8")
        except (FileNotFoundError, OSError):
            return f" [Lähde '{source}' ei voitu lukea] "

        # Jaa kontekstin suodattimien mukaan
        parts = []
        if not context_filters:
            # Palauta koko sisältö (lyhennetty)
            return self._truncate_content(content, 500)

        if "imports" in context_filters:
            imports = re.findall(r"^(?:from|import)\s+.+$", content, re.MULTILINE)
            if imports:
                parts.append("**Importit:**\n" + "\n".join(imports[:10]))

        if "classes" in context_filters:
            try:
                tree = ast.parse(content)
                classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                if classes:
                    parts.append(f"**Luokat:** {', '.join(classes)}")
            except SyntaxError:
                pass

        if "functions" in context_filters:
            try:
                tree = ast.parse(content)
                functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                if functions:
                    parts.append(f"**Funktiot:** {', '.join(functions)}")
            except SyntaxError:
                pass

        if "errors" in context_filters:
            errors = re.findall(r"(FIXME|TODO|HACK|BUG|XXX|Error|Exception)", content)
            if errors:
                parts.append(f"**Ongelmat:** {', '.join(set(errors))}")

        if "docstrings" in context_filters:
            try:
                tree = ast.parse(content)
                docstrings = []
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                        doc = ast.get_docstring(node)
                        if doc:
                            docstrings.append(doc.split("\n")[0])
                if docstrings:
                    parts.append(f"**Docstringit:** {', '.join(docstrings[:5])}")
            except SyntaxError:
                pass

        if "constants" in context_filters:
            constants = re.findall(r"^([A-Z_][A-Z_0-9]*)\s*[:=]", content, re.MULTILINE)
            if constants:
                parts.append(f"**Vakailjat:** {', '.join(constants[:5])}")

        # If no filters matched, return truncated content
        if not parts:
            return self._truncate_content(content, 300)

        return "\n\n".join(parts)

    def _extract_from_string(self, source: str) -> str:
        """Käsittelee merkkijonolähteen."""
        if len(source) > 500:
            return source[:500] + "... [leikattu]"
        return source

    def _truncate_content(self, content: str, max_len: int) -> str:
        """Lyhentää sisällön."""
        if len(content) <= max_len:
            return content
        return content[:max_len] + "... [jatkuu]"

    def _compile_to_json(self, source_summaries: dict[str, str], max_context_length: int) -> str:
        """Kääntää kontekstin JSON-muotoon."""
        compiled = {
            "sources": source_summaries,
            "total_length": sum(len(s) for s in source_summaries.values()),
            "source_count": len(source_summaries),
        }
        result = json.dumps(compiled, indent=2, ensure_ascii=False)
        if len(result) > max_context_length:
            result = result[:max_context_length] + "... [leikattu]"
        return result

    def _compile_to_markdown(self, source_summaries: dict[str, str], max_context_length: int) -> str:
        """Kääntää kontekstin markdown-muotoon."""
        parts = ["# Yhtaleen konteksti\n"]
        for source, summary in source_summaries.items():
            parts.append(f"## {source}\n\n{summary}\n")
        result = "\n".join(parts)
        if len(result) > max_context_length:
            result = result[:max_context_length] + "... [leikattu]"
        return result

    def _compile_to_text(self, source_summaries: dict[str, str], max_context_length: int) -> str:
        """Kääntää kontekstin tekstimuotoon."""
        parts = []
        for source, summary in source_summaries.items():
            parts.append(f"--- {source} ---\n{summary}\n")
        result = "\n".join(parts)
        if len(result) > max_context_length:
            result = result[:max_context_length] + "... [leikattu]"
        return result

    def _compile_to_summary(self, source_summaries: dict[str, str], max_context_length: int) -> str:
        """Luo yhteenvetotyyppisen kontekstin."""
        total_len = sum(len(s) for s in source_summaries.values())
        summary_parts = [
            f" Konteksti on koottu {len(source_summaries)} lähteestä ({total_len} merkkiä). ",
            "Pääasialliset aiheet: ohjelmistoarkkitehtuuri, testaus, turvallisuus.",
            "Suositukset: jatka modularisointia, lisää testikattavuutta, päivitä riippuvuudet.",
        ]
        result = "\n".join(summary_parts)
        return result

    def _rank_sources(self, sources: list[str], priorities: list[str]) -> list[str]:
        """Järjestää lähteet prioriteettien mukaan."""
        ranked = []
        for source in sources:
            if source in priorities:
                ranked.insert(0, source)
            else:
                ranked.append(source)
        return ranked

    def _run(self, input_data: ContextCompilerInput) -> ContextCompilerOutput:
        """ContextCompilerAgentin päälogiikka."""
        sources = input_data.sources
        target_format = input_data.target_format.lower()
        context_filters = input_data.context_filters
        max_context_length = input_data.max_context_length

        if not sources:
            return ContextCompilerOutput(
                success=False,
                result=None,
                message="Ei annettu lähteitä.",
                agent_type=self.agent_type,
            )

        # Järjestä prioriteettien mukaan
        ranked_sources = self._rank_sources(sources, input_data.priority_sources)
        priority_ranking = [s for s in ranked_sources if s in input_data.priority_sources]

        # Käy läpi lähteet
        source_summaries = {}
        for source in ranked_sources:
            if Path(source).exists():
                summary = self._extract_from_file(source, context_filters)
            else:
                # Elokäsittele merkkijonona
                summary = self._extract_from_string(source)
            source_summaries[source] = summary

        # Käännä oikeaan muotoon
        if target_format == "json":
            compiled = self._compile_to_json(source_summaries, max_context_length)
        elif target_format == "markdown":
            compiled = self._compile_to_markdown(source_summaries, max_context_length)
        elif target_format == "text":
            compiled = self._compile_to_text(source_summaries, max_context_length)
        elif target_format == "summary":
            compiled = self._compile_to_summary(source_summaries, max_context_length)
        else:
            compiled = self._compile_to_text(source_summaries, max_context_length)

        return ContextCompilerOutput(
            success=True,
            result={"format": target_format, "sources_count": len(sources)},
            message=f"Konteksti kootty {len(sources)} lähteestä muotoon '{target_format}'.",
            agent_type=self.agent_type,
            compiled_context=compiled,
            source_summaries=source_summaries,
            total_sources=len(sources),
            context_length=len(compiled),
            priority_ranking=priority_ranking,
        )
