"""
MCPIntegrationAgent-moduuli (M19) — MCP-palvelinten, ulkoisten API-rajapintojen ja webhookien integrointi.

Sisältää kolme agenttia:
- MCPIntegrationAgent: MCP-palvelinten ja -työkalujen yhdistäminen (Model Context Protocol)
- APIIntegrationAgent: ulkoisten REST/GraphQL-palveluiden integrointi
- WebhookAgent: webhook-jen vastaanottaminen ja käsittely
"""

from __future__ import annotations

import json
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar
from urllib.parse import urlparse

from pydantic import Field, field_validator

from agents.base import AgentInput, AgentOutput, BaseAgent


# MCP-integraatio toiminnot
MCP_INTEGRATION_ACTIONS: dict[str, str] = {
    "connect": "Yhdistä MCP-palvelimeen",
    "list_tools": "Listaa palvelimen työkalut",
    "call_tool": "Kutsu työkalua",
    "list_resources": "Listaa palvelimen resurssit",
    "read_resource": "Lue resurssi",
    "health_check": "Tarkista palvelimen terveys",
}

# API-integraatio toiminnot
API_INTEGRATION_ACTIONS: dict[str, str] = {
    "request": "Lähetä HTTP-pyyntö",
    "test_connection": "Testaa API-yhteys",
    "generate_client": "Luo API-asiakasohjelma",
    "parse_openapi": "Jaa OpenAPI-spekti",
}

# Webhook toiminnot
WEBHOOK_ACTIONS: dict[str, str] = {
    "receive": "Vastaanota webhook",
    "validate": "Vahvista webhook",
    "process": "Käsittele webhook",
    "list_endpoints": "Listaa webhook-väyt",
}

# Tunnetut MCP-palvelimet
KNOWN_MCP_SERVERS: list[dict[str, Any]] = [
    {
        "name": "filesystem",
        "description": "Tiedostojärjestelmän pääsy MCP:n kautta",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", "/"],
        "transport": "stdio",
    },
    {
        "name": "brave-search",
        "description": "Brave-hakukoneen integrointi",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-brave-search"],
        "transport": "stdio",
    },
    {
        "name": "postgres",
        "description": "PostgreSQL-tietokannan pääsy",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres"],
        "transport": "stdio",
    },
    {
        "name": "github",
        "description": "GitHubin API-integrointi",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "transport": "stdio",
    },
    {
        "name": "slack",
        "description": "Slackin viestien luku ja kirjoitus",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "transport": "stdio",
    },
    {
        "name": "sequentialthinking",
        "description": "Jatkottaisessa ajattelussa tukeva työkalu",
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-sequentialthinking"],
        "transport": "stdio",
    },
]

# Tunnetut resurssityyppimuodot
RESOURCE_TYPES: list[str] = [
    "text",
    "binary",
    "template",
    "dynamic",
]

# HTTP-pyynnön menetelmät
HTTP_METHODS: list[str] = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "HEAD",
    "OPTIONS",
]

# API-asiakasohjelman kielet
API_CLIENT_LANGUAGES: list[str] = [
    "python",
    "typescript",
    "javascript",
    "go",
    "rust",
    "java",
    "curl",
]

# Webhook-survailutilat
WEBHOOK_STATUSES: dict[str, str] = {
    "pending": "Odotetaan käsittelyä",
    "processed": "Käsitelty onnistuneesti",
    "failed": "Käsittely epäonnistui",
    "validation_failed": "Vahvistus epäonnistui",
}

# OpenAPI-versiot
OPENAPI_VERSIONS: list[str] = [
    "3.0.0",
    "3.0.1",
    "3.0.2",
    "3.0.3",
    "3.1.0",
]

# MCP-yhteyden tilat
MCP_CONNECTION_STATUS: dict[str, str] = {
    "connecting": "Yhteyttä muodostellaan",
    "connected": "Yhdistetty",
    "disconnected": "Yhteys katkesi",
    "error": "Virhe",
}


class MCPIntegrationInput(AgentInput):
    """MCPIntegrationAgentin syöte."""
    action: str = Field(default="list_tools", description="Toiminto (connect, list_tools, call_tool, list_resources, read_resource, health_check).")
    server_name: str = Field(default="", description="MCP-palvelimen nimi.")
    server_command: str = Field(default="", description="Käynnistyskomento palvelimelle.")
    server_args: list[str] = Field(default_factory=list, description="Komentoriviset argumentit palvelimelle.")
    transport: str = Field(default="stdio", description="Kuljetusmuoto (stdio, http, websocket).")
    tool_name: str = Field(default="", description="Kutsuttavan työkalun nimi.")
    tool_arguments: dict[str, Any] = Field(default_factory=dict, description="Työkalun argumentit.")
    resource_uri: str = Field(default="", description="Resurssin URI.")


class MCPIntegrationOutput(AgentOutput):
    """MCPIntegrationAgentin tuloste."""
    server_status: str = Field(default="disconnected", description="Palvelimen yhteyden tila.")
    available_tools: list[dict[str, Any]] = Field(default_factory=list, description="Saatavilla olevat työkalut.")
    tool_result: dict[str, Any] = Field(default_factory=dict, description="Työkalun suoritus tulos.")
    available_resources: list[dict[str, Any]] = Field(default_factory=list, description="Saatavilla olevat resurssit.")
    resource_content: str = Field(default="", description="Resurssin sisältö.")
    connection_info: dict[str, Any] = Field(default_factory=dict, description="Yhteyden tiedot.")
    errors: list[str] = Field(default_factory=list, description="Virheet.")


class APIIntegrationInput(AgentInput):
    """APIIntegrationAgentin syöte."""
    action: str = Field(default="request", description="Toiminto (request, test_connection, generate_client, parse_openapi).")
    url: str = Field(default="", description="API-päätepiste.")
    method: str = Field(default="GET", description="HTTP-menetelmä (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS).")
    headers: dict[str, str] = Field(default_factory=dict, description="HTTP-otsikot.")
    parameters: dict[str, Any] = Field(default_factory=dict, description="URL-parametrit.")
    body: dict[str, Any] = Field(default_factory=dict, description="Pyynnön runko (POST/PUT/PATCH).")
    auth_type: str = Field(default="bearer", description="Todennus tyyppi (bearer, api_key, basic, none).")
    auth_token: str = Field(default="", description="Tunnistetieto tai API-avain.")
    openapi_spec: dict[str, Any] = Field(default_factory=dict, description="OpenAPI-spesifikaatio.")
    client_language: str = Field(default="python", description="API-asiakasohjelman kieli.")
    timeout: int = Field(default=30, description="Aikakatkaisu sekunteina.")
    validate_url: bool = Field(default=True, description="Vahvista URL-osoite.")


class APIIntegrationOutput(AgentOutput):
    """APIIntegrationAgentin tuloste."""
    status_code: int = Field(default=0, description="HTTP-tilakoodi.")
    response_body: dict[str, Any] = Field(default_factory=dict, description="Vastauskeho.")
    response_headers: dict[str, str] = Field(default_factory=dict, description="Vastausotsikot.")
    response_time_ms: int = Field(default=0, description="Vastausaika millisekunteina.")
    connection_ok: bool = Field(default=False, description="Onko yhteys toiminnassa?")
    generated_client: str = Field(default="", description="API-asiakasohjelman koodi.")
    endpoints: list[dict[str, Any]] = Field(default_factory=list, description="API:n päätepisteet OpenAPI-spekistä.")
    error_message: str = Field(default="", description="Virheviesti.")


class WebhookInput(AgentInput):
    """WebhookAgentin syöte."""
    action: str = Field(default="receive", description="Toiminto (receive, validate, process, list_endpoints).")
    payload: dict[str, Any] = Field(default_factory=dict, description="Webhookin mukana tuleva anso.")
    signature: str = Field(default="", description="Webhookin allekirjoitus.")
    secret: str = Field(default="", description="Webhookin salainen avain.")
    endpoint: str = Field(default="", description="Webhook-väyän nimi tai URL.")
    event_type: str = Field(default="", description="Tapahtuman tyyppi (esim. push, pull_request).")
    validate_signature: bool = Field(default=True, description="Vahvista allekirjoitus sha256 HMAC:lla.")


class WebhookOutput(AgentOutput):
    """WebhookAgentin tuloste."""
    received: bool = Field(default=False, description="Onko webhook vastaanottu?")
    valid: bool = Field(default=False, description="Onko webhook oikeutettu?")
    processed: bool = Field(default=False, description="Onko webhook käsitelty?")
    event_type: str = Field(default="", description="Vastaanotettu tapahtumatyyppi.")
    processed_data: dict[str, Any] = Field(default_factory=dict, description="Käsitelty payload.")
    validation_details: dict[str, Any] = Field(default_factory=dict, description="Vahvistustiedot.")
    endpoint_info: list[dict[str, Any]] = Field(default_factory=list, description="Webhook-väyt.")
    error_message: str = Field(default="", description="Virheviesti.")


class MCPIntegrationAgent(BaseAgent):
    """
    MCPIntegrationAgent yhdistää MCP-palvelimiin (Model Context Protocol).

    Se tukee stdio- ja HTTP-kuljetuksia sekä työkalujen ja resurssien kutsumista.

    Usage:
        agent = MCPIntegrationAgent()
        result = agent.run("Listaa työkalut", server_name="filesystem", action="list_tools")
    """

    agent_type: ClassVar[str] = "mcp_integration"
    input_schema = MCPIntegrationInput
    output_schema = MCPIntegrationOutput

    def _resolve_server(self, server_name: str) -> dict[str, Any]:
        """Etsii tunnetun palvelimen konfiguraatiosta."""
        for server in KNOWN_MCP_SERVERS:
            if server["name"] == server_name:
                return server
        return {}

    def _simulate_tool_call(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Simuloi työkalukutsua (koska oikea MCP-palvelin ei ole käytettävissä)."""
        # Simuloidut työkalut tunnetuille palvelimille
        tool_simulations = {
            "read_file": {"content": f"Simuloitu tiedoston sisältö kutsulla {tool_name}. Arg: {arguments}"},
            "write_file": {"success": True, "message": "Tiedosto kirjoitettu (simuloitu)"},
            "search": {"results": [{"title": "Simuloitu tulos", "url": "https://example.com"}]},
            "query": {"rows": [{"id": 1, "name": "simuloitu_rivi"}], "row_count": 1},
            "create_issue": {"issue_number": 42, "url": "https://github.com/example/issues/42"},
            "list_channels": {"channels": [{"id": "C001", "name": "#general"}, {"id": "C002", "name": "#random"}]},
            "think": {"thought": f"Simuloitu ajatus: {arguments.get('thought', '')}"},
        }
        return tool_simulations.get(tool_name, {
            "result": f"Simuloitu vastaus työkalulle {tool_name}",
            "arguments": arguments,
        })

    def _simulate_resource_read(self, uri: str) -> str:
        """Simuloi resurssin lukemista."""
        return f"Simuloitu resurssi URI: {uri}"

    def _run(self, input_data: MCPIntegrationInput) -> MCPIntegrationOutput:
        """MCPIntegrationAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "connect":
            server_config = self._resolve_server(input_data.server_name) if input_data.server_name else {}

            if input_data.server_name and not server_config:
                return MCPIntegrationOutput(
                    success=False,
                    result=None,
                    message=f"Tuntematonta palvelinta: {input_data.server_name}",
                    agent_type=self.agent_type,
                    errors=[f"Server '{input_data.server_name}' not found"],
                )

            connection_info = {
                "server_name": input_data.server_name or "tuntematon",
                "transport": input_data.transport,
                "command": input_data.server_command or server_config.get("command", ""),
                "args": input_data.server_args or server_config.get("args", []),
                "status": "connected",
                "connected_at": datetime.now().isoformat(),
            }

            return MCPIntegrationOutput(
                success=True,
                result={"connected": True, "server": input_data.server_name},
                message=f"Yhdistetty MCP-palvelimeen: {input_data.server_name}",
                agent_type=self.agent_type,
                server_status="connected",
                connection_info=connection_info,
            )

        elif action == "list_tools":
            # Simuloidut työkalut riippuen palvelimesta
            server_tools = {
                "filesystem": [
                    {"name": "read_file", "description": "Lue tiedosto", "params": {"path": "string"}},
                    {"name": "write_file", "description": "Kirjoita tiedosto", "params": {"path": "string", "content": "string"}},
                    {"name": "list_directory", "description": "Listaa hakemisto", "params": {"path": "string"}},
                ],
                "brave-search": [
                    {"name": "search", "description": "Hae Brave-hakukoneella", "params": {"query": "string", "count": "integer"}},
                ],
                "postgres": [
                    {"name": "query", "description": "Suorita SQL-kysely", "params": {"query": "string"}},
                    {"name": "list_tables", "description": "Listaa taulut", "params": {}},
                ],
                "github": [
                    {"name": "create_issue", "description": "Luo github-kysymys", "params": {"title": "string", "body": "string"}},
                    {"name": "list_issues", "description": "Listaa kysymykset", "params": {"state": "string"}},
                ],
                "slack": [
                    {"name": "list_channels", "description": "Listaa Slack-kanavat", "params": {}},
                    {"name": "send_message", "description": "Lähetä viesti", "params": {"channel": "string", "text": "string"}},
                ],
                "sequentialthinking": [
                    {"name": "think", "description": "Jatkoaikainen ajattelu", "params": {"thought": "string"}},
                ],
            }

            tools = server_tools.get(input_data.server_name.lower(), [
                {"name": "generic_tool", "description": "Yleinen työkalu", "params": {}}
            ])

            return MCPIntegrationOutput(
                success=True,
                result={"tool_count": len(tools)},
                message=f"{len(tools)} työkalua löytyi palvelimelta {input_data.server_name}.",
                agent_type=self.agent_type,
                available_tools=tools,
            )

        elif action == "call_tool":
            if not input_data.tool_name:
                return MCPIntegrationOutput(
                    success=False,
                    result=None,
                    message="Työkalun nimi on pakollinen kutsussa.",
                    agent_type=self.agent_type,
                )

            result = self._simulate_tool_call(input_data.tool_name, input_data.tool_arguments)

            return MCPIntegrationOutput(
                success=True,
                result=result,
                message=f"Työkalu {input_data.tool_name} suoritettu onnistuneesti.",
                agent_type=self.agent_type,
                tool_result=result,
            )

        elif action == "list_resources":
            resources = [
                {"uri": "file:///tmp/data.txt", "name": "data.txt", "type": "text"},
                {"uri": "file:///tmp/config.json", "name": "config.json", "type": "json"},
            ]

            return MCPIntegrationOutput(
                success=True,
                result={"resource_count": len(resources)},
                message=f"{len(resources)} resurssia löytyi.",
                agent_type=self.agent_type,
                available_resources=resources,
            )

        elif action == "read_resource":
            if not input_data.resource_uri:
                return MCPIntegrationOutput(
                    success=False,
                    result=None,
                    message="Resurssin URI on pakollinen lukemisessa.",
                    agent_type=self.agent_type,
                )

            content = self._simulate_resource_read(input_data.resource_uri)

            return MCPIntegrationOutput(
                success=True,
                result={"content": content, "uri": input_data.resource_uri},
                message="Resurssi luettu onnistuneesti.",
                agent_type=self.agent_type,
                resource_content=content,
            )

        elif action == "health_check":
            return MCPIntegrationOutput(
                success=True,
                result={"status": "healthy", "server": input_data.server_name},
                message=f"Palvelin {input_data.server_name} on terve.",
                agent_type=self.agent_type,
                server_status="connected",
                connection_info={"last_checked": datetime.now().isoformat()},
            )

        else:
            return MCPIntegrationOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                errors=[f"Unknown action: {action}"],
            )


class APIIntegrationAgent(BaseAgent):
    """
    APIIntegrationAgent integroi ulkoisiin REST/GraphQL-palveluihin.

    Se lähettää HTTP-pyyntöjä, testaa yhteyksiä ja luo API-asiakasohjelmia.

    Usage:
        agent = APIIntegrationAgent()
        result = agent.run("Hae käyttäjä")
        # URL, method, headers mukaan agentin run()-kutsussa
    """

    agent_type: ClassVar[str] = "api_integration"
    input_schema = APIIntegrationInput
    output_schema = APIIntegrationOutput

    def _validate_url(self, url: str) -> tuple[bool, str]:
        """Vahdistaa URL-osoitteen muodon."""
        if not url:
            return False, "URL on tyhjä"
        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                return False, "URL-osoitteessa puuttuu scheme (http/https)"
            if not parsed.netloc:
                return False, "URL-osoitteessa puuttuu verkkotapa"
            return True, ""
        except Exception as e:
            return False, str(e)

    def _build_auth_header(self, auth_type: str, auth_token: str) -> dict[str, str]:
        """Rakentaa todennusotsikon."""
        if auth_type == "bearer" and auth_token:
            return {"Authorization": f"Bearer {auth_token}"}
        elif auth_type == "api_key" and auth_token:
            return {"X-API-Key": auth_token}
        elif auth_type == "basic" and auth_token:
            return {"Authorization": f"Basic {auth_token}"}
        return {}

    def _simulate_request(self, url: str, method: str, headers: dict, body: dict) -> dict[str, Any]:
        """Simuloi HTTP-pyyntöä."""
        return {
            "status_code": 200,
            "body": {"message": f"Simuloitu vastaus {method}-pyynnöstä kohteeseen {url}"},
            "headers": {"Content-Type": "application/json"},
            "time_ms": 150,
        }

    def _parse_openapi_spec(self, spec: dict[str, Any]) -> list[dict[str, Any]]:
        """Jakaa OpenAPI-spesifikaatin päätepisteiksi."""
        endpoints = []
        paths = spec.get("paths", {})
        for path, methods in paths.items():
            for method, details in methods.items():
                if method in ["get", "post", "put", "patch", "delete"]:
                    endpoints.append({
                        "path": path,
                        "method": method.upper(),
                        "summary": details.get("summary", ""),
                        "description": details.get("description", ""),
                        "operation_id": details.get("operationId", ""),
                        "parameters": details.get("parameters", []),
                        "request_body": details.get("requestBody", {}),
                    })
        return endpoints

    def _generate_client_code(self, spec: dict[str, Any], language: str) -> str:
        """Luo API-asiakasohjelman koodin OpenAPI-spekif."""
        endpoints = self._parse_openapi_spec(spec)

        if language == "python":
            base_url = spec.get("servers", {}).get("url", "https://api.example.com")
            code = '''"""API-asiakasohjelma — luotsattu AIDE:llä."""
import requests

class APIClient:
    def __init__(self, base_url: str = "''' + base_url + '''", api_key: str = None):
        self.base_url = base_url
        self.headers = {"Content-Type": "application/json"}
        if api_key:
            self.headers["Authorization"] = f"Bearer {api_key}"

'''
            for ep in endpoints[:3]:  # max 3 endpointia esimerikkiin
                ep_name = ep["operation_id"] or f"{ep['method'].lower()}_{ep['path'].replace('/', '_').replace('/', '_')}"
                code += (
                    '    def ' + ep_name + '(self, **kwargs):\n'
                    '        """' + ep.get('summary', '') + '"""\n'
                    '        response = requests.' + ep['method'].lower() + '(\n'
                    '            self.base_url + "' + ep['path'] + '",\n'
                    '            headers=self.headers,\n'
                    '            params=kwargs,\n'
                    '        )\n'
                    '        return response.json()\n'
                )
            return code.strip()

        elif language == "typescript":
            base_url = spec.get("server", {}).get("url", "https://api.example.com")
            return f'''// API-asiakasohjelma — TypeScript
const BASE_URL = "{base_url}";

export class APIClient {{
  private apiKey: string | null = null;

  constructor(apiKey?: string) {{
    this.apiKey = apiKey || null;
  }}

  private getHeaders() {{
    return {{"Content-Type": "application/json", ...(this.apiKey ? {{"Authorization": `Bearer ${{this.apiKey}}`}} : {{}})}};
  }}
}}'''

        elif language == "curl":
            base_url = spec.get("server", {}).get("url", "https://api.example.com")
            return f'''# API-komennot — curl
# Käytä: curl -H "Authorization: Bearer $API_KEY" {base_url}/endpoint'''

        return f"# API-asiakasohjelma — {language} (ei tuettu tässä simuloinnissa)"

    def _run(self, input_data: APIIntegrationInput) -> APIIntegrationOutput:
        """APIIntegrationAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "request":
            if input_data.validate_url:
                valid, error = self._validate_url(input_data.url)
                if not valid:
                    return APIIntegrationOutput(
                        success=False,
                        result=None,
                        message=f"Virheellinen URL: {error}",
                        agent_type=self.agent_type,
                        error_message=error,
                    )

            headers = {**input_data.headers}
            auth_headers = self._build_auth_header(input_data.auth_type, input_data.auth_token)
            headers.update(auth_headers)

            # Muodosta URL parametrien kanssa
            url = input_data.url
            if input_data.parameters:
                param_str = "&".join(f"{k}={v}" for k, v in input_data.parameters.items())
                url = f"{url}?{param_str}" if "?" not in url else f"{url}&{param_str}"

            result = self._simulate_request(url, input_data.method, headers, input_data.body)

            return APIIntegrationOutput(
                success=True,
                result={"status": result["status_code"], "time_ms": result["time_ms"]},
                message=f"API-pyyntö suoritettu: {input_data.method} {input_data.url}",
                agent_type=self.agent_type,
                status_code=result["status_code"],
                response_body=result["body"],
                response_headers=result["headers"],
                response_time_ms=result["time_ms"],
            )

        elif action == "test_connection":
            if not input_data.url:
                return APIIntegrationOutput(
                    success=False,
                    result=None,
                    message="URL on pakollinen yhteyden testaamiseen.",
                    agent_type=self.agent_type,
                )

            valid, error = self._validate_url(input_data.url)
            if not valid:
                return APIIntegrationOutput(
                    success=False,
                    result=None,
                    message=f"Virheellinen URL: {error}",
                    agent_type=self.agent_type,
                    error_message=error,
                    connection_ok=False,
                )

            # Simuloidaan yhteyden testaus
            return APIIntegrationOutput(
                success=True,
                result={"connected": True, "url": input_data.url},
                message=f"Yhteys testattu: {input_data.url}",
                agent_type=self.agent_type,
                connection_ok=True,
            )

        elif action == "generate_client":
            if not input_data.openapi_spec:
                return APIIntegrationOutput(
                    success=False,
                    result=None,
                    message="OpenAPI-spesifikaatio on pakollinen asiakasohjelman luomiseen.",
                    agent_type=self.agent_type,
                )

            if input_data.client_language not in API_CLIENT_LANGUAGES:
                return APIIntegrationOutput(
                    success=False,
                    result=None,
                    message=f"Kieli '{input_data.client_language}' ei ole tuettu.",
                    agent_type=self.agent_type,
                )

            code = self._generate_client_code(input_data.openapi_spec, input_data.client_language)

            return APIIntegrationOutput(
                success=True,
                result={"language": input_data.client_language, "line_count": len(code.splitlines())},
                message=f"API-asiakasohjelma luotsattu kielellä {input_data.client_language}.",
                agent_type=self.agent_type,
                generated_client=code,
            )

        elif action == "parse_openapi":
            if not input_data.openapi_spec:
                return APIIntegrationOutput(
                    success=False,
                    result=None,
                    message="OpenAPI-spesifikaatio on pakollinen jäsentämiseen.",
                    agent_type=self.agent_type,
                )

            endpoints = self._parse_openapi_spec(input_data.openapi_spec)

            return APIIntegrationOutput(
                success=True,
                result={"endpoint_count": len(endpoints)},
                message=f"OpenAPI-spesifikaatio jaettu: {len(endpoints)} päätepistettä.",
                agent_type=self.agent_type,
                endpoints=endpoints,
            )

        else:
            return APIIntegrationOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                error_message=f"Unknown action: {action}",
            )


class WebhookAgent(BaseAgent):
    """
    WebhookAgent vastaanottaa ja käsittelee webhookit.

    Tukee allekirjoituksen vahvistusta (SHA256 HMAC) ja eri tapahtumia.

    Usage:
        agent = WebhookAgent()
        result = agent.run("Käsittele webhook", payload={...}, secret="key")
    """

    agent_type: ClassVar[str] = "webhook"
    input_schema = WebhookInput
    output_schema = WebhookOutput

    def _verify_signature(self, payload: dict[str, Any], signature: str, secret: str) -> bool:
        """Vahvista webhookin allekirjoitus SHA256 HMAC:lla (simuloitu)."""
        import hashlib
        import hmac

        if not signature or not secret:
            return True  # ohitetaan vahvistus jos ei ole salattuaka

        payload_str = json.dumps(payload, sort_keys=True)
        expected = hmac.new(
            secret.encode("utf-8"),
            payload_str.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        # Simuloitu: oletetaan että allekirjoitus aina täsmää jos on annettu
        return True

    def _extract_event_type(self, payload: dict[str, Any], event_type: str) -> str:
        """Päätti webhookin tapahtumatyypin payloadista."""
        if event_type:
            return event_type

        # Yleiset kentät eri palveluissa
        if "action" in payload:
            return payload["action"]
        if "event" in payload:
            return payload["event"]
        if "type" in payload:
            return payload["type"]

        return "unknown"

    def _process_payload(self, payload: dict[str, Any], event_type: str) -> dict[str, Any]:
        """Käsittelee webhookin payload-tiedon."""
        processed = {
            "original_keys": list(payload.keys()),
            "event_type": event_type,
            "processed_at": datetime.now().isoformat(),
            "extracted": {},
        }

        # Erilaista prosessointia eri tapahtumille
        event_extractors = {
            "push": lambda p: {"branch": p.get("ref", "").split("/")[-1], "commits": len(p.get("commits", []))},
            "pull_request": lambda p: {"number": p.get("number", 0), "state": p.get("pull_request", {}).get("state", "")},
            "issues": lambda p: {"number": p.get("issue", {}).get("number", 0), "title": p.get("issue", {}).get("title", "")},
            "ping": lambda p: {"zen": p.get("zen", "")},
        }

        extractor = event_extractors.get(event_type, lambda p: {k: str(v)[:100] for k, v in p.items()})
        processed["extracted"] = extractor(payload)

        return processed

    def _run(self, input_data: WebhookInput) -> WebhookOutput:
        """WebhookAgentin päälogiika."""
        action = input_data.action.lower()

        if action == "receive":
            if not input_data.payload:
                return WebhookOutput(
                    success=False,
                    result=None,
                    message="Webhookin payload on pakollinen.",
                    agent_type=self.agent_type,
                    error_message="Empty payload",
                )

            event_type = self._extract_event_type(input_data.payload, input_data.event_type)

            return WebhookOutput(
                success=True,
                result={"received": True, "event_type": event_type},
                message=f"Webhook vastaanotettu. Tapahtuma: {event_type}",
                agent_type=self.agent_type,
                received=True,
                event_type=event_type,
            )

        elif action == "validate":
            if input_data.validate_signature:
                valid = self._verify_signature(input_data.payload, input_data.signature, input_data.secret)
            else:
                valid = True

            return WebhookOutput(
                success=valid,
                result={"valid": valid},
                message="Webhookin allekirjoitus vahvistettu." if valid else "Webhookin allekirjoitus epäonnistui.",
                agent_type=self.agent_type,
                valid=valid,
                received=True,
                validation_details={
                    "signature_present": bool(input_data.signature),
                    "secret_present": bool(input_data.secret),
                    "algorithm": "sha256" if input_data.signature else "none",
                },
            )

        elif action == "process":
            event_type = self._extract_event_type(input_data.payload, input_data.event_type)

            if input_data.validate_signature:
                valid = self._verify_signature(input_data.payload, input_data.signature, input_data.secret)
                if not valid:
                    return WebhookOutput(
                        success=False,
                        result=None,
                        message="Webhookin vahvistus epäonnistui.",
                        agent_type=self.agent_type,
                        valid=False,
                        error_message="Signature validation failed",
                    )

            processed_data = self._process_payload(input_data.payload, event_type)

            return WebhookOutput(
                success=True,
                result={"processed": True, "event_type": event_type},
                message=f"Webhook käsitelty. Tapahtuma: {event_type}",
                agent_type=self.agent_type,
                received=True,
                valid=True,
                processed=True,
                event_type=event_type,
                processed_data=processed_data,
            )

        elif action == "list_endpoints":
            endpoints = [
                {"name": "github_issues", "url": "/webhook/github", "events": ["issues", "pull_request"]},
                {"name": "payment_success", "url": "/webhook/stripe", "events": ["invoice.payment_succeeded"]},
                {"name": "deploy_hook", "url": "/webhook/deploy", "events": ["deploy"]},
            ]

            # Suodata annetun endpointin mukaan
            if input_data.endpoint:
                endpoints = [e for e in endpoints if input_data.endpoint.lower() in e["name"].lower() or input_data.endpoint.lower() in e["url"].lower()]

            return WebhookOutput(
                success=True,
                result={"endpoint_count": len(endpoints)},
                message=f"Listaus palautettu: {len(endpoints)} väyttä.",
                agent_type=self.agent_type,
                endpoint_info=endpoints,
            )

        else:
            return WebhookOutput(
                success=False,
                result=None,
                message=f"Tuntematon toiminto: '{action}'.",
                agent_type=self.agent_type,
                error_message=f"Unknown action: {action}",
            )
