import type { ConceptScheme } from '@models/conceptscheme';
import type { Concept } from '@models/concept';
import { HttpService } from './http.service';

export class ApiService extends HttpService {
  constructor() {
    super();
  }

  async getConceptschemes(): Promise<ConceptScheme[]> {
    return (await this.get<ConceptScheme[]>('/conceptschemes')).data;
  }

  async getConceptscheme(schemeId: string, options: { type?: string; sort?: string }): Promise<Concept[]> {
    return (await this.get<Concept[]>(`/conceptschemes/${schemeId}/c`, { params: options })).data;
  }
}
