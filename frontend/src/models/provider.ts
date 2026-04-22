export interface Provider {
  id: string;
  id_generation_strategy: string;
  type: string;
  conceptscheme_uri: string;
  uri_pattern: string;
  default_language: string;
  subject: string[];
  force_display_language: string;
  expand_strategy: string;
  metadata: {
    uri: string;
    [key: string]: unknown;
  };
}
