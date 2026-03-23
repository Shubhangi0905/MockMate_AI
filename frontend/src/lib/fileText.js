import * as pdfjsLib from "pdfjs-dist";
import pdfWorker from "pdfjs-dist/build/pdf.worker.mjs?url";

pdfjsLib.GlobalWorkerOptions.workerSrc = pdfWorker;

function readAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.onload = () => resolve(String(reader.result || ""));
    reader.readAsText(file);
  });
}

function readAsArrayBuffer(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = () => reject(new Error("Failed to read file"));
    reader.onload = () => resolve(reader.result);
    reader.readAsArrayBuffer(file);
  });
}

async function extractPdfText(file) {
  const buf = await readAsArrayBuffer(file);
  const pdf = await pdfjsLib.getDocument({ data: buf }).promise;
  let fullText = "";
  for (let pageNum = 1; pageNum <= pdf.numPages; pageNum += 1) {
    const page = await pdf.getPage(pageNum);
    const content = await page.getTextContent();
    const strings = content.items.map((it) => (it && it.str ? it.str : "")).filter(Boolean);
    fullText += strings.join(" ") + "\n";
  }
  return fullText.trim();
}

export async function extractTextFromFile(file) {
  if (!file) return "";
  const name = (file.name || "").toLowerCase();
  if (name.endsWith(".pdf") || file.type === "application/pdf") {
    return extractPdfText(file);
  }
  if (
    name.endsWith(".txt") ||
    name.endsWith(".md") ||
    name.endsWith(".json") ||
    file.type.startsWith("text/")
  ) {
    return (await readAsText(file)).trim();
  }
  throw new Error("Unsupported file type. Upload a .pdf or .txt");
}

