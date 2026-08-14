-- Calixta | Configuración de alertas por correo + envíos programados
-- Ejecutar después de las migraciones de catálogos admin.

create table if not exists public.config_alertas_email (
  id text primary key default 'DEFAULT',
  activo boolean not null default false,
  envios_por_dia integer not null default 1 check (envios_por_dia between 1 and 3),
  horario_1 time not null default '08:00',
  horario_2 time not null default '14:00',
  horario_3 time not null default '18:00',
  solo_si_hay_alertas boolean not null default true,
  zona_horaria text not null default 'America/Bogota',
  fecha_actualizacion timestamptz not null default now()
);

insert into public.config_alertas_email (id)
values ('DEFAULT')
on conflict (id) do nothing;

create table if not exists public.alertas_destinatarios (
  id text primary key,
  email text not null,
  nombre text not null default '',
  activo boolean not null default true,
  fecha_registro timestamptz not null default now(),
  constraint alertas_destinatarios_email_unique unique (email)
);

create index if not exists idx_alertas_destinatarios_activo
  on public.alertas_destinatarios (activo, email);

create table if not exists public.alertas_envios_log (
  id bigserial primary key,
  slot integer not null check (slot between 1 and 3),
  fecha date not null,
  enviado_en timestamptz not null default now(),
  destinatarios text not null default '',
  productos_count integer not null default 0,
  exito boolean not null default true,
  mensaje text not null default '',
  constraint alertas_envios_log_fecha_slot_unique unique (fecha, slot)
);

create index if not exists idx_alertas_envios_log_enviado_en
  on public.alertas_envios_log (enviado_en desc);
