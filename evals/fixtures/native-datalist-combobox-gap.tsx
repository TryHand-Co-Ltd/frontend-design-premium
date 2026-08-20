export function CustomerAutocomplete() {
  return (
    <label>
      顧客名
      <input list="customers" className="w-full rounded-xl border-2" />
      <datalist id="customers">
        <option value="株式会社青空" />
        <option value="みらい商事株式会社" />
      </datalist>
    </label>
  );
}
