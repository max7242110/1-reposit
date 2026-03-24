export interface Brand {
  id: number;
  name: string;
}

export interface RegionAvailability {
  region_code: string;
  region_display: string;
}

export interface ParameterScore {
  criterion_code: string;
  criterion_name: string;
  criterion_note?: string;
  compressor_model?: string;
  unit: string;
  raw_value: string;
  normalized_score: number;
  weighted_score: number;
  above_reference: boolean;
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

export interface ACModelSummary {
  id: number;
  brand: string;
  inner_unit: string;
  series: string;
  nominal_capacity: number | null;
  total_index: number;
  /** Верхняя граница индекса (сумма весов по активной методике). */
  index_max: number;
  publish_status: string;
  region_availability: RegionAvailability[];
}

export interface ACModelDetail {
  id: number;
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
  youtube_url: string;
  rutube_url: string;
  vk_url: string;
  parameter_scores: ParameterScore[];
  raw_values: RawValue[];
  methodology_version: string | null;
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
  is_lab: boolean;
  region_scope: string;
  is_public: boolean;
  display_order: number;
}

export interface Methodology {
  version: string;
  name: string;
  description: string;
  is_active: boolean;
  criteria: CriterionInfo[];
}

// v1 compat types
export interface AirConditionerSummary {
  id: number;
  rank: number;
  brand: string;
  model_name: string;
  total_score: number;
}

export interface ParameterValue {
  id: number;
  parameter_name: string;
  raw_value: string;
  unit: string;
  score: number;
}

export interface AirConditionerDetail extends AirConditionerSummary {
  youtube_url: string;
  rutube_url: string;
  vk_url: string;
  parameters: ParameterValue[];
}
