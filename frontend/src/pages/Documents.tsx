import { useEffect, useState } from "react";
import { api, type Customer, type DocumentItem } from "../api/client";

const DOC_TYPES = ["brd", "prd", "user_story", "acceptance_criteria", "existing_test_case", "qbp"];

export default function Documents({ customer }: { customer: Customer }) {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  // Single workbook upload — doc type is fixed; the backend still requires one.
  const docType = DOC_TYPES[0];
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const refreshDocuments = () =>
    api.listDocuments(customer.id).then(setDocuments).catch((e) => setError(String(e)));

  useEffect(() => {
    refreshDocuments();
  }, [customer.id]);

  const upload = async () => {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".xlsx")) {
      setError("Only Excel files (.xlsx) are supported. Please upload an Excel workbook.");
      return;
    }
    setUploading(true);
    setError(null);
    try {
      await api.uploadDocument(customer.id, docType, file);
      setFile(null);
      await refreshDocuments();
    } catch (e) {
      setError(String(e));
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="page-fade-in">
      <div className="page-header">
        <div>
          <h2 className="page-title">Documents</h2>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      <div className="card">
        <div className="form-row">
          <label className="file-picker">
            <input
              type="file"
              accept=".xlsx"
              className="file-input-hidden"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
            <span className="file-picker-icon">⬆</span>
            Choose file
          </label>
          <span className="file-name">
            {file ? file.name : <span className="file-name-empty">No file selected (.xlsx)</span>}
          </span>
        </div>
        <div className="form-row" style={{ marginTop: 12 }}>
          <button className="btn btn-primary" onClick={upload} disabled={!file || uploading}>
            {uploading ? (
              <>
                <span className="spinner" /> Uploading...
              </>
            ) : (
              "Upload"
            )}
          </button>
        </div>
      </div>

      {documents.length === 0 ? (
        <div className="empty-state">No documents uploaded yet.</div>
      ) : (
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                <th>Filename</th>
                <th>Preview</th>
                <th>Uploaded</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((d) => (
                <tr key={d.id}>
                  <td>{d.filename}</td>
                  <td style={{ maxWidth: 320, color: "var(--text-muted)" }}>{d.extracted_text_preview.slice(0, 120)}</td>
                  <td style={{ color: "var(--text-muted)", whiteSpace: "nowrap" }}>
                    {new Date(d.uploaded_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
