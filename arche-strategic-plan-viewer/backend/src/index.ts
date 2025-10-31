import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import cron from 'node-cron';
import { connectDB } from './config/database';
import profileRoutes from './api/profiles.routes';
// import { runExtraction } from './services/arche.service';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

connectDB();

app.use('/api/profiles', profileRoutes);

// Schedule the data extraction to run once a day at 3:00 AM
// cron.schedule('0 3 * * *', () => {
//   console.log('Starting nightly data extraction...');
//   runExtraction();
// });

app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
