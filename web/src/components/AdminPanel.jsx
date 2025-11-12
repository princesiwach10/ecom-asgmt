import { useAdminStatsQuery, useAdminGenerateMutation } from "../app/api";
import { useState } from "react";

export default function AdminPanel() {
  const { data: stats, refetch, isFetching, isError } = useAdminStatsQuery();

  const [generate, { isLoading }] = useAdminGenerateMutation();

  const [msg, setMsg] = useState(null);

  return (
    <div className="grid md:grid-cols-2 gap-6">
      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="font-semibold mb-3">Generate Discount</h2>
        <button
          className="px-3 py-2 rounded bg-black text-white disabled:opacity-50"
          onClick={async () => {
            setMsg(null);
            try {
              const r = await generate().unwrap();
              setMsg(`Code: ${r.code} (${r.discount_pct}%) @ ${r.created_at}`);
            } catch (err) {
              setMsg(err?.data?.detail ?? "Not eligible or active code exists");
            }
            refetch();
          }}
          disabled={isLoading}
        >
          Generate Code
        </button>
        {msg && <p className="mt-2 text-sm">{msg}</p>}
        <p className="text-xs text-gray-500 mt-2">
          Requires correct X-Admin-Key.
        </p>
      </div>

      <div className="bg-white shadow rounded-xl p-4">
        <h2 className="font-semibold mb-3">Stats</h2>
        {isFetching ? (
          <div>Loading…</div>
        ) : isError ? (
          <div className="text-red-600">Failed to load stats.</div>
        ) : stats ? (
          <div className="space-y-2 text-sm">
            <div>
              Items purchased: <b>{stats.items_purchased}</b>
            </div>
            <div>
              Gross amount: <b>₹ {stats.gross_amount}</b>
            </div>
            <div>
              Total discount: <b>₹ {stats.total_discount_amount}</b>
            </div>
            <div>
              Net amount: <b>₹ {stats.net_amount}</b>
            </div>
            <div className="pt-2">
              <div className="font-medium">Discount Codes</div>
              <ul className="list-disc pl-5">
                {stats.discount_codes.map((c) => (
                  <li key={c.code}>
                    <code>{c.code}</code> — {c.discount_pct}% —{" "}
                    {c.used ? "USED" : "ACTIVE"} — {c.created_at}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
