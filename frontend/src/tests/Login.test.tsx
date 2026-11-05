import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Login from "@/pages/Login";
import { queryClient } from "@/lib/queryClient";

const loginMock = vi.hoisted(() => ({ mutate: vi.fn() }));

vi.mock("@/hooks/useAuth", () => ({
  useLogin: () => ({ mutate: loginMock.mutate, isPending: false, isError: false }),
  extractErrorMessage: () => "Error de autenticación",
}));

function renderLogin() {
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter><Login /></MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("Login", () => {
  beforeEach(() => loginMock.mutate.mockClear());

  it("muestra un error accesible para un email inválido", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.type(screen.getByLabelText(/correo corporativo/i), "no-valido");
    await user.click(screen.getByRole("button", { name: /acceder/i }));
    expect(await screen.findByText(/correo electrónico inválido/i)).toBeInTheDocument();
    expect(loginMock.mutate).not.toHaveBeenCalled();
  });

  it("valida campos vacíos", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.click(screen.getByRole("button", { name: /acceder/i }));
    expect(await screen.findByText(/correo electrónico requerido/i)).toBeInTheDocument();
    expect(screen.getByText(/contraseña requerida/i)).toBeInTheDocument();
  });

  it("envía un formulario válido al hook de login", async () => {
    const user = userEvent.setup();
    renderLogin();
    await user.type(screen.getByLabelText(/correo corporativo/i), "admin@example.com");
    await user.type(screen.getByLabelText(/contraseña/i), "password-seguro");
    await user.click(screen.getByRole("button", { name: /acceder/i }));
    expect(loginMock.mutate).toHaveBeenCalledWith({
      email: "admin@example.com",
      password: "password-seguro",
    });
  });
});
