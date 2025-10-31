import puppeteer, { Browser, Page } from 'puppeteer';
import { Profile } from '../models/profile.model';
import { ExtractionResult, SearchConfig, VerificationRule } from '../types';
import crypto from 'crypto';

interface PlatformHandler {
  search: (config: SearchConfig, page: Page) => Promise<any[]>;
  extractProfile: (rawData: any) => Profile | null;
  verifyDataAccuracy: (profile: Profile) => boolean;
}

/**
 * ArchE Data Gathering Service
 * Focuses on real data extraction with maximum identifying information for verification
 */
class ArcheService {
  private browser: Browser | null = null;
  private verificationRules: VerificationRule[];

  constructor() {
    // Initialize verification rules for data accuracy
    this.verificationRules = [
      { field: 'name', required: true, minLength: 2 },
      { field: 'location', required: true },
      { field: 'platform', required: true },
      { field: 'profileType', required: true },
      { field: 'age', required: true, min: 18, max: 120 },
      { field: 'description', required: false, minLength: 0 },
      { field: 'imageUrl', required: false },
      { field: 'tags', required: false }
    ];
  }

  /**
   * Main entry point for data extraction
   * Extracts comprehensive identifying information for accuracy
   */
  async runExtraction(): Promise<ExtractionResult> {
    const startTime = Date.now();
    const result: ExtractionResult = {
      success: false,
      profiles: [],
      metadata: {
        extractionDate: new Date(),
        source: 'ArchE Data Collector',
        profilesFound: 0,
        processingTime: 0
      },
      errors: []
    };

    try {
      // Initialize browser for data extraction
      this.browser = await this.initializeBrowser();
      
      // Define search configurations for each platform
      const searchConfigs: SearchConfig[] = [
        {
          platform: 'fetlife',
          location: 'Michigan',
          keywords: ['provider', 'professional', 'kalamazoo', 'grand rapids', 'battle creek'],
          maxResults: 50 // Extract more comprehensive data
        },
        {
          platform: 'skipthegames',
          location: 'Michigan',
          keywords: ['escort', 'provider', 'companion'],
          maxResults: 50
        },
        {
          platform: 'chaturbate',
          location: 'Michigan',
          keywords: ['cam model', 'streamer'],
          maxResults: 30
        }
      ];

      // Process each configuration
      for (const config of searchConfigs) {
        try {
          const platformProfiles = await this.extractFromPlatform(config);
          
          // Verify and filter for accurate profiles
          const verifiedProfiles = platformProfiles.filter(profile => 
            this.verifyDataAccuracy(profile)
          );
          
          result.profiles.push(...verifiedProfiles);
        } catch (error) {
          result.errors?.push(`Platform ${config.platform} extraction failed: ${error}`);
        }
      }

      // Store profiles in database
      if (result.profiles.length > 0) {
        await this.storeProfiles(result.profiles);
      }

      result.success = result.profiles.length > 0;
      result.metadata.profilesFound = result.profiles.length;
      result.metadata.processingTime = Date.now() - startTime;

    } catch (error) {
      result.errors?.push(`Extraction process failed: ${error}`);
    } finally {
      if (this.browser) {
        await this.browser.close();
      }
    }

    return result;
  }

  /**
   * Initialize Puppeteer browser for data extraction
   */
  private async initializeBrowser(): Promise<Browser> {
    return await puppeteer.launch({
      headless: 'new',
      args: [
        '--no-sandbox',
        '--disable-setuid-sandbox',
        '--disable-blink-features=AutomationControlled'
      ],
      ignoreHTTPSErrors: true
    });
  }

  /**
   * Extract data from a specific platform
   */
  private async extractFromPlatform(config: SearchConfig): Promise<Profile[]> {
    const page = await this.browser!.newPage();
    
    try {
      // Set realistic user agent for better data access
      await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

      // Navigate to platform with comprehensive search
      const platformUrl = this.getPlatformUrl(config);
      await page.goto(platformUrl, { waitUntil: 'networkidle2', timeout: 30000 });

      // Extract all available identifying information
      const rawProfiles = await this.extractRawProfiles(page, config);
      
      // Transform to Profile objects with maximum detail
      const profiles = rawProfiles
        .map(raw => this.transformToProfile(raw, config))
        .filter(profile => profile !== null && this.isValidProfile(profile));

      return profiles as Profile[];
    } finally {
      await page.close();
    }
  }

  /**
   * Extract comprehensive raw profile data from the page
   */
  private async extractRawProfiles(page: Page, config: SearchConfig): Promise<any[]> {
    try {
      // Wait for content to load
      await page.waitForSelector('body', { timeout: 10000 });

      // Scroll to load more content
      await page.evaluate(() => {
        window.scrollTo(0, document.body.scrollHeight);
      });
      await new Promise(resolve => setTimeout(resolve, 2000));

      // Extract comprehensive profile data
      const profiles = await page.evaluate((platformName, maxResults) => {
        const profileElements = document.querySelectorAll(
          '[data-profile], .profile-card, .user-card, .member-card, .profile, [class*="profile"], [class*="user"], [class*="member"]'
        );
        const rawData: any[] = [];

        Array.from(profileElements).forEach((element, index) => {
          if (index >= maxResults) return;
          
          const profile: any = {
            id: null,
            name: null,
            username: null,
            displayName: null,
            age: null,
            location: null,
            region: null,
            city: null,
            platform: platformName,
            profileUrl: null,
            imageUrl: null,
            images: [],
            description: null,
            bio: null,
            extendedDescription: null,
            tags: [],
            profileType: null,
            status: null,
            online: false,
            lastSeen: null,
            verificationStatus: null,
            accountAge: null,
            rating: null,
            reviews: null,
            contactInfo: {},
            socialLinks: {},
            pricing: {},
            availability: {},
            extractedDetails: []
          };

          // Extract unique identifier
          const profileIdEl = element.querySelector('[data-id], [data-user-id], [data-profile-id]');
          const href = element.getAttribute('href') || element.querySelector('a')?.href;
          profile.id = profileIdEl?.getAttribute('data-id') || 
                       profileIdEl?.getAttribute('data-user-id') || 
                       href?.split('/').pop()?.split('?')[0] ||
                       `extracted_${platformName}_${index}_${Date.now()}`;

          // Extract name (check multiple possible selectors)
          const nameSelectors = ['.name', '.username', '.display-name', '[data-name]', 
                               'h1, h2, h3, h4', '.profile-name', '.user-name'];
          for (const selector of nameSelectors) {
            const el = element.querySelector(selector);
            if (el?.textContent?.trim()) {
              profile.name = el.textContent.trim();
              break;
            }
          }

          // Extract username separately
          const usernameEl = element.querySelector('.username, [data-username]');
          profile.username = usernameEl?.textContent?.trim() || null;

          // Extract display name
          const displayNameEl = element.querySelector('.display-name, .screen-name');
          profile.displayName = displayNameEl?.textContent?.trim() || null;

          // Extract age (check multiple formats)
          const ageEl = element.querySelector('.age, [data-age], [title*="age"]');
          if (ageEl) {
            const ageText = ageEl.textContent || ageEl.getAttribute('title') || '';
            const ageMatch = ageText.match(/\d+/);
            profile.age = ageMatch ? parseInt(ageMatch[0]) : null;
          }

          // Extract location information
          const locationSelectors = ['.location', '.city', '.region', '[data-location]', 
                                   '.profile-location', '.user-location', '[title*="location"]'];
          for (const selector of locationSelectors) {
            const el = element.querySelector(selector);
            if (el?.textContent?.trim() || el?.getAttribute('title')) {
              profile.location = el.textContent?.trim() || el.getAttribute('title') || null;
              break;
            }
          }

          // Extract city and region separately
          const cityEl = element.querySelector('.city, [data-city]');
          profile.city = cityEl?.textContent?.trim() || null;
          
          const regionEl = element.querySelector('.region, .state, [data-region]');
          profile.region = regionEl?.textContent?.trim() || null;

          // Extract profile URL
          const linkEl = element.querySelector('a[href*="profile"], a[href*="user"], a[href]');
          profile.profileUrl = linkEl?.getAttribute('href') || 
                              element.getAttribute('href') || 
                              null;
          if (profile.profileUrl && !profile.profileUrl.startsWith('http')) {
            profile.profileUrl = new URL(profile.profileUrl, window.location.href).href;
          }

          // Extract images (primary and all)
          const imgEl = element.querySelector('img');
          if (imgEl) {
            profile.imageUrl = imgEl.getAttribute('src') || 
                              imgEl.getAttribute('data-src') || 
                              imgEl.getAttribute('data-lazy') ||
                              null;
          }

          // Extract all images
          const allImages = Array.from(element.querySelectorAll('img')).map(img => 
            img.getAttribute('src') || img.getAttribute('data-src') || null
          ).filter(Boolean);
          profile.images = allImages;

          // Extract description/bio
          const descSelectors = ['.description', '.bio', '.about', '[data-description]', 
                               '.profile-description', '.user-bio'];
          for (const selector of descSelectors) {
            const el = element.querySelector(selector);
            if (el?.textContent?.trim()) {
              profile.description = el.textContent.trim();
              break;
            }
          }

          // Extract bio separately
          const bioEl = element.querySelector('.bio, .about-me, .user-bio');
          profile.bio = bioEl?.textContent?.trim() || null;

          // Extract extended description
          const extendedDescEl = element.querySelector('.extended-description, .full-description');
          profile.extendedDescription = extendedDescEl?.textContent?.trim() || null;

          // Extract tags
          const tagElements = element.querySelectorAll('.tag, [data-tag], .category, .interest, [class*="tag"]');
          profile.tags = Array.from(tagElements)
            .map(el => el.textContent?.trim())
            .filter(Boolean)
            .filter(tag => tag.length > 0);

          // Extract profile type
          const typeEl = element.querySelector('.profile-type, .category, [data-type]');
          profile.profileType = typeEl?.textContent?.trim().toLowerCase() || null;

          // Extract status
          const statusEl = element.querySelector('.status, .online-status, [data-status]');
          profile.status = statusEl?.textContent?.trim() || null;

          // Extract online status
          profile.online = element.classList.contains('online') || 
                          element.querySelector('.online-indicator') !== null ||
                          false;

          // Extract last seen
          const lastSeenEl = element.querySelector('.last-seen, [data-last-seen]');
          profile.lastSeen = lastSeenEl?.textContent?.trim() || null;

          // Extract verification status
          profile.verificationStatus = element.querySelector('.verified, .verified-badge') !== null;

          // Extract account age (if available)
          const accountAgeEl = element.querySelector('.account-age, [data-joined]');
          profile.accountAge = accountAgeEl?.textContent?.trim() || null;

          // Extract rating
          const ratingEl = element.querySelector('.rating, .stars, [data-rating]');
          profile.rating = ratingEl?.textContent?.trim() || 
                          ratingEl?.getAttribute('data-rating') ||
                          null;

          // Extract reviews count
          const reviewsEl = element.querySelector('.reviews-count, [data-reviews]');
          profile.reviews = reviewsEl?.textContent?.trim() || null;

          // Extract contact information
          const phoneEl = element.querySelector('[data-phone], .phone, a[href^="tel:"]');
          if (phoneEl) {
            profile.contactInfo.phone = phoneEl.textContent?.trim() || phoneEl.getAttribute('href')?.replace('tel:', '');
          }

          const emailEl = element.querySelector('[data-email], .email, a[href^="mailto:"]');
          if (emailEl) {
            profile.contactInfo.email = emailEl.textContent?.trim() || emailEl.getAttribute('href')?.replace('mailto:', '');
          }

          // Extract social links
          Array.from(element.querySelectorAll('a[href*="twitter"], a[href*="instagram"], a[href*="facebook"]')).forEach(link => {
            const href = link.getAttribute('href');
            const platform = href?.includes('twitter') ? 'twitter' :
                           href?.includes('instagram') ? 'instagram' :
                           href?.includes('facebook') ? 'facebook' : 'other';
            profile.socialLinks[platform] = href;
          });

          // Extract pricing information
          const priceEl = element.querySelector('.price, .rate, [data-price]');
          profile.pricing.rate = priceEl?.textContent?.trim() || null;

          // Extract availability
          const availEl = element.querySelector('.availability, [data-availability]');
          profile.availability.current = availEl?.textContent?.trim() || null;

          // Build extracted details
          profile.extractedDetails = [];
          
          if (profile.username) {
            profile.extractedDetails.push({ title: 'Username', items: [profile.username] });
          }
          if (profile.status) {
            profile.extractedDetails.push({ title: 'Status', items: [profile.status] });
          }
          if (profile.online) {
            profile.extractedDetails.push({ title: 'Online Status', items: ['Currently Online'] });
          }
          if (profile.verificationStatus) {
            profile.extractedDetails.push({ title: 'Verification', items: ['Verified Account'] });
          }
          if (profile.rating) {
            profile.extractedDetails.push({ title: 'Rating', items: [profile.rating] });
          }
          if (profile.reviews) {
            profile.extractedDetails.push({ title: 'Reviews', items: [profile.reviews] });
          }
          if (Object.keys(profile.contactInfo).length > 0) {
            profile.extractedDetails.push({ 
              title: 'Contact Info', 
              items: Object.entries(profile.contactInfo).map(([k, v]) => `${k}: ${v}`) 
            });
          }
          if (Object.keys(profile.socialLinks).length > 0) {
            profile.extractedDetails.push({ 
              title: 'Social Links', 
              items: Object.values(profile.socialLinks) 
            });
          }
          if (profile.pricing.rate) {
            profile.extractedDetails.push({ title: 'Pricing', items: [profile.pricing.rate] });
          }
          if (profile.accountAge) {
            profile.extractedDetails.push({ title: 'Account Age', items: [profile.accountAge] });
          }
          if (profile.lastSeen) {
            profile.extractedDetails.push({ title: 'Last Seen', items: [profile.lastSeen] });
          }

          // Only add if we have minimum required data
          if (profile.name || profile.description || profile.username) {
            rawData.push(profile);
          }
        });

        return rawData;
      }, config.platform, config.maxResults || 50);

      return profiles;
    } catch (error) {
      console.error(`Error extracting profiles from ${config.platform}:`, error);
      return [];
    }
  }

  /**
   * Transform raw data into Profile object with comprehensive details
   */
  private transformToProfile(raw: any, config: SearchConfig): Profile | null {
    try {
      // Use the most complete identifying information available
      const profile: Profile = {
        id: raw.id || this.generateUniqueId(raw),
        name: this.selectBestName(raw),
        age: raw.age || 0,
        location: this.selectBestLocation(raw, config.location),
        platform: config.platform as any,
        profileType: this.inferProfileType(raw),
        tags: this.cleanTags(raw.tags || []),
        imageUrl: raw.imageUrl || raw.images?.[0] || '',
        description: this.combineDescriptions(raw),
        extendedDescription: this.buildExtendedDescription(raw),
        extractedDetails: this.buildExtractedDetails(raw)
      };

      return profile;
    } catch (error) {
      console.error('Profile transformation failed:', error);
      return null;
    }
  }

  /**
   * Generate unique ID from available data
   */
  private generateUniqueId(raw: any): string {
    const identifier = raw.username || raw.profileUrl || raw.name || crypto.randomUUID();
    return identifier.toString().replace(/[^a-zA-Z0-9-_]/g, '_').substring(0, 100);
  }

  /**
   * Select the best available name
   */
  private selectBestName(raw: any): string {
    return raw.displayName || raw.name || raw.username || 'Unknown';
  }

  /**
   * Select the best available location
   */
  private selectBestLocation(raw: any, fallback: string): string {
    return raw.city || raw.region || raw.location || fallback || 'Unknown';
  }

  /**
   * Clean and validate tags
   */
  private cleanTags(tags: any[]): string[] {
    if (!Array.isArray(tags)) return [];
    return tags
      .filter(tag => tag && typeof tag === 'string' && tag.length > 0)
      .map(tag => tag.trim())
      .filter((tag, index, self) => self.indexOf(tag) === index); // Remove duplicates
  }

  /**
   * Combine all descriptions
   */
  private combineDescriptions(raw: any): string {
    const parts = [];
    if (raw.description) parts.push(raw.description);
    if (raw.bio && raw.bio !== raw.description) parts.push(raw.bio);
    return parts.join('\n\n') || '';
  }

  /**
   * Build extended description
   */
  private buildExtendedDescription(raw: any): string {
    const sections = [];
    
    if (raw.username) sections.push(`Username: ${raw.username}`);
    if (raw.status) sections.push(`Status: ${raw.status}`);
    if (raw.online !== null) sections.push(`Online: ${raw.online ? 'Yes' : 'No'}`);
    if (raw.verificationStatus) sections.push('Verified: Yes');
    if (raw.rating) sections.push(`Rating: ${raw.rating}`);
    if (raw.reviews) sections.push(`Reviews: ${raw.reviews}`);
    if (raw.profileUrl) sections.push(`Profile: ${raw.profileUrl}`);
    if (raw.accountAge) sections.push(`Member Since: ${raw.accountAge}`);
    if (raw.lastSeen) sections.push(`Last Seen: ${raw.lastSeen}`);
    if (raw.tags && raw.tags.length > 0) sections.push(`Tags: ${raw.tags.join(', ')}`);
    
    return sections.join('\n') || '';
  }

  /**
   * Build extracted details array
   */
  private buildExtractedDetails(raw: any): any[] {
    const details = [];

    if (raw.username && raw.username !== raw.name) {
      details.push({ title: 'Username', items: [raw.username] });
    }
    
    if (raw.description) {
      details.push({ title: 'Description', items: [raw.description] });
    }
    
    if (raw.tags && raw.tags.length > 0) {
      details.push({ title: 'Tags & Interests', items: raw.tags });
    }
    
    if (raw.status) {
      details.push({ title: 'Status', items: [raw.status] });
    }
    
    if (raw.verificationStatus) {
      details.push({ title: 'Verification', items: ['Verified'] });
    }
    
    if (raw.online) {
      details.push({ title: 'Status', items: ['Online'] });
    }
    
    if (raw.rating) {
      details.push({ title: 'Rating', items: [raw.rating] });
    }
    
    if (raw.reviews) {
      details.push({ title: 'Review Count', items: [raw.reviews] });
    }
    
    if (raw.profileUrl) {
      details.push({ title: 'Profile URL', items: [raw.profileUrl] });
    }
    
    if (raw.accountAge) {
      details.push({ title: 'Member Since', items: [raw.accountAge] });
    }

    return details;
  }

  /**
   * Infer profile type from available data
   */
  private inferProfileType(raw: any): 'provider' | 'hobbyist' | 'enthusiast' {
    const combined = `${raw.profileType || ''} ${raw.description || ''} ${raw.tags?.join(' ') || ''}`.toLowerCase();

    if (combined.includes('provider') || combined.includes('professional') || 
        combined.includes('escort') || combined.includes('companion')) {
      return 'provider';
    }
    
    if (combined.includes('hobbyist') || combined.includes('casual') || 
        combined.includes('amateur')) {
      return 'hobbyist';
    }
    
    return 'enthusiast';
  }

  /**
   * Verify data accuracy and completeness
   */
  private verifyDataAccuracy(profile: Profile): boolean {
    // Must have identifying information
    if (!profile.name || profile.name === 'Unknown') {
      return false;
    }

    // Location must be present
    if (!profile.location || profile.location === 'Unknown') {
      return false;
    }

    // Platform must be valid
    if (!profile.platform) {
      return false;
    }

    // Age must be reasonable (if provided)
    if (profile.age && (profile.age < 18 || profile.age > 120)) {
      return false;
    }

    // Must have at least some descriptive content
    const hasContent = profile.description || profile.tags.length > 0;
    if (!hasContent) {
      return false;
    }

    return true;
  }

  /**
   * Validate profile before storing
   */
  private isValidProfile(profile: Profile): boolean {
    // Name is critical
    if (!profile.name || profile.name.trim().length < 2) return false;
    
    // Location is critical
    if (!profile.location || profile.location.trim().length < 2) return false;
    
    // Platform must be valid
    const validPlatforms = ['fetlife', 'skipthegames', 'chaturbate'];
    if (!profile.platform || !validPlatforms.includes(profile.platform.toLowerCase())) return false;
    
    return true;
  }

  /**
   * Store profiles in MongoDB with conflict resolution
   */
  private async storeProfiles(profiles: Profile[]): Promise<void> {
    for (const profile of profiles) {
      try {
        // Use upsert with unique ID to handle duplicates
        await Profile.findOneAndUpdate(
          { id: profile.id },
          profile,
          { upsert: true, new: true, setDefaultsOnInsert: true }
        );
      } catch (error) {
        console.error(`Failed to store profile ${profile.id}:`, error);
      }
    }
  }

  /**
   * Get platform URL based on configuration
   */
  private getPlatformUrl(config: SearchConfig): string {
    const baseUrls: Record<string, string> = {
      fetlife: 'https://fetlife.com',
      skipthegames: 'https://skipthegames.com',
      chaturbate: 'https://chaturbate.com'
    };

    const baseUrl = baseUrls[config.platform.toLowerCase()] || 'https://example.com';
    const location = encodeURIComponent(config.location);
    const keyword = config.keywords?.[0] || '';
    const keywordParam = keyword ? `&keyword=${encodeURIComponent(keyword)}` : '';
    
    return `${baseUrl}/search?location=${location}${keywordParam}`;
  }
}

export const archeService = new ArcheService();
export const runExtraction = () => archeService.runExtraction();
