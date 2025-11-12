import { useProductsQuery, useAddCartMutation } from "../app/api";
import { useState } from "react";

export default function ProductList() {
  const { data, isLoading, isError } = useProductsQuery();

  const [addCart, { isLoading: saving }] = useAddCartMutation();

  const [qty, setQty] = useState({});

  if (isLoading) return <div>Loading products…</div>;

  if (isError || !data)
    return <div className="text-red-600">Failed to load products.</div>;

  return (
    <div className="bg-white shadow rounded-xl p-4">
      <h2 className="font-semibold mb-3">Products</h2>
      <ul className="divide-y">
        {data.map((p) => (
          <li key={p.id} className="flex items-center justify-between py-3">
            <div>
              <div className="font-medium">{p.name}</div>
              <div className="text-sm text-gray-600">₹ {p.price}</div>
            </div>
            <div className="flex items-center gap-2">
              <input
                type="number"
                min={1}
                className="border rounded px-2 py-1 w-20"
                value={qty[p.id] ?? 1}
                onChange={(e) =>
                  setQty((s) => ({ ...s, [p.id]: Number(e.target.value) }))
                }
              />
              <button
                className="px-3 py-1 rounded bg-black text-white disabled:opacity-50"
                disabled={saving}
                onClick={() =>
                  addCart({ product_id: p.id, quantity: qty[p.id] ?? 1 })
                }
              >
                Add
              </button>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
