-- Add pinned column to scores table
ALTER TABLE scores ADD COLUMN pinned TINYINT(1) DEFAULT 0 NOT NULL AFTER perfect;
CREATE INDEX scores_pinned_index ON scores (pinned);
CREATE INDEX scores_userid_pinned_index ON scores (userid, pinned);
