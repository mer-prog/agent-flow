import { useCallback, useEffect, useState } from "react";
import { apiFetch, clearTokens, setTokens } from "../api/client";
import type { User, TokenResponse } from "../types";

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchUser = useCallback(async () => {
    try {
      const u = await apiFetch<User>("/auth/me");
      setUser(u);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, [fetchUser]);

  const login = async (email: string, password: string) => {
    const res = await apiFetch<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    setTokens(res.access_token, res.refresh_token);
    await fetchUser();
  };

  const register = async (email: string, password: string, fullName: string) => {
    await apiFetch("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password, full_name: fullName }),
    });
    await login(email, password);
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return { user, loading, login, register, logout };
}
