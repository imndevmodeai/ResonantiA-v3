import { Schema, model, Document } from 'mongoose';

export interface IProfile extends Document {
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

const ProfileSchema = new Schema<IProfile>({
  id: { type: String, required: true, unique: true },
  name: { type: String, required: true },
  age: { type: Number, required: true },
  location: { type: String, required: true },
  platform: { type: String, required: true },
  tags: [{ type: String }],
  description: { type: String, required: true },
  extendedDescription: { type: String, required: true },
  profileType: { type: String, enum: ['provider', 'hobbyist', 'enthusiast'], required: true },
  extractedDetails: [{
    title: String,
    items: [String]
  }]
});

ProfileSchema.index({ name: 'text', description: 'text', extendedDescription: 'text', tags: 'text' });

export const Profile = model<IProfile>('Profile', ProfileSchema);
