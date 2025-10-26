require('dotenv').config();
const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');

puppeteer.use(StealthPlugin());

// Custom promise-based timeout function
function wait(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

const GOOGLE_EMAIL = process.env.GOOGLE_EMAIL;
const GOOGLE_PASSWORD = process.env.GOOGLE_PASSWORD;
const TARGET_PHONE_NUMBER = process.env.TARGET_PHONE_NUMBER;

async function scrape() {
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--incognito', '--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();

    const url = 'https://voice.google.com/';

    // Wait for the sign-in button and click it
    await page.goto(url);
    await page.waitForSelector('a.signUpLink[href]');
    await page.click('a.signuplink[href]');
    await wait(250);

    // Wait for the username input, type the username and press Enter
    await page.waitForSelector('input[type="email"]');
    await wait(575);
    await page.type('input[type="email"]', GOOGLE_EMAIL);
    await page.keyboard.press('Enter');
    await wait(1750);

    // Wait for the password input, type the password and press Enter
    await page.waitForSelector('input[type="password"]', { visible: true });
    await wait(250);
    await page.type('input[type="password"]', GOOGLE_PASSWORD);
    await wait(250);
    await page.keyboard.press('Enter');

    // Wait for navigation to complete login
    await page.waitForNavigation();

    console.log('Logged in successfully');
    await wait(250);

    // Navigate to send message
    await page.waitForSelector('button[aria-label="Send a message"]');
    await page.click('button[aria-label="Send a message"]');
    await wait(250);

    // Wait for the phone number input, type the target phone number
    await page.waitForSelector('input[aria-label="Phone number"]');
    await page.type('input[aria-label="Phone number"]', TARGET_PHONE_NUMBER);
    await wait(250);

    // Wait for the message input, type the message
    const messageContent = process.argv[2] || 'Hello from Puppeteer!';
    await page.waitForSelector('textarea[aria-label="Text message"]');
    await page.type('textarea[aria-label="Text message"]', messageContent);
    await wait(250);

    // Send the message
    await page.keyboard.press('Enter');

    console.log('Message sent successfully');

    // Close the browser
    // await browser.close();
    return (page, browser);
}

scrape();