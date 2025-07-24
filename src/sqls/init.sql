create table service.workflow
(
    service_id   varchar               not null
        constraint workflow_pk
            primary key,
    minutes_left integer default 10000 not null,
    external_id  varchar(32)
);

comment on table service.workflow is 'таблица со счетчиками минут до отправки сервисных sms';

comment on column service.workflow.service_id is 'Id модема';

comment on column service.workflow.external_id is 'id telegram или другие для внешней связи';


create table service.sms_log
(
    id            bigserial
        primary key,
    sender        varchar not null,
    content       text    not null,
    received_date timestamp default now(),
    partial       jsonb,
    service_id    varchar   default 'huawey modem'::character varying
        constraint sms_log_service_id_wf_fk
            references service.workflow
);
