import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

export const api = createApi({
  reducerPath: "api",
  baseQuery: fetchBaseQuery({
    baseUrl: import.meta.env.VITE_API_BASE,
    prepareHeaders: (headers, { getState }) => {
      const s = getState();
      const userId = s.settings.userId;
      const adminKey = s.settings.adminKey;
      headers.set("Content-Type", "application/json");
      if (userId) headers.set("X-User-Id", userId);
      if (adminKey) headers.set("X-Admin-Key", adminKey);
      return headers;
    },
  }),
  tagTypes: ["Cart", "Products", "Stats"],
  endpoints: (build) => ({
    addCart: build.mutation({
      query: (body) => ({ url: "cart/items/", method: "POST", body }),
      invalidatesTags: ["Cart"],
    }),
    adminGenerate: build.mutation({
      query: () => ({ url: "admin/generate-discount/", method: "POST" }),
      invalidatesTags: ["Stats"],
    }),
    adminStats: build.query({
      query: () => "admin/stats/",
      providesTags: ["Stats"],
    }),
    cart: build.query({
      query: () => "cart/",
      providesTags: ["Cart"],
    }),
    checkout: build.mutation({
      query: (body) => ({ url: "checkout/", method: "POST", body }),
      invalidatesTags: ["Cart", "Stats"],
    }),
    products: build.query({
      query: () => "products/",
      providesTags: ["Products"],
    }),
    removeCartItem: build.mutation({
      query: (product_id) => ({
        url: `cart/items/${product_id}/`,
        method: "DELETE",
      }),
      invalidatesTags: ["Cart"],
    }),
    setCartItem: build.mutation({
      query: ({ product_id, quantity }) => ({
        url: `cart/items/${product_id}/`,
        method: "PUT",
        body: { quantity },
      }),
      invalidatesTags: ["Cart"],
    }),
  }),
});

export const {
  useAddCartMutation,
  useAdminGenerateMutation,
  useAdminStatsQuery,
  useCartQuery,
  useCheckoutMutation,
  useProductsQuery,
  useRemoveCartItemMutation,
  useSetCartItemMutation,
} = api;
