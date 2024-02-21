const express = require('express');
const { MongoClient } = require('mongodb');

const app = express();
const client = new MongoClient('mongodb://localhost:27017/');
const db = client.db('socialmedia');
const usersCollection = db.collection('users');

app.use(express.json());

app.get('/', (req, res) => {
  res.send('Hello, World!');
});

app.get('/users', async (req, res) => {
  try {
    const users = await usersCollection.find().toArray();
    const result = users.map((user) => ({
      username: user.username,
      email: user.email,
      user_id: user.user_id,
    }));
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.post('/users', async (req, res) => {
    const lastUser = await usersCollection.find().sort({ user_id: -1 }).limit(1).toArray();
    const user_id = lastUser.length ? lastUser[0].user_id + 1 : 1;
    const user = {
      username: req.body.username,
      email: req.body.email,
      user_id,
      posts: [],
    };
    await usersCollection.insertOne(user);
    res.json({ username: req.body.username, email: req.body.email, user_id });
});

app.put('/users/:user_id', async (req, res) => {
  try {
    const user_id = parseInt(req.params.user_id);
    const user = await usersCollection.findOne({ user_id });
    if (!user) {
      res.status(404).json({ error: 'User not found' });
      return;
    }
    await usersCollection.updateOne({ user_id }, { $set: { username: req.body.username, email: req.body.email } });
    res.json({ username: req.body.username, email: req.body.email, user_id });
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.delete('/users/:user_id', async (req, res) => {
  try {
    const user_id = parseInt(req.params.user_id);
    const user = await usersCollection.findOne({ user_id });
    if (!user) {
      res.status(404).json({ error: 'User not found' });
      return;
    }
    await usersCollection.deleteOne({ user_id });
    res.json({ message: 'User deleted' });
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/users/posts', async (req, res) => {
  try {
    const users = await usersCollection.find().toArray();
    const result = [];
    for (const user of users) {
      for (const post of user.posts) {
        const postWithUser = {
          content: post.content,
          user: {
            email: user.email,
            user_id: user.user_id,
            username: user.username,
          },
        };
        result.push(postWithUser);
      }
    }
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/users/comments', async (req, res) => {
  try {
    const users = await usersCollection.find().toArray();
    const commentsUserIdMapping = {};
    for (const user of users) {
      for (const post of user.posts) {
        for (const comment of post.comments) {
          if (!(comment.user_id in commentsUserIdMapping)) {
            commentsUserIdMapping[comment.user_id] = [];
          }
          commentsUserIdMapping[comment.user_id].push({ comment_text: comment.comment_text });
        }
      }
    }
    const result = [];
    for (const [user_id, comments] of Object.entries(commentsUserIdMapping)) {
      const user = await usersCollection.findOne({ user_id: parseInt(user_id) });
      result.push({ user: { email: user.email, user_id: user.user_id, username: user.username }, comments });
    }
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/posts/likes', async (req, res) => {
  try {
    const users = await usersCollection.find().toArray();
    const likesPostIdMapping = {};
    for (const user of users) {
      for (const post of user.posts) {
        for (const like of post.likes) {
          if (!(post.content in likesPostIdMapping)) {
            likesPostIdMapping[post.content] = [];
          }
          likesPostIdMapping[post.content].push({ user_id: like.user_id });
        }
      }
    }
    const result = [];
    for (const [post, likes] of Object.entries(likesPostIdMapping)) {
      result.push({ post, likes });
    }
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

app.get('/posts/likes/users', async (req, res) => {
  try {
    const users = await usersCollection.find().toArray();
    const likesPostIdMapping = {};
    for (const user of users) {
      for (const post of user.posts) {
        for (const like of post.likes) {
          if (!(post.content in likesPostIdMapping)) {
            likesPostIdMapping[post.content] = [];
          }
          const likedUser = await usersCollection.findOne({ user_id: like.user_id });
          likesPostIdMapping[post.content].push({ user_id: like.user_id, username: likedUser.username, email: likedUser.email });
        }
      }
    }
    const result = [];
    for (const [post, likes] of Object.entries(likesPostIdMapping)) {
      result.push({ post, likes });
    }
    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

const port = 8012;
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});
