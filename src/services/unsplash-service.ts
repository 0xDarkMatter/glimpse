import axios from 'axios';
import { ImageSource, UnsplashPhoto } from '../types';
import { logger } from '../utils/logger';

export class UnsplashService implements ImageSource {
  name = 'unsplash';
  private accessKey: string;
  private baseUrl = 'https://api.unsplash.com';

  constructor(accessKey: string) {
    if (!accessKey) {
      throw new Error('Unsplash access key is required');
    }
    this.accessKey = accessKey;
  }

  async fetchRandomImage(): Promise<{
    url: string;
    description: string;
    sourceUrl: string;
  }> {
    try {
      logger.debug('Fetching random image from Unsplash...');

      const response = await axios.get<UnsplashPhoto>(`${this.baseUrl}/photos/random`, {
        headers: {
          Authorization: `Client-ID ${this.accessKey}`,
        },
        params: {
          orientation: 'landscape',
        },
      });

      const photo = response.data;

      return {
        url: photo.urls.regular,
        description:
          photo.description || photo.alt_description || 'No description available',
        sourceUrl: photo.links.html,
      };
    } catch (error) {
      if (axios.isAxiosError(error)) {
        logger.error('Unsplash API error:', error.response?.data || error.message);
        throw new Error(`Failed to fetch image from Unsplash: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Test the Unsplash API connection
   */
  async testConnection(): Promise<boolean> {
    try {
      await axios.get(`${this.baseUrl}/photos/random`, {
        headers: {
          Authorization: `Client-ID ${this.accessKey}`,
        },
      });
      return true;
    } catch (error) {
      return false;
    }
  }
}
