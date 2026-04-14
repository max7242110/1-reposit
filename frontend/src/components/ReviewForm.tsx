"use client";

import { useState } from "react";

import { ApiError, createReview } from "@/lib/api";

interface Props {
  modelId: number;
}

function StarsInput({
  value,
  onChange,
}: {
  value: number;
  onChange: (v: number) => void;
}) {
  const [hover, setHover] = useState(0);
  const display = hover || value;
  return (
    <div
      className="inline-flex gap-0.5 text-2xl leading-none"
      onMouseLeave={() => setHover(0)}
      role="radiogroup"
      aria-label="Оценка"
    >
      {[1, 2, 3, 4, 5].map((i) => (
        <button
          key={i}
          type="button"
          role="radio"
          aria-checked={value === i}
          aria-label={`${i} из 5`}
          onClick={() => onChange(i)}
          onMouseEnter={() => setHover(i)}
          className={`transition-colors cursor-pointer ${
            i <= display ? "text-yellow-400" : "text-gray-300 dark:text-gray-600"
          } hover:text-yellow-500`}
        >
          ★
        </button>
      ))}
    </div>
  );
}

export default function ReviewForm({ modelId }: Props) {
  const [authorName, setAuthorName] = useState("");
  const [rating, setRating] = useState(0);
  const [pros, setPros] = useState("");
  const [cons, setCons] = useState("");
  const [comment, setComment] = useState("");
  const [website, setWebsite] = useState(""); // honeypot
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [errorMsg, setErrorMsg] = useState("");

  const reset = () => {
    setAuthorName("");
    setRating(0);
    setPros("");
    setCons("");
    setComment("");
    setWebsite("");
  };

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!authorName.trim() || rating < 1) {
      setStatus("error");
      setErrorMsg("Укажите имя и оценку.");
      return;
    }
    setStatus("loading");
    setErrorMsg("");
    try {
      await createReview({
        model: modelId,
        author_name: authorName.trim(),
        rating,
        pros: pros.trim(),
        cons: cons.trim(),
        comment: comment.trim(),
        website,
      });
      setStatus("success");
      reset();
    } catch (e) {
      setStatus("error");
      if (e instanceof ApiError) {
        setErrorMsg(
          e.status === 429
            ? "Слишком много отправок с вашего IP. Попробуйте позже."
            : "Не удалось отправить отзыв. Проверьте поля и попробуйте ещё раз.",
        );
      } else {
        setErrorMsg("Сетевая ошибка. Попробуйте позже.");
      }
    }
  }

  if (status === "success") {
    return (
      <div className="mt-6 p-4 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 border border-emerald-200 dark:border-emerald-800 text-sm text-emerald-800 dark:text-emerald-300">
        Спасибо! Отзыв появится после модерации.{" "}
        <button
          type="button"
          onClick={() => setStatus("idle")}
          className="underline font-medium"
        >
          Оставить ещё
        </button>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mt-6 p-4 sm:p-6 rounded-xl bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-800 space-y-4"
    >
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
        Оставить отзыв
      </h3>

      {/* honeypot — скрыт визуально и от скринридеров */}
      <input
        type="text"
        name="website"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        value={website}
        onChange={(e) => setWebsite(e.target.value)}
        className="hidden"
      />

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Ваше имя <span className="text-rose-600">*</span>
        </label>
        <input
          type="text"
          required
          maxLength={100}
          value={authorName}
          onChange={(e) => setAuthorName(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Оценка <span className="text-rose-600">*</span>
        </label>
        <StarsInput value={rating} onChange={setRating} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Достоинства
          </label>
          <textarea
            rows={3}
            value={pros}
            onChange={(e) => setPros(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            Недостатки
          </label>
          <textarea
            rows={3}
            value={cons}
            onChange={(e) => setCons(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
          />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
          Комментарий
        </label>
        <textarea
          rows={4}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-sm"
        />
      </div>

      {status === "error" && (
        <p className="text-sm text-rose-700 dark:text-rose-400">{errorMsg}</p>
      )}

      <div className="flex items-center justify-between gap-3">
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Отзыв публикуется после модерации администратором.
        </p>
        <button
          type="submit"
          disabled={status === "loading"}
          className="px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white text-sm font-medium transition-colors"
        >
          {status === "loading" ? "Отправка…" : "Отправить"}
        </button>
      </div>
    </form>
  );
}
