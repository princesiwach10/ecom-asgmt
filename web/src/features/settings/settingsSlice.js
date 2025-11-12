import { createSlice } from "@reduxjs/toolkit";

const initial = {
  userId: localStorage.getItem("userId") || "u1",
  adminKey: localStorage.getItem("adminKey") || "",
};

const slice = createSlice({
  name: "settings",
  initialState: initial,
  reducers: {
    setUserId(state, action) {
      state.userId = action.payload;
      localStorage.setItem("userId", state.userId);
    },
    setAdminKey(state, action) {
      state.adminKey = action.payload;
      localStorage.setItem("adminKey", state.adminKey);
    },
  },
});

export const { setUserId, setAdminKey } = slice.actions;
export default slice.reducer;
