import { setUserId, setAdminKey } from "../features/settings/settingsSlice";
import { useDispatch, useSelector } from "react-redux";

export default function SettingsBar() {
  const { userId, adminKey } = useSelector((s) => s.settings);

  const dispatch = useDispatch();

  return (
    <div className="bg-gray-100 border-b">
      <div className="max-w-5xl mx-auto px-4 py-2 flex flex-col md:flex-row gap-2 md:items-center md:justify-between">
        <div className="text-sm">
          Headers: <code>X-User-Id</code>, <code>X-Admin-Key</code>
        </div>
        <div className="flex gap-2">
          <input
            className="border rounded px-2 py-1 text-sm w-40"
            value={userId}
            onChange={(e) => dispatch(setUserId(e.target.value))}
            placeholder="User Id (e.g. u1)"
          />
          <input
            className="border rounded px-2 py-1 text-sm w-60"
            value={adminKey}
            onChange={(e) => dispatch(setAdminKey(e.target.value))}
            placeholder="Admin Key"
          />
        </div>
      </div>
    </div>
  );
}
