export interface RVTarget {
  code: string;
  targetUrl: string;
  targetDescription: string;
  targetSource: 'unsplash' | 'pexels' | 'pixabay';
  revealed: boolean;
  revealedAt?: Date;
}

export interface RVSession {
  id: string;
  name?: string;
  targets: RVTarget[];
  createdAt: Date;
  revealAt: Date;
  notes?: string;
}

export interface UnsplashPhoto {
  id: string;
  urls: {
    raw: string;
    full: string;
    regular: string;
    small: string;
    thumb: string;
  };
  description: string | null;
  alt_description: string | null;
  user: {
    name: string;
    username: string;
  };
  links: {
    html: string;
  };
}

export interface StorageAdapter {
  saveSession(session: RVSession): Promise<void>;
  getSession(id: string): Promise<RVSession | null>;
  getAllSessions(): Promise<RVSession[]>;
  updateSession(id: string, updates: Partial<RVSession>): Promise<void>;
  deleteSession(id: string): Promise<void>;
}

export interface ImageSource {
  name: string;
  fetchRandomImage(): Promise<{
    url: string;
    description: string;
    sourceUrl: string;
  }>;
}

export interface Config {
  unsplashAccessKey?: string;
  pexelsApiKey?: string;
  pixabayApiKey?: string;
  defaultRevealDuration: number; // in minutes
  dataDirectory: string;
}
