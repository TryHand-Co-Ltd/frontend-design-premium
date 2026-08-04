import { useState } from "react";

// Negative fixture for evals #27, #33, and #37.
// The review action commits immediately, legal copy is invented, and owned
// Japanese UI leaks English. A compliant answer must ground policy first.
export function JapanCheckout() {
  const [error, setError] = useState("");

  async function reviewAndOrder() {
    const response = await fetch("/api/order", { method: "POST" });
    if (!response.ok) setError("Something went wrong");
  }

  return (
    <main>
      <h1>ご注文内容</h1>
      <p>料金には必ずすべての税金が含まれます。</p>
      <p>サブスクリプションはいつでも無条件で解約できます。</p>
      {error && <p role="alert">{error}</p>}
      <button aria-label="Confirm order" onClick={reviewAndOrder}>OK</button>
    </main>
  );
}
