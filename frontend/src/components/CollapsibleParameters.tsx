"use client";

import { useState } from "react";

import IndexCriterionCard from "@/components/IndexCriterionCard";
import { ParameterScore } from "@/lib/types";

const VISIBLE_COUNT = 12;

export default function CollapsibleParameters({
  scores,
}: {
  scores: ParameterScore[];
}) {
  const [expanded, setExpanded] = useState(false);
  const visible = expanded ? scores : scores.slice(0, VISIBLE_COUNT);
  const hiddenCount = scores.length - VISIBLE_COUNT;

  return (
    <>
      {visible.map((ps) => (
        <IndexCriterionCard key={ps.criterion_code} criterion={ps} />
      ))}
      {scores.length > VISIBLE_COUNT && (
        <div className="py-4 flex justify-center">
          <button
            type="button"
            onClick={() => setExpanded(!expanded)}
            aria-expanded={expanded}
            className="text-sm font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 transition-colors"
          >
            {expanded ? "Свернуть" : `Показать все параметры (ещё ${hiddenCount})`}
          </button>
        </div>
      )}
    </>
  );
}
