/**
 * Fixture for eval #24 — layer-contract.
 * Intentionally broken overlay stacking: magic z-index, toast under dialog,
 * missing focus trap / escape / restore, and drawer opening a dialog incorrectly.
 */
import React, { useState } from "react";

export default function OverlayChaosPage() {
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [dialogOpen, setDialogOpen] = useState(true);
  const [toastVisible] = useState(true);

  return (
    <main className="relative min-h-screen p-6">
      <h1 className="text-xl font-medium">Job detail</h1>
      <button type="button" onClick={() => setDrawerOpen(true)}>
        Open details
      </button>

      {/* BUG: arbitrary z-index; no focus trap; backdrop click not defined */}
      {drawerOpen && (
        <aside
          className="fixed right-0 top-0 h-full w-96 bg-white p-4 shadow-xl"
          style={{ zIndex: 9999 }}
        >
          <h2>Details drawer</h2>
          <button type="button" onClick={() => setDialogOpen(true)}>
            Confirm revoke
          </button>
          <button type="button" onClick={() => setDrawerOpen(false)}>
            Close
          </button>
        </aside>
      )}

      {/* BUG: dialog below drawer (z-index 50); no aria-modal / focus restore */}
      {dialogOpen && (
        <>
          <div
            className="fixed inset-0 bg-black/40"
            style={{ zIndex: 40 }}
            onClick={() => setDialogOpen(false)}
          />
          <div
            className="fixed left-1/2 top-1/2 w-96 -translate-x-1/2 -translate-y-1/2 rounded bg-white p-6"
            style={{ zIndex: 50 }}
            role="dialog"
          >
            <h2>Revoke access?</h2>
            <p>This cannot be undone.</p>
            <div className="mt-4 flex justify-end gap-2">
              <button type="button" onClick={() => setDialogOpen(false)}>
                Cancel
              </button>
              <button type="button">Revoke</button>
            </div>
          </div>
        </>
      )}

      {/* BUG: toast under dialog/drawer; no live region */}
      {toastVisible && (
        <div
          className="fixed bottom-4 right-4 rounded bg-neutral-900 px-4 py-2 text-white"
          style={{ zIndex: 30 }}
        >
          Saved
        </div>
      )}
    </main>
  );
}
