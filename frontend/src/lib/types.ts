export interface Brand {
  id: number;
  name: string;
  logo: string;
}

export interface RegionAvailability {
  region_code: string;
  region_display: string;
}

export interface ParameterScore {
  criterion_code: string;
  criterion_name: string;
  criterion_description?: string;
  compressor_model?: string;
  unit: string;
  raw_value: string;
  normalized_score: number;
  weighted_score: number;
  above_reference: boolean;
  is_active: boolean;
}

export interface RawValue {
  criterion_code: string;
  criterion_name: string;
  raw_value: string;
  numeric_value: number | null;
  source: string;
  source_url: string;
  verification_status: string;
  verification_display: string;
}

export interface Photo {
  id: number;
  image_url: string;
  alt: string;
  order: number;
}

export interface Supplier {
  id: number;
  name: string;
  url: string;
  order: number;
}

export interface ACModelSummary {
  id: number;
  slug: string;
  brand: string;
  brand_logo: string;
  inner_unit: string;
  series: string;
  nominal_capacity: number | null;
  total_index: number;
  /** Верхняя граница индекса (сумма весов по активной методике). */
  index_max: number;
  publish_status: string;
  region_availability: RegionAvailability[];
  price: string | null;
  noise_score: number | null;
  has_noise_measurement: boolean;
  /** Словарь {criterion_code: normalized_score} для пользовательского рейтинга. */
  scores: Record<string, number>;
  is_ad: boolean;
  ad_position: number | null;
}

export interface ACModelDetail {
  id: number;
  slug: string;
  brand: Brand;
  series: string;
  inner_unit: string;
  outer_unit: string;
  nominal_capacity: number | null;
  total_index: number;
  /** Верхняя граница индекса (по методике последнего расчёта или активной). */
  index_max: number;
  publish_status: string;
  region_availability: RegionAvailability[];
  price: string | null;
  pros_text: string;
  cons_text: string;
  youtube_url: string;
  rutube_url: string;
  vk_url: string;
  photos: Photo[];
  suppliers: Supplier[];
  parameter_scores: ParameterScore[];
  raw_values: RawValue[];
  methodology_version: string | null;
}

export interface BrandOption {
  id: number;
  name: string;
}

export interface CriterionInfo {
  code: string;
  name_ru: string;
  name_en: string;
  description_ru: string;
  unit: string;
  value_type: string;
  scoring_type: string;
  weight: number;
  min_value: number | null;
  median_value: number | null;
  max_value: number | null;
  region_scope: string;
  is_public: boolean;
  display_order: number;
  photo_url: string;
}

export interface Review {
  id: number;
  author_name: string;
  rating: number;
  pros: string;
  cons: string;
  comment: string;
  created_at: string;
}

export interface Methodology {
  version: string;
  name: string;
  description: string;
  tab_description_index: string;
  tab_description_quiet: string;
  tab_description_custom: string;
  is_active: boolean;
  criteria: CriterionInfo[];
}
