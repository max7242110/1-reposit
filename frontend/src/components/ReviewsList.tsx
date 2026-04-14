import { Review } from "@/lib/types";

const DATE_FORMATTER = new Intl.DateTimeFormat("ru-RU", {
  day: "2-digit",
  month: "long",
  year: "numeric",
});

function Stars({ rating }: { rating: number }) {
  const r = Math.max(0, Math.min(5, Math.round(rating)));
  return (
    <span aria-label={`Оценка ${r} из 5`} className="inline-flex text-lg leading-none">
      {Array.from({ length: 5 }, (_, i) => (
        <span
          key={i}
          className={i < r ? "text-yellow-400" : "text-gray-300 dark:text-gray-600"}
        >
          ★
        </span>
      ))}
    </span>
  );
}

function ReviewCard({ review }: { review: Review }) {
  const date = DATE_FORMATTER.format(new Date(review.created_at));
  return (
    <article className="py-5 border-b border-gray-200 dark:border-gray-700 last:border-b-0">
      <header className="flex flex-wrap items-center gap-3 mb-2">
        <span className="font-semibold text-gray-900 dark:text-white">
          {review.author_name}
        </span>
        <Stars rating={review.rating} />
        <span className="text-xs text-gray-500 dark:text-gray-400 ml-auto">{date}</span>
      </header>

      {review.pros && (
        <p className="text-sm mb-1.5">
          <span className="font-semibold text-emerald-700 dark:text-emerald-400">
            Достоинства:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
            {review.pros}
          </span>
        </p>
      )}
      {review.cons && (
        <p className="text-sm mb-1.5">
          <span className="font-semibold text-rose-700 dark:text-rose-400">
            Недостатки:{" "}
          </span>
          <span className="text-gray-700 dark:text-gray-300 whitespace-pre-line">
            {review.cons}
          </span>
        </p>
      )}
      {review.comment && (
        <p className="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-line">
          {review.comment}
        </p>
      )}
    </article>
  );
}

export default function ReviewsList({ reviews }: { reviews: Review[] }) {
  if (reviews.length === 0) {
    return (
      <p className="text-sm text-gray-500 dark:text-gray-400 py-6 text-center">
        Пока нет отзывов. Будьте первым.
      </p>
    );
  }
  return (
    <div className="divide-y divide-gray-200 dark:divide-gray-700">
      {reviews.map((r) => (
        <ReviewCard key={r.id} review={r} />
      ))}
    </div>
  );
}
