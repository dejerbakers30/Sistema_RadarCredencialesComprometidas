import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import Training from "@/pages/Training";
import { api } from "@/lib/api";

const access = vi.hoisted(() => ({ admin: true }));
vi.mock("@/hooks/useCan", () => ({ useCan: () => access.admin }));
vi.mock("@/lib/api", () => ({ api: { get: vi.fn(), post: vi.fn() }, extractErrorMessage: () => "Error de conexión" }));
const overview = { models: [], features: [], labels: ["Bajo", "Medio", "Crítico"], datasets: [], runs: [],
  active: { mode: "heuristic_fallback", run_id: null }, task: "Debilidad", research_status: "Pendiente" };
function renderLab() { return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}><Training /></QueryClientProvider>); }

describe("Laboratorio IA", () => {
  beforeEach(() => { access.admin = true; vi.mocked(api.get).mockResolvedValue({ data: overview }); });
  afterEach(() => { cleanup(); vi.clearAllMocks(); });
  it("explica el alcance y no inventa métricas sin ejecuciones", async () => {
    renderLab();
    expect(await screen.findByText("La evidencia empieza aquí")).toBeInTheDocument();
    expect(screen.getByText(/una contraseña fuerte no descarta una filtración/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Comparación" }));
    expect(screen.getByText("Aún no hay una comparación final")).toBeInTheDocument();
    expect(screen.queryByText("Seleccionado")).not.toBeInTheDocument();
  });
  it("mantiene importación y entrenamiento deshabilitados para lectores", async () => {
    access.admin = false; renderLab();
    expect(await screen.findByRole("button", { name: "Validar e importar" })).toBeDisabled();
    expect(screen.getByText(/Modo consulta/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: "Modelos y particiones" }));
    expect(screen.getByRole("button", { name: "Entrenar los tres modelos" })).toBeDisabled();
  });
  it("permite reintentar una conexión fallida", async () => {
    vi.mocked(api.get).mockRejectedValueOnce(new Error("offline"));
    renderLab();
    expect(await screen.findByRole("alert")).toHaveTextContent("No se pudo cargar el laboratorio");
    await userEvent.click(screen.getByRole("button", { name: "Reintentar" }));
    expect(await screen.findByText("La evidencia empieza aquí")).toBeInTheDocument();
    await waitFor(() => expect(api.get).toHaveBeenCalledTimes(2));
  });
});
