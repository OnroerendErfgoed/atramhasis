import type { AxiosError } from 'axios';
import { useI18n } from 'vue-i18n';

export interface ApiValidationErrorItem {
  [field: string]: string;
}

export interface ApiValidationError {
  message: string;
  errors: ApiValidationErrorItem[];
}

export function useApiError() {
  const toast = useToast();
  const { t } = useI18n();

  const handleApiError = (error: unknown) => {
    const axiosError = error as AxiosError<ApiValidationError>;
    const errorMessage = axiosError.response?.data?.message;
    const validationErrors = axiosError.response?.data?.errors;

    toast.add({
      title: errorMessage || t('errors.generic.title'),
      description: validationErrors
        ? validationErrors
            .flatMap((validationError) =>
              Object.entries(validationError).map(([field, message]) => `${field}: ${String(message)}`)
            )
            .join('\n')
        : t('errors.generic.description'),
      icon: 'i-lucide-alert-triangle',
      color: 'error',
      class: 'whitespace-pre-line',
      duration: 10000,
    });
  };

  return { handleApiError };
}
