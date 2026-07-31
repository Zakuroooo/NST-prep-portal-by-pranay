import { MongoClient } from 'mongodb';

async function run() {
  const uri = "mongodb://adityarajsharma7360_db_user:ahWf6zyvgC9YqzP7@ac-sz8jwd6-shard-00-00.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-01.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-02.wpzbzfx.mongodb.net:27017/placeprep_staging?tls=true&authSource=admin&replicaSet=atlas-xxp6q7-shard-0&retryWrites=true&w=majority&tlsInsecure=true";
  const client = new MongoClient(uri);
  try {
    await client.connect();
    console.log("Connected successfully using direct with tlsInsecure!");
    const db = client.db();
    const count = await db.collection('companies').countDocuments();
    console.log(`Companies: ${count}`);
  } catch (err) {
    console.error("Connection failed:", err.message);
  } finally {
    await client.close();
  }
}
run();
