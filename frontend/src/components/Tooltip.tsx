interface Props {
  text: string;
  children: React.ReactNode;
}

export default function Tooltip({ text, children }: Props) {
  return (
    <span className="relative group/tip">
      {children}
      <span
        role="tooltip"
        className="pointer-events-none absolute bottom-full left-1/2 -translate-x-1/2 mb-2 w-max max-w-xs px-3 py-2 rounded-lg bg-gray-900 dark:bg-gray-100 text-white dark:text-gray-900 text-xs leading-relaxed shadow-lg opacity-0 group-hover/tip:opacity-100 transition-opacity duration-150 z-50"
      >
        {text}
      </span>
    </span>
  );
}
