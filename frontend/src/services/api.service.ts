import type { ConceptScheme } from '@models/conceptscheme';
import type { Concept, OverviewConcept } from '@models/concept';
import { HttpService } from './http.service';
import type { Provider } from '@models/provider';

export class ApiService extends HttpService {
  constructor() {
    super();
  }

  /* Conceptschemes */
  async getConceptschemes(): Promise<ConceptScheme[]> {
    return (await this.get<ConceptScheme[]>('/conceptschemes')).data;
  }

  async getConceptscheme(schemeId: string): Promise<ConceptScheme> {
    return (await this.get<ConceptScheme>(`/conceptschemes/${schemeId}`)).data;
  }

  async getConceptsByConceptscheme(
    schemeId: string,
    options?: { label?: string; match?: string }
  ): Promise<OverviewConcept[]> {
    return (await this.get<OverviewConcept[]>(`/conceptschemes/${schemeId}/c`, { params: options })).data;
  }

  async getConceptByConceptschemeAndId(schemeId: string, conceptId: number): Promise<Concept> {
    return this.get<Concept>(`/conceptschemes/${schemeId}/c/${conceptId}`).then((response) => response.data);
  }

  /* Providers */
  async getProviders(): Promise<Provider[]> {
    return (await this.get<Provider[]>('/providers')).data;
  }
}
