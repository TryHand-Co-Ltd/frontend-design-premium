import React, { useState } from "react";

// BUG: 14-column table, no horizontal scroll
// BUG: Bulk revoke without confirmation
// BUG: Expandable details not accessible
// BUG: Long IDs truncated with no tooltip/full-text display
// BUG: No mobile responsive behavior

const COLUMNS = [
  "ID", "ユーザー", "操作", "リソース", "IPアドレス",
  "日時", "ステータス", "詳細", "カテゴリ", "環境",
  "セッションID", "リクエストID", "オリジン", "結果",
];

const DATA = Array.from({ length: 50 }, (_, i) => ({
  id: `aud_${String(i).padStart(6, "0")}_${crypto.randomUUID?.().slice(0, 8) ?? "xxxx"}`,
  user: `user-${i}@example.com`,
  action: "delete",
  resource: `/api/keys/${i}`,
  ip: `192.168.${Math.floor(i / 10)}.${i % 10}`,
  date: new Date(Date.now() - i * 86400000).toISOString(),
  status: i % 3 === 0 ? "success" : i % 3 === 1 ? "failure" : "pending",
  detail: "API key revoked",
  category: "key_management",
  env: "production",
  sessionId: `sess_${crypto.randomUUID?.().slice(0, 8) ?? "yyyy"}`,
  requestId: `req_${crypto.randomUUID?.().slice(0, 8) ?? "zzzz"}`,
  origin: "dashboard",
  result: "ok",
}));

export default function AuditRecordsPage() {
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [expanded, setExpanded] = useState<string | null>(null);

  const toggleSelect = (id: string) => {
    const next = new Set(selected);
    if (next.has(id)) next.delete(id); else next.add(id);
    setSelected(next);
  };

  // BUG: No confirmation for bulk revoke
  const handleBulkRevoke = () => {
    fetch("/api/audit/revoke", {
      method: "POST",
      body: JSON.stringify({ ids: [...selected] }),
    });
  };

  return (
    <div className="p-4">
      <h1 className="text-xl font-medium">監査記録</h1>

      {/* BUG: Breadcrumbs hardcoded, not from shared component */}
      <nav className="my-2 text-sm text-gray-500">
        <span>ホーム</span> &gt; <span>管理</span> &gt; <span>監査</span>
      </nav>

      {selected.size > 0 && (
        // BUG: No danger styling, no confirmation dialog
        <button onClick={handleBulkRevoke}
          className="mb-2 rounded bg-red-500 px-3 py-1 text-white">
          {selected.size}件を取り消し
        </button>
      )}

      {/* BUG: No horizontal scroll wrapper — columns overflow */}
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs">
          <thead>
            <tr>
              <th><input type="checkbox" /></th>
              {COLUMNS.map((col) => (
                <th key={col} className="whitespace-nowrap px-2 py-1 text-left">{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {DATA.slice(0, 20).map((row) => (
              <tr key={row.id} className="border-t">
                <td>
                  <input type="checkbox"
                    checked={selected.has(row.id)}
                    onChange={() => toggleSelect(row.id)} />
                </td>
                <td className="px-2 py-1">
                  {/* BUG: Truncated ID with no full-text display */}
                  <code className="text-[10px]">{row.id.slice(0, 16)}...</code>
                </td>
                <td className="px-2 py-1">{row.user}</td>
                <td className="px-2 py-1">{row.action}</td>
                <td className="px-2 py-1">{row.resource}</td>
                <td className="px-2 py-1">{row.ip}</td>
                <td className="px-2 py-1">{row.date}</td>
                <td className="px-2 py-1">{row.status}</td>
                <td className="px-2 py-1">
                  {/* BUG: Expandable not keyboard accessible */}
                  <button onClick={() =>
                    setExpanded(expanded === row.id ? null : row.id)
                  } type="button">
                    {expanded === row.id ? "▲" : "▼"}
                  </button>
                  {expanded === row.id && (
                    <div className="mt-1 text-xs">{row.detail}</div>
                  )}
                </td>
                <td className="px-2 py-1">{row.category}</td>
                <td className="px-2 py-1">{row.env}</td>
                <td className="px-2 py-1">{row.sessionId}</td>
                <td className="px-2 py-1">{row.requestId}</td>
                <td className="px-2 py-1">{row.origin}</td>
                <td className="px-2 py-1">{row.result}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
