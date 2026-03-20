import { render, screen } from "@testing-library/react";
import ParameterBar from "@/components/ParameterBar";
import { ParameterValue } from "@/lib/types";

const mockParam: ParameterValue = {
  id: 1,
  parameter_name: "Шум мин.",
  raw_value: "32",
  unit: "дБ(А)",
  score: 36.0,
};

describe("ParameterBar", () => {
  it("renders parameter name", () => {
    render(<ParameterBar parameter={mockParam} maxScore={70} />);
    expect(screen.getByText("Шум мин.")).toBeTruthy();
  });

  it("renders raw value with unit", () => {
    render(<ParameterBar parameter={mockParam} maxScore={70} />);
    expect(screen.getByText("32 дБ(А)")).toBeTruthy();
  });

  it("renders score", () => {
    render(<ParameterBar parameter={mockParam} maxScore={70} />);
    expect(screen.getByText("36.0")).toBeTruthy();
  });

  it("renders progressbar with ARIA attributes", () => {
    render(<ParameterBar parameter={mockParam} maxScore={72} />);
    const bar = screen.getByRole("progressbar");
    expect(bar).toBeTruthy();
    expect(bar.getAttribute("aria-valuenow")).toBe("36");
    expect(bar.getAttribute("aria-valuemax")).toBe("72");
  });

  it("renders progress bar with correct width", () => {
    const { container } = render(
      <ParameterBar parameter={mockParam} maxScore={72} />
    );
    const bar = container.querySelector("[style]");
    expect(bar).not.toBeNull();
    expect(bar?.getAttribute("style")).toContain("50%");
  });

  it("handles zero maxScore", () => {
    const { container } = render(
      <ParameterBar parameter={mockParam} maxScore={0} />
    );
    const bar = container.querySelector("[style]");
    expect(bar?.getAttribute("style")).toContain("0%");
  });

  it("renders without unit when empty", () => {
    const noUnitParam = { ...mockParam, unit: "" };
    render(<ParameterBar parameter={noUnitParam} maxScore={70} />);
    expect(screen.getByText("32")).toBeTruthy();
  });
});
