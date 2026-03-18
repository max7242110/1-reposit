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
