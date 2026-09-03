"""
Testit Workflow Engine -moduulille (workflows/engine.py).
"""

import pytest

from workflows.engine import (
    WorkflowEngine,
    WorkflowState,
    WorkflowExecution,
    PhaseResult,
    WorkflowError,
    STATE_TRANSITIONS,
)


@pytest.fixture
def workflow_dir(tmp_path):
    """Luo testi-workflow-kansion."""
    wf = tmp_path / "workflows"
    wf.mkdir()

    (wf / "base.yaml").write_text(
        "name: base\n"
        "description: Test workflow\n"
        "phases:\n"
        "  - name: analyze\n"
        "    agent: researcher\n"
        "  - name: plan\n"
        "    agent: planner\n"
        "  - name: implement\n"
        "    agent: developer\n"
        "  - name: test\n"
        "    agent: tester\n"
        "  - name: review\n"
        "    agent: reviewer\n"
        "  - name: document\n"
        "    agent: writer\n",
        encoding="utf-8",
    )

    (wf / "bugfix.yaml").write_text(
        "name: bugfix\n"
        "phases:\n"
        "  - name: analyze\n"
        "    agent: researcher\n"
        "  - name: implement\n"
        "    agent: developer\n"
        "  - name: test\n"
        "    agent: tester\n",
        encoding="utf-8",
    )

    return str(wf)


@pytest.fixture
def engine(workflow_dir):
    """Luo WorkflowEnginein testi-kansiosta."""
    return WorkflowEngine(workflow_dir=workflow_dir)


class TestWorkflowState:
    """Testit WorkflowState-enumille."""

    def test_states_are_strings(self):
        """Kaikki tilat ovat merkkijonoja (str, Enum)."""
        assert WorkflowState.INIT.value == "init"
        assert WorkflowState.ANALYZE.value == "analyze"
        assert WorkflowState.PLAN.value == "plan"
        assert WorkflowState.IMPLEMENT.value == "implement"
        assert WorkflowState.TEST.value == "test"
        assert WorkflowState.REVIEW.value == "review"
        assert WorkflowState.DOCUMENT.value == "document"
        assert WorkflowState.COMPLETE.value == "complete"
        assert WorkflowState.ERROR.value == "error"


class TestStateTransitions:
    """Testit tilan siirtymisille."""

    def test_init_to_analyze(self):
        """INIT → ANALYZE on sallittua."""
        assert WorkflowState.ANALYZE in STATE_TRANSITIONS[WorkflowState.INIT]

    def test_analyze_to_plan(self):
        """ANALYZE → PLAN on sallittua."""
        assert WorkflowState.PLAN in STATE_TRANSITIONS[WorkflowState.ANALYZE]

    def test_plan_to_implement(self):
        """PLAN → IMPLEMENT on sallittua."""
        assert WorkflowState.IMPLEMENT in STATE_TRANSITIONS[WorkflowState.PLAN]

    def test_implement_to_test(self):
        """IMPLEMENT → TEST on sallittua."""
        assert WorkflowState.TEST in STATE_TRANSITIONS[WorkflowState.IMPLEMENT]

    def test_test_to_review(self):
        """TEST → REVIEW on sallittua."""
        assert WorkflowState.REVIEW in STATE_TRANSITIONS[WorkflowState.TEST]

    def test_review_to_document(self):
        """REVIEW → DOCUMENT on sallittua."""
        assert WorkflowState.DOCUMENT in STATE_TRANSITIONS[WorkflowState.REVIEW]

    def test_document_to_complete(self):
        """DOCUMENT → COMPLETE on sallittua."""
        assert WorkflowState.COMPLETE in STATE_TRANSITIONS[WorkflowState.DOCUMENT]

    def test_complete_has_no_transitions(self):
        """COMPLETE-tilasta ei voi siirtyä eteenpäin."""
        assert STATE_TRANSITIONS[WorkflowState.COMPLETE] == []

    def test_error_to_analyze(self):
        """ERROR → ANALYZE on sallittua (uudelleenyrittäminen)."""
        assert WorkflowState.ANALYZE in STATE_TRANSITIONS[WorkflowState.ERROR]

    def test_validate_transition_valid(self):
        """validate_transition palauttaa True kelvolle siirtymiselle."""
        assert WorkflowEngine.validate_transition(WorkflowState.INIT, WorkflowState.ANALYZE) is True
        assert WorkflowEngine.validate_transition(WorkflowState.ANALYZE, WorkflowState.PLAN) is True

    def test_validate_transition_invalid(self):
        """validate_transition palauttaa False kelvottomille siirtymisille."""
        assert WorkflowEngine.validate_transition(WorkflowState.INIT, WorkflowState.COMPLETE) is False
        assert WorkflowEngine.validate_transition(WorkflowState.COMPLETE, WorkflowState.INIT) is False


class TestWorkflowEngine:
    """Testit WorkflowEngine-luokalle."""

    def test_list_workflows(self, engine):
        """Listaa saatavilla olevat workflowt."""
        workflows = engine.list_workflows()
        assert "base" in workflows
        assert "bugfix" in workflows

    def test_load_workflow_base(self, engine):
        """Lataa base-workflowin."""
        config = engine.load_workflow("base")
        assert config["name"] == "base"
        assert len(config["phases"]) == 6

    def test_load_workflow_with_extension(self, engine):
        """Lataa workflow myös .yml-päätteellä."""
        # Luo .yml-extensiivinen workflow
        import os
        path = os.path.join(engine.workflow_dir, "test.yml")
        with open(path, "w") as f:
            f.write("name: test\ntasks: []\n")
        config = engine.load_workflow("test")
        assert config["name"] == "test"

    def test_load_workflow_not_found(self, engine):
        """Puuttunutta workflow-tä ei löydy — WorkflowError."""
        with pytest.raises(WorkflowError, match="ei löydy"):
            engine.load_workflow("nonexistent")

    def test_list_workflows_empty_dir(self, tmp_path):
        """Tyhjässä kansiossa ei ole workflowja."""
        engine = WorkflowEngine(workflow_dir=str(tmp_path))
        assert engine.list_workflows() == []

    def test_list_workflows_nonexistent_dir(self, tmp_path):
        """Ei olemassa olevassakaankaistiin ei ole workflowja."""
        engine = WorkflowEngine(workflow_dir=str(tmp_path / "missing"))
        assert engine.list_workflows() == []


class TestWorkflowExecution:
    """Testit WorkflowExecution:lle."""

    def test_create_execution(self, engine):
        """Luodaan suoritus base-workflowille."""
        exec_obj = engine.create_execution("base")
        assert exec_obj.workflow_name == "base"
        assert exec_obj.state == WorkflowState.INIT
        assert "analyze" in exec_obj.phases
        assert "document" in exec_obj.phases
        assert exec_obj.phase_results == []
        assert len(exec_obj.events) > 0

    def test_create_execution_bugfix(self, engine):
        """Luodaan bugfix-workflowin suoritus."""
        exec_obj = engine.create_execution("bugfix")
        assert exec_obj.workflow_name == "bugfix"
        assert len(exec_obj.phases) == 3  # analyze, implement, test

    def test_can_transition_to_analyze_from_init(self, engine):
        """INIT-tilasta voi siirtyä ANALYZE-tilaan."""
        exec_obj = engine.create_execution("base")
        assert exec_obj.can_transition_to(WorkflowState.ANALYZE) is True

    def test_cannot_transition_to_complete_from_init(self, engine):
        """INIT-tilasta EI voi suoraan COMPLETE-tilaan."""
        exec_obj = engine.create_execution("base")
        assert exec_obj.can_transition_to(WorkflowState.COMPLETE) is False

    def test_transition_to(self, engine):
        """transition_to() muuttaa tilaa."""
        exec_obj = engine.create_execution("base")
        exec_obj.transition_to(WorkflowState.ANALYZE)
        assert exec_obj.state == WorkflowState.ANALYZE

    def test_invalid_transition_raises(self, engine):
        """Virheellinen siirtyminen raiseaa WorkflowErrorin."""
        exec_obj = engine.create_execution("base")
        with pytest.raises(WorkflowError, match="ei ole sallittu"):
            exec_obj.transition_to(WorkflowState.COMPLETE)


class TestPhaseExecution:
    """Testit phasejen suorittamiselle."""

    def test_execute_phase_success(self, engine):
        """Onnistunut vaihe tuottaa PhaseResultin."""
        exec_obj = engine.create_execution("base")

        def handler(ctx):
            return "Analyysi valmis"

        result = engine.execute_phase(exec_obj, "analyze", handler)
        assert result.success is True
        assert result.output == "Analyysi valmis"
        assert result.phase_name == "analyze"
        assert "suoritettu" in result.message

    def test_execute_phase_error(self, engine):
        """Virheellinen vaihe asettaa tilan ERRORiksi."""
        exec_obj = engine.create_execution("base")

        def handler(ctx):
            raise ValueError("Koodivirhe!")

        result = engine.execute_phase(exec_obj, "analyze", handler)
        assert result.success is False
        assert "Koodivirhe" in result.error
        assert exec_obj.state == WorkflowState.ERROR

    def test_execute_phase_transition_to_error(self, engine):
        """Vaiheen virhe siirtyy ERROR-tilaan."""
        exec_obj = engine.create_execution("base")

        def handler(ctx):
            raise RuntimeError("Testi-virhe")

        engine.execute_phase(exec_obj, "analyze", handler)
        assert exec_obj.state == WorkflowState.ERROR

    def test_execute_phase_context_passed(self, engine):
        """Handlerille välitetään konteksti."""
        exec_obj = engine.create_execution("base")
        captured_ctx = {}

        def handler(ctx):
            captured_ctx.update(ctx)
            return "OK"

        engine.execute_phase(exec_obj, "analyze", handler, context={"data": "value"})
        assert captured_ctx["phase"] == "analyze"
        assert captured_ctx["agent"] == "researcher"
        assert captured_ctx["data"] == "value"


class TestExecuteAll:
    """Testit täydille workflow-executionille."""

    def test_execute_all_success(self, engine):
        """Kaikki vaiheet suoritetaan onnistuneesti."""
        exec_obj = engine.create_execution("base")

        handlers = {
            "analyze": lambda ctx: "A1",
            "plan": lambda ctx: "P1",
            "implement": lambda ctx: "I1",
            "test": lambda ctx: "T1",
            "review": lambda ctx: "R1",
            "document": lambda ctx: "D1",
        }

        result = engine.execute_all(exec_obj, handlers=handlers)
        assert result.state == WorkflowState.COMPLETE
        assert len(result.phase_results) == 6
        assert all(r.success for r in result.phase_results)
        assert "🎉" in result.events[-1]

    def test_execute_all_with_dummy_handlers(self, engine):
        """Dummy-handlerit toimivat jos mitään anntaa."""
        exec_obj = engine.create_execution("base")
        result = engine.execute_all(exec_obj)
        assert result.state == WorkflowState.COMPLETE
        assert all(r.success for r in result.phase_results)

    def test_execute_all_partial_failure(self, engine):
        """Yksi epäonnistunut vaihe asettaa tilan ERRORiksi."""
        exec_obj = engine.create_execution("base")

        handlers = {
            "analyze": lambda ctx: "OK",
            "plan": lambda ctx: "OK",
            "implement": lambda ctx: 1 / 0,  # Virhe
            "test": lambda ctx: "OK",
            "review": lambda ctx: "OK",
            "document": lambda ctx: "OK",
        }

        result = engine.execute_all(exec_obj, handlers=handlers)
        assert result.state == WorkflowState.ERROR
        assert any(not r.success for r in result.phase_results)
        assert "virhe" in result.events[-1].lower() or "⚠️" in result.events[-1]

    def test_execute_all_short_workflow(self, engine):
        """Lyhyt workflow (bugfix) suoritetaan oikein."""
        exec_obj = engine.create_execution("bugfix")
        result = engine.execute_all(exec_obj)
        assert result.state == WorkflowState.COMPLETE
        assert len(result.phase_results) == 3

    def test_execute_all_collects_phase_results(self, engine):
        """Kaikki vaiheiden tulokset kerättyinä."""
        exec_obj = engine.create_execution("base")

        handlers = {
            "analyze": lambda ctx: f"Result-{ctx['phase']}",
            "plan": lambda ctx: f"Result-{ctx['phase']}",
            "implement": lambda ctx: f"Result-{ctx['phase']}",
            "test": lambda ctx: f"Result-{ctx['phase']}",
            "review": lambda ctx: f"Result-{ctx['phase']}",
            "document": lambda ctx: f"Result-{ctx['phase']}",
        }

        result = engine.execute_all(exec_obj, handlers=handlers)
        assert result.phase_results[0].output == "Result-analyze"
        assert result.phase_results[5].output == "Result-document"
