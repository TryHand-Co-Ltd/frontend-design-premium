export function WideOrderTable() {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-[200rem]">
        <thead>
          <tr>
            <th>注文番号</th>
            <th>注文ステータス</th>
            <th>顧客名</th>
          </tr>
        </thead>
      </table>
    </div>
  );
}
