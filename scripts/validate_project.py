from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open(encoding="utf-8") as file:
        return json.load(file)


def validate_pilot(pilot: dict) -> list[str]:
    errors: list[str] = []
    canvas = pilot.get("canvas", {})
    width, height = canvas.get("width"), canvas.get("height")
    if not all(isinstance(value, int) and value > 0 for value in (width, height)) or width >= height:
        errors.append("O canvas deve ser vertical e ter dimensoes positivas.")
    duration = pilot.get("duration_seconds")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool) or duration <= 0:
        errors.append("A duracao deve ser positiva.")
    if pilot.get("publication_enabled") is not False:
        errors.append("A publicacao deve permanecer desativada no MVP.")
    if pilot.get("external_generation_enabled") is not False:
        errors.append("Geracao externa deve permanecer desativada no MVP.")
    if pilot.get("acceptance", {}).get("publish") is not False:
        errors.append("O aceite do MVP nao pode incluir publicacao.")
    acceptance = pilot.get("acceptance", {})
    if (acceptance.get("width"), acceptance.get("height"), acceptance.get("duration_seconds")) != (width, height, duration):
        errors.append("O aceite deve repetir canvas e duracao declarados.")

    timeline = pilot.get("timeline", [])
    cursor = 0
    for index, scene in enumerate(timeline, start=1):
        if scene.get("scene") != index:
            errors.append(f"Cena {index}: identificador fora de ordem.")
        if scene.get("start") != cursor:
            errors.append(f"Cena {index}: lacuna ou sobreposicao antes de {scene.get('start')} s.")
        start, end = scene.get("start"), scene.get("end")
        if (not isinstance(start, (int, float)) or isinstance(start, bool)
                or not isinstance(end, (int, float)) or isinstance(end, bool)
                or (isinstance(start, (int, float)) and end <= start)):
            errors.append(f"Cena {index}: intervalo invalido.")
            continue
        cursor = scene["end"]

    if cursor != duration:
        errors.append("A linha do tempo nao termina na duracao declarada.")
    return errors


def validate_pipeline(pipeline: dict, pilot: dict, agent_ids: list[int]) -> list[str]:
    errors: list[str] = []
    states = pipeline.get("states", [])
    state_ids = [state.get("id") for state in states]
    state_by_id = {state.get("id"): state for state in states}
    if len(state_ids) != len(set(state_ids)) or not state_ids:
        errors.append("Os estados do pipeline devem existir e ter IDs unicos.")
    if pipeline.get("pipeline_id") != pilot.get("pipeline_id"):
        errors.append("O piloto e o pipeline devem ter o mesmo identificador.")
    if pilot.get("pipeline_state") not in state_by_id:
        errors.append("O estado atual do piloto nao existe no pipeline.")
    if not pipeline.get("state_semantics"):
        errors.append("A semantica dos estados precisa estar documentada.")
    if pipeline.get("mvp_terminal_state") != "qa_passed":
        errors.append("O MVP deve terminar no gate de qualidade.")
    if pipeline.get("publication_requires_explicit_authorization") is not True:
        errors.append("O pipeline deve exigir autorizacao explicita para publicacao.")
    execution = pipeline.get("execution_policy", {})
    if execution.get("mode") != "single_pass" or execution.get("generic_self_review_reports") is not False:
        errors.append("O pipeline deve usar passagem direta sem relatorios genericos de auto-revisao.")
    if execution.get("single_visual_system_per_video") is not True:
        errors.append("O pipeline deve exigir um unico sistema visual por video.")
    for state in states:
        next_state = state.get("next")
        if next_state is not None and next_state not in state_by_id:
            errors.append(f"Estado {state.get('id')}: proxima transicao inexistente.")
        if state.get("owner_role") not in agent_ids:
            errors.append(f"Estado {state.get('id')}: papel responsavel invalido.")
        if state.get("consult_role") is not None and state["consult_role"] not in agent_ids:
            errors.append(f"Estado {state.get('id')}: papel consultor invalido.")
        if not state.get("output"):
            errors.append(f"Estado {state.get('id')}: artefato de saida ausente.")

    # A ordem fixa protege o gate de qualidade e a autorizacao humana.
    required_order = ["draft", "brief_approved", "research_approved", "script_approved",
                      "visual_approved", "media_ready", "audio_ready", "edit_ready",
                      "qa_passed", "packaging_ready", "metadata_ready",
                      "publish_authorized", "published", "metrics_reviewed"]
    if state_ids != required_order or any(
        state_by_id.get(current, {}).get("next") != following
        for current, following in zip(required_order, required_order[1:] + [None])
    ):
        errors.append("A sequencia de gates foi alterada ou permite pular autorizacao.")
    return errors


def main() -> int:
    context = load_json("docs/contexto_projeto.json")
    pipeline = load_json("config/pipeline_fatonauta.json")
    pilot = load_json(pipeline["default_manifest"])
    errors = validate_pilot(pilot)

    agent_ids = [agent.get("id") for agent in context.get("agents", [])]
    if agent_ids != list(range(1, 16)):
        errors.append("O contexto deve manter quinze papeis com IDs de 1 a 15.")
    if not context.get("security_and_licenses"):
        errors.append("Regras de seguranca e licencas estao ausentes.")
    for agent_id in range(1, 16):
        contracts = list((ROOT / ".agents" / "roles").glob(f"{agent_id:02d}-*.md"))
        if len(contracts) != 1:
            errors.append(f"Papel {agent_id}: contrato Markdown ausente ou duplicado.")

    styles = load_json("config/visual_styles.json")
    style_ids = [style.get("id") for style in styles.get("styles", [])]
    if len(style_ids) != len(set(style_ids)) or len(style_ids) < 9:
        errors.append("O catalogo visual requer ao menos nove estilos com IDs unicos.")
    visual = pilot.get("visual_style_selection", {})
    if visual.get("visual_system_id") not in style_ids:
        errors.append("O piloto referencia sistema visual desconhecido.")
    engines = load_json("config/render_engines.json")
    engine_ids = [engine.get("id") for engine in engines.get("engines", [])]
    if len(engine_ids) != len(set(engine_ids)) or not engine_ids:
        errors.append("O catalogo de motores precisa de IDs unicos.")
    if any(engine not in engine_ids for engine in visual.get("engine_candidates", [])):
        errors.append("O piloto referencia motor de render desconhecido.")

    errors.extend(validate_pipeline(pipeline, pilot, agent_ids))

    if errors:
        print("VALIDACAO: FALHOU")
        for error in errors:
            print(f"- {error}")
        return 1

    print("VALIDACAO: OK")
    print(f"Video: {pilot['video_id']}")
    print(f"Cenas: {len(pilot['timeline'])}")
    print(f"Agentes: {len(context['agents'])}")
    print(f"Estados do pipeline: {len(pipeline['states'])}")
    print("Publicacao: desativada")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

