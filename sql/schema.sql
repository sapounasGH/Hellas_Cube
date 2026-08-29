-- HELLAS_CUBE SQL PREVIEW FILE
-- this is a file about the SQL that was and is being executed for Hellas_Cube

CREATE TABLE public.users (
	user_id uuid NOT NULL,
	"password" varchar NOT NULL,
	declared_geo_json json NULL,
	"email" public."email" NOT NULL,
	CONSTRAINT user_email_key UNIQUE (email),
	CONSTRAINT user_email_not_null NOT NULL email,
	CONSTRAINT user_id_pk PRIMARY KEY (user_id),
	CONSTRAINT user_password_not_null NOT NULL password,
	CONSTRAINT user_user_id_not_null NOT NULL user_id
);

CREATE DOMAIN public."email" AS character varying(255)
	COLLATE "default"
	CONSTRAINT email_check CHECK (VALUE::text ~* '^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$'::text);

CREATE TABLE public.request_log_file (
	request_id uuid NOT NULL,
	req_timestamp timestamptz DEFAULT now() NOT NULL,
	status varchar NOT NULL,
	status_timestamp timestamptz DEFAULT now() NOT NULL,
	CONSTRAINT request_log_file_req_timestamp_not_null NOT NULL req_timestamp,
	CONSTRAINT request_log_file_request_id_not_null NOT NULL request_id,
	CONSTRAINT request_log_file_status_not_null NOT NULL status,
	CONSTRAINT request_log_file_status_timestamp_not_null NOT NULL status_timestamp,
	CONSTRAINT request_pk PRIMARY KEY (request_id)
);

CREATE TABLE public.general_results (
	res_id uuid NOT NULL,
	analysis varchar NOT NULL,
	area_name varchar NOT NULL,
	res_json json NULL,
	date_range daterange NOT NULL,
	request_id uuid NULL,
	CONSTRAINT g_res_analysis_not_null NOT NULL analysis,
	CONSTRAINT g_res_area_id_not_null NOT NULL area_name,
	CONSTRAINT g_res_date_range_not_null NOT NULL date_range,
	CONSTRAINT g_res_pk PRIMARY KEY (res_id),
	CONSTRAINT g_res_res_id_not_null NOT NULL res_id,
	CONSTRAINT general_results_request_log_file_fk FOREIGN KEY (request_id) REFERENCES public.request_log_file(request_id)
);

CREATE TABLE public.user_results (
	res_id uuid NOT NULL,
	analysis varchar NOT NULL,
	date_range daterange NOT NULL,
	res_json json NULL,
	request_id uuid NOT NULL,
	user_id uuid NULL,
	CONSTRAINT default_res_analysis_not_null NOT NULL analysis,
	CONSTRAINT default_res_date_range_not_null NOT NULL date_range,
	CONSTRAINT default_res_pk PRIMARY KEY (res_id),
	CONSTRAINT default_res_res_id_not_null NOT NULL res_id,
	CONSTRAINT user_results_request_id_not_null NOT NULL request_id,
	CONSTRAINT user_results_request_log_file_fk FOREIGN KEY (request_id) REFERENCES public.request_log_file(request_id),
	CONSTRAINT user_results_users_fk FOREIGN KEY (user_id) REFERENCES public.users(user_id)
);

CREATE TABLE public.api_k (
	api_key varchar NOT NULL,
	exp_date timestamptz DEFAULT now() + '24:00:00'::interval NOT NULL,
	user_id varchar NOT NULL,
	CONSTRAINT api_k_pk PRIMARY KEY (api_key),
	CONSTRAINT owner_id_fk FOREIGN KEY (user_id) REFERENCES public.users(user_id)
);

--trigger to insert a slot in the api_k table for every user
CREATE OR REPLACE FUNCTION public.create_api_key_slot()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$
BEGIN
    -- Now we can insert a truly blank slot
    INSERT INTO public.api_k (user_id, api_key, exp_date)
    VALUES (NEW.user_id, NULL, NULL);
    
    RETURN NEW;
END;
$function$
;

CREATE TRIGGER trg_create_api_key_slot
AFTER INSERT ON public.users
FOR EACH ROW
EXECUTE FUNCTION public.create_api_key_slot();