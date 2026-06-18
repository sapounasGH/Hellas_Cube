--Needed a scheduler extention, to delete api keys every hour
CREATE EXTENSION pg_cron;
-- schedule job
--here are scheduling that every hour we are going to check if there are any expired keys (#note: we should check i we can lower it)
SELECT cron.schedule(
    'clear-expired-keys',         
    '0 * * * *',                  
    $$UPDATE api_k   SET is_active = false, exp_date = NULL  WHERE exp_date < NOW()$$
);

--deleting deactivated api_keys
SELECT cron.schedule(
    'sweep-expired-keys',         
    '0 1 * * *',                  
    $$DELETE FROM api_k 
      WHERE is_active=false$$
);
--unshcedule the job, if wrong
SELECT cron.unschedule('clear-expired-keys');
--see all shcedulers
SELECT * FROM cron.job;