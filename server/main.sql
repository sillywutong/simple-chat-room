-- --------
-- USER TABLE
-- --------
DROP TABLE IF EXISTS "main"."users";
CREATE TABLE "users"(
"id" INTEGER not NULL,
"username" TEXT not NULL,
"password" TEXT not NULL,
"nickname" TEXT not NULL,
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
"target_name" INTEGER not NULL,
"source_name" INTEGER not NULL,
"msg" BLOB,
PRIMARY KEY("id" ASC)    
);
/* history id 用来标识一条记录，否则4个字段都是主键 */


-- -----------------------------------------------
-- GROUP TABLE
-- -----------------------------------------------
DROP TABLE IF EXISTS "main"."group";
CREATE TABLE "group"(
"group_id" INTEGER NOT NULL,
"user_id" INTEGER NOT NULL,
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
