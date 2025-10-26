const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs').promises;

// --- Configuration ---
const LEADS_FILE_PATH = path.join(__dirname, 'leads.json');
const USER_DATA_DIR = path.join(__dirname, 'chrome_user_data');
const GOOGLE_VOICE_URL = 'https://voice.google.com/'; // REVERTED: Start at the base URL, the script will handle sign-in.

// --- Main Function ---
async function runSelfDrivingSales() {
    console.log('->| Launching Self-Driving Sales Assistant...');

    // Launch Puppeteer with a persistent user data directory
    // This is the core of our secure login strategy.
    const browser = await puppeteer.launch({
        headless: false, // Set to false for the initial manual login
        userDataDir: USER_DATA_DIR,
        executablePath: '/usr/bin/google-chrome', // ADDED: Use standard Chrome instead of testing version
        args: [
            '--disable-infobars', // Hide "Chrome is being controlled..."
            '--window-size=1280,800',
            '--no-sandbox', // ADDED: Required for some Linux environments
            '--disable-setuid-sandbox' // ADDED: Often needed with --no-sandbox
        ],
    });
    const page = await browser.newPage();

    await page.setViewport({ width: 1280, height: 800 });

    console.log('->| Navigating to Google Voice...');
    await page.goto(GOOGLE_VOICE_URL, { waitUntil: 'networkidle2' });

    // --- One-Time Login Check ---
    const loggedInSelector = 'a[aria-label="Messages"]';
    try {
        await page.waitForSelector(loggedInSelector, { timeout: 15000 }); // Short timeout to check if already logged in
        console.log('->| SUCCESS: Logged in session found.');
    } catch (error) {
        console.log('->| Logged in session NOT found. Initiating sign-in flow...');
        
        // Actively click the "Sign in" button to navigate to the login page.
        // This is a much more robust method than relying on redirects.
        const signInButtonSelector = 'a[href*="accounts.google.com"]';
        try {
            await page.waitForSelector(signInButtonSelector, { timeout: 10000 });
            console.log('->| "Sign In" button found. Clicking to proceed to login page...');
            await page.click(signInButtonSelector);
        } catch (clickError) {
            console.error('->| Could not find the "Sign In" button on the page. Please manually click "Sign In" in the browser to proceed.');
        }

        console.log('->| ACTION REQUIRED: Please manually log in to your Google Voice account in the browser window.');
        console.log('->| Complete any 2FA prompts. This is a one-time setup.');
        console.log('->| Once you are successfully logged in, the script will wait for the application to load.');
        await page.waitForSelector(loggedInSelector, { timeout: 300000 }); // Wait up to 5 minutes for login and app load
        console.log('->| SUCCESS: Manual login detected. Session is now saved for future headless runs.');
    }
    
    // --- Placeholder for Core Logic ---
    console.log('\n->| Core logic would run here...');
    // 1. Load leads from leads.json
    // 2. Iterate through leads and send messages
    // 3. Monitor for responses
    // 4. Trigger handoff protocol

    console.log('\n->| Pausing for 10 seconds before closing...');
    await new Promise(resolve => setTimeout(resolve, 10000));


    await browser.close();
    console.log('->| Self-Driving Sales Assistant finished run.');
}


// --- Execute the main function ---
runSelfDrivingSales().catch(error => {
    console.error('An unhandled error occurred:', error);
    process.exit(1);
});
