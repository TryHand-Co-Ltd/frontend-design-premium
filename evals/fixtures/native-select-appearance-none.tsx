export function AccountTypeSelect() {
  return (
    <select className="appearance-none w-full rounded-xl border-2 border-indigo-600">
      <option value="individual">個人</option>
      <option value="corporate">法人</option>
    </select>
  );
}
