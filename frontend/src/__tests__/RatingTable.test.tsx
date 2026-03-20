import { render, screen } from "@testing-library/react";
import RatingTable from "@/components/RatingTable";
import { AirConditionerSummary } from "@/lib/types";

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

const mockData: AirConditionerSummary[] = [
  { id: 1, rank: 1, brand: "Фунай ONSEN", model_name: "RAC-I-ON30HP", total_score: 297.6 },
  { id: 2, rank: 2, brand: "LG Deluxe Pro", model_name: "H12S1D", total_score: 242.3 },
  { id: 3, rank: 3, brand: "MDV NOVA", model_name: "MDSAH-09HRFN8", total_score: 184.4 },
];

describe("RatingTable", () => {
  it("renders all conditioners", () => {
    render(<RatingTable conditioners={mockData} />);
    expect(screen.getByText("Фунай ONSEN")).toBeTruthy();
    expect(screen.getByText("LG Deluxe Pro")).toBeTruthy();
    expect(screen.getByText("MDV NOVA")).toBeTruthy();
  });

  it("displays scores", () => {
    render(<RatingTable conditioners={mockData} />);
    expect(screen.getByText("297.6")).toBeTruthy();
    expect(screen.getByText("242.3")).toBeTruthy();
  });

  it("has accessible table with caption", () => {
    render(<RatingTable conditioners={mockData} />);
    expect(screen.getByRole("table")).toBeTruthy();
  });

  it("renders column headers with scope", () => {
    const { container } = render(<RatingTable conditioners={mockData} />);
    const ths = container.querySelectorAll("th[scope='col']");
    expect(ths.length).toBe(4);
  });

  it("renders links to detail pages", () => {
    render(<RatingTable conditioners={mockData} />);
    const links = screen.getAllByRole("link");
    expect(links.length).toBe(3);
    expect(links[0].getAttribute("href")).toBe("/conditioner/1");
  });

  it("renders empty state", () => {
    render(<RatingTable conditioners={[]} />);
    const rows = screen.queryAllByRole("row");
    expect(rows.length).toBe(1);
  });

  it("displays model names", () => {
    render(<RatingTable conditioners={mockData} />);
    expect(screen.getAllByText("RAC-I-ON30HP").length).toBeGreaterThan(0);
  });
});
