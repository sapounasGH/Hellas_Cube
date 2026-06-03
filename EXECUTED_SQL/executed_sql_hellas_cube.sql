-- HELLAS_CUBE SQL PREVIEW FILE
-- this is a file about the SQL that was and is being executed for Hellas_Cube

CREATE TABLE public."user" (
	user_id varchar NOT NULL,
	user_api_key varchar NULL,
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
