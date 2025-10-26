const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { createHash } = require('crypto');

class CaptureManager {
    constructor(config = {}) {
        this.config = {
            screenshotDir: config.screenshotDir || path.join(__dirname, 'screenshots'),
            htmlDir: config.htmlDir || path.join(__dirname, 'html_captures'),
            pdfDir: config.pdfDir || path.join(__dirname, 'pdf_captures'),
            maxRetries: config.maxRetries || 3,
            quality: config.quality || 80,
            ...config
        };

        this.initialize();
    }

    initialize() {
        // Create necessary directories
        [this.config.screenshotDir, this.config.htmlDir, this.config.pdfDir].forEach(dir => {
            if (!fs.existsSync(dir)) {
                fs.mkdirSync(dir, { recursive: true });
            }
        });
    }

    generateFilename(prefix, extension) {
        const timestamp = new Date().toISOString().replace(/:/g, '-');
        const randomSuffix = crypto.randomBytes(4).toString('hex');
        return `${prefix}_${timestamp}_${randomSuffix}.${extension}`;
    }

    async captureScreenshot(page, options = {}) {
        const {
            fullPage = true,
            quality = this.config.quality,
            type = 'png',
            element = null,
            retryCount = 0
        } = options;

        try {
            let screenshot;
            if (element) {
                screenshot = await element.screenshot({
                    type,
                    quality: type === 'jpeg' ? quality : undefined
                });
            } else {
                screenshot = await page.screenshot({
                    fullPage,
                    type,
                    quality: type === 'jpeg' ? quality : undefined
                });
            }

            const filename = this.generateFilename('screenshot', type);
            const filepath = path.join(this.config.screenshotDir, filename);
            
            await fs.promises.writeFile(filepath, screenshot);
            return {
                success: true,
                filepath,
                type,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            if (retryCount < this.config.maxRetries) {
                console.error(`Screenshot capture failed, retrying (${retryCount + 1}/${this.config.maxRetries})...`);
                return this.captureScreenshot(page, { ...options, retryCount: retryCount + 1 });
            }
            throw error;
        }
    }

    async captureHTML(page, options = {}) {
        const {
            includeStyles = true,
            includeScripts = true,
            format = true,
            retryCount = 0
        } = options;

        try {
            const html = await page.evaluate((includeStyles, includeScripts) => {
                const getStyles = () => {
                    const styles = Array.from(document.styleSheets)
                        .map(sheet => {
                            try {
                                return Array.from(sheet.cssRules)
                                    .map(rule => rule.cssText)
                                    .join('\n');
                            } catch (e) {
                                return '';
                            }
                        })
                        .join('\n');
                    return `<style>\n${styles}\n</style>`;
                };

                const getScripts = () => {
                    return Array.from(document.scripts)
                        .map(script => script.outerHTML)
                        .join('\n');
                };

                let html = document.documentElement.outerHTML;
                
                if (includeStyles) {
                    const styles = getStyles();
                    html = html.replace('</head>', `${styles}\n</head>`);
                }
                
                if (includeScripts) {
                    const scripts = getScripts();
                    html = html.replace('</body>', `${scripts}\n</body>`);
                }

                return html;
            }, includeStyles, includeScripts);

            const filename = this.generateFilename('html_capture', 'html');
            const filepath = path.join(this.config.htmlDir, filename);

            let formattedHTML = html;
            if (format) {
                // Basic HTML formatting
                formattedHTML = html
                    .replace(/></g, '>\n<')
                    .replace(/(<[^>]+>)/g, (match) => {
                        return match.startsWith('</') ? `\n${match}` : match;
                    });
            }

            await fs.promises.writeFile(filepath, formattedHTML);
            return {
                success: true,
                filepath,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            if (retryCount < this.config.maxRetries) {
                console.error(`HTML capture failed, retrying (${retryCount + 1}/${this.config.maxRetries})...`);
                return this.captureHTML(page, { ...options, retryCount: retryCount + 1 });
            }
            throw error;
        }
    }

    async capturePDF(page, options = {}) {
        const {
            format = 'A4',
            landscape = false,
            printBackground = true,
            margin = { top: '20px', right: '20px', bottom: '20px', left: '20px' },
            retryCount = 0
        } = options;

        try {
            const pdf = await page.pdf({
                format,
                landscape,
                printBackground,
                margin
            });

            const filename = this.generateFilename('pdf_capture', 'pdf');
            const filepath = path.join(this.config.pdfDir, filename);
            
            await fs.promises.writeFile(filepath, pdf);
            return {
                success: true,
                filepath,
                timestamp: new Date().toISOString()
            };
        } catch (error) {
            if (retryCount < this.config.maxRetries) {
                console.error(`PDF capture failed, retrying (${retryCount + 1}/${this.config.maxRetries})...`);
                return this.capturePDF(page, { ...options, retryCount: retryCount + 1 });
            }
            throw error;
        }
    }

    async captureAll(page, options = {}) {
        const {
            screenshot = true,
            html = true,
            pdf = true,
            screenshotOptions = {},
            htmlOptions = {},
            pdfOptions = {}
        } = options;

        const results = {};

        if (screenshot) {
            results.screenshot = await this.captureScreenshot(page, screenshotOptions);
        }

        if (html) {
            results.html = await this.captureHTML(page, htmlOptions);
        }

        if (pdf) {
            results.pdf = await this.capturePDF(page, pdfOptions);
        }

        return results;
    }

    async captureElement(page, selector, options = {}) {
        const element = await page.$(selector);
        if (!element) {
            throw new Error(`Element not found: ${selector}`);
        }

        const {
            screenshot = true,
            html = true,
            screenshotOptions = {},
            htmlOptions = {}
        } = options;

        const results = {};

        if (screenshot) {
            results.screenshot = await this.captureScreenshot(page, {
                ...screenshotOptions,
                element
            });
        }

        if (html) {
            results.html = await this.captureHTML(page, {
                ...htmlOptions,
                element
            });
        }

        return results;
    }
}

module.exports = CaptureManager; 