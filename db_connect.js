// db_connect.js (Node.js میں)
const { MongoClient } = require('mongodb');

const uri = "mongodb+srv://YOUR_USERNAME:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/";
const client = new MongoClient(uri);

async function connectToDB() {
    await client.connect();
    const db = client.db('DigiDSearch');
    const collection = db.collection('sites');
    
    // data.js کا ڈیٹا ڈالو
    const data = require('./data.js');
    await collection.insertMany(data);
    
    console.log("Data uploaded to MongoDB!");
    return collection;
}

module.exports = { connectToDB };
