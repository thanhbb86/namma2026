"""Trích xuất toàn bộ các sheet đề thi từ file Excel NMPP 2026 thành JSON và JS."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import openpyxl

ROOT_DIR = Path(__file__).resolve().parent.parent
EXCEL_PATH = ROOT_DIR / "Câu hỏi chuyên môn ôn tập năm 2026.xlsx"
DATA_DIR = ROOT_DIR / "data"
EXTRA_DECKS_PATH = DATA_DIR / "extra-decks.json"
JSON_OUT = DATA_DIR / "nmpp-2026.json"
JS_OUT = DATA_DIR / "nmpp-2026.js"

ROMAN_NUMERALS = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
]

GROUP_RULES = [
    ("ĐIỀU HÀNH VIÊN", "Điều Hành Viên"),
    ("DIEU HANH VIEN", "Điều Hành Viên"),
    ("ĐHV", "Điều Hành Viên"),
    ("DHV", "Điều Hành Viên"),
    ("TRƯỞNG KÍP", "Trưởng Kíp"),
    ("TRUONG KIP", "Trưởng Kíp"),
    ("TK", "Trưởng Kíp"),
    ("TRƯỞNG CA", "Trưởng Ca"),
    ("TRUONG CA", "Trưởng Ca"),
    ("TC", "Trưởng Ca"),
    ("SỬA CHỮA CƠ", "Sửa Chữa Cơ"),
    ("SC CO", "Sửa Chữa Cơ"),
    ("SỬA CHỮA ĐIỆN", "Sửa Chữa Điện"),
    ("SC DIEN", "Sửa Chữa Điện"),
    ("AN TOÀN", "An Toàn"),
    ("AN TOAN", "An Toàn"),
    ("ATĐ", "An Toàn"),
    ("VHDN", "Văn Hóa DN"),
    ("VĂN HÓA", "Văn Hóa DN"),
]


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    return re.sub(r"[ \t]+", " ", re.sub(r"\r?\n+", "\n", text)).strip()


def normalize_sheet_label(sheet_name: str) -> str:
    return re.sub(r"\s+", " ", sheet_name.strip())


def normalize_da_marker(value: Any) -> bool:
    """Nhận diện dấu đáp án đúng ('ĐA', 'DA', 'X')."""
    raw = clean_text(value).upper()
    cleaned = re.sub(r"[^A-ZĐ]", "", raw)
    return cleaned in ("ĐA", "DA", "X")


def detect_group(sheet_label: str) -> str:
    upper = sheet_label.strip().upper()
    for prefix, label in GROUP_RULES:
        if upper.startswith(prefix):
            return label
    return sheet_label


def to_roman(index_1based: int) -> str:
    if 1 <= index_1based <= len(ROMAN_NUMERALS):
        return ROMAN_NUMERALS[index_1based - 1]
    return str(index_1based)


def atomic_write_text(target_path: Path, content: str, encoding: str = "utf-8") -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_suffix(target_path.suffix + ".tmp")
    try:
        tmp_path.write_text(content, encoding=encoding)
        tmp_path.replace(target_path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink(missing_ok=True)


def find_next_nonempty_col1(ws: Any, start_row: int, max_row: int) -> str:
    for r in range(start_row, min(start_row + 5, max_row + 1)):
        c1 = clean_text(ws.cell(r, 1).value)
        c2 = clean_text(ws.cell(r, 2).value)
        if c1 or c2:
            return c1.upper()
    return ""


def parse_sheet(ws: Any, raw_sheet_name: str) -> dict[str, Any] | None:
    sheet_label = normalize_sheet_label(raw_sheet_name)

    # Tìm dòng tiêu đề ("CÂU HỎI") — nếu không có thì bỏ qua (ví dụ sheet Tổng hợp)
    start_row = None
    title_lines: list[str] = []
    for r in range(1, min(10, ws.max_row + 1)):
        c1 = clean_text(ws.cell(r, 1).value).upper()
        c2 = clean_text(ws.cell(r, 2).value)
        if c1 in ("CÂU HỎI", "CAU HOI"):
            start_row = r + 1
            break
        if c2:
            title_lines.append(c2)

    if start_row is None:
        return None

    org_title = title_lines[0] if len(title_lines) >= 1 else "NHÀ MÁY THỦY ĐIỆN NẬM MÁ"
    role_title = " - ".join(title_lines[1:]) if len(title_lines) >= 2 else sheet_label

    sections: list[dict[str, Any]] = []
    questions: list[dict[str, Any]] = []
    warnings: list[str] = []

    current_section: dict[str, Any] | None = None
    current_question: dict[str, Any] | None = None
    auto_q_num = 0

    def finalize_question(q: dict[str, Any] | None) -> None:
        if q is None:
            return
        correct_indices = [i for i, opt in enumerate(q["options"]) if opt["isCorrect"]]
        if len(q["options"]) < 2:
            warnings.append(
                f"[{sheet_label}] Dòng {q['sourceRow']} (Câu {q['number']}): chỉ có {len(q['options'])} đáp án."
            )
        if len(correct_indices) == 0:
            warnings.append(
                f"[{sheet_label}] Dòng {q['sourceRow']} (Câu {q['number']}): chưa có đáp án đúng (ĐA)."
            )
        q["correctIndex"] = correct_indices[0] if correct_indices else 0
        if len(correct_indices) > 1:
            q["correctIndices"] = correct_indices
        q["options"] = [{"label": opt["label"], "text": opt["text"]} for opt in q["options"]]
        questions.append(q)

    for r in range(start_row, ws.max_row + 1):
        col1 = clean_text(ws.cell(r, 1).value)
        col2 = clean_text(ws.cell(r, 2).value)
        is_da = normalize_da_marker(ws.cell(r, 3).value)

        if not col1 and not col2:
            continue

        # Bỏ qua dòng số 0 thừa ở cuối sheet
        if col1 == "0" and not col2:
            continue

        # Phương án A..L
        if re.match(r"^[A-L]$", col1.upper()) and current_question is not None:
            current_question["options"].append(
                {
                    "label": col1.upper(),
                    "text": col2,
                    "isCorrect": is_da,
                }
            )
            continue

        # Câu hỏi mới (có số thứ tự + nội dung, hoặc ô số trống nhưng dòng kế tiếp là phương án A)
        next_col1 = find_next_nonempty_col1(ws, r + 1, ws.max_row) if (not col1 and col2) else ""
        is_blank_question = not col1 and bool(col2) and next_col1 == "A"

        if (re.match(r"^\d+$", col1) and bool(col2)) or is_blank_question:
            finalize_question(current_question)
            if current_section is None:
                current_section = {"id": "I", "title": "Phần chung", "questionCount": 0}
                sections.append(current_section)

            auto_q_num = int(col1) if re.match(r"^\d+$", col1) else (auto_q_num + 1)
            current_section["questionCount"] += 1
            current_question = {
                "id": f"{sheet_label}__{current_section['id']}-{auto_q_num}-{len(questions) + 1}",
                "number": auto_q_num,
                "sectionId": current_section["id"],
                "sectionTitle": current_section["title"],
                "text": col2,
                "options": [],
                "correctIndex": 0,
                "sourceRow": r,
            }
            continue

        # Tiêu đề chuyên đề mới (cả dạng có mã ở cột A lẫn dạng cột A trống + cột B ghi tên chuyên đề)
        if col1 or col2:
            finalize_question(current_question)
            current_question = None
            auto_q_num = 0
            sec_id = col1 if col1 else to_roman(len(sections) + 1)
            sec_title = col2 or f"Chuyên đề {sec_id}"
            current_section = {
                "id": sec_id,
                "title": sec_title,
                "questionCount": 0,
            }
            sections.append(current_section)

    finalize_question(current_question)

    if len(questions) == 0:
        return None

    return {
        "id": sheet_label,
        "name": sheet_label,
        "group": detect_group(sheet_label),
        "title": role_title,
        "organization": org_title,
        "totalSections": len(sections),
        "totalQuestions": len(questions),
        "sections": sections,
        "questions": questions,
        "warnings": warnings,
    }


def main() -> int:
    try:
        if not EXCEL_PATH.exists():
            raise FileNotFoundError(f"Không tìm thấy file Excel: {EXCEL_PATH}")

        wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
        try:
            decks = []
            total_questions = 0
            all_warnings = []

            for sheet_name in wb.sheetnames:
                deck = parse_sheet(wb[sheet_name], sheet_name)
                if deck is None:
                    print(f"Bỏ qua sheet không phải bộ đề: {sheet_name}")
                    continue
                decks.append(deck)
                total_questions += deck["totalQuestions"]
                all_warnings.extend(deck["warnings"])

            # Tự động gộp các bộ đề dùng chung (An toàn, Văn hóa Doanh nghiệp) nếu có
            if EXTRA_DECKS_PATH.exists():
                extra_decks = json.loads(EXTRA_DECKS_PATH.read_text(encoding="utf-8"))
                existing_ids = {d["id"] for d in decks}
                if isinstance(extra_decks, list):
                    for ed in extra_decks:
                        if isinstance(ed, dict) and ed.get("id") and ed["id"] not in existing_ids:
                            decks.append(ed)
                            existing_ids.add(ed["id"])
                            total_questions += int(ed.get("totalQuestions", len(ed.get("questions", []))))
                            all_warnings.extend(ed.get("warnings", []))

            payload = {
                "meta": {
                    "title": "QUIZ TEST NMPP 2026",
                    "organization": "NHÀ MÁY THỦY ĐIỆN NẬM MÁ",
                    "sourceFile": EXCEL_PATH.name,
                    "totalDecks": len(decks),
                    "totalQuestions": total_questions,
                    "generatedAt": datetime.now(timezone.utc).isoformat(),
                },
                "decks": decks,
            }
        finally:
            wb.close()

        json_text = json.dumps(payload, ensure_ascii=False, indent=2)
        js_text = (
            "// Tự động sinh bởi scripts/build_nmpp_data.py - Không sửa tay\n"
            "window.NMPP_DATA = " + json_text + ";\n"
        )

        atomic_write_text(JSON_OUT, json_text, encoding="utf-8")
        atomic_write_text(JS_OUT, js_text, encoding="utf-8")

        print(f"Đã xuất {len(decks)} bộ đề với tổng {total_questions} câu hỏi:")
        for d in decks:
            print(
                f" - {d['id']:20s} | {d['group']:16s} | {d['totalSections']:2d} chuyên đề | "
                f"{d['totalQuestions']:3d} câu | cảnh báo: {len(d['warnings'])}"
            )
        if all_warnings:
            print(f"Tổng cảnh báo ({len(all_warnings)}):")
            for w in all_warnings[:20]:
                print(f"  * {w}")
        return 0
    except Exception as exc:
        print(f"Lỗi: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
