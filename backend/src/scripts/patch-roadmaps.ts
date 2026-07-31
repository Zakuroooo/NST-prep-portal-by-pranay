import mongoose from 'mongoose';
import * as dotenv from 'dotenv';
import connectDB from '../config/db';
import Roadmap from '../models/UserRoadmap';
import Company from '../models/Company';

dotenv.config();

async function run() {
  await connectDB();
  
  const roadmaps = await Roadmap.find({});
  console.log(`Found ${roadmaps.length} existing roadmaps to patch.`);

  let patched = 0;
  for (const roadmap of roadmaps) {
    const company = await Company.findOne({ slug: roadmap.companySlug });
    if (!company) continue;

    const topTopics = company.topicFrequency?.map(t => t.topicName) || [];
    const fallbackTopics = ["Arrays", "Strings", "Dynamic Programming", "Graphs", "Trees", "Sorting", "Greedy", "Hash Table", "Binary Search", "Two Pointers"];
    
    const numWeeks = roadmap.weeksCommitted || 12;
    roadmap.weeks = Array.from({ length: numWeeks }).map((_, i) => {
      const topic = topTopics.length > 0 
        ? topTopics[i % topTopics.length] 
        : fallbackTopics[i % fallbackTopics.length];
      return {
        weekNumber: i + 1,
        topicLabel: topic,
        totalQuestions: 10,
        doneQuestions: 0,
        status: i === 0 ? 'active' : 'locked',
      };
    });

    await roadmap.save();
    patched++;
  }
  
  console.log(`Patched ${patched} roadmaps with real company topics.`);
  process.exit(0);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
