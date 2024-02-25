const express = require('express');
const bodyParser = require('body-parser');
const neo4j = require('neo4j-driver');

const app = express();
app.use(bodyParser.json());

const driver = neo4j.driver('bolt://localhost:7687', neo4j.auth.basic('neo4j', 'yourStrongPasswordHere'));
const session = driver.session();

app.get('/', (req, res) => {
    res.send('Hello, World!');
});

app.get('/users', async (req, res) => {
    const result = await session.run('MATCH (u:User) RETURN u.username AS username, u.email AS email, u.user_id AS user_id');
    res.json(result.records.map(record => record.toObject()));
});

app.post('/users', async (req, res) => {
    const data = req.body;
    const maxUserIdResult = await session.run('MATCH (u:User) RETURN max(u.user_id) AS max_user_id');
    const maxUserId = maxUserIdResult.records[0].get('max_user_id');
    const userId = maxUserId ? maxUserId.toNumber() + 1 : 1;

    const createUserResult = await session.run('CREATE (u:User {username: $username, email: $email, user_id: $user_id}) RETURN u.user_id AS user_id', {
        username: data.username,
        email: data.email,
        user_id: neo4j.int(userId)
    });
    const createdUserId = createUserResult.records[0].get('user_id');
    res.json({ username: data.username, email: data.email, user_id: createdUserId.toNumber() });
});

app.put('/users/:user_id', async (req, res) => {
    const userId = parseInt(req.params.user_id);
    const data = req.body;

    const updateUserResult = await session.run('MATCH (u:User {user_id: $user_id}) SET u.username = $username, u.email = $email RETURN u.user_id AS user_id', {
        user_id: neo4j.int(userId),
        username: data.username,
        email: data.email
    });

    if (updateUserResult.records.length === 0) {
        res.status(404).json({ error: 'User not found' });
    } else {
        res.json({ username: data.username, email: data.email, user_id: userId });
    }
});

app.delete('/users/:user_id', async (req, res) => {
    const userId = parseInt(req.params.user_id);

    const deleteUserResult = await session.run('MATCH (u:User {user_id: $user_id}) DELETE u RETURN count(u) AS count', {
        user_id: neo4j.int(userId)
    });

    if (deleteUserResult.records[0].get('count').toNumber() === 0) {
        res.status(404).json({ error: 'User not found' });
    } else {
        res.json({ message: 'User deleted' });
    }
});

app.get('/users/posts', async (req, res) => {
    const result = await session.run(`
        MATCH (u:User)-[:POSTED]->(p:Post)
        RETURN p.content AS content, u.email AS email, u.user_id AS user_id, u.username AS username
    `);
    res.json(result.records.map(record => record.toObject()));
});

app.get('/users/comments', async (req, res) => {
    const result = await session.run(`
        MATCH (u:User)-[c:COMMENTED]->(p:Post)
        RETURN u.email AS email, u.user_id AS user_id, u.username AS username, c.comment_text AS comment_text
    `);
    const commentsUserMapping = {};

    result.records.forEach(record => {
        const data = record.toObject();
        if (!commentsUserMapping[data.user_id]) {
            commentsUserMapping[data.user_id] = { user: { email: data.email, user_id: data.user_id, username: data.username }, comments: [] };
        }
        commentsUserMapping[data.user_id].comments.push({ comment_text: data.comment_text });
    });

    res.json(Object.values(commentsUserMapping));
});

app.get('/comments', async (req, res) => {
    const result = await session.run(`
        MATCH (u:User)-[c:COMMENTED]->(p:Post)
        RETURN u.username AS username, p.content AS post_content, c.comment_text AS comment_text, c.timestamp AS timestamp
    `);
    res.json(result.records.map(record => record.toObject()));
});

app.get('/posts/likes', async (req, res) => {
    const result = await session.run(`
        MATCH (u:User)-[:POSTED]->(p:Post)<-[:LIKED]-(l:User)
        RETURN p.content AS content, l.user_id AS user_id
    `);
    const likesPostMapping = {};

    result.records.forEach(record => {
        const data = record.toObject();
        if (!likesPostMapping[data.content]) {
            likesPostMapping[data.content] = { post: data.content, likes: [] };
        }
        likesPostMapping[data.content].likes.push({ user_id: data.user_id });
    });

    res.json(Object.values(likesPostMapping));
});

app.get('/posts/likes/users', async (req, res) => {
    const result = await session.run(`
        MATCH (u:User)-[:POSTED]->(p:Post)<-[:LIKED]-(l:User)
        RETURN p.content AS content, l.user_id AS user_id, l.username AS username, l.email AS email
    `);
    const likesPostMapping = {};

    result.records.forEach(record => {
        const data = record.toObject();
        if (!likesPostMapping[data.content]) {
            likesPostMapping[data.content] = { post: data.content, likes: [] };
        }
        likesPostMapping[data.content].likes.push({ user_id: data.user_id, username: data.username, email: data.email });
    });

    res.json(Object.values(likesPostMapping));
});

app.listen(8022, () => {
    console.log('Server running on port 8021');
});
