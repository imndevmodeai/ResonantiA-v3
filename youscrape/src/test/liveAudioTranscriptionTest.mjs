import VLC from 'node-vlc-player';
import recorder from 'node-record-lv2';
import speech from '@google-cloud/speech';
import fs from 'fs';

async function transcribeFromVLC(videoUrl) {
    // Initialize VLC
    const vlc = new VLC({
        arguments: ['--no-video'] // Audio only mode
    });
    
    // Initialize audio recorder
    const audioStream = recorder.record({
        sampleRate: 16000,
        channels: 1,
        audioType: 'raw'
    });

    // Initialize Speech-to-Text client
    const client = new speech.SpeechClient();

    // Start playing video
    vlc.play(videoUrl);

    // Configure streaming recognition
    const request = {
        config: {
            encoding: 'LINEAR16',
            sampleRateHertz: 16000,
            languageCode: 'en-US',
        },
        interimResults: true,
    };

    // Create recognition stream
    const recognizeStream = client
        .streamingRecognize(request)
        .on('error', console.error)
        .on('data', data => {
            process.stdout.write(
                data.results[0] && data.results[0].alternatives[0]
                    ? `Transcription: ${data.results[0].alternatives[0].transcript}\n`
                    : '\n'
            );
        });

    // Pipe VLC audio output to recognition
    audioStream.pipe(recognizeStream);

    // Keep running for 5 minutes
    await new Promise(resolve => setTimeout(resolve, 300000));

    // Cleanup
    vlc.stop();
    audioStream.stop();
}

// Test URL
const videoUrl = 'https://www.youtube.com/watch?v=IMXRpbxifq8';
transcribeFromVLC(videoUrl); 