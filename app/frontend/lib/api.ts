import axios from "axios";

export const apiClient = (password: string | null) => {
  return axios.create({
    baseURL: process.env.NEXT_PUBLIC_BACKEND_URL || "http://localhost:8000/api",
    headers: password ? { "x-admin-password": password } : {}
  });
};
