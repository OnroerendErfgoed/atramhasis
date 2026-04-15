import type { ConceptScheme } from '@models/conceptscheme';
import { HttpService } from './http.service';

export class ApiService extends HttpService {
  constructor() {
    super();
  }

  async getConceptschemes(): Promise<ConceptScheme[]> {
    return (await this.get<ConceptScheme[]>('/conceptschemes')).data;
  }
}
