import React from 'react';
import { Profile } from '../types';
import { LocationMarkerIcon, TagIcon } from './icons';

interface ProfileCardProps {
    profile: Profile;
    onClick: () => void;
}

const platformColors: { [key: string]: string } = {
    FetLife: 'bg-cyan-600 text-cyan-100',
    SkipTheGames: 'bg-purple-600 text-purple-100',
    Chaturbate: 'bg-pink-600 text-pink-100',
};

export const ProfileCard: React.FC<ProfileCardProps> = ({ profile, onClick }) => {
    return (
        <button
            onClick={onClick}
            className="bg-gray-800/80 rounded-lg overflow-hidden shadow-lg border border-gray-700/50 flex flex-col h-full text-left w-full transition-transform duration-300 hover:transform hover:-translate-y-1 hover:shadow-cyan-500/20 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-900 focus:ring-cyan-500"
        >
            <div className="relative">
                <img className="w-full h-48 object-cover" src={profile.imageUrl} alt={profile.name} />
                <span className={`absolute top-2 right-2 text-xs font-semibold px-2 py-1 rounded-full ${platformColors[profile.platform]}`}>
                    {profile.platform}
                </span>
            </div>
            <div className="p-4 flex flex-col flex-grow">
                <h3 className="text-xl font-bold text-white">{profile.name} <span className="text-gray-400 font-normal text-lg">({profile.age})</span></h3>
                <div className="flex items-center text-gray-400 mt-1 text-sm">
                    <LocationMarkerIcon className="w-4 h-4 mr-1.5" />
                    <span>{profile.location} - {profile.profileType}</span>
                </div>
                <p className="text-gray-300 mt-3 text-sm flex-grow">
                    {profile.description}
                </p>
                <div className="mt-4 pt-3 border-t border-gray-700/50">
                    <div className="flex items-center text-xs text-gray-400 mb-2">
                        <TagIcon className="w-4 h-4 mr-1.5" />
                        <span>Interests</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {profile.tags.map(tag => (
                            <span key={tag} className="bg-gray-700 text-gray-300 text-xs font-medium px-2.5 py-1 rounded-full">
                                {tag}
                            </span>
                        ))}
                    </div>
                </div>
            </div>
        </button>
    );
};