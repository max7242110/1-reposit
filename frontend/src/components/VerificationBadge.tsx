interface Props {
  status: string;
  display: string;
}

const BADGE_STYLES: Record<string, string> = {
  catalog: "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300",
  editorial: "bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300",
  lab: "bg-green-100 dark:bg-green-900/40 text-green-700 dark:text-green-300",
};

export default function VerificationBadge({ status, display }: Props) {
  const style = BADGE_STYLES[status] || BADGE_STYLES.catalog;
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${style}`}>
      {display}
    </span>
  );
}
