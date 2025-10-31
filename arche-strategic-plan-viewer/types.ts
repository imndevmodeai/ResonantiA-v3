export interface Section {
  title: string;
  items: string[];
}

export interface Phase {
  id: number;
  title: string;
  duration: number; // in weeks
  isOngoing?: boolean;
  startWeek: number;
  sections: Section[];
}

export type Platform = 'FetLife' | 'SkipTheGames' | 'Chaturbate';
export type ProfileType = 'Female' | 'Couple';
export type Location = 'Kalamazoo' | 'Battle Creek' | 'Grand Rapids';

export interface ExtractedDetail {
  title: string;
  items: string[];
}

export interface Profile {
  id: string;
  name: string;
  age: number;
  location: Location;
  platform: Platform;
  profileType: ProfileType;
  tags: string[];
  imageUrl: string;
  description: string;
  extendedDescription: string;
  extractedDetails: ExtractedDetail[];
}

export interface FilterState {
  keyword: string;
  locations: Location[];
  platforms: Platform[];
  profileType: 'All' | ProfileType;
}