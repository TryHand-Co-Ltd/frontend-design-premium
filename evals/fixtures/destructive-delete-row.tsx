// BUG: No confirmation dialog for destructive action
// BUG: No loading state on async operation
// BUG: No error recovery (error disappears on dialog close)
// BUG: No danger/destructive visual styling

import React, { useState } from "react";

interface User {
  id: string;
  name: string;
  email: string;
}

const USERS: User[] = [
  { id: "1", name: "田中太郎", email: "tanaka@example.com" },
  { id: "2", name: "山田花子", email: "yamada@example.com" },
  { id: "3", name: "佐藤次郎", email: "sato@example.com" },
];

export default function UserListPage() {
  const [users] = useState(USERS);

  // BUG: Direct delete without confirmation
  const handleDelete = async (userId: string) => {
    try {
      const res = await fetch(`/api/users/${userId}`, { method: "DELETE" });
      if (!res.ok) throw new Error("Delete failed");
      // BUG: No toast on success
    } catch (err) {
      // BUG: alert instead of in-page error
      alert("削除に失敗しました: " + (err as Error).message);
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-xl font-medium">ユーザー管理</h1>
      <table className="mt-4 w-full">
        <thead>
          <tr>
            <th>名前</th>
            <th>メール</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id} className="border-t">
              <td className="px-4 py-2">{user.name}</td>
              <td className="px-4 py-2">{user.email}</td>
              <td className="px-4 py-2">
                {/* BUG: No confirmation dialog, no danger styling */}
                <button
                  onClick={() => handleDelete(user.id)}
                  type="button"
                  className="rounded bg-gray-200 px-3 py-1 text-sm"
                >
                  削除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
