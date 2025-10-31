import { Phase, Profile } from './types';

export const projectData: Phase[] = [
  {
    id: 1,
    title: "Phase 1: Ethical and Legal Foundation",
    duration: 2,
    startWeek: 1,
    sections: [
      {
        title: "Goal",
        items: ["Establish a solid ethical and legal framework to guide ArchE's development and operation."],
      },
      {
        title: "Actions",
        items: [
          "Comprehensive Legal Review: Consult with legal counsel specializing in data privacy (GDPR, CCPA), online content regulations, and terms of service compliance. Document all legal constraints.",
          "Ethics Board Formation: Assemble an internal ethics board composed of AI ethicists, legal experts, and community representatives (if feasible) to review and approve all data collection and analysis strategies.",
          "Data Privacy Impact Assessment (DPIA): Conduct a thorough DPIA to identify and mitigate potential risks to individual privacy.",
          "Terms of Service (ToS) Analysis: Meticulously review the ToS of FetLife, SkipTheGames, Chaturbate, and other target sites. Document permissible and prohibited activities.",
          "Transparency Documentation: Create a public-facing document outlining ArchE's purpose, data collection methods, and privacy policies. This document should be easily accessible and understandable.",
        ],
      },
      {
        title: "Deliverables",
        items: ["Legal Compliance Report", "Ethics Board Charter and Meeting Minutes", "Data Privacy Impact Assessment Report", "ToS Compliance Matrix", "Public Transparency Document"],
      },
      {
        title: "Metrics",
        items: ["Completion of all legal and ethical reviews.", "Approval of DPIA by the Ethics Board.", "Documentation of ToS compliance for each target site."],
      },
    ],
  },
  {
    id: 2,
    title: "Phase 2: Technology Stack and Infrastructure Setup",
    duration: 3,
    startWeek: 3,
    sections: [
      {
        title: "Goal",
        items: ["Build a secure and scalable infrastructure to support ArchE's operations."],
      },
      {
        title: "Actions",
        items: [
          "Secure Credential Vault Implementation: Deploy HashiCorp Vault or AWS Secrets Manager to securely store and manage login credentials. Implement strict access controls and audit logging.",
          "Headless Browser Infrastructure: Set up a scalable headless browser infrastructure using Docker and Kubernetes. Configure rotating proxies and user agents to mitigate anti-bot detection.",
          "API Integration: Prioritize API integration with FetLife, SkipTheGames, and other platforms where available. Obtain necessary API keys and documentation.",
          "Data Storage and Processing: Establish a secure data storage and processing environment using cloud-based services like AWS S3 and AWS Lambda. Implement data encryption at rest and in transit.",
          "Monitoring and Alerting: Implement a comprehensive monitoring and alerting system to track ArchE's performance and identify potential issues.",
        ],
      },
      {
        title: "Deliverables",
        items: ["Secure Credential Vault Implementation", "Headless Browser Infrastructure Deployment", "API Integration Documentation", "Data Storage and Processing Environment Setup", "Monitoring and Alerting System Configuration"],
      },
      {
        title: "Metrics",
        items: ["Successful deployment of all infrastructure components.", "Secure storage of login credentials.", "Functional API integration with target platforms.", "Real-time monitoring of system performance."],
      },
    ],
  },
  {
    id: 3,
    title: "Phase 3: Query Processing and Search Strategy Development",
    duration: 4,
    startWeek: 6,
    sections: [
      {
        title: "Goal",
        items: ["Develop and refine ArchE's query processing and search strategies to effectively identify relevant information."],
      },
      {
        title: "Actions",
        items: [
          "Universal Abstraction Implementation: Implement the universal abstraction framework for query processing. Develop algorithms to decompose queries into constituent parts, identify alternative interpretations, and iteratively expand the search space.",
          "Keyword Expansion and Synonym Generation: Utilize NLP techniques (Word2Vec, BERT) to generate related keywords and synonyms for initial search terms.",
          "Location-Based Search Optimization: Develop location-based search strategies using geographic coordinates and place names for Kalamazoo, Battle Creek, and Grand Rapids.",
          "Niche Community Discovery Algorithms: Implement algorithms to identify niche communities based on link analysis, forum crawling, and social network analysis.",
          "Alternative Search Strategies: Develop alternative search strategies, including direct URL searches, platform-specific search terms, and niche community discovery methods.",
          "Anti-Bot Evasion Techniques: Implement and test anti-bot evasion techniques, including rotating user agents, random delays, and CAPTCHA solving. Emphasis on responsible and ethical implementation to avoid overwhelming target sites.",
        ],
      },
      {
        title: "Deliverables",
        items: ["Universal Abstraction Query Processing Engine", "Keyword Expansion and Synonym Generation Module", "Location-Based Search Optimization Module", "Niche Community Discovery Algorithms", "Alternative Search Strategies Documentation", "Anti-Bot Evasion Implementation"],
      },
      {
        title: "Metrics",
        items: ["Query Coverage: Percentage of the initial query's \"superposition state\" explored.", "Relevance Score: Measure of the relevance of retrieved results to the user's intent.", "Search Efficiency: Time required to complete a search query."],
      },
    ],
  },
  {
    id: 4,
    title: "Phase 4: Platform-Specific Search and Data Extraction",
    duration: 4,
    startWeek: 10,
    sections: [
      {
        title: "Goal",
        items: ["Implement platform-specific search and data extraction strategies for FetLife, SkipTheGames, Chaturbate, and other identified platforms."],
      },
      {
        title: "Actions",
        items: [
          "FetLife Search and Profile Extraction: Develop automated scripts to search FetLife for female and couples profiles in Southwest Michigan. Implement data extraction routines to collect relevant profile information (age, location, interests, etc.). Prioritize ethical data collection and anonymization.",
          "SkipTheGames Search and Profile Extraction: Develop automated scripts to search SkipTheGames for relevant profiles in Southwest Michigan. Implement data extraction routines to collect relevant profile information. Prioritize ethical data collection and anonymization.",
          "Chaturbate Search and Profile Extraction: Develop automated scripts to search Chaturbate for relevant profiles in Southwest Michigan, focusing on individuals advertising modeling or video creation options. Implement data extraction routines to collect relevant profile information. Prioritize ethical data collection and anonymization. Be extremely cautious about collecting any data from Chaturbate due to the sensitive nature of the platform.",
          "Porn Star/Former Porn Star Identification: Develop algorithms to identify porn stars or former porn stars advertising modeling or video creation options. Utilize image recognition and text analysis techniques. Prioritize ethical data collection and anonymization.",
          "Data Validation and Cleaning: Implement data validation and cleaning routines to ensure data accuracy and completeness.",
        ],
      },
      {
        title: "Deliverables",
        items: ["FetLife Search and Profile Extraction Scripts", "SkipTheGames Search and Profile Extraction Scripts", "Chaturbate Search and Profile Extraction Scripts (with extreme caution and ethical considerations)", "Porn Star/Former Porn Star Identification Algorithms", "Data Validation and Cleaning Routines"],
      },
      {
        title: "Metrics",
        items: ["Coverage of Target Sites: Percentage of relevant profiles found on each platform.", "Data Extraction Accuracy: Accuracy of data extracted from profiles.", "Data Completeness: Completeness of data extracted from profiles."],
      },
    ],
  },
  {
    id: 5,
    title: "Phase 5: Analysis and Reporting",
    duration: 4,
    startWeek: 14,
    isOngoing: true,
    sections: [
      {
        title: "Goal",
        items: ["Analyze the collected data and generate reports on adult party and play communities in Southwest Michigan. This phase requires careful consideration of how the data will be used and presented to avoid perpetuating harmful stereotypes or violating individual privacy."],
      },
      {
        title: "Actions",
        items: [
          "Data Analysis: Analyze the collected data to identify trends and patterns in adult party and play communities in Southwest Michigan.",
          "Report Generation: Generate reports summarizing the findings of the data analysis. Ensure reports are anonymized and do not contain any personally identifiable information.",
          "Ethical Review of Reports: Submit all reports to the Ethics Board for review and approval prior to dissemination.",
          "Continuous Monitoring and Adaptation: Continuously monitor ArchE's performance and adapt its strategies as needed.",
        ],
      },
      {
        title: "Deliverables",
        items: ["Data Analysis Reports", "Ethical Review Documentation", "Continuous Monitoring Reports"],
      },
      {
        title: "Metrics",
        items: ["Report Accuracy: Accuracy of the data presented in the reports.", "Report Completeness: Completeness of the data presented in the reports.", "Ethical Compliance: Adherence to ethical guidelines in report generation."],
      },
    ],
  },
];

export const mockProfileData: Profile[] = [
    { 
        id: 'fl1', 
        name: 'InkedUpReader', 
        age: 29, 
        location: 'Kalamazoo', 
        platform: 'FetLife', 
        profileType: 'Female', 
        tags: ['literature', 'tattoos', 'kink-positive', 'intellectual'], 
        imageUrl: 'https://placehold.co/300x300/0E7490/FFFFFF/png?text=IR', 
        description: 'Bookworm with a love for body art. Seeking connections that are as much mental as they are physical. Let\'s discuss Foucault and floggers.',
        extendedDescription: 'By day, I\'m a librarian, surrounded by stories. By night, I\'m exploring the narratives of the local kink scene. I am an experienced dominant, but value communication and consent above all else. Looking for a partner who is intelligent, articulate, and not afraid to explore their darker side. I am active in the Kalamazoo community and occasionally attend local munches.',
        extractedDetails: [
            { title: 'Communication Style', items: ['Articulate', 'Direct', 'Intellectual'] },
            { title: 'Availability', items: ['Prefers evenings', 'Attends local events'] },
            { title: 'Potential Interests', items: ['BDSM', 'Philosophy', 'Local community events'] }
        ]
    },
    { 
        id: 'stg1', 
        name: 'GR_Adventurers', 
        age: 36, 
        location: 'Grand Rapids', 
        platform: 'SkipTheGames', 
        profileType: 'Couple', 
        tags: ['professional', 'discreet', 'dining', 'lifestyle'], 
        imageUrl: 'https://placehold.co/300x300/7C3AED/FFFFFF/png?text=GR', 
        description: 'Professional couple, new to the scene. We value discretion and are looking to meet other open-minded couples for drinks and seeing where things go.',
        extendedDescription: 'We are a married, professional couple (M38/F36) who have recently started exploring the lifestyle. We\'re looking to dip our toes in slowly, starting with public meets for dinner or cocktails. We are active, enjoy hiking on weekends, and love exploring the Grand Rapids food scene. Absolutely no single men. Discretion is paramount for us due to our careers.',
        extractedDetails: [
            { title: 'Relationship Status', items: ['Married Couple', 'New to lifestyle'] },
            { title: 'Seeking', items: ['Couples only', 'Slow progression', 'Public first meet'] },
            { title: 'Stated Boundaries', items: ['High discretion required', 'No single men'] }
        ]
    },
    { 
        id: 'cb1', 
        name: 'Pixel_Vixen99', 
        age: 22, 
        location: 'Battle Creek', 
        platform: 'Chaturbate', 
        profileType: 'Female', 
        tags: ['gamer', 'cosplay', 'art', 'video creation'], 
        imageUrl: 'https://placehold.co/300x300/DB2777/FFFFFF/png?text=PV', 
        description: 'Gamer girl and digital artist. I do cosplay streams and create custom video content. Let\'s make something cool together!',
        extendedDescription: 'Hey! I\'m a full-time streamer and content creator. My main focus is on gaming (mostly RPGs and indie titles) and creating unique cosplay looks. I offer a menu of options for custom video and photo sets for my subscribers. I\'m always looking for creative collaboration ideas. This is my job, so please be professional and respectful when making inquiries.',
        extractedDetails: [
            { title: 'Services Offered', items: ['Streaming', 'Custom photo sets', 'Custom video content'] },
            { title: 'Primary Platform Focus', items: ['Gaming', 'Cosplay'] },
            { title: 'Professional Keywords', items: ['Subscribers', 'Inquiries', 'Collaboration'] }
        ]
    },
    { 
        id: 'fl2', 
        name: 'RopeAndRhyme', 
        age: 42, 
        location: 'Kalamazoo', 
        platform: 'FetLife', 
        profileType: 'Couple', 
        tags: ['shibari', 'poetry', 'workshops', 'mentor'], 
        imageUrl: 'https://placehold.co/300x300/0E7490/FFFFFF/png?text=RR', 
        description: 'Experienced couple passionate about the art of shibari and spoken word. We sometimes host educational workshops.',
        extendedDescription: 'We (M42/F39) have been part of the kink community for over 15 years. Our passion is the intersection of art and intimacy, primarily through Japanese rope bondage (shibari) and poetry. We are experienced riggers and bottoms. We occasionally host small, private workshops in the Kalamazoo area for those genuinely interested in learning. We are open to connecting with other experienced individuals or mentoring those who are serious and respectful.',
        extractedDetails: [
            { title: 'Expertise Level', items: ['Highly experienced (15+ years)', 'Mentors/Educators'] },
            { title: 'Specific Interests', items: ['Shibari', 'Spoken word poetry'] },
            { title: 'Community Involvement', items: ['Hosts private workshops'] }
        ]
    },
    {
        id: 'stg2',
        name: 'CityStarlight',
        age: 26,
        location: 'Grand Rapids',
        platform: 'SkipTheGames',
        profileType: 'Female',
        tags: ['traveling', 'no strings', 'upscale', 'companion'],
        imageUrl: 'https://placehold.co/300x300/7C3AED/FFFFFF/png?text=CS',
        description: 'Traveling for work and in Grand Rapids for the next few weeks. Looking for a charming guide to show me the best the city has to offer.',
        extendedDescription: 'I work in corporate consulting, which keeps me on the road. I\'ll be in GR until the end of the month. I\'m looking for a fun, intelligent, and respectful companion for upscale dinners, cocktails, and pleasant conversation. I\'m not looking for anything serious, just a mutually enjoyable time while I\'m here. I appreciate a man who knows how to treat a lady.',
        extractedDetails: [
            { title: 'Availability', items: ['Temporary (in town for a few weeks)'] },
            { title: 'Seeking', items: ['Short-term companion', 'No strings attached'] },
            { title: 'Sentiment Analysis', items: ['Prefers upscale experiences', 'Values respect and charm'] }
        ]
    },
    {
        id: 'fl3',
        name: 'Switchy_Spirit',
        age: 34,
        location: 'Battle Creek',
        platform: 'FetLife',
        profileType: 'Female',
        tags: ['switch', 'board games', 'psychology', 'demisexual'],
        imageUrl: 'https://placehold.co/300x300/0E7490/FFFFFF/png?text=SS',
        description: 'A versatile switch with a love for board games and deep conversation. Connection is key.',
        extendedDescription: 'I find the psychology of D/s fascinating and identify as a switch, though I lean dominant. Outside of kink, I\'m a huge board game geek (ask me about my Gloomhaven campaign!) and love to talk about anything from psychology to silly memes. I identify as demisexual, so building a genuine connection and trust is essential for me before any play happens. I\'m not into one-night stands.',
        extractedDetails: [
            { title: 'Kink Identity', items: ['Switch (dominant lean)', 'Requires emotional connection'] },
            { title: 'Stated Boundaries', items: ['No one-night stands', 'Connection before play'] },
            { title: 'Potential Interests', items: ['Board games', 'Psychology', 'Deep conversation'] }
        ]
    },
    {
        id: 'stg3',
        name: 'KzooHomebodies',
        age: 31,
        location: 'Kalamazoo',
        platform: 'SkipTheGames',
        profileType: 'Couple',
        tags: ['hosting', 'movies', 'cooking', 'low-key'],
        imageUrl: 'https://placehold.co/300x300/7C3AED/FFFFFF/png?text=KH',
        description: 'Homebody couple looking for another couple to join us for low-key fun. We prefer hosting movie nights and cooking together.',
        extendedDescription: 'We (M33/F31) are much more comfortable in our own space than out at loud bars. Our ideal evening involves trying a new recipe, opening a bottle of wine, and watching a good movie. We\'re looking for a like-minded couple who enjoys relaxed, intimate gatherings. We are 420-friendly. We require verification and a video chat before meeting to ensure everyone is comfortable and on the same page.',
        extractedDetails: [
            { title: 'Social Preference', items: ['Prefers hosting', 'Low-key gatherings'] },
            { title: 'Vetting Process', items: ['Requires verification', 'Requires video chat before meeting'] },
            { title: 'Mentioned Activities', items: ['Cooking', 'Movie nights', 'Wine'] }
        ]
    },
    {
        id: 'cb2',
        name: 'VintageVideoStar',
        age: 27,
        location: 'Grand Rapids',
        platform: 'Chaturbate',
        profileType: 'Female',
        tags: ['former porn star', 'retro', 'customs', 'modeling'],
        imageUrl: 'https://placehold.co/300x300/DB2777/FFFFFF/png?text=VS',
        description: 'Former adult film actress now creating my own retro-style content. Available for custom clips and artistic modeling projects.',
        extendedDescription: 'After a few years in the mainstream adult industry, I\'m now focused on producing my own content with a 70s/80s vintage aesthetic. I run my own site and offer a wide range of custom video services. I am also available for paid modeling work for photographers and artists who share my vision. All business is handled professionally and through my official channels.',
        extractedDetails: [
            { title: 'Professional Background', items: ['Former adult film actress', 'Independent content creator'] },
            { title: 'Services Offered', items: ['Custom video production', 'Artistic modeling'] },
            { title: 'Key Identifiers', items: ['Porn Star/Former Porn Star', 'Runs own website'] }
        ]
    }
];