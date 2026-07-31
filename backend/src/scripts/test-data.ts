import fs from 'fs';
import path from 'path';

// Define paths to the local JSON files
const questionsPath = path.join(__dirname, '../data/questions.json');
const companiesPath = path.join(__dirname, '../data/companies.json');

function runProofOfConcept() {
  console.log("==========================================");
  console.log("🚀 PLACEPREP BACKEND DATA PROOF OF CONCEPT");
  console.log("==========================================\n");

  // 1. Read Companies Data
  const companiesData = JSON.parse(fs.readFileSync(companiesPath, 'utf8'));
  console.log(`✅ Successfully loaded ${companiesData.length} companies from local JSON.`);
  
  // Show a sample company (Google)
  const google = companiesData.find((c: any) => c.slug === 'google');
  if (google) {
    console.log(`\n🏢 SAMPLE COMPANY: ${google.name}`);
    console.log(`   - Industry Category: ${google.category}`);
    console.log(`   - Difficulty Spread: ${google.difficultyDistribution.Easy}% Easy, ${google.difficultyDistribution.Medium}% Medium, ${google.difficultyDistribution.Hard}% Hard`);
    
    // Show top 3 topics
    console.log(`   - Top 3 Interview Topics:`);
    google.topicFrequency.slice(0, 3).forEach((topic: any, index: number) => {
      console.log(`       ${index + 1}. ${topic.topicName} (${topic.frequencyPct}%)`);
    });
  }

  // 2. Read Questions Data
  const questionsData = JSON.parse(fs.readFileSync(questionsPath, 'utf8'));
  console.log(`\n✅ Successfully loaded ${questionsData.length} questions from local JSON.`);

  // Find 3 hard Google questions
  const googleHardQuestions = questionsData.filter((q: any) => 
    q.companySlug === 'google' && q.difficulty === 'Hard'
  );

  console.log(`\n📝 SAMPLE DATA: Found ${googleHardQuestions.length} Hard questions for Google. Here are the first 3:`);
  googleHardQuestions.slice(0, 3).forEach((q: any, index: number) => {
    console.log(`   ${index + 1}. [${q.difficulty}] ${q.problemSummary}`);
    console.log(`      Topics: ${q.topics.join(', ')}`);
    console.log(`      LeetCode URL: ${q.leetcodeUrl}`);
  });
  
  console.log("\n==========================================");
  console.log("Proof of concept complete. The backend can successfully process the scraped data!");
  console.log("==========================================");
}

runProofOfConcept();
