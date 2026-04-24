import type { Conceptscheme, OverviewConceptscheme } from '@models/conceptscheme';
import type { Concept, OverviewConcept } from '@models/concept';
import { HttpService } from './http.service';
import type { Provider, ProviderForm } from '@models/provider';
import type { Language } from '@models/language';

export class ApiService extends HttpService {
  constructor() {
    super();
  }

  // Getters
  async getConceptschemes(): Promise<OverviewConceptscheme[]> {
    return (await this.get<OverviewConceptscheme[]>('/conceptschemes')).data;
  }

  async getConceptscheme(schemeId: string): Promise<Conceptscheme> {
    return (await this.get<Conceptscheme>(`/conceptschemes/${schemeId}`)).data;
  }

  async getConceptsByConceptscheme(
    schemeId: string,
    options?: { label?: string; match?: string }
  ): Promise<OverviewConcept[]> {
    return (await this.get<OverviewConcept[]>(`/conceptschemes/${schemeId}/c`, { params: options })).data;
  }

  async getConceptByConceptschemeAndId(schemeId: string, conceptId: number): Promise<Concept> {
    return (await this.get<Concept>(`/conceptschemes/${schemeId}/c/${conceptId}`)).data;
  }

  async getProviders(): Promise<Provider[]> {
    return (await this.get<Provider[]>('/providers')).data;
  }

  async getLanguages(): Promise<Language[]> {
    return (await this.get<Language[]>('/languages')).data;
  }

  // Creators
  async createProvider(provider: ProviderForm): Promise<Provider> {
    return (await this.post<Provider, ProviderForm>('/providers', provider)).data;
  }

  // Updaters
  async updateProvider(provider: ProviderForm): Promise<Provider> {
    return (await this.put<Provider, ProviderForm>(`/providers/${provider.id}`, provider)).data;
  }
}
