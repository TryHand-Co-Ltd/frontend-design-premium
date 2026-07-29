export default function AdminApiKeysPage() {
  // BUG: No pagination — loads all records
  // BUG: window.confirm for delete
  // BUG: Search fires on every keystroke, no debounce
  // BUG: Clickable div rows without role/keyboard
  // BUG: Layout shifts when loading
  const [keys] = React.useState([
    { id: "sk-xxx1", name: "Production", status: "active" },
    { id: "sk-xxx2", name: "Staging", status: "active" },
    { id: "sk-xxx3", name: "Development", status: "revoked" },
  ]);
  const [search, setSearch] = React.useState("");
  const [results, setResults] = React.useState(keys);
  const [loading, setLoading] = React.useState(false);
  const [showForm, setShowForm] = React.useState(false);

  // BUG: No debounce, no AbortController, no IME guard
  React.useEffect(() => {
    if (!search) {
      setResults(keys);
      return;
    }
    setLoading(true);
    fetch(`/api/keys?q=${search}`)
      .then((r) => r.json())
      .then(setResults)
      .finally(() => setLoading(false));
  }, [search]);

  // BUG: window.confirm
  const handleDelete = (id: string) => {
    if (confirm("本当に削除しますか？")) {
      fetch(`/api/keys/${id}`, { method: "DELETE" });
    }
  };

  // BUG: Clickable div without role/tabIndex/keyboard
  return (
    <div className="p-4">
      <h1 className="text-xl font-medium">APIキー管理</h1>

      {/* BUG: Search without clear button */}
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="キーを検索..."
        className="w-full border p-2"
      />

      <button onClick={() => setShowForm(true)} className="mt-2 rounded bg-blue-500 px-4 py-2 text-white">
        + 新規作成
      </button>

      {loading && <div className="mt-4 h-8 bg-gray-200 animate-pulse" />}
      {/* BUG: No fixed height — pushes content below */}

      <table className="mt-4 w-full">
        <thead>
          <tr>
            <th>名前</th>
            <th>APIキー</th>
            <th>ステータス</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          {results.map((key) => (
            // BUG: Clickable div inside row
            <tr
              key={key.id}
              onClick={() => navigator.clipboard.writeText(key.id)}
              className="cursor-pointer"
            >
              <td>{key.name}</td>
              <td>
                {/* BUG: API key fully visible, no mask */}
                <code className="text-sm">{key.id}</code>
              </td>
              <td>{key.status}</td>
              <td>
                <button onClick={() => handleDelete(key.id)} type="button">
                  削除
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {showForm && <ApiKeyForm onClose={() => setShowForm(false)} />}
    </div>
  );
}

function ApiKeyForm({ onClose }: { onClose: () => void }) {
  const [name, setName] = React.useState("");
  const [keyValue, setKeyValue] = React.useState("");

  // BUG: No form validation, no noValidate
  // BUG: Japanese labels missing
  // BUG: No loading state on submit
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/50">
      <div className="rounded bg-white p-6">
        <h2 className="text-lg font-medium">APIキー作成</h2>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            fetch("/api/keys", {
              method: "POST",
              body: JSON.stringify({ name, key: keyValue }),
            });
            onClose();
          }}
        >
          <label>
            Name
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </label>
          {/* BUG: textarea without resize: none */}
          <label>
            Key
            <textarea value={keyValue} onChange={(e) => setKeyValue(e.target.value)} />
          </label>
          <div className="mt-4 flex gap-2">
            <button type="submit" className="rounded bg-blue-500 px-4 py-2 text-white">
              Create
            </button>
            <button type="button" onClick={onClose}>
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
