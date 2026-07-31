const mongoose = require('mongoose');
const uri = "mongodb://adityarajsharma7360_db_user:ahWf6zyvgC9YqzP7@ac-sz8jwd6-shard-00-00.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-01.wpzbzfx.mongodb.net:27017,ac-sz8jwd6-shard-00-02.wpzbzfx.mongodb.net:27017/placeprep_staging?ssl=true&authSource=admin&replicaSet=atlas-xxp6q7-shard-0&retryWrites=true&w=majority";

mongoose.connect(uri, { serverSelectionTimeoutMS: 5000, family: 4 })
  .then(() => {
    console.log("Connected successfully with family: 4!");
    process.exit(0);
  })
  .catch(err => {
    console.error("Failed:", err);
    process.exit(1);
  });
