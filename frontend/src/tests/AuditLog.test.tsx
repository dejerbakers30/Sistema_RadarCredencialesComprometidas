import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import AuditLog from "@/pages/AuditLog";

const refetch = vi.fn();

vi.mock("@/hooks/useAudit", () => ({
  useAudit: () => ({
    data: [{ id: 1, ts: "2026-01-01T10:00:00Z", tz: "UTC", usuario_email: "admin@example.com", modulo: "auth", accion: "login", entidad: "user", entidad_id: "1", resultado: "ok", detalle: null, hash_actual: "abcdef1234567890" }],
    isLoading: false,
    isError: false,
  }),
  useVerifyChain: () => ({ data: { total: 1, broken: [], ok: true }, isFetching: false, refetch }),
}));

describe("AuditLog", () => {
  it("muestra integridad y permite verificar la cadena", () => {
    render(<MemoryRouter><AuditLog /></MemoryRouter>);
    expect(screen.getByText("Cadena íntegra")).toBeInTheDocument();
    expect(screen.getByText("admin@example.com")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /verificar integridad/i }));
    expect(refetch).toHaveBeenCalled();
  });
});
