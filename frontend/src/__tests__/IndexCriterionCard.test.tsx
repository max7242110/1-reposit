import { render, screen } from "@testing-library/react";
import IndexCriterionCard from "@/components/IndexCriterionCard";
import { ParameterScore } from "@/lib/types";

const mockCriterion: ParameterScore = {
  criterion_code: "noise",
  criterion_name: "Уровень шума",
  unit: "дБ(А)",
  raw_value: "32",
  normalized_score: 48.5,
  weighted_score: 10,
  above_reference: false,
};

describe("IndexCriterionCard", () => {
  it("renders name, raw value with unit, and scores", () => {
    render(<IndexCriterionCard criterion={mockCriterion} />);
    expect(screen.getByText("Уровень шума")).toBeTruthy();
    expect(screen.getByText("32")).toBeTruthy();
    expect(screen.getByText("дБ(А)")).toBeTruthy();
    expect(screen.getByText("48.5")).toBeTruthy();
    expect(screen.getByText(/Вклад в индекс:/)).toBeTruthy();
    expect(screen.getByText("10.00")).toBeTruthy();
  });

  it("shows above-reference badge when set", () => {
    render(
      <IndexCriterionCard criterion={{ ...mockCriterion, above_reference: true }} />,
    );
    expect(screen.getByText("выше эталона")).toBeTruthy();
  });

  it("renders progressbar for 0–100 scale", () => {
    render(<IndexCriterionCard criterion={mockCriterion} />);
    const bar = screen.getByRole("progressbar");
    expect(bar.getAttribute("aria-valuemax")).toBe("100");
    expect(bar.getAttribute("aria-valuenow")).toBe("48.5");
  });

  it("renders em dash when raw value is empty", () => {
    render(<IndexCriterionCard criterion={{ ...mockCriterion, raw_value: "  " }} />);
    expect(screen.getByText("—")).toBeTruthy();
  });
});
