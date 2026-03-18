const db = require("./db");

const express = require("express");
const app = express();

// Middleware
app.use(express.json());

app.get("/test-db", (req, res) => {
  const db = require("./db");

  db.query("SELECT 1 + 1 AS result", (err, results) => {
    if (err) {
      return res.send("DB error");
    }
    res.json(results);
  });
});
// Start server
app.listen(3000, () => {
  console.log("Server running on port 3000");
});