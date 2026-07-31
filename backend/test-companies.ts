import mongoose from 'mongoose';
import * as dotenv from 'dotenv';
import connectDB from './src/config/db';
import { companyRepository } from './src/repositories/company.repository';

dotenv.config();

async function run() {
  process.env.MONGODB_URI = "mongodb://adityarajsharma7360_db_user:ahWf6zyvgC9YqzP7@ac-sz8jwd6-shard-00-00.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-01.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-02.wpzbzfx.mongodb.net:27017/placeprep_staging?tls=true&authSource=admin&replicaSet=atlas-xxp6q7-shard-0&retryWrites=true&w=majority&tlsInsecure=true";
  await connectDB();
  try {
    const companies = await companyRepository.findAll({});
    console.log(`Success! Found ${companies.length} companies.`);
    console.log(companies[0]);
  } catch (error) {
    console.error("Aggregation Error:");
    console.error(error);
  }
  process.exit(0);
}
run();
