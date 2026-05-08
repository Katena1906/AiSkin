export interface Product {
  name: string;
  brand: string;
  price: number;
  old_price?: number;
  description: string;
  action: string;
  how_to_use: string;
  effectiveness: number;
  reason: string;
  match_score: number;
}

export interface AnalysisResult {
  disease: string;
  confidence: number;
  all_probabilities: Record<string, number>;
  needs_doctor: boolean;
  heatmap?: string;
  bounding_boxes?: Array<{
    x: number;
    y: number;
    width: number;
    height: number;
    label: string;
    disease_name: string;
    confidence: number;
  }>;
}

export interface DrugRecommendation {
  name: string;
  generic_name: string;
  brand_names: string[];
  drug_class: string;
  how_it_works: string;
  side_effects: string[];
  warning: string;
  prescription_required: boolean;
  risk_level?: string;
  risk_message?: string;
}

export interface TreatmentPlan {
  disease: string;
  confidence: number;
  severity: string;
  explanation: string;
  treatment_goals: string[];
  first_line_treatments: string[];
  second_line_treatments: string[];
  prescription_medications: DrugRecommendation[];
  otc_recommendations: DrugRecommendation[];
  lifestyle_modifications: Array<{category: string, tip: string, why: string}>;
  warning_level: string;
  doctor_consultation_required: boolean;
}

export interface Recommendations {
  disease: string;
  confidence: number;
  treatment_plan: TreatmentPlan;
  ingredient_focus: string[];
  skin_type_advice: {
    text: string;
    tips: string[];
    avoid: string[];
  };
  seasonal_advice: {
    season: string;
    advice: string;
  };
  general_advice: string[];
  skincare_routine: {
    morning: string[];
    evening: string[];
  };
}

export interface ApiResponse {
  success: boolean;
  analysis: AnalysisResult;
  recommendations: Recommendations;
}

export interface BoundingBox {
  x: number;
  y: number;
  width: number;
  height: number;
  label: string;
  confidence: number;
}