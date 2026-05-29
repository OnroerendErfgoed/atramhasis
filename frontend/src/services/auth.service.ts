import type { UserInfo } from '@models/auth';
import { HttpService } from './http.service';

export class AuthService extends HttpService {
  constructor() {
    super();
  }

  async getUserInfo(): Promise<UserInfo> {
    return (await this.get<UserInfo>('/userinfo')).data;
  }
}
