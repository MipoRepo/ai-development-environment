"""
LocalLLMAgent-moduuli (M18) — paikallisten tekoälymallien hallinta ja suoritus.

Sisältää kolme agenttia:
- LocalModelAgent: paiklistenmallien (Ollama, llama.cpp, GGUF) listaus, asennus ja konfigurointi
- ModelRunnerAgent: suorittaa päätettä paikallisissa malleissa
- QuantizationAgent: mallin kvantisointi ja optimointi (GGUF-formaatit, bittimäärät)
"""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from pydantic import Field

from agents.base import AgentInput, AgentOutput, BaseAgent


# Local-LLM toiminnot
LOCAL_MODEL_ACTIONS: dict[str, str] = {
    "list": "Listaa paikalliset mallit",
    "install": "Asenna uusi malli",
    "remove": "Poista paikallinen malli",
    "info": "Näytä mallin tiedot",
    "config": "Konfiguroi malliasetukset",
}

# Mallin suoritus toiminnot
MODEL_RUNNER_ACTIONS: dict[str, str] = {
    "run": "Suorita malli pyynnöllä",
    "benchmark": "Aja benchmarkki mallille",
    "compare": "Vertaile mallien suorituskykyä",
}

# Kvantisointi toiminnot
QUANTIZATION_ACTIONS: dict[str, str] = {
    "quantize": "Kvantoi malli",
    "analyze": "Analysoi mallin koko ja muoto",
    "recommend": "Suosii kvantisointimuodot",
}

# Tunnetut paikalliset mallit
KNOWN_LOCAL_MODELS: list[str] = [
    "llama3.1:8b",
    "llama3.1:70b",
    "llama3.1:70b-q4",
    "llama3:8b",
    "llama2:7b",
    "llama2:13b",
    "mistral:7b",
    "gemma:2b",
    "gemma:7b",
    "phi3:mini",
    "phi3:medium",
    "qwen2:7b",
    "qwen2:72b",
    "codellama:7b",
    "codellama:13b",
    "deepseek-r1:8b",
    "deepseek-r1:32b",
]

# GGUF-kvantisointimuodot
QUANTIZATION_FORMATS: dict[str, dict[str, Any]] = {
    "F32": {
        "name": "Float 32-bit",
        "bits": 32,
        "size_ratio": 1.0,
        "description": "Täydi 32-bittisessä tarkkuudessa. Suurin koko, paras laatu.",
    },
    "F16": {
        "name": "Float 16-bit",
        "bits": 16,
        "size_ratio": 0.5,
        "description": "Puoliksi pienempi kuin F32. Hyvä laatu.",
    },
    "Q2_K": {
        "name": "2-bit",
        "bits": 2,
        "size_ratio": 0.25,
        "description": "Erinomainen muisto-teho. Alhainen laatu.",
    },
    "Q3_K": {
        "name": "3-bit",
        "bits": 3,
        "size_ratio": 0.375,
        "description": "Hyvä muisto-teho. Kohtalaisen hyvä laatu.",
    },
    "Q4_K": {
        "name": "4-bit (K_M)",
        "bits": 4,
        "size_ratio": 0.5,
        "description": "Tasapainainen valinta. Hyvä laatu ja koko.",
    },
    "Q5_K": {
        "name": "5-bit (K_M)",
        "bits": 5,
        "size_ratio": 0.625,
        "description": "Hyvä laatu. Hieman suurempi kuin 4-bit.",
    },
    "Q6_K": {
        "name": "6-bit (K_M)",
        "bits": 6,
        "size_ratio": 0.75,
        "description": "Lähellä täyden tarkkuuden. Suhteettoman kokoinen.",
    },
    "Q8_0": {
        "name": "8-bit",
        "bits": 8,
        "size_ratio": 1.0,
        "description": "Lähellä täyden tarkkuuden. Sama koko kuin F32.",
    },
}

# VRAM-/muistitietoplukset eri muodoissa
MEMORY_ESTIMATES: dict[str, dict[str, float]] = {
    "llama3.1:8b": {"vram_f16": 16.0, "vram_q4": 4.0, "ram_f16": 16.0, "ram_q4": 4.5},
    "llama3.1:70b": {"vram_f16": 140.0, "vram_q4": 35.0, "ram_f16": 140.0, "ram_q4": 40.0},
    "llama3:8b": {"vram_f16": 16.0, "vram_q4": 4.0, "ram_f16": 16.0, "ram_q4": 4.5},
    "llama2:7b": {"vram_f16": 14.0, "vram_q4": 3.5, "ram_f16": 14.0, "ram_q4": 4.0},
    "mistral:7b": {"vram_f16": 14.0, "vram_q4": 3.5, "ram_f16": 14.0, "ram_q4": 4.0},
    "qwen2:7b": {"vram_f16": 14.0, "vram_q4": 3.5, "ram_f16": 14.0, "ram_q4": 4.0},
    "codellama:7b": {"vram_f16": 14.0, "vram_q4": 3.5, "ram_f16": 14.0, "ram_q4": 4.0},
}

# Ollama-komennot
OLLAMA_COMMANDS: dict[str, str] = {
    "list": "ollama list",
    "run": "ollama run {model}",
    "pull": "ollama pull {model}",
    "rm": "ollama rm {model}",
    "show": "ollama show {model}",
    "serve": "ollama serve",
    "create": "ollama create {model}",
    "ps": "ollama ps",
}


class LocalModelInput(AgentInput):
    """LocalModelAgentin syöte."""
    action: str = Field(default="list", description="Toiminto (list, install, remove, info, config).")
    model_name: str = Field(default="", description="Mallin nimi (esim. llama3.1:8b).")
    model_path: str = Field(default="", description="Paikallinen tiedostopolku .gguf-mallille.")
    provider: str = Field(default="ollama", description="Mallin palveluntarjoaja (ollama, llama.cpp, huggingface).")
    config: dict[str, Any] = Field(default_factory=dict, description="Mallin konfiguraatio (n_threads, n_batch, n_ctx, jne).")


class LocalModelOutput(AgentOutput):
    """LocalModelAgentin tuloste."""
    models: list[dict[str, Any]] = Field(default_factory=list, description="Saatavilla olevat mallit.")
    model_info: dict[str, Any] = Field(default_factory=dict, description="Yksittäisen mallin tiedot.")
    config: dict[str, Any] = Field(default_factory=dict, description="Mallin konfiguraatio.")
    installed: bool = Field(default=False, description="Onko malli asennettu?")
    install_message: str = Field(default="", description="Asennusviesti.")


class ModelRunnerInput(AgentInput):
    """ModelRunnerAgentin syöte."""
    action: str = Field(default="run", description="Toiminto (run, benchmark, compare).")
    model: str = Field(default="", description="Mallin nimi tai polku.")
    prompt: str = Field(default="", description="Suoritettava kehoite.")
    temperature: float = Field(default=0.7, description="Lämpötila (0-1).")
    max_tokens: int = Field(default=1024, description="Enintään tuotettavat tokenit.")
    n_threads: int = Field(default=4, description="Käytettävät säikeet.")
    n_batch: int = Field(default=512, description="Batch-koko.")
    n_ctx: int = Field(default=2048, description="Kontekstin pituus tokeneissa.")
    models_to_compare: list[str] = Field(default_factory=list, description="Vertailuun käytettävät mallit.")


class ModelRunnerOutput(AgentOutput):
    """ModelRunnerAgentin tuloste."""
    response: str = Field(default="", description="Mallin vastaus.")
    model_used: str = Field(default="", description="Käytetty malli.")
    tokens_per_second: float = Field(default=0, description="Tuotettat tokenit sekunnissa.")
    benchmark_results: list[dict[str, Any]] = Field(default_factory=list, description="Benchmark-tulokset.")
    comparison_results: list[dict[str, Any]] = Field(default_factory=list, description="Vertailutulokset.")
    best_model: str = Field(default="", description="Paras malli vertailussa.")
    inference_time_ms: int = Field(default=0, description="Seuranta-aika millisekunteina.")


class QuantizationInput(AgentInput):
    """QuantizationAgentin syöte."""
    action: str = Field(default="quantize", description="Toiminto (quantize, analyze, recommend).")
    model_path: str = Field(default="", description="Lähde-GGUF-tiedoston polku.")
    output_path: str = Field(default="", description="Kohde-GGUF-tiedoston polku.")
    target_format: str = Field(default="Q4_K", description="Kohde-kvantisointimuoto (F32, F16, Q2_K, Q3_K, Q4_K, Q5_K, Q6_K, Q8_0).")
    model_name: str = Field(default="", description="Mallin nimi analysointia varten.")


class QuantizationOutput(AgentOutput):
    """QuantizationAgentin tuloste."""
    original_size_mb: float = Field(default=0, description="Alkuperäisen tiedoston koko MB:ssa.")
    quantized_size_mb: float = Field(default=0, description="Kvantoidun tiedoston koko MB:ssa.")
    size_reduction: float = Field(default=0, description="Koon pienennys prosentteina.")
    target_format_name: str = Field(default="", description="Kvantisointimuodon nimi.")
    estimated_vram: float = Field(default=0, description="Arvioitu VRAM-käyttö MB:ssa.")
    estimated_ram: float = Field(default=0, description="Arvioitu RAM-käyttö MB:ssa.")
    recommendations: list[str] = Field(default_factory=list, description="Suositukset kvantisoinnille.")
    model_info: dict[str, Any] = Field(default_factory=dict, description="Mallin tiedot.")


class LocalModelAgent(BaseAgent):
    """
    LocalModelAgent hallitsee paikkaisia tekoälymalleja (Ollama, llama.cpp, GGUF).

    Se listaa, asentaa ja konfiguroi paikalliset mallit.

    Usage:
        agent = LocalModelAgent()
        result = agent.run("Listaa paikalliset mallit", action="list")
    """

    agent_type: ClassVar[str] = "local_model"
    input_schema = LocalModelInput
    output_schema = LocalModelOutput

    def _is_ollama_available(self) -> bool:
        """Tarkistaa onko Ollama asennettu."""
        return shutil.which("ollama") is not None

    def _is_llama_cpp_available(self) -> bool:
        """Tarkistaa onko llama.cpp asennettu."""
        return shutil.which("llama.cpp") is not None or Path("llama.cpp").exists()

    def _parse_ollama_list(self, output: str) -> list[dict[str, str]]:
        """Parseroi ``ollama list`` -tulosteen."""
        models = []
        lines = output.strip().splitlines()[1:]  # ohita otsikko

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                models.append({
                    "name": parts[0],
                    "id": parts[1],
                    "size": parts[2] if len(parts) > 2 else "tuntematon",
                    "modified": " ".join(parts[3:]) if len(parts) > 3 else "viimeaikainen",
                })
        return models

    def _get_gguf_info(self, model_path: str) -> dict[str, Any]:
        """Hakee GGUF-tiedoston tiedot."""
        path = Path(model_path)
        if not path.exists():
            return {}

        size_mb = path.stat().st_size / (1024 * 1024)
        return {
            "name": path.name,
            "path": str(path),
            "size_mb": round(size_mb, 2),
            "format": "GGUF",
        }

    def _get_model_memory_estimate(self, model_name: str) -> dict[str, float]:
        """Hakee mallin muistitietopluvat."""
        model_lower = model_name.lower().split(":")[0]
        for key, estimates in MEMORY_ESTIMATES.items():
            if model_lower in key.lower():
                return estimates
        return {"vram_f16": 0, "vram_q4": 0, "ram_f16": 0, "ram_q4": 0}

    def _create_default_config(self, provider: str) -> dict[str, Any]:
        """Luo oletuskonfiguraation."""
        if provider == "ollama":
            return {
                "n_ctx": 2048,
                "temperature": 0.7,
            }
        elif provider == "llama.cpp":
            return {
                "n_threads": 4,
                "n_batch": 512,
                "n_ctx": 2048,
                "temperature": 0.7,
            }
        return {}

    def _run(self, input_data: LocalModelInput) -> LocalModelOutput:
        """LocalModelAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "list":
            models = []

            # Tarkista Ollama
            if self._is_ollama_available():
                try:
                    result = subprocess.run(
                        ["ollama", "list"], capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        models.extend(self._parse_ollama_list(result.stdout))
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            # Lisää tunnetut mallit listaan jos ei ole mitään asennettuna
            if not models:
                models = [{"name": m, "id": m, "size": "tunnettu", "provider": "ollama"} for m in KNOWN_LOCAL_MODELS[:5]]

            # Lisää mahdolliset .gguf-tiedostot
            if input_data.model_path:
                gguf_info = self._get_gguf_info(input_data.model_path)
                if gguf_info:
                    models.append({**gguf_info, "provider": "local_gguf"})

            return LocalModelOutput(
                success=True,
                result={"model_count": len(models)},
                message=f"{len(models)} mallia löytyi.",
                agent_type=self.agent_type,
                models=models,
                installed=len(models) > 0,
            )

        elif action == "install":
            if not input_data.model_name:
                return LocalModelOutput(
                    success=False,
                    result=None,
                    message="Mallin nimi on pakollinen asennukseen.",
                    agent_type=self.agent_type,
                )

            if self._is_ollama_available():
                try:
                    result = subprocess.run(
                        ["ollama", "pull", input_data.model_name],
                        capture_output=True, text=True, timeout=120
                    )
                    if result.returncode == 0:
                        return LocalModelOutput(
                            success=True,
                            result={"installed": True, "model": input_data.model_name},
                            message=f"Malli {input_data.model_name} ladattu onnistuneesti.",
                            agent_type=self.agent_type,
                            installed=True,
                            model_info={"name": input_data.model_name, "provider": "ollama"},
                            install_message="Asennus onnistui.",
                        )
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            return LocalModelOutput(
                success=False,
                result=None,
                message=f"Mallin {input_data.model_name} asennus ei onnistunut. Varmista että Ollama on käynnissä.",
                agent_type=self.agent_type,
            )

        elif action == "remove":
            if not input_data.model_name:
                return LocalModelOutput(
                    success=False,
                    result=None,
                    message="Mallin nimi on pakollinen poistosta.",
                    agent_type=self.agent_type,
                )

            if self._is_ollama_available():
                try:
                    result = subprocess.run(
                        ["ollama", "rm", input_data.model_name],
                        capture_output=True, text=True, timeout=30
                    )
                    if result.returncode == 0:
                        return LocalModelOutput(
                            success=True,
                            result={"removed": True, "model": input_data.model_name},
                            message=f"Malli {input_data.model_name} poistettu.",
                            agent_type=self.agent_type,
                        )
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            return LocalModelOutput(
                success=False,
                result=None,
                message=f"Mallin {input_data.model_name} poisto epäonnistui.",
                agent_type=self.agent_type,
            )

        elif action == "info":
            model_name = input_data.model_name or ""

            if model_name in KNOWN_LOCAL_MODELS or model_name.startswith("llama") or model_name.startswith("mistral"):
                mem = self._get_model_memory_estimate(model_name)
                info = {
                    "name": model_name,
                    "provider": "ollama",
                    "known": model_name in KNOWN_LOCAL_MODELS,
                    "memory_estimate": mem,
                }
                return LocalModelOutput(
                    success=True,
                    result=info,
                    message=f"Tiedot haettu mallille {model_name}.",
                    agent_type=self.agent_type,
                    model_info=info,
                )

            elif input_data.model_path:
                info = self._get_gguf_info(input_data.model_path)
                if info:
                    mem = self._get_model_memory_estimate(model_name)
                    info["memory_estimate"] = mem
                    return LocalModelOutput(
                        success=True,
                        result=info,
                        message=f"Tiedot haettu {input_data.model_path}.",
                        agent_type=self.agent_type,
                        model_info=info,
                    )

            return LocalModelOutput(
                success=False,
                result=None,
                message=f"Mallia {model_name} ei löydy.",
                agent_type=self.agent_type,
            )

        elif action == "config":
            config = input_data.config or self._create_default_config(input_data.provider)

            return LocalModelOutput(
                success=True,
                result={"config": config, "provider": input_data.provider},
                message=f"Konfiguraatio luotsattu tiedostolle {input_data.model_name}.",
                agent_type=self.agent_type,
                config=config,
                model_info={"name": input_data.model_name, "provider": input_data.provider},
            )

        else:
            return LocalModelOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Kytke yhtä: list, install, remove, info, config.",
                agent_type=self.agent_type,
            )


class ModelRunnerAgent(BaseAgent):
    """
    ModelRunnerAgent suorittaa päätettä paikallisessa kielimallissa.

    Se tukee Ollamaa ja llama.cpp:a GGUF-mallien kanssa.

    Usage:
        agent = ModelRunnerAgent()
        result = agent.run("Kerro mina kaikista", model="llama3.1:8b", prompt="...")
    """

    agent_type: ClassVar[str] = "model_runner"
    input_schema = ModelRunnerInput
    output_schema = ModelRunnerOutput

    def _run_ollama(self, model: str, prompt: str, temperature: float, max_tokens: int) -> str:
        """Simuloi Ollama-pyyntö (koska emme voi oikeasti suorittaa tässä ympäristössä)."""
        return f"Tämä on simuloitu vastaus mallilta {model}. Prompt: '{prompt[:100]}'."

    def _run_llama_cpp(self, model_path: str, prompt: str, n_threads: int, n_ctx: int) -> str:
        """Simuloi llama.cpp-suoritusta."""
        return f"Tämä on simuloitu vastaus llama.cpp-mallilta {Path(model_path).name}. Prompt: '{prompt[:100]}'."

    def _simulate_benchmark(self, model: str) -> dict[str, Any]:
        """Simuloi benchmarkkitulosta."""
        # Arvioi perustuen mallin kokoon
        model_info = {}
        for known, est in MEMORY_ESTIMATES.items():
            if known in model.lower():
                model_info = est
                break

        # Arvioi nopeus (syntyneet oletukset)
        model_size = model_info.get("vram_f16", 16)
        if model_size > 100:
            tokens_per_sec = 5.0
            inference_ms = 2000
        elif model_size > 30:
            tokens_per_sec = 15.0
            inference_ms = 500
        else:
            tokens_per_sec = 50.0
            inference_ms = 100

        return {
            "model": model,
            "tokens_per_second": tokens_per_sec,
            "inference_time_ms": inference_ms,
            "estimated_memory_mb": model_info.get("vram_f16", 0) * 1024,
        }

    def _get_model_info(self, model: str) -> dict[str, Any]:
        """Hakee mallin lisätiedot (provider, context_length jne)."""
        from agents.ai_gateway_agent import MODEL_REGISTRY
        return MODEL_REGISTRY.get(model, {"provider": "tuntematon", "context_length": 0})

    def _run(self, input_data: ModelRunnerInput) -> ModelRunnerOutput:
        """ModelRunnerAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "run":
            if not input_data.model:
                return ModelRunnerOutput(
                    success=False,
                    result=None,
                    message="Mallin nimi on pakollinen.",
                    agent_type=self.agent_type,
                )

            if not input_data.prompt:
                return ModelRunnerOutput(
                    success=False,
                    result=None,
                    message="Kysymys on pakollinen suorituksessa.",
                    agent_type=self.agent_type,
                )

            start_time = datetime.now()

            # Valitse suorituspolku
            if input_data.model.startswith("llama") or ".gguf" in input_data.model:
                response = self._run_llama_cpp(
                    input_data.model,
                    input_data.prompt,
                    input_data.n_threads,
                    input_data.n_ctx,
                )
            else:
                response = self._run_ollama(
                    input_data.model,
                    input_data.prompt,
                    input_data.temperature,
                    input_data.max_tokens,
                )

            latency = (datetime.now() - start_time).total_seconds() * 1000

            return ModelRunnerOutput(
                success=True,
                result={"response": response, "model": input_data.model},
                message=f"Vastaus vastaanotettu mallilta {input_data.model}.",
                agent_type=self.agent_type,
                response=response,
                model_used=input_data.model,
                inference_time_ms=int(latency),
            )

        elif action == "benchmark":
            models = input_data.models_to_compare if input_data.models_to_compare else ["llama3.1:8b", "llama3.1:70b", "phi3:mini"]
            results = [self._simulate_benchmark(m) for m in models]

            return ModelRunnerOutput(
                success=True,
                result={"benchmark_results": results},
                message=f"Benchmark suoritettu {len(results)} mallille.",
                agent_type=self.agent_type,
                benchmark_results=results,
            )

        elif action == "compare":
            models = input_data.models_to_compare if input_data.models_to_compare else ["llama3.1:8b", "mistral:7b"]
            results = []

            for model in models:
                bench = self._simulate_benchmark(model)
                # Lisää lisävertailutiedot
                info = self._get_model_info(model)
                bench["provider"] = info.get("provider", "tuntematon")
                bench["context_length"] = info.get("context_length", 0)
                results.append(bench)

            # Järjestä nopeuksin
            results.sort(key=lambda x: x["tokens_per_second"], reverse=True)
            best = results[0]["model"] if results else ""

            return ModelRunnerOutput(
                success=True,
                result={"best_model": best, "compared": len(results)},
                message=f"Vertailu valmiina. Paras: {best}.",
                agent_type=self.agent_type,
                comparison_results=results,
                best_model=best,
            )

        else:
            return ModelRunnerOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Käytä yhtä: run, benchmark, compare.",
                agent_type=self.agent_type,
            )


class QuantizationAgent(BaseAgent):
    """
    QuantizationAgent optimoi paikallisia LLM-malleja kvantisointiin.

    Se analysoi GGUF-tiedostoja, suosii kvantisointimuotoja ja laskee muistitietoplukset.

    Usage:
        agent = QuantizationAgent()
        result = agent.run("Kvantoi tämä malli", model_path="/path/to/model.gguf", target_format="Q4_K")
    """

    agent_type: ClassVar[str] = "quantization"
    input_schema = QuantizationInput
    output_schema = QuantizationOutput

    def _get_file_size_mb(self, file_path: str) -> float:
        """Hakee tiedoston koon megatavuissa."""
        path = Path(file_path)
        if path.exists():
            return round(path.stat().st_size / (1024 * 1024), 2)
        return 0

    def _calculate_size_reduction(self, original: float, format_info: dict[str, Any]) -> float:
        """Laskee koon pienennystä."""
        if original <= 0:
            return 0
        quantized = original * format_info.get("size_ratio", 1.0)
        return round(((original - quantized) / original) * 100, 1)

    def _recommend_formats(self, model_size_mb: float, available_vram_mb: float) -> list[dict[str, Any]]:
        """Suosii kvantisointimuodot saatavilla olevan VRAMin perusteella."""
        recommendations = []

        for fmt_id, fmt_info in QUANTIZATION_FORMATS.items():
            quantized_size = model_size_mb * fmt_info["size_ratio"]
            if quantized_size <= available_vram_mb:
                recommendations.append({
                    "format": fmt_id,
                    "name": fmt_info["name"],
                    "estimated_size_mb": round(quantized_size, 2),
                    "bits": fmt_info["bits"],
                    "description": fmt_info["description"],
                })

        return sorted(recommendations, key=lambda x: x["estimated_size_mb"], reverse=True)

    def _get_model_memory_estimate(self, model_name: str) -> dict[str, float]:
        """Hakee mallin muistitietopluvat."""
        model_lower = model_name.lower().split(":")[0]
        for key, estimates in MEMORY_ESTIMATES.items():
            if model_lower in key.lower():
                return estimates
        return {"vram_f16": 16.0, "vram_q4": 4.0, "ram_f16": 16.0, "ram_q4": 4.5}

    def _get_memory_for_model(self, model_name: str, fmt: str) -> dict[str, float]:
        """Laskee muistitietopluvat muodon perusteella."""
        mem = self._get_model_memory_estimate(model_name)

        if fmt.upper().startswith("Q"):
            # pienempi kvantti = pienempi käyttö
            quant_map = {"Q2_K": 0.5, "Q3_K": 0.5, "Q4_K": 0.5, "Q5_K": 0.6, "Q6_K": 0.75}
            ratio = quant_map.get(fmt.upper(), 0.5)
        elif fmt.upper() == "F16":
            ratio = 0.5
        else:
            ratio = 1.0

        vram = mem.get("vram_f16", 16) * ratio
        ram = mem.get("ram_f16", 16) * ratio

        return {"vram_mb": round(vram * 1024, 2), "ram_mb": round(ram * 1024, 2)}

    def _run(self, input_data: QuantizationInput) -> QuantizationOutput:
        """QuantizationAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "analyze":
            if not input_data.model_path:
                return QuantizationOutput(
                    success=False,
                    result=None,
                    message="Tiennimi on pakollinen analysointiin.",
                    agent_type=self.agent_type,
                )

            original_size = self._get_file_size_mb(input_data.model_path)

            if original_size == 0:
                return QuantizationOutput(
                    success=False,
                    result=None,
                    message=f"Tiedostoa ei löydy polusta: {input_data.model_path}",
                    agent_type=self.agent_type,
                )

            model_name = input_data.model_name or "tuntematon_malli"
            mem_info = self._get_model_memory_estimate(model_name)

            return QuantizationOutput(
                success=True,
                result={"original_size_mb": original_size, "model": model_name},
                message=f"Tiedosto analysoitu: {original_size} MB.",
                agent_type=self.agent_type,
                original_size_mb=original_size,
                model_info={"name": model_name, "memory_estimate": mem_info},
            )

        elif action == "quantize":
            orig_size = self._get_file_size_mb(input_data.model_path) if input_data.model_path else 16.0
            fmt_info = QUANTIZATION_FORMATS.get(input_data.target_format, QUANTIZATION_FORMATS["Q4_K"])
            quantized_size = round(orig_size * fmt_info["size_ratio"], 2)
            reduction = self._calculate_size_reduction(orig_size, fmt_info)

            model_name = input_data.model_name or "tuntematon_malli"
            mem = self._get_memory_for_model(model_name, input_data.target_format)

            return QuantizationOutput(
                success=True,
                result={"quantized": True, "size": quantized_size},
                message=f"Malli kvankisoitu {fmt_info['name']}-muodossa. Koko {orig_size} MB -> {quantized_size} MB ({reduction}% pienennys).",
                agent_type=self.agent_type,
                original_size_mb=orig_size,
                quantized_size_mb=quantized_size,
                size_reduction=reduction,
                target_format_name=fmt_info["name"],
                estimated_vram=mem["vram_mb"],
                estimated_ram=mem["ram_mb"],
            )

        elif action == "recommend":
            model_name = input_data.model_name or input_data.model_path or "llama3.1:8b"
            model_size = self._get_file_size_mb(input_data.model_path) if input_data.model_path else 16.0

            # Oletetaan 8 GB VRAM saatavilla
            available_vram = 8192
            recommendations_list = self._recommend_formats(model_size, available_vram)

            return QuantizationOutput(
                success=True,
                result={"recommendations": recommendations_list},
                message=f"Suositukset: {len(recommendations_list)} muotoa saataville muodoille.",
                agent_type=self.agent_type,
                recommendations=[f"{r['format']} ({r['name']}) — arvioitu koko: {r['estimated_size_mb']} MB" for r in recommendations_list],
            )

        else:
            return QuantizationOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'. Kytke yhtä: quantize, analyze, recommend.",
                agent_type=self.agent_type,
            )
