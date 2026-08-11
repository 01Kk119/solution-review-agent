from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover
    PdfReader = None


VEHICLE_TERMS = re.compile(
    r"(?i)\b(?:AGV|AMR|vehicle|forklift|fleet|VNE[\w()\-]*|VNP[\w()\-]*)\b|车辆|叉车"
)
QUANTITY_TERMS = re.compile(
    r"(?i)\b(?:qty|quantity|total|units?|required|count|existing|current|new|expansion|simulation|spare)\b|数量|合计|总数|台"
)
MODEL_PATTERN = re.compile(r"(?i)\b(V(?:NE|NP)[A-Z0-9()\-]*(?:-\d+)?)\b")
ZONE_PATTERN = re.compile(r"(?i)\bzone\s*[-:]?\s*(\d+)\b")
NUMBER_BEFORE_MODEL = re.compile(
    r"(?i)(\d{1,4})\s*(?:units?|台)?\s*(?:of\s+)?"
    r"(V(?:NE|NP)[A-Z0-9()\-]*(?:-\d+)?)"
)
MODEL_BEFORE_NUMBER = re.compile(
    r"(?i)(V(?:NE|NP)[A-Z0-9()\-]*(?:-\d+)?)"
    r"[^.\n|]{0,50}?(\d{1,4})\s*(?:units?|台)\b"
)
GENERIC_VEHICLE_COUNT = re.compile(
    r"(?i)(?:AGV|AMR|vehicles?|forklifts?|车辆)[^.\n|]{0,35}?"
    r"(\d{1,4})\s*(?:units?|台)?\b"
)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _xml_text(raw: bytes) -> str:
    root = ElementTree.fromstring(raw)
    values = [
        (node.text or "").strip()
        for node in root.iter()
        if _local_name(node.tag) in {"t", "v"} and (node.text or "").strip()
    ]
    return "\n".join(values)


def _numbered_xml_entries(names: list[str], prefix: str, suffix: str) -> list[str]:
    selected = [name for name in names if name.startswith(prefix) and name.endswith(suffix)]
    return sorted(
        selected,
        key=lambda name: int(re.search(r"\d+", Path(name).stem).group()),
    )


def _index_pptx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        slides = _numbered_xml_entries(names, "ppt/slides/slide", ".xml")
        return [
            {"locator": f"slide{index}", "text": _xml_text(archive.read(name))}
            for index, name in enumerate(slides, start=1)
        ]


def _shared_strings(archive: zipfile.ZipFile, names: list[str]) -> list[str]:
    if "xl/sharedStrings.xml" not in names:
        return []
    root = ElementTree.fromstring(archive.read("xl/sharedStrings.xml"))
    strings: list[str] = []
    for item in root:
        if _local_name(item.tag) != "si":
            continue
        strings.append("".join((node.text or "") for node in item.iter() if _local_name(node.tag) == "t"))
    return strings


def _sheet_names(archive: zipfile.ZipFile, names: list[str]) -> dict[str, str]:
    if "xl/workbook.xml" not in names or "xl/_rels/workbook.xml.rels" not in names:
        return {}
    rel_root = ElementTree.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relationships = {
        node.attrib.get("Id", ""): node.attrib.get("Target", "")
        for node in rel_root
        if _local_name(node.tag) == "Relationship"
    }
    workbook = ElementTree.fromstring(archive.read("xl/workbook.xml"))
    result: dict[str, str] = {}
    for node in workbook.iter():
        if _local_name(node.tag) != "sheet":
            continue
        rel_id = next((value for key, value in node.attrib.items() if key.endswith("}id")), "")
        target = relationships.get(rel_id, "")
        if target:
            normalized = target.lstrip("/")
            if not normalized.startswith("xl/"):
                normalized = f"xl/{normalized}"
            result[normalized] = node.attrib.get("name", Path(normalized).stem)
    return result


def _xlsx_sheet_text(raw: bytes, shared: list[str]) -> str:
    root = ElementTree.fromstring(raw)
    values: list[str] = []
    for cell in (node for node in root.iter() if _local_name(node.tag) == "c"):
        cell_type = cell.attrib.get("t", "")
        value_node = next((node for node in cell if _local_name(node.tag) == "v"), None)
        inline_nodes = [node for node in cell.iter() if _local_name(node.tag) == "t"]
        if cell_type == "inlineStr" and inline_nodes:
            value = "".join((node.text or "") for node in inline_nodes)
        elif value_node is not None and value_node.text is not None:
            value = value_node.text
            if cell_type == "s":
                try:
                    value = shared[int(value)]
                except (IndexError, ValueError):
                    pass
        else:
            continue
        if value.strip():
            values.append(f"{cell.attrib.get('r', '')}={value.strip()}")
    return "\n".join(values)


def _index_xlsx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        shared = _shared_strings(archive, names)
        name_map = _sheet_names(archive, names)
        sheets = _numbered_xml_entries(names, "xl/worksheets/sheet", ".xml")
        return [
            {
                "locator": name_map.get(name, Path(name).stem),
                "text": _xlsx_sheet_text(archive.read(name), shared),
            }
            for name in sheets
        ]


def _index_docx(path: Path) -> list[dict[str, str]]:
    with zipfile.ZipFile(path) as archive:
        if "word/document.xml" not in archive.namelist():
            return []
        return [{"locator": "document", "text": _xml_text(archive.read("word/document.xml"))}]


def _index_pdf(path: Path) -> list[dict[str, str]]:
    if PdfReader is None:
        raise RuntimeError("pypdf unavailable")
    reader = PdfReader(str(path), strict=False)
    return [
        {"locator": f"page{number}", "text": (page.extract_text() or "").strip()}
        for number, page in enumerate(reader.pages, start=1)
    ]


def index_source_units(path: Path) -> dict[str, Any]:
    extension = path.suffix.lower()
    handlers = {
        ".pptx": _index_pptx,
        ".xlsx": _index_xlsx,
        ".docx": _index_docx,
        ".pdf": _index_pdf,
    }
    try:
        if extension in handlers:
            units = handlers[extension](path)
        elif extension in {".md", ".txt", ".json", ".csv", ".log", ".yaml", ".yml"}:
            units = [{"locator": "document", "text": path.read_text(encoding="utf-8", errors="replace")}]
        else:
            return {
                "file": path.name,
                "supported": False,
                "total_units": 0,
                "indexed_units": 0,
                "complete": True,
                "units": [],
            }
        return {
            "file": path.name,
            "supported": True,
            "total_units": len(units),
            "indexed_units": len(units),
            "complete": True,
            "units": units,
        }
    except Exception as exc:
        return {
            "file": path.name,
            "supported": True,
            "total_units": 0,
            "indexed_units": 0,
            "complete": False,
            "error": f"{type(exc).__name__}: {exc}",
            "units": [],
        }


def _quantity_kind(text: str) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("project total", "fleet total", "total vehicles", "车辆总数", "总配置")):
        return "project_total"
    if any(token in lowered for token in ("existing", "current", "现有", "既有")):
        return "existing"
    if any(token in lowered for token in ("new", "additional", "expansion", "新增", "扩容")):
        return "new"
    if any(token in lowered for token in ("simulation", "仿真")):
        return "simulation"
    if any(token in lowered for token in ("spare", "备用")):
        return "spare"
    if any(token in lowered for token in ("required", "count analysis", "需求", "配置")):
        return "required"
    return "unknown"


def _statement_type(text: str) -> str:
    lowered = text.lower()
    if "conclusion" in lowered:
        return "conclusion"
    if "total" in lowered or "合计" in text:
        return "table_total"
    return "detail"


def _authority(statement_type: str, kind: str) -> int:
    if kind == "project_total":
        return 5
    if statement_type == "table_total":
        return 3
    if statement_type == "conclusion":
        return 2
    return 1


def extract_vehicle_records(index: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    seen: set[tuple[str, str, int, str, str]] = set()
    last_zone = ""
    for unit in index.get("units", []):
        text = str(unit.get("text", ""))
        zone_match = ZONE_PATTERN.search(text)
        if zone_match:
            last_zone = f"Zone {zone_match.group(1)}"
        if not VEHICLE_TERMS.search(text) or not QUANTITY_TERMS.search(text):
            continue
        compact = re.sub(r"\s+", " ", text).strip()
        kind = _quantity_kind(compact)
        statement = _statement_type(compact)
        matches: list[tuple[str, int, str]] = []
        for match in NUMBER_BEFORE_MODEL.finditer(compact):
            matches.append((match.group(2).upper(), int(match.group(1)), match.group(0)))
        for match in MODEL_BEFORE_NUMBER.finditer(compact):
            matches.append((match.group(1).upper(), int(match.group(2)), match.group(0)))
        if not matches:
            generic = GENERIC_VEHICLE_COUNT.search(compact)
            if generic:
                model_match = MODEL_PATTERN.search(compact)
                matches.append(((model_match.group(1).upper() if model_match else "UNSPECIFIED"), int(generic.group(1)), generic.group(0)))
        for model, quantity, evidence in matches:
            if quantity <= 0 or quantity > 1000:
                continue
            key = (last_zone, model, quantity, kind, unit["locator"])
            if key in seen:
                continue
            seen.add(key)
            records.append(
                {
                    "scope": last_zone or "project",
                    "model": model,
                    "quantity": quantity,
                    "kind": kind,
                    "statement_type": statement,
                    "authority": _authority(statement, kind),
                    "source": f"{index['file']}#{unit['locator']}",
                    "evidence": evidence[:300],
                }
            )
    return records


def _load_override(files: list[Path]) -> dict[str, Any] | None:
    for path in files:
        if path.name.lower() != "vehicle_total_override.json":
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        total = data.get("authoritative_total")
        if isinstance(total, int) and total > 0:
            return data
    return None


def reconcile_vehicle_records(
    indexes: list[dict[str, Any]],
    records: list[dict[str, Any]],
    confirmed_total: dict[str, Any] | None = None,
) -> dict[str, Any]:
    supported = [item for item in indexes if item.get("supported")]
    coverage_complete = bool(supported) and all(item.get("complete") for item in supported)
    coverage = [
        {
            "file": item["file"],
            "indexed": item["indexed_units"],
            "total": item["total_units"],
            "complete": item["complete"],
            **({"error": item["error"]} if item.get("error") else {}),
        }
        for item in supported
    ]

    conflicts: list[dict[str, Any]] = []
    conflict_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in records:
        conflict_groups.setdefault((record["scope"], record["model"]), []).append(record)
        grouped.setdefault((record["scope"], record["model"], record["kind"]), []).append(record)
    for key, items in conflict_groups.items():
        quantities = sorted({item["quantity"] for item in items})
        statement_types = {item["statement_type"] for item in items}
        if len(quantities) > 1 and {"conclusion", "table_total"}.issubset(statement_types):
            conflicts.append(
                {
                    "type": "conclusion_table_mismatch",
                    "scope": key[0],
                    "model": key[1],
                    "quantities": quantities,
                    "sources": [item["source"] for item in items],
                }
            )

    selected: list[dict[str, Any]] = []
    for items in grouped.values():
        selected.append(max(items, key=lambda item: (item["authority"], item["quantity"])))
    calculable = [item for item in selected if item["kind"] in {"new", "required"}]
    calculated_subtotal = sum(item["quantity"] for item in calculable) if calculable else None

    authoritative_total = None
    expression = ""
    if confirmed_total:
        authoritative_total = confirmed_total["authoritative_total"]
        expression = str(confirmed_total.get("expression", authoritative_total))
        if calculated_subtotal is not None and calculated_subtotal != authoritative_total:
            conflicts.append(
                {
                    "type": "authoritative_total_detail_gap",
                    "authoritative_total": authoritative_total,
                    "calculated_subtotal": calculated_subtotal,
                    "difference": authoritative_total - calculated_subtotal,
                }
            )

    if not coverage_complete:
        status = "BLOCKED"
    elif authoritative_total is not None:
        status = "PASS" if not conflicts else "PASS_WITH_NOTE"
    elif conflicts or calculated_subtotal is None:
        status = "BLOCKED"
    else:
        status = "PASS"

    return {
        "schema_version": 1,
        "coverage": {"complete": coverage_complete, "files": coverage},
        "records": records,
        "authoritative_total": authoritative_total,
        "expression": expression,
        "calculated_subtotal": calculated_subtotal,
        "conflicts": conflicts,
        "status": status,
        "rules": {
            "model_may_override_total": False,
            "blocked_allows_definite_total": False,
        },
    }


def build_vehicle_reconciliation(files: list[Path]) -> dict[str, Any]:
    indexes = [index_source_units(path) for path in files]
    records = [record for index in indexes for record in extract_vehicle_records(index)]
    return reconcile_vehicle_records(indexes, records, _load_override(files))


def compact_vehicle_context(result: dict[str, Any], max_chars: int = 2400) -> str:
    compact = {
        "coverage": result["coverage"],
        "authoritative_total": result["authoritative_total"],
        "expression": result["expression"],
        "calculated_subtotal": result["calculated_subtotal"],
        "conflicts": result["conflicts"],
        "status": result["status"],
        "instruction": (
            "车辆总数只能采用authoritative_total；status=BLOCKED时禁止输出确定总数；"
            "模型不得重新求和或覆盖程序结果。"
        ),
    }
    text = json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    return text[:max_chars]
