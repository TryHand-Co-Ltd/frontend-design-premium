// BUG: No form validation (no RHF/Zod, no Formik/Yup)
// BUG: No noValidate — browser native validation
// BUG: No common error banner for server errors
// BUG: No inline field errors
// BUG: No Japanese locale messages
// BUG: Submit button doesn't show loading state
// BUG: No password reveal toggle
// BUG: textarea without resize: none

import React, { useState } from "react";

export default function ProfileEditForm() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [bio, setBio] = useState("");

  // BUG: Plain fetch without form state management
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetch("/api/profile", {
      method: "PUT",
      body: JSON.stringify({ name, email, password, bio }),
    })
      .then((r) => r.json())
      .then((data) => {
        // BUG: No toast/success feedback
        console.log("Saved", data);
      })
      .catch((err) => {
        // BUG: No common error banner
        alert("Error: " + err.message);
      });
  };

  return (
    <div className="mx-auto max-w-lg p-6">
      <h1 className="text-xl font-medium">プロフィール編集</h1>

      {/* BUG: noValidate missing */}
      <form onSubmit={handleSubmit}>
        <div className="mt-4">
          <label className="block text-sm font-medium">名前</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            className="mt-1 w-full rounded border p-2"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium">メールアドレス</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 w-full rounded border p-2"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium">
            パスワード
          </label>
          {/* BUG: type="password" without show/hide button */}
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="mt-1 w-full rounded border p-2"
          />
        </div>

        <div className="mt-4">
          <label className="block text-sm font-medium">自己紹介</label>
          {/* BUG: no resize: none */}
          <textarea
            value={bio}
            onChange={(e) => setBio(e.target.value)}
            className="mt-1 w-full rounded border p-2"
            rows={4}
          />
        </div>

        {/* BUG: No loading state, no disabled during submit */}
        <button
          type="submit"
          className="mt-6 rounded bg-blue-500 px-4 py-2 text-white"
        >
          保存
        </button>
      </form>
    </div>
  );
}
