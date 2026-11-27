/**
 * Bộ phân tích file Excel nhiều sheet (Quiz Test NMPP 2026) phía trình duyệt dùng SheetJS.
 * Đồng bộ quy tắc nhận diện chuyên đề & bộ đề với scripts/build_nmpp_data.py.
 */
(function (global) {
  "use strict";

  const ROMAN_NUMERALS = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV", "XVI", "XVII", "XVIII", "XIX", "XX",
  ];

  const GROUP_RULES = [
    ["ĐIỀU HÀNH VIÊN", "Điều Hành Viên"],
    ["DIEU HANH VIEN", "Điều Hành Viên"],
    ["ĐHV", "Điều Hành Viên"],
    ["DHV", "Điều Hành Viên"],
    ["TRƯỞNG KÍP", "Trưởng Kíp"],
    ["TRUONG KIP", "Trưởng Kíp"],
    ["TK", "Trưởng Kíp"],
    ["TRƯỞNG CA", "Trưởng Ca"],
    ["TRUONG CA", "Trưởng Ca"],
    ["TC", "Trưởng Ca"],
    ["SỬA CHỮA CƠ", "Sửa Chữa Cơ"],
    ["SC CO", "Sửa Chữa Cơ"],
    ["SỬA CHỮA ĐIỆN", "Sửa Chữa Điện"],
    ["SC DIEN", "Sửa Chữa Điện"],
    ["AN TOÀN", "An Toàn"],
    ["AN TOAN", "An Toàn"],
    ["ATĐ", "An Toàn"],
    ["VHDN", "Văn Hóa DN"],
    ["VĂN HÓA", "Văn Hóa DN"],
  ];

  function cleanText(val) {
    if (val === null || val === undefined) return "";
    return String(val)
      .replace(/\r?\n+/g, "\n")
      .replace(/[ \t]+/g, " ")
      .trim();
  }

  function normalizeSheetLabel(sheetName) {
    return String(sheetName || "").trim().replace(/\s+/g, " ");
  }

  function normalizeDaMarker(val) {
    const cleaned = cleanText(val)
      .toUpperCase()
      .replace(/[^A-ZĐ]/g, "");
    return cleaned === "ĐA" || cleaned === "DA" || cleaned === "X";
  }

  function detectGroup(sheetLabel) {
    const upper = sheetLabel.trim().toUpperCase();
    for (const [prefix, label] of GROUP_RULES) {
      if (upper.startsWith(prefix)) return label;
    }
    return sheetLabel;
  }

  function toRoman(index1Based) {
    if (index1Based >= 1 && index1Based <= ROMAN_NUMERALS.length) {
      return ROMAN_NUMERALS[index1Based - 1];
    }
    return String(index1Based);
  }

  function findNextNonEmptyCol1(rows, startIdx) {
    for (let i = startIdx; i < Math.min(startIdx + 5, rows.length); i++) {
      const r = rows[i] || [];
      const c1 = cleanText(r[0]);
      const c2 = cleanText(r[1]);
      if (c1 || c2) return c1.toUpperCase();
    }
    return "";
  }

  function parseSheetRows(rows, rawSheetName) {
    const sheetLabel = normalizeSheetLabel(rawSheetName);

    let startIdx = -1;
    const titleLines = [];
    for (let i = 0; i < Math.min(10, rows.length); i++) {
      const c1 = cleanText(rows[i] && rows[i][0]).toUpperCase();
      const c2 = cleanText(rows[i] && rows[i][1]);
      if (c1 === "CÂU HỎI" || c1 === "CAU HOI") {
        startIdx = i + 1;
        break;
      }
      if (c2) titleLines.push(c2);
    }

    if (startIdx < 0) return null;

    const orgTitle = titleLines[0] || "NHÀ MÁY THỦY ĐIỆN NẬM MÁ";
    const roleTitle = titleLines.length >= 2 ? titleLines.slice(1).join(" - ") : sheetLabel;

    const sections = [];
    const questions = [];
    const warnings = [];
    let currentSection = null;
    let currentQuestion = null;
    let autoQNum = 0;

    function finalizeQuestion(q) {
      if (!q) return;
      const correctIndices = [];
      q.options.forEach((opt, idx) => {
        if (opt.isCorrect) correctIndices.push(idx);
      });
      if (q.options.length < 2) {
        warnings.push(`[${sheetLabel}] Dòng ${q.sourceRow} (Câu ${q.number}): ít hơn 2 đáp án.`);
      }
      if (correctIndices.length === 0) {
        warnings.push(`[${sheetLabel}] Dòng ${q.sourceRow} (Câu ${q.number}): chưa có đáp án ĐA.`);
      }
      q.correctIndex = correctIndices.length > 0 ? correctIndices[0] : 0;
      if (correctIndices.length > 1) {
        q.correctIndices = correctIndices;
      }
      q.options = q.options.map((o) => ({ label: o.label, text: o.text }));
      questions.push(q);
    }

    for (let r = startIdx; r < rows.length; r++) {
      const row = rows[r] || [];
      const col1 = cleanText(row[0]);
      const col2 = cleanText(row[1]);
      const isDa = normalizeDaMarker(row[2]);

      if (!col1 && !col2) continue;
      if (col1 === "0" && !col2) continue;

      if (/^[A-L]$/i.test(col1) && currentQuestion !== null) {
        currentQuestion.options.push({
          label: col1.toUpperCase(),
          text: col2,
          isCorrect: isDa,
        });
        continue;
      }

      const nextCol1 = !col1 && col2 ? findNextNonEmptyCol1(rows, r + 1) : "";
      const isBlankQuestion = !col1 && Boolean(col2) && nextCol1 === "A";

      if ((/^\d+$/.test(col1) && Boolean(col2)) || isBlankQuestion) {
        finalizeQuestion(currentQuestion);
        if (!currentSection) {
          currentSection = { id: "I", title: "Phần chung", questionCount: 0 };
          sections.push(currentSection);
        }
        autoQNum = /^\d+$/.test(col1) ? parseInt(col1, 10) : autoQNum + 1;
        currentSection.questionCount += 1;
        currentQuestion = {
          id: `${sheetLabel}__${currentSection.id}-${autoQNum}-${questions.length + 1}`,
          number: autoQNum,
          sectionId: currentSection.id,
          sectionTitle: currentSection.title,
          text: col2,
          options: [],
          correctIndex: 0,
          sourceRow: r + 1,
        };
        continue;
      }

      if (col1 || col2) {
        finalizeQuestion(currentQuestion);
        currentQuestion = null;
        autoQNum = 0;
        const secId = col1 || toRoman(sections.length + 1);
        const secTitle = col2 || `Chuyên đề ${secId}`;
        currentSection = {
          id: secId,
          title: secTitle,
          questionCount: 0,
        };
        sections.push(currentSection);
      }
    }

    finalizeQuestion(currentQuestion);

    if (questions.length === 0) return null;

    return {
      id: sheetLabel,
      name: sheetLabel,
      group: detectGroup(sheetLabel),
      title: roleTitle,
      organization: orgTitle,
      totalSections: sections.length,
      totalQuestions: questions.length,
      sections,
      questions,
      warnings,
    };
  }

  async function parseMultiSheetExcel(file) {
    if (!file) throw new Error("Chưa chọn file nào.");
    if (typeof global.XLSX === "undefined") {
      throw new Error("Thư viện SheetJS chưa sẵn sàng. Vui lòng kiểm tra kết nối mạng.");
    }

    const buffer = await file.arrayBuffer();
    const workbook = global.XLSX.read(buffer, { type: "array" });
    const decks = [];
    let totalQuestions = 0;
    const allWarnings = [];

    for (const sheetName of workbook.SheetNames) {
      const ws = workbook.Sheets[sheetName];
      const rows = global.XLSX.utils.sheet_to_json(ws, { header: 1, defval: "" });
      const deck = parseSheetRows(rows, sheetName);
      if (deck && deck.totalQuestions > 0) {
        decks.push(deck);
        totalQuestions += deck.totalQuestions;
        allWarnings.push(...deck.warnings);
      }
    }

    if (decks.length === 0) {
      throw new Error("Không tìm thấy bộ đề hợp lệ nào trong file Excel.");
    }

    return {
      meta: {
        title: "QUIZ TEST NMPP 2026",
        organization: "NHÀ MÁY THỦY ĐIỆN NẬM MÁ",
        sourceFile: file.name,
        totalDecks: decks.length,
        totalQuestions,
        generatedAt: new Date().toISOString(),
      },
      decks,
      warnings: allWarnings,
    };
  }

  global.NmppExcelParser = {
    parseMultiSheetExcel,
  };
})(window);
