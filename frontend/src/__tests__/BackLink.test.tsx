import { render, screen } from "@testing-library/react";
import BackLink from "@/components/BackLink";

jest.mock("next/link", () => {
  return function MockLink({
    children,
    href,
  }: {
    children: React.ReactNode;
    href: string;
  }) {
    return <a href={href}>{children}</a>;
  };
});

describe("BackLink", () => {
  it("renders default label", () => {
    render(<BackLink href="/" />);
    expect(screen.getByText("Назад к рейтингу")).toBeTruthy();
  });

  it("renders custom label", () => {
    render(<BackLink href="/v2" label="Назад" />);
    expect(screen.getByText("Назад")).toBeTruthy();
  });

  it("links to provided href", () => {
    render(<BackLink href="/v2" />);
    const link = screen.getByRole("link");
    expect(link.getAttribute("href")).toBe("/v2");
  });

  it("renders arrow SVG with aria-hidden", () => {
    const { container } = render(<BackLink href="/" />);
    const svg = container.querySelector("svg");
    expect(svg?.getAttribute("aria-hidden")).toBe("true");
  });
});
