import { render, screen } from "@testing-library/react";
import VerificationBadge from "@/components/VerificationBadge";

describe("VerificationBadge", () => {
  it("renders badge with display text", () => {
    render(<VerificationBadge status="catalog" display="Данные по каталогу" />);
    expect(screen.getByText("Данные по каталогу")).toBeTruthy();
  });

  it("applies catalog styles by default", () => {
    const { container } = render(
      <VerificationBadge status="catalog" display="Каталог" />,
    );
    const badge = container.querySelector("span");
    expect(badge?.className).toContain("bg-gray-100");
  });

  it("applies editorial styles", () => {
    const { container } = render(
      <VerificationBadge status="editorial" display="Проверено" />,
    );
    const badge = container.querySelector("span");
    expect(badge?.className).toContain("bg-blue-100");
  });

  it("applies lab styles", () => {
    const { container } = render(
      <VerificationBadge status="lab" display="Лаборатория" />,
    );
    const badge = container.querySelector("span");
    expect(badge?.className).toContain("bg-green-100");
  });

  it("falls back to catalog style for unknown status", () => {
    const { container } = render(
      <VerificationBadge status="unknown" display="Неизвестно" />,
    );
    const badge = container.querySelector("span");
    expect(badge?.className).toContain("bg-gray-100");
  });
});
