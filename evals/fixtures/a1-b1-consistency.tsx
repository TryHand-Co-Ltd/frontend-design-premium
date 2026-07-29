// Two sibling flows: A1 (existing) creates and returns to list A with a toast.
// B1 (new) must match this pattern exactly — but currently returns to nowhere with no feedback.
// Expected: B1 create returns to list B with success toast.

"use client";
import React, { useState } from "react";

// === Flow A1 (existing, canonical) ===
// Save → returns to list A + toast "Created successfully"

interface ItemA {
  id: string;
  name: string;
}

const initialA: ItemA[] = [
  { id: "1", name: "API Key Production" },
  { id: "2", name: "API Key Staging" },
];

function ListA() {
  const [items, setItems] = useState(initialA);
  return (
    <div>
      <h1>List A</h1>
      {items.map((i) => (
        <div key={i.id}>{i.name}</div>
      ))}
    </div>
  );
}

export function CreateAForm({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("");

  const handleSave = async () => {
    // Canonical: saves to API, returns to list, shows toast
    await fetch("/api/items-a", {
      method: "POST",
      body: JSON.stringify({ name }),
    });
    // Correct behavior: return to list A + toast
    onClose();
    // toast("Created successfully");
  };

  return (
    <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
      <label>
        Name
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <button type="submit">Save</button>
      <button type="button" onClick={onClose}>Cancel</button>
    </form>
  );
}

// === Flow B1 (new, must match A1's pattern) ===
// CURRENT BUG: Save closes form but does NOT return to list B
// CURRENT BUG: No success toast
// CURRENT BUG: No noValidate
// CURRENT BUG: Password field without show/hide

interface ItemB {
  id: string;
  name: string;
  password: string;
  notes: string;
}

export function CreateBForm({ onClose }: { onClose: () => void }) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [notes, setNotes] = useState("");

  const handleSave = async () => {
    await fetch("/api/items-b", {
      method: "POST",
      body: JSON.stringify({ name, password, notes }),
    });
    // BUG: Does not return to list B — closes without navigating
    // BUG: No success toast
    onClose();
  };

  return (
    // BUG: no noValidate
    <form onSubmit={(e) => { e.preventDefault(); handleSave(); }}>
      <label>
        Name
        <input value={name} onChange={(e) => setName(e.target.value)} required />
      </label>
      <label>
        Password
        {/* BUG: No show/hide toggle */}
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      <label>
        Notes
        {/* BUG: textarea without resize: none */}
        <textarea value={notes} onChange={(e) => setNotes(e.target.value)} />
      </label>
      <button type="submit">Save</button>
      <button type="button" onClick={onClose}>Cancel</button>
    </form>
  );
}
