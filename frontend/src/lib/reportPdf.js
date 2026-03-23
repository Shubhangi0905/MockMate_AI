import { jsPDF } from "jspdf";

function ensurePage(doc, y, marginTop, marginBottom) {
  const pageHeight = doc.internal.pageSize.getHeight();
  if (y >= pageHeight - marginBottom) {
    doc.addPage();
    return marginTop;
  }
  return y;
}

function safeText(doc, ln, x, y, marginTop, marginBottom, lineHeight) {
  y = ensurePage(doc, y, marginTop, marginBottom);
  doc.text(ln, x, y);
  return y + lineHeight;
}

function safeLine(doc, ln, x, y, marginTop, marginBottom) {
  y = ensurePage(doc, y, marginTop, marginBottom);
  doc.text(ln, x, y);
  return y;
}

function addWrapped(doc, text, x, y, maxWidth, lineHeight, marginTop, marginBottom) {
  const lines = doc.splitTextToSize(String(text || ""), maxWidth);
  lines.forEach((ln) => {
    y = safeText(doc, ln, x, y, marginTop, marginBottom, lineHeight);
  });
  return y;
}

function addBullets(doc, items, x, y, maxWidth, lineHeight, marginTop, marginBottom) {
  (items || []).forEach((it) => {
    const lines = doc.splitTextToSize(`• ${it}`, maxWidth);
    lines.forEach((ln) => {
      y = safeText(doc, ln, x, y, marginTop, marginBottom, lineHeight);
    });
  });
  return y;
}

export function buildReportPdf({ sessionId, analysis, questions, answers, evaluations, report }) {
  const doc = new jsPDF({ unit: "pt", format: "a4" });

  const margin = 56;
  const maxWidth = doc.internal.pageSize.getWidth() - margin * 2;
  const line = 16;
  let y = margin;

  const pageW = doc.internal.pageSize.getWidth();
  const pageH = doc.internal.pageSize.getHeight();

  function hr() {
    y = ensurePage(doc, y, margin, margin);
    doc.setDrawColor(180);
    doc.setLineWidth(0.6);
    doc.line(margin, y, pageW - margin, y);
    y += 14;
  }

  function section(title) {
    y = ensurePage(doc, y + 10, margin, margin);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    y = safeLine(doc, title, margin, y, margin, margin);
    y += 10;
    doc.setFont("helvetica", "normal");
    doc.setFontSize(11.5);
  }

  doc.setFont("helvetica", "bold");
  doc.setFontSize(18);
  doc.text("MockMate AI — Interview Report", margin, y);
  y += 10;
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11);
  doc.setTextColor(120);
  doc.text("Structured feedback and actionable next steps", margin, y);
  doc.setTextColor(0);
  y += 18;
  hr();

  section("Summary");
  y = addWrapped(
    doc,
    `Overall score: ${report?.overall_score ?? "—"}/100`,
    margin,
    y,
    maxWidth,
    line,
    margin,
    margin
  );
  y += 8;

  section("Strengths");
  y = addBullets(doc, report?.strengths || [], margin, y, maxWidth, line, margin, margin);
  y += 8;

  section("Weaknesses");
  y = addBullets(doc, report?.weaknesses || [], margin, y, maxWidth, line, margin, margin);
  y += 8;

  section("Suggestions");
  y = addBullets(doc, report?.suggestions || [], margin, y, maxWidth, line, margin, margin);
  y += 8;

  section("Verdict");
  y = addWrapped(doc, report?.verdict || "—", margin, y, maxWidth, line, margin, margin);

  doc.addPage();
  y = margin;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Analysis Snapshot", margin, y);
  y += 18;
  hr();
  doc.setFontSize(11.5);
  doc.setFont("helvetica", "normal");
  y = addWrapped(doc, `Role: ${analysis?.inferred_role || "—"}`, margin, y, maxWidth, line, margin, margin);
  if (analysis?.match_score !== null && analysis?.match_score !== undefined) {
    y = addWrapped(
      doc,
      `Match score: ${analysis?.match_score}`,
      margin,
      y,
      maxWidth,
      line,
      margin,
      margin
    );
  }
  y += 10;
  section("Skills");
  y = addBullets(doc, analysis?.skills || [], margin, y, maxWidth, line, margin, margin);

  if (analysis?.missing_skills?.length) {
    y += 10;
    section("Missing Skills");
    y = addBullets(doc, analysis?.missing_skills || [], margin, y, maxWidth, line, margin, margin);
  }

  doc.addPage();
  y = margin;
  doc.setFont("helvetica", "bold");
  doc.setFontSize(16);
  doc.text("Transcript & Evaluations", margin, y);
  y += 18;
  hr();
  doc.setFont("helvetica", "normal");
  doc.setFontSize(11.5);

  const n = Math.max(questions?.length || 0, answers?.length || 0, evaluations?.length || 0);
  for (let i = 0; i < n; i += 1) {
    // Start each Q/A block on a fresh page if we're low on space
    if (y > pageH - margin - 220) {
      doc.addPage();
      y = margin;
    }
    doc.setFont("helvetica", "bold");
    y = safeLine(doc, `Q${i + 1}`, margin, y, margin, margin);
    y += 14;
    doc.setFont("helvetica", "normal");
    y = addWrapped(doc, questions?.[i] || "", margin, y, maxWidth, line, margin, margin);
    y += 10;
    doc.setFont("helvetica", "bold");
    y = safeLine(doc, "Answer", margin, y, margin, margin);
    y += 14;
    doc.setFont("helvetica", "normal");
    y = addWrapped(doc, answers?.[i] || "", margin, y, maxWidth, line, margin, margin);
    const ev = evaluations?.[i];
    if (ev) {
      y += 10;
      doc.setFont("helvetica", "bold");
      y = safeLine(doc, `Score: ${ev.score}/10`, margin, y, margin, margin);
      y += 14;
      doc.setFont("helvetica", "normal");
      y = addWrapped(doc, ev.feedback || "", margin, y, maxWidth, line, margin, margin);
      y += 10;
      doc.setFont("helvetica", "italic");
      y = addWrapped(doc, `Tip: ${ev.improvement_tip || ""}`, margin, y, maxWidth, line, margin, margin);
      doc.setFont("helvetica", "normal");
    }
    y += 18;
    hr();
  }

  return doc;
}
