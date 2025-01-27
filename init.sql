-- target table

create table service.sms_log (
    id bigserial PRIMARY KEY,
    service_id varchar default 'huawey modem',
    sender varchar not null,
    content text not null,
    received_date timestamp without time zone default now(),
    partial jsonb
)