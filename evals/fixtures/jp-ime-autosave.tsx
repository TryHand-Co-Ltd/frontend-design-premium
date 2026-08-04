import { useEffect, useState } from "react";

// Negative fixture for evals #28 and #32.
// It deliberately lets incomplete IME text trigger autosave, shortcuts,
// validation, counters, and remote suggestions. A correct result must replace
// the shared input behavior, not add an "IME safe" comment.
export function JapaneseProfileEditor() {
  const [company, setCompany] = useState("");
  const [suggestions, setSuggestions] = useState<string[]>([]);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void fetch("/api/profile", {
        method: "PUT",
        body: JSON.stringify({ company }),
      });
      void fetch(`/api/companies?q=${encodeURIComponent(company)}`)
        .then((response) => response.json())
        .then(setSuggestions);
    }, 100);
    return () => window.clearTimeout(timer);
  }, [company]);

  return (
    <form onSubmit={() => void fetch("/api/profile/submit", { method: "POST" })}>
      <label htmlFor="company">会社名</label>
      <input
        id="company"
        value={company}
        maxLength={30}
        onChange={(event) => setCompany(event.target.value)}
        onKeyDown={(event) => {
          if (event.key === "Enter") event.currentTarget.form?.requestSubmit();
          if (event.ctrlKey && event.key.toLowerCase() === "k") alert("command");
        }}
      />
      <output>{company.length}/30</output>
      <ul>{suggestions.map((item) => <li key={item}>{item}</li>)}</ul>
    </form>
  );
}
