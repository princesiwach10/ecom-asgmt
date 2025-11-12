import {
  useCartQuery,
  useCheckoutMutation,
  useRemoveCartItemMutation,
  useSetCartItemMutation,
} from "../app/api";
import { useState } from "react";

export default function Cart() {
  const { data: cart, refetch } = useCartQuery();

  const [setQty] = useSetCartItemMutation();

  const [removeItem] = useRemoveCartItemMutation();

  const [checkout, { isLoading }] = useCheckoutMutation();

  const [code, setCode] = useState("");

  if (!cart)
    return <div className="bg-white shadow rounded-xl p-4">Loading cart…</div>;

  const onSet = (pid, q) => setQty({ product_id: pid, quantity: q });
  const onRemove = (pid) => removeItem(pid);

  return (
    <div className="bg-white shadow rounded-xl p-4 sticky top-4">
      <h2 className="font-semibold mb-3">Cart</h2>
      {cart.items.length === 0 ? (
        <div className="text-gray-500">Your cart is empty.</div>
      ) : (
        <>
          <ul className="divide-y mb-3">
            {cart.items.map((it) => (
              <li
                key={it.product_id}
                className="flex items-center justify-between py-2"
              >
                <div>Product #{it.product_id}</div>
                <div className="flex items-center gap-2">
                  <input
                    type="number"
                    min={0}
                    className="border rounded px-2 py-1 w-20"
                    defaultValue={it.quantity}
                    onBlur={(e) => onSet(it.product_id, Number(e.target.value))}
                  />
                  <button
                    className="text-sm text-red-600"
                    onClick={() => onRemove(it.product_id)}
                  >
                    Remove
                  </button>
                </div>
              </li>
            ))}
          </ul>

          <div className="flex items-center justify-between mb-3">
            <div className="text-sm text-gray-600">Total</div>
            <div className="font-semibold">₹ {cart.total}</div>
          </div>

          <div className="flex gap-2 mb-3">
            <input
              className="border rounded px-2 py-1 flex-1"
              placeholder="Discount code (optional)"
              value={code}
              onChange={(e) => setCode(e.target.value)}
            />
            <button
              className="px-3 py-2 rounded bg-black text-white disabled:opacity-50"
              disabled={isLoading}
              onClick={async () => {
                await checkout({ discount_code: code || undefined });
                refetch();
                setCode("");
              }}
            >
              Checkout
            </button>
          </div>
          <p className="text-xs text-gray-500">Set quantity to 0 to remove.</p>
        </>
      )}
    </div>
  );
}
