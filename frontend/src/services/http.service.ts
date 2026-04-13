import axios, { type AxiosInstance } from 'axios';
import type { AxiosRequestConfig, AxiosResponse } from 'axios';

export const axiosInstance: AxiosInstance = axios.create({
  headers: { Accept: 'application/json' },
});

export class HttpService {
  protected get<T>(url: string, options?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.get(url, options);
  }

  protected post<T, D>(url: string, data: D, options?: AxiosRequestConfig<D>): Promise<AxiosResponse<T>> {
    return axiosInstance.post(url, data, options);
  }

  protected put<T, D>(url: string, data: D, options?: AxiosRequestConfig<D>): Promise<AxiosResponse<T>> {
    return axiosInstance.put(url, data, options);
  }

  protected delete<T>(url: string, options?: AxiosRequestConfig): Promise<AxiosResponse<T>> {
    return axiosInstance.delete(url, options);
  }
}
