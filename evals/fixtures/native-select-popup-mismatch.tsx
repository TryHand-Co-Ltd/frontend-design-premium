export function AccountTypeField() {
  return (
    <label className="grid gap-2">
      <span>顧客区分</span>
      <select className="h-12 w-full rounded-xl border-2 border-indigo-600 px-4">
        <option value="individual">個人</option>
        <option value="corporate">法人</option>
      </select>
    </label>
  );
}
