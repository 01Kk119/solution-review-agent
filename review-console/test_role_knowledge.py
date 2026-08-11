import app


def test_all_role_knowledge_files_exist_and_load():
    for role, relative_paths in app.ROLE_KNOWLEDGE_FILES.items():
        assert relative_paths, role
        assert all((app.KNOWLEDGE_BASE_DIR / path).is_file() for path in relative_paths), role
        assert app.load_role_knowledge(role).strip(), role


def test_software_role_uses_compact_5_2_2_first_indexes():
    assert app.ROLE_KNOWLEDGE_FILES["software"] == (
        "risk_indexes/software_core_development_risk_index.md",
        "risk_indexes/software_5_2_2_risk_index.md",
    )
    assert app.ROLE_KNOWLEDGE_FILES["software_next_version"] == (
        "risk_indexes/software_5_3_2_risk_index.md",
    )
    knowledge = app.load_role_knowledge("software")
    assert "强制版本顺序" in knowledge
    assert "先仅用 5.2.2" in knowledge
    assert "5.3.2" in knowledge
    next_knowledge = app.load_role_knowledge("software_next_version")
    assert "增量能力" in next_knowledge
    assert "长路径滚动下发" in next_knowledge


def test_pick_place_role_uses_analyzed_risk_index_only():
    assert app.ROLE_KNOWLEDGE_FILES["pick_place"] == (
        "risk_indexes/pick_place_development_risk_index.md",
    )
    assert app.ROLE_SOURCE_FILES["pick_place"] == (
        "capability_specs/pick_place_knowledge/pick_and_place_review_master_guide.md",
        "capability_specs/pick_place_knowledge/pick_and_place_version_boundary_matrix.md",
        "capability_specs/pick_and_place_capability_spec.md",
        "capability_specs/load_carrier_capability_spec.md",
    )
    assert "hardware_safety" not in app.ROLE_KNOWLEDGE_FILES


def test_binary_mingmou_source_is_not_part_of_default_agent_context():
    assert app.ROLE_KNOWLEDGE_FILES["mingmou"] == (
        "risk_indexes/brighteyes_development_risk_index.md",
    )
    assert app.ROLE_SOURCE_FILES["mingmou"] == (
        "brighteyes/brighteyes_capability_spec.md",
    )
    assert "brighteyes_specification.md" not in app.ROLE_SOURCE_FILES["mingmou"]
    knowledge = app.load_role_knowledge("mingmou")
    assert "明确不使用" in knowledge
