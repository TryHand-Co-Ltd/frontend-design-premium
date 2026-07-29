import React, { useState } from "react";

// BUG: ComboBox without accessible keyboard/aria support
// BUG: Date fields without locale
// BUG: Upload without validation/progress/retry
// BUG: Stepper without per-step validation
// BUG: No draft save

const companies = ["株式会社A", "有限会社B", "合同会社C"];

export default function OnboardingWizard() {
  const [step, setStep] = useState(1);
  const [company, setCompany] = useState("");
  const [image, setImage] = useState<File | null>(null);
  const [estDate, setEstDate] = useState("");

  // BUG: Non-accessible combobox — no aria, no keyboard
  return (
    <div className="p-6">
      <h1>会社登録</h1>

      {/* Step 1: 会社情報 */}
      {step === 1 && (
        <div>
          {/* BUG: Combobox as plain input */}
          <label>
            会社名
            <input
              list="companies"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
            />
            <datalist id="companies">
              {companies.map((c) => (
                <option key={c} value={c} />
              ))}
            </datalist>
          </label>

          {/* BUG: Date without locale */}
          <label>
            設立日
            <input type="date" value={estDate}
              onChange={(e) => setEstDate(e.target.value)} />
          </label>

          {/* BUG: Upload without validation */}
          <label>
            ロゴ
            <input type="file" accept="image/*"
              onChange={(e) => setImage(e.target.files?.[0] ?? null)} />
          </label>
        </div>
      )}

      {/* Step 2: 確認 (not implemented — BUG) */}
      {step === 2 && <div>確認画面</div>}

      {/* BUG: Steps can advance without validation */}
      <div className="mt-6 flex gap-2">
        <button onClick={() => setStep(Math.max(1, step - 1))}
          disabled={step === 1}>
          戻る
        </button>
        <button onClick={() => setStep(Math.min(3, step + 1))}>
          {step === 3 ? "完了" : "次へ"}
        </button>
      </div>
    </div>
  );
}
