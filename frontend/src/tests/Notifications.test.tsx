import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import Notifications from "@/pages/Notifications";

vi.mock("@tanstack/react-query", () => ({
  useQuery: () => ({
    data: { items: [{ id: "1", destinatario: "user@example.com", canal: "email", plantilla: "Alerta de seguridad", enviado_en: "2026-01-01T10:00:00Z", estado: "enviado", error_detalle: null }], total: 1, limit: 20, offset: 0 },
    isLoading: false,
    isError: false,
  }),
}));

describe("Notifications", () => {
  it("presenta el estado de una notificación real", () => {
    render(<MemoryRouter><Notifications /></MemoryRouter>);
    expect(screen.getByText("Alerta de seguridad")).toBeInTheDocument();
    expect(screen.getByText("Enviado")).toBeInTheDocument();
    expect(screen.getByText(/user@example.com/)).toBeInTheDocument();
  });
});
