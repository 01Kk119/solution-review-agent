import unittest

import app


def decision(version: str, risk: str, fit_522: str, fit_532: str) -> str:
    return (
        f"项目统一版本：{version}\n"
        f"版本风险等级：{risk}\n"
        f"5.2.2满足全部需求：{fit_522}\n"
        f"5.3.2满足全部需求：{fit_532}\n"
        "版本上探5.3.2：否\n"
    )


def test_fixed_version_risk_mapping_is_accepted():
    app.validate_unified_version_decision(decision("5.2.2", "低", "是", "未评估"))
    app.validate_unified_version_decision(decision("5.3.2", "中", "否", "是"))
    app.validate_unified_version_decision(
        decision("暂无标准版本可满足", "高", "否", "否")
    )
    app.validate_unified_version_decision(
        decision("5.3.2（项目统一升级）", "中风险", "否", "是（需现场验证）")
    )


def test_wrong_version_risk_mapping_is_rejected():
    with unittest.TestCase().assertRaisesRegex(RuntimeError, "版本与风险映射不一致"):
        app.validate_unified_version_decision(decision("5.3.2", "低", "否", "是"))


def test_module_specific_target_version_is_rejected():
    content = decision("5.3.2", "中", "否", "是")
    content += "\n软件目标版本：5.3.2\n算法目标版本：5.2.2\n"
    with unittest.TestCase().assertRaisesRegex(
        RuntimeError, "不得按模块分别指定目标版本"
    ):
        app.validate_unified_version_decision(content)


def test_version_risk_level_is_extracted_for_project_card():
    assert app.extract_version_risk_level(decision("5.2.2", "低", "是", "未评估")) == "低"
    assert app.extract_version_risk_level(decision("5.3.2", "中风险", "否", "是")) == "中"
