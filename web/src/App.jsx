import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import AdminPanel from "./components/AdminPanel";
import Cart from "./components/Cart";
import ProductList from "./components/ProductList";
import SettingsBar from "./components/SettingsBar";

export default function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50 text-gray-900">
        <header className="border-b bg-white">
          <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
            <Link to="/" className="font-bold text-lg">
              E-Commerce Assignment
            </Link>
            <nav className="flex gap-4">
              <NavLink
                to="/"
                end
                className={({ isActive }) => (isActive ? "font-semibold" : "")}
              >
                Shop
              </NavLink>
              <NavLink
                to="/admin"
                className={({ isActive }) => (isActive ? "font-semibold" : "")}
              >
                Admin
              </NavLink>
            </nav>
          </div>
        </header>

        <SettingsBar />

        <main className="max-w-5xl mx-auto px-4 py-6">
          <Routes>
            <Route
              path="/"
              element={
                <div className="grid md:grid-cols-3 gap-6">
                  <div className="md:col-span-2">
                    <ProductList />
                  </div>
                  <div className="md:col-span-1">
                    <Cart />
                  </div>
                </div>
              }
            />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
