-- --------
-- USER TABLE
-- --------
DROP TABLE IF EXISTS "users";
CREATE TABLE "users"(
"username" TEXT not NULL,
"password" TEXT not NULL,
PRIMARY KEY("username" ASC)
);

-- ------------------------------------------------
-- CHAT HISTORY TABLE
-- only reserve chat history when users is off-line
-- ------------------------------------------------
DROP TABLE IF EXISTS "history_private_text";
CREATE TABLE "history_private_text"(
"id" INTEGER not NULL,
"target_username" TEXT not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"text" TEXT not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("target_username") REFERENCES "users"("username"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);

DROP TABLE IF EXISTS "history_private_image";
CREATE TABLE "history_private_image"(
"id" INTEGER not NULL,
"target_username" TEXT not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"img" BLOB not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("target_username") REFERENCES "users"("username"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);

DROP TABLE IF EXISTS "history_group_text";
CREATE TABLE "history_group_text"(
"id" INTEGER not NULL,
"group_id" INTEGER not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"text" TEXT not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);

DROP TABLE IF EXISTS "history_group_image";
CREATE TABLE "history_group_image"(
"id" INTEGER not NULL,
"group_id" INTEGER not NULL,
"source_username" TEXT not NULL,
"time" DATETIME not NULL,
"img" BLOB not NULL,
PRIMARY KEY("id" ASC),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("source_username") REFERENCES "users"("username")
);

-- -----------------------------------------------
-- GROUP USERS TABLE
-- -----------------------------------------------
DROP TABLE IF EXISTS "group_member";
CREATE TABLE "group_member"(
"group_id" INTEGER NOT NULL,
"username" TEXT NOT NULL,
PRIMARY KEY("group_id" ASC, "username"),
FOREIGN KEY ("group_id") REFERENCES "groups"("group_id"),
FOREIGN KEY ("username") REFERENCES "users"("username")
);

-- ----------------------------------------------
-- GROUP TABLE
-- ----------------------------------------------
DROP TABLE IF EXISTS "groups";
CREATE TABLE "groups"(
"group_id" INTEGER NOT NULL,
"group_name" TEXT NOT NULL,
PRIMARY KEY("group_id" ASC)
);

-- --------------------------------------------
-- FRIEND TABLE
-- ---------------------------------------------
DROP TABLE IF EXISTS "friends";
CREATE TABLE "friends"(
"username1" TEXT NOT NULL,
"username2" TEXT NOT NULL,
PRIMARY KEY("username1", "username2"),
FOREIGN KEY ("username1") REFERENCES "users"("username"),
FOREIGN KEY ("username2") REFERENCES "users"("username")
);