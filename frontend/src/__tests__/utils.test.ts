import { getMedalColor } from "@/lib/utils";

describe("getMedalColor", () => {
  it("returns gold for 1st place", () => {
    expect(getMedalColor(1)).toBe("text-yellow-500");
  });

  it("returns silver for 2nd place", () => {
    expect(getMedalColor(2)).toBe("text-gray-400");
  });

  it("returns bronze for 3rd place", () => {
    expect(getMedalColor(3)).toBe("text-amber-700");
  });

  it("returns default for other positions", () => {
    expect(getMedalColor(4)).toBe("text-gray-500");
    expect(getMedalColor(100)).toBe("text-gray-500");
  });
});
