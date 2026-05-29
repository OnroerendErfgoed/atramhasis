import type { UserInfo } from '@models/auth';
import { AuthService } from '@services/auth.service';
import { defineStore } from 'pinia';
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';

export const useAuthStore = defineStore('auth', () => {
  const { t } = useI18n();

  const authService = new AuthService();

  const userInfo = ref<UserInfo>();

  const fetchUserInfo = async () => {
    try {
      userInfo.value = await authService.getUserInfo();
    } catch (error) {
      console.error(t('auth.error'), error);
    }
  };

  return { fetchUserInfo, userInfo };
});
