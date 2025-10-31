const { chromium } = require('playwright');
const path = require('path');
const fs =require('fs').promises;
const { exec } = require('child_process');

// --- Configuration ---
const LEADS_FILE_PATH = path.join(__dirname, 'leads.json');
const USER_DATA_DIR = path.join(__dirname, 'google_messages_data'); // Persist login
const GOOGLE_MESSAGES_URL = 'https://messages.google.com/web/';
const POLLING_INTERVAL_MS = 15000; // Check every 15 seconds
const HEADLESS_MODE = false; // Set to true to run in the background

// --- Locators for Google Messages ---
// These are more robust selectors that are less likely to change.
const SELECTORS = {
    CONVERSATION_LIST: 'mws-conversation-list-item',
    CONVERSATION_ITEM_NAME: '.name',
    NEW_CONVERSATION_BUTTON: 'a[href="/web/conversations/new"]',
    CONTACT_INPUT: 'input[placeholder="Type a name, phone number, or email"]',
    START_CONVERSATION_BUTTON: 'button.m3-button--label',
    MESSAGE_TEXT_AREA: 'textarea[placeholder="Text message"]',
    SEND_BUTTON: 'button[aria-label="Send message"]',
    MESSAGE_CONTENT: 'div.text-msg-content',
    SPINNER_OVERLAY: 'div.spinner-container-overlay'
};

// --- Helper Functions ---
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms));

const log = (level, message) => {
    const timestamp = new Date().toISOString();
    console.log(`[${timestamp}] [${level.toUpperCase()}] ${message}`);
};

// --- Core Application Logic ---

/**
 * Initializes the browser and navigates to the Google Messages page.
 * Handles the initial login and QR code scanning process.
 */
async function initializeBrowser() {
    log('info', 'Launching browser and setting up context...');
    const context = await chromium.launchPersistentContext(USER_DATA_DIR, {
        headless: HEADLESS_MODE,
        viewport: { width: 1280, height: 900 },
        args: ['--no-sandbox', '--disable-setuid-sandbox'],
    });

    const page = await context.newPage();
    log('info', `Navigating to ${GOOGLE_MESSAGES_URL}`);
    await page.goto(GOOGLE_MESSAGES_URL, { waitUntil: 'load', timeout: 90000 });

    try {
        log('info', 'Waiting for interface to load...');
        await page.waitForSelector(SELECTORS.NEW_CONVERSATION_BUTTON, { timeout: 60000 });
        log('success', 'Interface loaded successfully.');
    } catch (e) {
        log('warn', 'Main interface not found. This might be a first run.');
        log('warn', 'Please scan the QR code with your phone to link Google Messages.');
        await page.waitForSelector(SELECTORS.NEW_CONVERSATION_BUTTON, { timeout: 180000 });
        log('success', 'Login successful! Continuing...');
    }
    return { context, page };
}

/**
 * Main application loop to process leads.
 */
async function main() {
    const { context, page } = await initializeBrowser();

    const mainLoop = async () => {
        try {
            await processNewLeads(page);
            await monitorForResponses(page);
            await generateAndSendReplies(page);
        } catch (error) {
            log('error', `An error occurred in the main loop: ${error.message}`);
            log('info', 'Attempting to recover by refreshing the page...');
            await page.reload({ waitUntil: 'load', timeout: 60000 });
        }
    };

    log('info', `Starting main loop. Will check every ${POLLING_INTERVAL_MS / 1000} seconds.`);
    setInterval(mainLoop, POLLING_INTERVAL_MS);

    process.on('SIGINT', async () => {
        log('info', 'SIGINT received. Shutting down gracefully.');
        await context.close();
        process.exit(0);
    });
}

/**
 * Processes leads with the status 'new'.
 */
async function processNewLeads(page) {
    log('info', 'Checking for new leads...');
    const leads = await readLeads();
    const newLeads = leads.filter(l => l.status === 'new');

    if (newLeads.length === 0) {
        log('info', 'No new leads to process.');
        return;
    }

    for (const lead of newLeads) {
        try {
            log('info', `Processing new lead: ${lead.name} (${lead.phone})`);
            await startConversationWith(page, lead.phone);
            await sendMessage(page, lead.message_to_send);
            lead.status = 'contacted';
            lead.conversation = [{ from: 'arche', message: lead.message_to_send, timestamp: new Date().toISOString() }];
            await writeLeads(leads);
            log('success', `Initial message sent to ${lead.name}.`);
            await page.goto(GOOGLE_MESSAGES_URL); // Return to main screen
        } catch (error) {
            log('error', `Failed to process new lead ${lead.name}: ${error.message}`);
            await page.goto(GOOGLE_MESSAGES_URL); // Attempt to recover
        }
    }
}

/**
 * Monitors for responses from leads.
 */
async function monitorForResponses(page) {
    log('info', 'Monitoring for responses...');
    const leads = await readLeads();
    const leadsToMonitor = leads.filter(l => l.status === 'contacted' || l.status === 'responded_to');

    if (leadsToMonitor.length === 0) {
        log('info', 'No leads to monitor for responses.');
        return;
    }

    for (const lead of leadsToMonitor) {
        try {
            log('info', `Checking for response from ${lead.name}`);
            const lastMessage = await findConversationAndReadLastMessage(page, lead.name);

            if (lastMessage) {
                const lastKnownMessage = lead.conversation[lead.conversation.length - 1];
                if (lastMessage.isFromLead && lastMessage.text !== lastKnownMessage.message) {
                    log('success', `New message from ${lead.name}: "${lastMessage.text}"`);
                    lead.conversation.push({ from: 'lead', message: lastMessage.text, timestamp: new Date().toISOString() });
                    lead.status = 'response_received';
                    await writeLeads(leads);
                }
            }
        } catch (error) {
            log('error', `Failed to monitor lead ${lead.name}: ${error.message}`);
            await page.goto(GOOGLE_MESSAGES_URL); // Attempt to recover
        }
    }
}

// --- New Helper Functions ---

async function readLeads() {
    const data = await fs.readFile(LEADS_FILE_PATH, 'utf-8');
    return JSON.parse(data);
}

async function writeLeads(leads) {
    await fs.writeFile(LEADS_FILE_PATH, JSON.stringify(leads, null, 2));
}

async function startConversationWith(page, phone) {
    await page.click(SELECTORS.NEW_CONVERSATION_BUTTON);
    await page.waitForSelector(SELECTORS.CONTACT_INPUT);
    await page.type(SELECTORS.CONTACT_INPUT, phone, { delay: 100 });
    await page.keyboard.press('Enter');
}

async function sendMessage(page, message) {
    await page.waitForSelector(SELECTORS.MESSAGE_TEXT_AREA);
    await page.type(SELECTORS.MESSAGE_TEXT_AREA, message, { delay: 120 });
    await page.click(SELECTORS.SEND_BUTTON);
    await delay(2000); // Wait for message to appear sent
}

async function findConversationAndReadLastMessage(page, name) {
    // This is a simplified version. A real implementation might need to scroll.
    const conversations = await page.$$(SELECTORS.CONVERSATION_LIST);
    for (const convo of conversations) {
        const convoName = await convo.$eval(SELECTORS.CONVERSATION_ITEM_NAME, el => el.textContent);
        if (convoName.trim().toLowerCase() === name.trim().toLowerCase()) {
            await convo.click();
            await page.waitForSelector(SELECTORS.MESSAGE_CONTENT);
            await delay(1000); // Let messages load
            const messages = await page.$$(SELECTORS.MESSAGE_CONTENT);
            if (messages.length > 0) {
                const lastMessageEl = messages[messages.length - 1];
                const text = await lastMessageEl.innerText();
                // This is a heuristic. We assume if it's not marked as "You ·", it's from the lead.
                const isFromLead = !(await lastMessageEl.textContent()).includes("You ·");
                return { text, isFromLead };
            }
            return null;
        }
    }
    log('warn', `Conversation with "${name}" not found on the first screen.`);
    return null;
}

/**
 * Generates and sends replies to leads who have responded.
 */
async function generateAndSendReplies(page) {
    log('info', 'Checking for leads who need a reply...');
    const leads = await readLeads();
    const leadsToReplyTo = leads.filter(l => l.status === 'response_received');

    if (leadsToReplyTo.length === 0) {
        log('info', 'No leads waiting for a reply.');
        return;
    }

    for (const lead of leadsToReplyTo) {
        try {
            log('info', `Generating reply for ${lead.name}...`);
            const response = await generateAiResponse(lead.conversation);

            if (response && response.message_to_send) {
                await startConversationWith(page, lead.phone);
                await sendMessage(page, response.message_to_send);
                lead.status = 'replied_to';
                lead.conversation.push({ from: 'arche', message: response.message_to_send, timestamp: new Date().toISOString() });
                await writeLeads(leads);
                log('success', `Reply sent to ${lead.name}.`);
                await page.goto(GOOGLE_MESSAGES_URL); // Return home
            } else {
                log('error', `Failed to generate AI response for ${lead.name}. Error: ${response.error}`);
            }
        } catch (error) {
            log('error', `Failed to send reply to ${lead.name}: ${error.message}`);
            await page.goto(GOOGLE_MESSAGES_URL); // Recover
        }
    }
}

function generateAiResponse(conversationHistory) {
    return new Promise((resolve) => {
        const historyString = JSON.stringify(conversationHistory);
        const command = `python3 "${path.join(__dirname, 'response_generator.py')}" '${historyString}'`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                log('error', `Python script execution error: ${error.message}`);
                resolve({ error: error.message });
            } else if (stderr) {
                log('error', `Python script stderr: ${stderr}`);
                resolve({ error: stderr });
            } else {
                try {
                    const response = JSON.parse(stdout);
                    resolve(response);
                } catch (e) {
                    log('error', `Error parsing Python script output: ${e.message}`);
                    resolve({ error: e.message });
                }
            }
        });
    });
}

main().catch(err => {
    log('critical', `A critical, unrecoverable error occurred: ${err.stack}`);
    process.exit(1);
});
