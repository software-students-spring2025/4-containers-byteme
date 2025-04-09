/*creates dummy data for mongodb database when first initialized*/

print("Running mongo-init.js...");

db = db.getSiblingDB("ml_app_db");

// Create a users collection with sample users
db.users.insertMany([
    {
      _id: ObjectId("661094fcf7a31f001e1a1111"),
      username: "kchan",
      email: "kchan@example.com",
      password: "hashed_password_123"
    },
    {
      _id: ObjectId("661094fcf7a31f001e1a2222"),
      username: "jdoe",
      email: "jdoe@example.com",
      password: "hashed_password_456"
    }
]);
  
  // Create entries collection with journal entries
db.entries.insertMany([
    {
      _id: ObjectId("661095fcf7a31f001e1a3333"),
      user_id: ObjectId("661094fcf7a31f001e1a1111"), // kchan
      text: "Today was such a good day. I finally finished my project!",
      timestamp: ISODate("2025-04-05T20:30:00Z"),
      sentiment: {
        negative: 0.01,
        neutral: 0.15,
        positive: 0.84,
        composite_score: 4.53
      }
    },
    {
      _id: ObjectId("661095fcf7a31f001e1a4444"),
      user_id: ObjectId("661094fcf7a31f001e1a2222"), // jdoe
      text: "Feeling overwhelmed by deadlines and meetings.",
      timestamp: ISODate("2025-04-05T21:00:00Z"),
      sentiment: {
        negative: 0.65,
        neutral: 0.25,
        positive: 0.10,
        composite_score: 2.05
      }
    }
]);