/**
 * Fixture for eval #23 — permission-ui.
 * Intentionally broken permission UX: hide vs disable confused, no why-disabled
 * explanation, native title tooltip, and 404 used for a known forbidden route.
 */
import React, { useState } from "react";

type Role = "viewer" | "editor" | "admin";

const CURRENT_ROLE: Role = "viewer";

export default function AnalysisDetailPage() {
  const [copied, setCopied] = useState(false);
  const analysisId = "an_9f3c2e1a";
  const canDelete = CURRENT_ROLE === "admin";
  const canEdit = CURRENT_ROLE === "editor" || CURRENT_ROLE === "admin";

  // BUG: clipboard has no accessible label change / failure feedback
  const handleCopy = () => {
    navigator.clipboard.writeText(analysisId);
    setCopied(true);
  };

  // BUG: disabled control still fires handler; no explanation of why
  const handleDelete = () => {
    if (!canDelete) return;
    window.confirm("Delete this analysis?");
  };

  return (
    <main className="p-6">
      <h1 className="text-xl font-medium">Analysis detail</h1>

      <div className="mt-4 flex items-center gap-2">
        <code className="text-sm">{analysisId}</code>
        <button type="button" onClick={handleCopy} title="Copy">
          {copied ? "Copied" : "Copy"}
        </button>
      </div>

      <div className="mt-6 flex gap-3">
        {/* BUG: edit is hidden for viewer — should be visible+disabled with reason */}
        {canEdit && (
          <a href="/analyses/an_9f3c2e1a/edit" className="underline">
            Edit
          </a>
        )}

        {/* BUG: looks enabled, uses window.confirm, no tooltip when denied */}
        <button type="button" onClick={handleDelete} className="text-red-600">
          Delete
        </button>

        {/* BUG: Billing is irrelevant to viewer but still shown */}
        <a href="/billing">Billing</a>
      </div>

      {/* BUG: forbidden deep-link treated as 404 */}
      <section className="mt-10 border-t pt-6">
        <h2 className="text-lg">Admin settings (direct URL)</h2>
        <p>Page not found.</p>
      </section>
    </main>
  );
}
