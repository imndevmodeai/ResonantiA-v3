import React, { useEffect, useRef } from 'react';
import { Profile } from '../types';
import { CloseIcon, LocationMarkerIcon, SparklesIcon, TagIcon } from './icons';

interface ProfileModalProps {
  profile: Profile;
  onClose: () => void;
}

const platformColors: { [key: string]: { base: string, text: string, border: string } } = {
    FetLife: { base: 'bg-cyan-900/50', text: 'text-cyan-300', border: 'border-cyan-700' },
    SkipTheGames: { base: 'bg-purple-900/50', text: 'text-purple-300', border: 'border-purple-700' },
    Chaturbate: { base: 'bg-pink-900/50', text: 'text-pink-300', border: 'border-pink-700' },
};


export const ProfileModal: React.FC<ProfileModalProps> = ({ profile, onClose }) => {
    const modalRef = useRef<HTMLDivElement>(null);

    // Effect to handle 'Escape' key press for closing the modal
    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === 'Escape') {
                onClose();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => {
            window.removeEventListener('keydown', handleKeyDown);
        };
    }, [onClose]);

    // Effect to handle clicks outside the modal to close it
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (modalRef.current && !modalRef.current.contains(event.target as Node)) {
                onClose();
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [onClose]);


    const color = platformColors[profile.platform] || platformColors.FetLife;

    return (
        <div 
            className="fixed inset-0 bg-black/70 z-50 flex items-center justify-center p-4 animate-fade-in"
            aria-modal="true"
            role="dialog"
        >
            <div 
                ref={modalRef} 
                className="bg-gray-800 rounded-lg shadow-2xl w-full max-w-2xl max-h-[90vh] flex flex-col overflow-hidden border border-gray-700"
            >
                {/* Header */}
                <div className={`relative ${color.border} border-b-2`}>
                    <img src={profile.imageUrl} alt={profile.name} className="w-full h-48 object-cover opacity-30" />
                    <div className="absolute inset-0 bg-gradient-to-t from-gray-800 to-transparent p-6 flex flex-col justify-end">
                         <h2 className="text-3xl font-bold text-white">{profile.name} <span className="text-gray-400 font-normal">({profile.age})</span></h2>
                         <div className="flex items-center text-gray-300 mt-2">
                            <LocationMarkerIcon className="w-5 h-5 mr-2" />
                            <span>{profile.location} - {profile.profileType}</span>
                         </div>
                    </div>
                    <button onClick={onClose} className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-500 rounded-full p-1">
                        <CloseIcon className="w-7 h-7" />
                        <span className="sr-only">Close profile details</span>
                    </button>
                </div>

                {/* Body */}
                <div className="p-6 overflow-y-auto flex-grow space-y-6">
                    {/* Description */}
                    <div>
                        <h3 className="text-lg font-semibold text-cyan-300 mb-2">About</h3>
                        <p className="text-gray-300 whitespace-pre-wrap">{profile.extendedDescription}</p>
                    </div>

                    {/* Tags */}
                    <div>
                         <h3 className="text-lg font-semibold text-cyan-300 mb-3 flex items-center">
                            <TagIcon className="w-5 h-5 mr-2" />
                            Interests
                        </h3>
                        <div className="flex flex-wrap gap-2">
                            {profile.tags.map(tag => (
                                <span key={tag} className="bg-gray-700 text-gray-300 text-sm font-medium px-3 py-1 rounded-full">
                                    {tag}
                                </span>
                            ))}
                        </div>
                    </div>

                    {/* AI Insights */}
                    <div className={`${color.base} ${color.border} border rounded-lg p-4`}>
                        <h3 className={`text-lg font-semibold ${color.text} mb-3 flex items-center`}>
                            <SparklesIcon className="w-5 h-5 mr-2" />
                            AI Extracted Insights
                        </h3>
                        <div className="space-y-4">
                            {profile.extractedDetails.map(detail => (
                                <div key={detail.title}>
                                    <h4 className="font-semibold text-gray-200">{detail.title}</h4>
                                    <ul className="list-disc list-inside mt-1 text-gray-300/80 text-sm space-y-1">
                                        {detail.items.map((item, index) => (
                                            <li key={index}>{item}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    </div>

                </div>
            </div>
             <style>{`
                @keyframes fade-in {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                .animate-fade-in {
                    animation: fade-in 0.3s ease-out forwards;
                }
            `}</style>
        </div>
    );
};
