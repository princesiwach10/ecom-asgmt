import { api } from "./api";
import { configureStore } from "@reduxjs/toolkit";
import settingsReducer from "../features/settings/settingsSlice";

export const store = configureStore({
  reducer: {
    [api.reducerPath]: api.reducer,
    settings: settingsReducer,
  },
  middleware: (gDM) => gDM().concat(api.middleware),
});
