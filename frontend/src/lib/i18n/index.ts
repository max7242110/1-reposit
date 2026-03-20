export const SUPPORTED_LOCALES = ["ru", "en", "de", "pt"] as const;
export type Locale = (typeof SUPPORTED_LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "ru";

type TranslationKeys = {
  rating_title: string;
  index_label: string;
  parameters: string;
  video_review: string;
  data_sources: string;
  above_reference: string;
  back_to_rating: string;
  all_regions: string;
  brand_search: string;
  not_found: string;
  loading: string;
  error_title: string;
  error_retry: string;
  footer_text: string;
};

const translations: Record<Locale, TranslationKeys> = {
  ru: {
    rating_title: "Рейтинг «Август-климат»",
    index_label: "Индекс «Август-климат»",
    parameters: "Параметры",
    video_review: "Видеообзор",
    data_sources: "Источники данных",
    above_reference: "выше эталона",
    back_to_rating: "Назад к рейтингу",
    all_regions: "Все регионы",
    brand_search: "Поиск по бренду...",
    not_found: "Модели не найдены",
    loading: "Загрузка...",
    error_title: "Что-то пошло не так",
    error_retry: "Попробовать снова",
    footer_text: "Данные основаны на независимых измерениях и тестированиях",
  },
  en: {
    rating_title: "August-Klimat Rating",
    index_label: "August-Klimat Index",
    parameters: "Parameters",
    video_review: "Video Review",
    data_sources: "Data Sources",
    above_reference: "above reference",
    back_to_rating: "Back to rating",
    all_regions: "All regions",
    brand_search: "Search by brand...",
    not_found: "No models found",
    loading: "Loading...",
    error_title: "Something went wrong",
    error_retry: "Try again",
    footer_text: "Data based on independent measurements and testing",
  },
  de: {
    rating_title: "August-Klimat Bewertung",
    index_label: "August-Klimat Index",
    parameters: "Parameter",
    video_review: "Videobewertung",
    data_sources: "Datenquellen",
    above_reference: "über dem Referenzwert",
    back_to_rating: "Zurück zur Bewertung",
    all_regions: "Alle Regionen",
    brand_search: "Nach Marke suchen...",
    not_found: "Keine Modelle gefunden",
    loading: "Laden...",
    error_title: "Etwas ist schiefgelaufen",
    error_retry: "Erneut versuchen",
    footer_text: "Daten basierend auf unabhängigen Messungen und Tests",
  },
  pt: {
    rating_title: "Classificação August-Klimat",
    index_label: "Índice August-Klimat",
    parameters: "Parâmetros",
    video_review: "Vídeo Análise",
    data_sources: "Fontes de Dados",
    above_reference: "acima da referência",
    back_to_rating: "Voltar à classificação",
    all_regions: "Todas as regiões",
    brand_search: "Pesquisar por marca...",
    not_found: "Nenhum modelo encontrado",
    loading: "Carregando...",
    error_title: "Algo deu errado",
    error_retry: "Tentar novamente",
    footer_text: "Dados baseados em medições e testes independentes",
  },
};

export function t(key: keyof TranslationKeys, locale: Locale = DEFAULT_LOCALE): string {
  return translations[locale]?.[key] || translations[DEFAULT_LOCALE][key] || key;
}

export function isValidLocale(locale: string): locale is Locale {
  return SUPPORTED_LOCALES.includes(locale as Locale);
}
