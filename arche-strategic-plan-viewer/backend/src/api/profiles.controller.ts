import { Request, Response } from 'express';
import { Profile } from '../models/profile.model';

export const getProfiles = async (req: Request, res: Response) => {
  try {
    const { keyword, locations, platforms, profileType } = req.query;

    const query: any = {};

    if (keyword) {
      query. = { : keyword as string };
    }

    if (locations) {
      query.location = { : (locations as string).split(',') };
    }

    if (platforms) {
      query.platform = { : (platforms as string).split(',') };
    }

    if (profileType) {
      query.profileType = profileType as string;
    }

    const profiles = await Profile.find(query);
    res.json(profiles);
  } catch (error) {
    res.status(500).json({ message: 'Error fetching profiles', error });
  }
};
