from app import select_relevant_markdown_sections, validate_solution_unresolved_output


VALID = """# 方案未决项清单

## 1. 汇总结论

| 未决项总数 | 高影响 | 中影响 | 低影响 | 最晚关闭节点 |
|---:|---:|---:|---:|---|
| 1 | 0 | 1 | 0 | 设计冻结前 |

## 2. 关键风险

| 风险ID | 风险描述 | 等级 | 当前依据 | 可能影响 | 关联待确认项 | 关闭动作 | 责任方 |
|---|---|---|---|---|---|---|---|
| PAP-001 | 托盘变形范围不清 | 中 | 项目资料 | 插取失败 | PEND-001 | 补充样本 | 客户 |

## 3. 待确认事项

| 未决ID | 待确认内容 | 无法确认原因 | 可能影响 | 暂定等级 | 关联风险 | 责任方 | 最晚确认节点 | 关闭条件 | 状态 |
|---|---|---|---|---|---|---|---|---|---|
| PEND-001 | 最大变形量 | 客户暂无数据 | 插取失败 | 中 | PAP-001 | 客户 | 设计冻结前 | 提供实测值 | 待获取 |
"""


def test_accepts_fixed_three_section_format():
    validate_solution_unresolved_output(VALID)


def test_rejects_removed_sections():
    try:
        validate_solution_unresolved_output(VALID + "\n## 4. 按假设推进事项\n")
    except ValueError as exc:
        assert "已删除章节" in str(exc)
    else:
        raise AssertionError("removed section must be rejected")


def test_selects_only_relevant_markdown_sections():
    source = """# 总结
不要传入

## 关键风险
保留风险

## 过程说明
不要传入

## 待确认事项
保留待确认
"""
    selected = select_relevant_markdown_sections(source, ("风险", "待确认"))
    assert "保留风险" in selected
    assert "保留待确认" in selected
    assert "不要传入" not in selected
