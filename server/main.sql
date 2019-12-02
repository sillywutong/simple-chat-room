-- --------
-- USER TABLE
-- --------
DROP TABLE IF EXISTS "main"."users";
CREATE TABLE "users"(
"id" INTEGER not NULL,
"username" TEXT not NULL,
"password" TEXT not NULL,
PRIMARY KEY("id" ASC)
);

-- ------------------------------------------------
-- CHAT HISTORY TABLE
-- only reserve chat history when users is off-line
-- ------------------------------------------------
DROP TABLE IF EXISTS "main"."history";
CREATE TABLE "history"(
"id" INTEGER not NULL,
"type" INTEGER not NULL,
"target_id" INTEGER not NULL,
"source_id" INTEGER not NULL,
"msg" BLOB,
PRIMARY KEY("id" ASC)    
);
/* history id 用来标识一条记录，否则4个字段都是主键 */
/* msg 里面包含了聊天记录的message: {type :, data:}、target name， source name 和 time 部分 */

-- -----------------------------------------------
-- GROUP USERS TABLE
-- -----------------------------------------------
DROP TABLE IF EXISTS "main"."group_member";
CREATE TABLE "group_member"(
"group_id" INTEGER NOT NULL,
"user_id" INTEGER NOT NULL,
PRIMARY KEY("group_id" ASC, "user_id")
);

-- ----------------------------------------------
-- GROUP TABLE
-- ----------------------------------------------
DROP TABLE IF EXISTS "main"."groups";
CREATE TABLE "groups"(
"group_id" INTEGER NOT NULL,
"group_name" TEXT NOT NULL,
PRIMARY KEY("group_id" ASC)
);

-- --------------------------------------------
-- FRIEND TABLE
-- ---------------------------------------------
DROP TABLE IF EXISTS "main"."friends";
CREATE TABLE "friends"(
"user_id1" INTEGER NOT NULL,
"user_id2" INTEGER NOT NULL,
PRIMARY KEY("user_id1", "user_id2")
);
/* 不可以删除好友 */