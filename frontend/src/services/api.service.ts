import type { ConceptScheme } from '@models/conceptscheme';
import { HttpService } from './http.service';
import type { Provider } from '@models/provider';

export class ApiService extends HttpService {
  constructor() {
    super();
  }

  async getConceptschemes(): Promise<ConceptScheme[]> {
    return (await this.get<ConceptScheme[]>('/conceptschemes')).data;
  }

  async getProviders(): Promise<Provider[]> {
    return (await this.get<Provider[]>('/providers')).data;
  }
}
