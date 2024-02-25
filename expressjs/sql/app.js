const express = require("express");
const { Sequelize, DataTypes } = require("sequelize");

// Initialize Express app
const app = express();
app.use(express.json());

// Set up Sequelize connection
const sequelize = new Sequelize("socialmedia", "root", "example", {
  host: "mysql",
  dialect: "mysql",
});

// Define models
const User = sequelize.define(
  "users",
  {
    user_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    username: { type: DataTypes.STRING, unique: true },
    email: { type: DataTypes.STRING, unique: true },
  },
  {
    timestamps: false,
  }
);

const Post = sequelize.define(
  "Post",
  {
    post_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    content: { type: DataTypes.TEXT },
    user_id: { type: DataTypes.INTEGER },
  },
  {
    tableName: "posts",
    timestamps: false,
  }
);

const Comment = sequelize.define(
  "Comment",
  {
    comment_id: {
      type: DataTypes.INTEGER,
      primaryKey: true,
      autoIncrement: true,
    },
    user_id: { type: DataTypes.INTEGER },
    post_id: { type: DataTypes.INTEGER },
    comment_text: { type: DataTypes.TEXT },
  },
  {
    tableName: "comments",
    timestamps: false,
  }
);

const Like = sequelize.define(
  "Like",
  {
    like_id: { type: DataTypes.INTEGER, primaryKey: true, autoIncrement: true },
    // Empty for now, assuming it's just a like without additional data
  },
  {
    tableName: "likes",
    timestamps: false,
  }
);

// Define relationships
Post.belongsTo(User, { foreignKey: "user_id" });
User.hasMany(Post, { foreignKey: "user_id" });

User.hasMany(Comment, { foreignKey: "user_id" });
Comment.belongsTo(User, { foreignKey: "user_id" });
Post.hasMany(Comment, { foreignKey: "post_id" });
Comment.belongsTo(Post, { foreignKey: "post_id" });

User.hasMany(Like, { foreignKey: "user_id" });
Like.belongsTo(User, { foreignKey: "user_id" });
Post.hasMany(Like, { foreignKey: "post_id" });
Like.belongsTo(Post, { foreignKey: "post_id" });

sequelize
  .authenticate()
  .then(() => {
    console.log("Connection has been established successfully.");
  })
  .catch((error) => {
    console.error("Unable to connect to the database: ", error);
  });

// Express routes
app.get("/users", async (req, res) => {
  try {
    const users = await User.findAll();
    res.json(users);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

app.post("/users", async (req, res) => {
  try {
    const user = await User.create(req.body);
    res.status(201).json(user);
  } catch (error) {
    res.status(400).send(error.message);
  }
});

// update user
app.put("/users/:id", async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) {
      return res.status(404).send("User not found");
    }
    await user.update(req.body);
    res.json(user);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// delete user

app.delete("/users/:id", async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) {
      return res.status(404).send("User not found");
    }
    await user.destroy();
    res.status(204).send("User deleted");
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// complex query to get the user and their posts
app.get("/users/posts", async (req, res) => {
  try {
    const users = await User.findAll({
      include: Post,
    });
    res.json(users);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

// compelex query to get the user and their comments and the post they commented on
app.get("/users/comments", async (req, res) => {
  try {
    const users = await User.findAll({
      include: { model: Comment },
    });
    res.json(users);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

app.get("/posts/likes", async (req, res) => {
  try {
    const posts = await Post.findAll({
      include: Like,
    });
    res.json(posts);
  } catch (error) {
    res.status(500).send(error.message);
  }
});

app.get('/posts/likes/users', async (req, res) => {
    try {
        const posts = await Post.findAll({
        include: {
            model: Like,
            include: User
        }
        });
        res.json(posts);
    } catch (error) {
        res.status(500).send(error.message);
    }
});

// Start Express server
const PORT = 8002;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
