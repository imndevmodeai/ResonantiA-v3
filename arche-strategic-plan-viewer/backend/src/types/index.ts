import { Document } from 'mongoose';

export interface Profile {
  id: string;
  name: string;
  age: number;
  location: string;
  platform: string;
  tags: string[];
  description: string;
  extendedDescription: string;
  profileType: 'provider' | 'hobbyist' | 'enthusiast';
  extractedDetails: {
    title: string;
    items: string[];
  }[];
}

export interface SearchConfig {
  platform: string;
  location: string;
  keywords?: string[];
  maxResults?: number;
}

export interface VerificationRule {
  field: string;
  required: boolean;
  minLength?: number;
  min?: number;
  max?: number;
}

export interface ExtractionResult {
  success: boolean;
  profiles: Profile[];
  metadata: {
    extractionDate: Date;
    source: string;
    profilesFound: number;
    processingTime: number;
  };
  errors?: string[];
}
