const BASE = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api";
export async function request(path, options = {}, token = null) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 15000);
  try {
    const response = await fetch(`${BASE}${path}`, {
      ...options,
      credentials: "omit",
      signal: controller.signal,
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
        ...options.headers,
      },
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      const error = new Error(
        typeof data.detail === "string"
          ? data.detail
          : "Permintaan gagal. Periksa input dan coba lagi.",
      );
      error.status = response.status;
      error.fields = data.errors || [];
      throw error;
    }
    return data;
  } catch (error) {
    if (error.name === "AbortError")
      throw new Error("Koneksi terlalu lama. Silakan coba lagi.");
    if (error instanceof TypeError)
      throw new Error(
        "Tidak dapat terhubung ke TechnoPark. Periksa koneksi dan coba lagi.",
      );
    throw error;
  } finally {
    clearTimeout(timer);
  }
}
