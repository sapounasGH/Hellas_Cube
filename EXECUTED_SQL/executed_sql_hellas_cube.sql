-- HELLAS_CUBE SQL PREVIEW FILE
-- this is a file about the SQL that was and is being executed for Hellas_Cube

CREATE TABLE public."user" (
	user_id varchar NOT NULL,
	"password" varchar NOT NULL,
	declared_geo_json json NULL,
	email public.email NOT NULL,
	CONSTRAINT user_email_key UNIQUE (email),
	CONSTRAINT user_id_pk PRIMARY KEY (user_id)
);

CREATE TABLE public.request_log_file (
	request_id varchar NOT NULL,
	req_timestamp timestamptz DEFAULT now() NOT NULL,
	status varchar NULL,
	status_timestamp timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT request_pk PRIMARY KEY (request_id)
);

CREATE TABLE public.g_res (
	res_id varchar NOT NULL,
	analysis varchar NOT NULL,
	area_id varchar NOT NULL,
	res_json json NULL,
	request_id varchar NULL,
	date_range daterange NOT NULL,
	CONSTRAINT g_res_pk PRIMARY KEY (res_id),
	CONSTRAINT request_id_fk FOREIGN KEY (request_id) REFERENCES public.request_log_file(request_id)
);

CREATE TABLE public.default_res (
	user_id varchar NOT NULL,
	res_id varchar NOT NULL,
	analysis varchar NOT NULL,
	date_range daterange NOT NULL,
	res_json json NULL,
	request_id varchar NULL,
	CONSTRAINT default_res_pk PRIMARY KEY (res_id),
	CONSTRAINT request_fk FOREIGN KEY (request_id) REFERENCES public.request_log_file(request_id),
	CONSTRAINT user_id FOREIGN KEY (user_id) REFERENCES public."user"(user_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE DOMAIN public."email" AS character varying(255)
	COLLATE "default"
	CONSTRAINT email_check CHECK (VALUE::text ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'::text);

CREATE TABLE public.api_k (
	api_key varchar NOT NULL,
	exp_date timestamptz DEFAULT now() + '24:00:00'::interval NOT NULL,
	user_id varchar NOT NULL,
	CONSTRAINT api_k_pk PRIMARY KEY (api_key),
	CONSTRAINT owner_id_fk FOREIGN KEY (user_id) REFERENCES public.users(user_id)
);

--trigger to insert a slot in the api_k table for every user
CREATE OR REPLACE FUNCTION public.create_api_key_slot()
RETURNS TRIGGER AS $$
BEGIN
    -- Now we can insert a truly blank slot
    INSERT INTO public.api_k (user_id, api_key, exp_date)
    VALUES (NEW.user_id, NULL, NULL);
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_create_api_key_slot
AFTER INSERT ON public.users
FOR EACH ROW
EXECUTE FUNCTION public.create_api_key_slot();

--Needed a scheduler extention, to delete api keys every hour
CREATE EXTENSION pg_cron;
-- schedule job
SELECT cron.schedule(
    'clear-expired-keys',         
    '0 * * * *',                  
    $$UPDATE api_k 
      SET api_key = NULL, 
          exp_date = NULL 
      WHERE exp_date < NOW()$$
);
--unshcedule the job, if wrong
SELECT cron.unschedule('clear-expired-keys');
--see all shcedulers
SELECT * FROM cron.job;
